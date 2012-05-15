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
#     pyexiv2
#
# Usage:
#     python exiv2retimer.py [OPTIONS] file or directory
#
# Options:
#     -p --plus           increase time DEFAULT
#     -m --minus          decrease time
#     -n --name           change file name to create time
#     -r --recursive      do everything recursively
#     -o --only-images    change only image files
#     --day DAY           how many days to change
#     --hour HOUR         how many hours to change
#     --minute MINUTE     how many minutes to change
#     --second SECOND     how many seconds to change
#
# Example:
#     python exiv2retimer.py -pn --hour 2 --minute 15 file
#     python exiv2retimer.py -m --day 1 --second 25 directory

import os
import sys
import getopt
import datetime
import pyexiv2

#For using unicode utf-8
if sys.version_info.major < 3:
    reload(sys).setdefaultencoding("utf-8")

DAY = 0
HOUR = 0
MINUTE = 0
SECOND = 0
ISPLUS = True
RENAME = False
RECURSIVE = False
ONLYIMAGE = False

def setNewTime(editFile):
    keys = ["Exif.Image.DateTime",
            "Exif.Photo.DateTimeOriginal",
            "Exif.Photo.DateTimeDigitized",
            "Exif.Thumbnail.DateTime"]
    meta = pyexiv2.ImageMetadata(editFile)
    try:
        meta.read()
        if "Exif.Photo.DateTimeOriginal" in meta.keys():
            isExif = True
            createDate = meta["Exif.Photo.DateTimeOriginal"].value
        elif "Exif.Photo.DateTimeDigitized" in meta.keys():
            isExif = True
            createDate = meta["Exif.Photo.DateTimeDigitized"].value
        elif "Exif.Image.DateTime" in meta.keys():
            isExif = True
            createDate = meta["Exif.Image.DateTime"].value
        else:
            isExif = False
    except IOError:
        isExif = False
        if ONLYIMAGE:
            return 0
    
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
            meta[key] = pyexiv2.ExifTag(key, newDate)
        
        meta.write()
        if delta != datetime.timedelta(seconds=0): #images time tags are same now
            print("%s is retimed."% editFile)
    
    if RENAME:
        ext = editFile.split(".")[-1].lower()
        newName = createDate.strftime("%Y-%m-%d %H.%M.%S")
        newName = newName + "." + ext
        n = 0
        while os.path.isfile(newName):
            name, ext = os.path.splitext(newName)
            if n == 0:
                newName = name + "(" + str(n) + ")" + ext
            else:
                newName = name.split("(")[0] + "(" + str(n) + ")" + ext
            n += 1
        os.rename(editFile, newName)
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
    msg = "Usage: exiv2retimer.py [OPTIONS] file or directory\n"
    msg += "Increase or decrease exif time.\n\nOptions:\n"
    msg += "-p --plus           increase time DEFAULT\n"
    msg += "-m --minus          decrease time\n"
    msg += "-n --name           change file name to create time\n"
    msg += "-r --recursive      do everything recursively\n"
    msg += "-o --only-images    change only image files\n"
    msg += "--day DAY           how many days to change\n"
    msg += "--hour HOUR         how many hours to change\n"
    msg += "--minute MINUTE     how many minutes to change\n"
    msg += "--second SECOND     how many seconds to change\n"
    msg += "-h --help           print this help\n"
    print(msg)
    sys.exit(returnArg)
        
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt( sys.argv[1:], "hpmnro",
                                    ["help", "day=", "hour=", "minute=",
                                    "second=", "plus", "minus", "name",
                                    "recursive", "only-images"])
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
        if o in ("--day"):
            DAY = int(a)
        if o in ("--hour"):
            HOUR = int(a)
        if o in ("--minute") and o not in ("-m"):
            MINUTE = int(a)
        if o in ("--second"):
            SECOND = int(a)
            
    retimer(" ".join(args))
