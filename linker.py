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
import datetime

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

AppDir = ".disthomelinker"
LogAddress = "/var/log/linker.log"

BlackList = [AppDir]
UserBlackList = []

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
        if "/home/" in i.pw_dir and os.path.isdir(i.pw_dir) and i.pw_name not in UserBlackList:
            usersIds.append(i.pw_uid)
            
    return usersIds
    
def writeLog(logText):
    logFile = open(LogAddress, "a")
    logFile.write("[%s] -- %s\n"% (datetime.datetime.now(), logText))
    logFile.close()
    
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
        writeLog("%s/%s/status.tmp created"% (self.userDir, AppDir))
        
    def firstStart(self):
        # create an empty blacklist
        os.chdir(os.path.join(self.userDir,AppDir))
        bLFile = open("blacklist", "w")
        bLFile.write("# Add the names line by line to be blacklisted.\n#\n")
        bLFile.close()
        
    def moveDirs(self, OtherDist=None):
        os.chdir(self.userDir)
        
        if OtherDist:
            UAD = os.path.join(self.userDir, AppDir, OtherDist)
        else:
            UAD = self.UAD
        
        if not os.path.exists(AppDir):
            os.mkdir(AppDir)
            os.chown(AppDir, self.userId, self.userGid)
            self.firstStart()
                
        if not os.path.exists(UAD):
            os.mkdir(UAD)
            os.chown(UAD, self.userId, self.userGid)
        
        LastHomeList = glob.glob(".*")
        OldHomeList = os.listdir(UAD)
        
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
            os.chdir(UAD)
            if os.path.isdir(i):
                shutil.rmtree(i)
            else:
                os.remove(i)
                
        os.chdir(self.userDir)
        for i in NeedMove:
            shutil.move(i, os.path.join(UAD, i))
            
    def link(self, way="move"):
        os.chdir(self.userDir)
        HomeList = os.listdir(self.UAD)
        
        if "DistName" in self.statuses.keys():
            if self.statuses["DistName"] == DistName:
                writeLog("%s wasn't closed normaly, Linker passing linking"% DistName)
                return
            else:
                self.unlink()
        
        for i in HomeList:
            if os.path.exists(i):
                if i in self.blackList:
                    pass
                elif os.path.islink(i):
                    os.unlink(i)
                elif os.path.isdir(i):
                    shutil.rmtree(i)
                else:
                    os.remove(i)
                writeLog("'%s' is overwrited."% i)
                    
            if way == "link":
                os.symlink(os.path.join(self.UAD, i), i)
            if way == "move":
                shutil.move(os.path.join(self.UAD, i), i)
            time.sleep(0.01)
            
        self.writeLoginStatus()
            
    def unlink(self):
        os.chdir(self.userDir)
        
        OtherDist = None
        
        if "DistName" in self.statuses.keys() and self.statuses["DistName"] != DistName:
            os.chdir(AppDir)
            if not os.path.exists(DistName):
                os.rename(self.statuses["DistName"], DistName)
                writeLog("Distro's name changed.")
            else:
                OtherDist = self.statuses["DistName"]
                writeLog("%s wasn't closed normaly, Linker backing up it"% OtherDist)
            os.chdir(self.userDir)
        
        self.moveDirs(OtherDist)
        
        HomeList = glob.glob(".*")
        
        for i in HomeList:
            if i in self.blackList:
                pass
            elif os.path.islink(i):
                os.unlink(i)
                time.sleep(0.01)
            else:
                writeLog("Is this a bug? %s"% i)
        
        if os.path.exists("%s/%s/status.tmp"% (self.userDir, AppDir)):
            os.remove("%s/%s/status.tmp"% (self.userDir, AppDir))
            writeLog("%s/%s/status.tmp deleted"% (self.userDir, AppDir))

if __name__ == "__main__":
    usersIds = getUsersOnDist()
    
    if len( set(["start","stop"]) & set(sys.argv) ) != 1:
        print """\
Usage:
 linker.py [command] [options]
 
 command:
    start       prepare users's home directories for using
    stop        clean users's home directories for shutdown
 
 options:
    start options:
      move      don't link configuration files/folders, move them (default)
      link      don't move configuration files/folders, link them\n"""
    
    else:
        for i in usersIds:
            userLink = Linker(i)
            if "start" in sys.argv:
                writeLog("Linker is started linking")
                if "move" in sys.argv:
                    userLink.link("move")
                elif "link" in sys.argv:
                    userLink.link("link")
                else:
                    userLink.link()
                writeLog("User %s linked"% i)
            elif "stop" in sys.argv:
                writeLog("Linker is started unlinking")
                userLink.unlink()
                writeLog("User %s unlinked"% i)
