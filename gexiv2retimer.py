#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Author: Osman Karagöz
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt
#
# For increasing or decreasing photos exif create date to given difference time.
#
# Dependence:
#     Gexiv2
#
# Usage:
#     python gexiv2retimer.py [OPTIONS] file or directory
#
# Options:
#     -p --plus           increase time DEFAULT
#     -m --minus          decrease time
#     -n --name           change file name to create time
#     -r --recursive      do everything recursively
#     -o --only-images    change only image files
#     -a --archive [YMD]  move images to (Y)ear/(M)ount/(D)ay directory
#     --day DAY           how many days to change
#     --hour HOUR         how many hours to change
#     --minute MINUTE     how many minutes to change
#     --second SECOND     how many seconds to change
#
# Example:
#     python gexiv2retimer.py -pn --hour 2 --minute 15 file
#     python gexiv2retimer.py -m --day 1 --second 25 directory
#     python gexiv2retimer.py -n -a YM directory

import os
import sys
import getopt
import datetime
import locale
from gi.repository import GExiv2

#For using unicode utf-8
if sys.version_info[0] < 3:
    reload(sys).setdefaultencoding("utf-8")

#For using locales full mount name
locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())

DAY = 0
HOUR = 0
MINUTE = 0
SECOND = 0
ISPLUS = True
RENAME = False
RECURSIVE = False
ONLYIMAGE = False
ARC_YEAR = False
ARC_MOUNT = False
ARC_DAY = False

def setNewTime(editFile):
    isExif = False
    keys = ["Exif.Photo.DateTimeOriginal",
            "Exif.Photo.DateTimeDigitized",
            "Exif.Image.DateTime",
            "Exif.Thumbnail.DateTime"]
    meta = GExiv2.Metadata()
    try:
        meta.open_path(editFile)
        if meta.has_exif():
            isExif = True
            for data in keys:
                if meta.get_tag_string(data) != "":
                    createDate = datetime.datetime.strptime(meta.get_tag_string(data), "%Y:%m:%d %H:%M:%S")
                    break
    except:
        if ONLYIMAGE:
            return 0
    finally:
        if not isExif:
            stat = os.stat(editFile)
            createDate = datetime.datetime.fromtimestamp(stat.st_mtime)
        
    delta = datetime.timedelta(days=DAY, hours=HOUR, minutes=MINUTE, seconds=SECOND)
    if ISPLUS:
        newDate = createDate + delta
    else:
        newDate = createDate - delta
    
    if isExif:
        for key in keys:
            meta.set_tag_string(key, newDate.strftime("%Y:%m:%d %H:%M:%S"))
        
        try:
            meta.save_file(editFile)
            if delta != datetime.timedelta(seconds=0): #images time tags are same now
                print("%s is retimed."% editFile)
        except:
            print("%s files Exif data could not changed"% editFile)
    
    if ARC_YEAR or ARC_MOUNT or ARC_DAY or RENAME:
        newDir = ""
        newName = editFile
        if ARC_YEAR:
            newDir += newDate.strftime("%Y") + "/"
        if ARC_MOUNT:
            newDir += newDate.strftime("%B") + "/"
        if ARC_DAY:
            newDir += newDate.strftime("%d") + "/"
        if RENAME:
            ext = editFile.split(".")[-1].lower()
            newName = newDate.strftime("%Y-%m-%d %H.%M.%S")
            newName = newName + "." + ext
        if newDir != "" or newName != editFile:
            if not os.path.isdir(newDir) and newDir != "":
                os.makedirs(newDir)
            newName = newDir + newName
            n = 0
            while os.path.isfile(newName):
                name, ext = os.path.splitext(newName)
                if n == 0:
                    newName = name + "(" + str(n) + ")" + ext
                else:
                    newName = name.split("(")[0] + "(" + str(n) + ")" + ext
                n += 1
            
            os.rename(editFile, newName)
            if newDir != "":
                print("%s moved to %s"% (editFile, newName))
            else:
                print("%s renamed to %s"% (editFile, newName))

def retimer(dirorfile):
    if os.path.isfile(dirorfile):
        setNewTime(dirorfile)
    elif os.path.isdir(dirorfile):
        os.chdir(dirorfile)
        listOfDir = os.listdir("./")
        listOfDir.sort()
        for i in listOfDir:
            if os.path.isfile(i):
                setNewTime(i)
            elif os.path.isdir(i) and RECURSIVE:
                retimer(i)
        os.chdir("..")
        
def usage(returnArg=0):
    msg = "Usage: gexiv2retimer.py [OPTIONS] file or directory\n"
    msg += "Increase or decrease exif time.\n\nOptions:\n"
    msg += "-p --plus           increase time DEFAULT\n"
    msg += "-m --minus          decrease time\n"
    msg += "-n --name           change file name to create time\n"
    msg += "-r --recursive      do everything recursively\n"
    msg += "-o --only-images    change only image files\n"
    msg += "-a --archive [YMD]  move images to (Y)ear/(M)ount/(D)ay directory\n"
    msg += "--day DAY           how many days to change\n"
    msg += "--hour HOUR         how many hours to change\n"
    msg += "--minute MINUTE     how many minutes to change\n"
    msg += "--second SECOND     how many seconds to change\n"
    msg += "-h --help           print this help\n"
    print(msg)
    sys.exit(returnArg)
        
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt( sys.argv[1:], "hpmnroa:",
                                    ["help", "day=", "hour=", "minute=",
                                    "second=", "plus", "minus", "name",
                                    "recursive", "only-images", "archive="])
    except getopt.GetoptError:
        usage(2)
    if args == []:
        usage(2)
        
    for o, a in opts:
        if o in ("-h", "--help"):
            usage(0)
        if o in ("-m", "--minus"):
            ISPLUS = False
        if o in ("-p", "--plus"):
            ISPLUS = True
        if o in ("-n", "--name"):
            RENAME = True
        if o in ("-r", "--recursive"):
            RECURSIVE = True
        if o in ("-o", "--only-images"):
            ONLYIMAGE = True
        if o in ("-a", "--archive"):
            if "Y" in a:
                ARC_YEAR = True
            if "M" in a:
                ARC_MOUNT = True
            if "D" in a:
                ARC_DAY = True
        if o in ("--day"):
            DAY = int(a)
        if o in ("--hour"):
            HOUR = int(a)
        if o in ("--minute") and o not in ("-m"):
            MINUTE = int(a)
        if o in ("--second"):
            SECOND = int(a)
            
    retimer(" ".join(args))
