#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Author: Osman Karagöz
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt

import os
import sys
import glob
import shutil
import pwd
import time
import datetime
import tarfile

#For using unicode utf-8 on python2
if sys.version_info[0] < 3:
    reload(sys).setdefaultencoding("utf-8")

AppDir = ".disthome"
LogAddress = "/var/log/prephome.log"

BlackList = [AppDir]
UserBlackList = []
ArchiveOnAllStop = False

try:
    releaseFile = open("/etc/lsb-release", "r")
    releaseLines = releaseFile.readlines()
    releaseFile.close()
    
    for i in releaseLines:
        if "DISTRIB_DESCRIPTION" in i:
            DistName = i.split("=")[1].replace('"',"").replace("\n","")

except:
    DistName = 0

def getUsersOnDist(username=None):
    usersIds = []
    allUsers = pwd.getpwall()
    for i in allUsers:
        if "/home/" in i.pw_dir and os.path.isdir(i.pw_dir) and i.pw_name not in UserBlackList:
            if username and i.pw_name == username:
                return i.pw_uid
            usersIds.append(i.pw_uid)
            
    return usersIds
    
def writeLog(logText):
    try:
        logFile = open(LogAddress, "a")
        logFile.write("[%s] -- %s\n"% (datetime.datetime.now(), logText))
        logFile.close()
    except IOError:
        print(logText)
    
class Preparer(object):
    def __init__(self, userid=None):
        self.userId = userid
        i = pwd.getpwuid(self.userId)
        self.userGid = i.pw_gid
        self.userDir = i.pw_dir
        self.UAD = os.path.join(self.userDir, AppDir, DistName)
        self.statuses = {}
        self.blackList = BlackList[:]
        self.readUserBlackList()
        self.readStatusFile()
                
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
    
    def readStatusFile(self):
        if os.path.exists(os.path.join(self.userDir,AppDir)):
            os.chdir(os.path.join(self.userDir,AppDir))
            if os.path.exists("status.tmp"):
                statFile = open("status.tmp", "r")
                statLines = statFile.readlines()
                statFile.close()
                for i in statLines:
                    if i[0] != "#":
                        key, value = i.split(":")
                        if value.strip().lower() == "true":
                            value = True
                        elif value.strip().lower() == "false":
                            value = False
                        else:
                            value = value.strip()
                        self.statuses[key.strip()] = value
        
    def writeStatusFile(self):
        os.chdir(os.path.join(self.userDir,AppDir))
        statFile = open("status.tmp", "w")
        statFile.write("# This file generated automatically\n#\n# DO NOT EDIT/REMOVE THIS FILE\n#\n")
        
        for i in self.statuses.keys():
            statFile.write("%s : %s\n"% (i, self.statuses[i]))
        statFile.close()
        os.chown("status.tmp", self.userId, self.userGid)
        writeLog("%s/%s/status.tmp created/updated"% (self.userDir, AppDir))
    
    def appendArchiveStatus(self, Stat=True):
        self.statuses["ArchiveOnStop"] = Stat
        self.writeStatusFile()
        
    def firstStart(self):
        # create an empty blacklist
        os.chdir(os.path.join(self.userDir,AppDir))
        bLFile = open("blacklist", "w")
        bLFile.write("# Add the names line by line to be blacklisted.\n#\n")
        bLFile.close()
        
    def archive(self):
        writeLog("Archiving is started")
        archiveFile = tarfile.open(self.UAD + ".tar", "w")
        archiveFile.add(self.UAD, DistName)
        archiveFile.close()
        os.chown(self.UAD + ".tar", self.userId, self.userGid)
        writeLog("Archiving completed")
        
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
                writeLog("%s wasn't closed normaly, PrepHome passing preparing"% DistName)
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
            
        self.statuses["DistName"] = DistName
        self.writeStatusFile()
            
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
                writeLog("%s wasn't closed normaly, PrepHome backing up it"% OtherDist)
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
        
        if ArchiveOnAllStop or ("ArchiveOnStop" in self.statuses and self.statuses["ArchiveOnStop"]):
            self.archive()

def usage(returnArg=0):
    msg = "Usage: prephome [COMMAND] [OPTIONS]\n\n"
    msg += "Commands:\n"
    msg += "  start                 prepare users's home directories for using\n"
    msg += "  stop                  backup users's home directories for shutdown\n"
    msg += "  archive USERNAME      archive user files on shutdown\n"
    msg += "  no-archive USERNAME   don't archive user files on shutdown\n"
    msg += "  -h --help             print this help\n\n"
    msg += "Options:\n"
    msg += "  start:\n"
    msg += "    move                use moving for preparing (default)\n"
    msg += "    link                use linking for preparing\n"
    print(msg)
    sys.exit(returnArg)

if __name__ == "__main__":
    usersIds = getUsersOnDist()
    
    command = None
    options = None
    
    argv = sys.argv[1:]
    if len(argv) > 0:
        command = argv[0]
    if len(argv) > 1:
        options = argv[1:]
    
    if not command:
        usage(2)
    
    for i in usersIds:
        userPrep = Preparer(i)
        if command in ("-h", "--help"):
            usage(0)
        
        elif command == "start":
            if os.getuid() != 0:
                writeLog("Only root user can run this command")
                sys.exit(2)
            writeLog("Prephome is preparing users home")
            if not options:
                userPrep.link("move")
            elif "move" in options:
                userPrep.link("move")
            elif "link" in options:
                userPrep.link("link")
            else:
                usage(2)
            writeLog("User %s prepared"% i)
        
        elif command == "stop":
            if os.getuid() != 0:
                writeLog("Only root user can run this command")
                sys.exit(2)
            writeLog("Prephome is backing up users home")
            userPrep.unlink()
            writeLog("User %s backed up"% i)
        
        elif command in ("no-archive", "archive"):
            if not options:
                if i == os.getuid():
                    isThisUser = True
                else:
                    isThisUser = False
            else:
                userid = getUsersOnDist(options[0])
                if type(userid) == int and i == userid:
                    if i == os.getuid() or os.getuid() == 0:
                        isThisUser = True
                    else:
                        isThisUser = False
                        writeLog("Only root user can change other users status")
                else:
                    isThisUser = False
            if isThisUser:
                if command == "archive":
                    userPrep.appendArchiveStatus(True)
                    writeLog("User files will archive on shutdown.")
                elif command == "no-archive":
                    userPrep.appendArchiveStatus(False)
                    writeLog("User files won't be able to archive on shutdown.")
        
        else:
            usage(2)

