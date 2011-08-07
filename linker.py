#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Author: Osman Karagöz
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import os
import sys
import glob
import shutil
import pwd
import time

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

AppDir = ".disthomelinker"

BlackList = [AppDir, ".pulse", ".gvfs"]

try:
    releaseFile = open("/etc/lsb-release", "r")
    releaseLines = releaseFile.readlines()
    releaseFile.close()
    
    for i in releaseLines:
        if "DISTRIB_DESCRIPTION" in i:
            DistName = i.split("=")[1].replace('"',"").replace("\n","")

except:
    DistName = 0

def getUsersOnDist():
    usersIds = []
    allUsers = pwd.getpwall()
    for i in allUsers:
        if "/home/" in i.pw_dir and os.path.isdir(i.pw_dir):
            usersIds.append(i.pw_uid)
            
    return usersIds
    
class Linker(object):
    def __init__(self, userid=None):
        self.userId = userid
        i = pwd.getpwuid(self.userId)
        self.userGid = i.pw_gid
        self.userDir = i.pw_dir
        self.UAD = os.path.join(self.userDir, AppDir, DistName)
        self.statuses = {}
        self.blackList = BlackList[:]
        self.readUserBlackList()
        self.readLoginStatus()
                
    def readUserBlackList(self):
        if os.path.exists(os.path.join(self.userDir,AppDir)):
            os.chdir(os.path.join(self.userDir,AppDir))
            if os.path.exists("blacklist"):
                bLFile = open("blacklist", "r")
                bLLines = bLFile.readlines()
                bLFile.close()
                for i in bLLines:
                    if i[0] != "#":
                        self.blackList.append(i.replace("\n","").strip())
    
    def readLoginStatus(self):
        if os.path.exists(os.path.join(self.userDir,AppDir)):
            os.chdir(os.path.join(self.userDir,AppDir))
            if os.path.exists("status.tmp"):
                statFile = open("status.tmp", "r")
                statLines = statFile.readlines()
                statFile.close()
                for i in statLines:
                    if i[0] != "#":
                        key, value = i.split(":")
                        self.statuses[key.strip()] = value.strip()
        
    def writeLoginStatus(self):
        os.chdir(os.path.join(self.userDir,AppDir))
        statFile = open("status.tmp", "w")
        statFile.write("# This file generated automatically\n#\n# DO NOT EDIT/REMOVE THIS FILE\n#\n")
        
        statFile.write("DistName : %s\n"% DistName)
        statFile.close()
        
    def firstStart(self):
        # create an empty blacklist
        os.chdir(os.path.join(self.userDir,AppDir))
        bLFile = open("blacklist", "w")
        bLFile.write("# Add the names line by line to be blacklisted.\n#\n")
        bLFile.close()
        
    def moveDirs(self):
        os.chdir(self.userDir)
        
        if not os.path.exists(AppDir):
            os.mkdir(AppDir)
            os.chown(AppDir, self.userId, self.userGid)
            self.firstStart()
                
        if not os.path.exists(self.UAD):
            os.mkdir(self.UAD)
            os.chown(self.UAD, self.userId, self.userGid)
        
        LastHomeList = glob.glob(".*")
        OldHomeList = os.listdir(self.UAD)
        
        NeedDelete = []
        NeedMove = []
        
        for i in LastHomeList:
            if i in self.blackList:
                pass
            elif i in OldHomeList and not os.path.islink(i):
                NeedDelete.append(i)
                NeedMove.append(i)
            elif i not in OldHomeList:
                NeedMove.append(i)
                
        for i in OldHomeList:
            if i not in LastHomeList:
                NeedDelete.append(i)
                
        for i in NeedDelete:
            os.chdir(self.UAD)
            if os.path.isdir(i):
                shutil.rmtree(i)
            else:
                os.remove(i)
                
        os.chdir(self.userDir)
        for i in NeedMove:
            shutil.move(i, os.path.join(self.UAD, i))
            
    def link(self):
        os.chdir(self.userDir)
        HomeList = os.listdir(self.UAD)
        
        for i in HomeList:
            if os.path.exists(i):
                if os.path.islink(i):
                    os.unlink(i)
                elif os.path.isdir(i):
                    shutil.rmtree(i)
                else:
                    os.remove(i)
                    
            os.symlink(os.path.join(self.UAD, i), i)
            time.sleep(0.01)
            
        self.writeLoginStatus()
            
    def unlink(self):
        os.chdir(self.userDir)
        
        if "DistName" in self.statuses.keys() and self.statuses["DistName"] != DistName:
            os.chdir(AppDir)
            if not os.path.exists(DistName):
                os.rename(self.statuses["DistName"], DistName)
            else:
                print "I don't understand problem! Check the contents of the directory..."
            os.chdir(self.userDir)
        
        self.moveDirs()
        
        HomeList = glob.glob(".*")
        
        for i in HomeList:
            if i in self.blackList:
                pass
            elif os.path.islink(i):
                os.unlink(i)
                time.sleep(0.01)
            else:
                print "Is this a bug?"
        
        if os.path.exists("%s/%s/status.tmp"% (self.userDir, AppDir)):
            os.remove("%s/%s/status.tmp"% (self.userDir, AppDir))

if __name__ == "__main__":
    usersIds = getUsersOnDist()
    
    if "start" or "stop" in sys.argv:
        for i in usersIds:
            userLink = Linker(i)
            if "start" in sys.argv:
                userLink.link()
                print "User %s linked"% i
            elif "stop" in sys.argv:
                userLink.unlink()
                print "User %s unlinked"% i
    else:
        print "Usage:\n linker.py start\n linker.py stop"
        
