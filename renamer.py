#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Author: Osman Karagöz
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.
#
# For renaming image's name to create date in DIRECTORIES.
# Usage:
#     python renamer.py DIRECTORY
#
# Dependence:
#     kaa.metadata

import os
import sys
import datetime

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

from warnings import simplefilter # for ignoriny DeprecationWarning.
simplefilter("ignore", DeprecationWarning)

import kaa.metadata as Meta

def getNewName(file):
    ext = file.split(".")[-1].lower()
    info = Meta.parse(file)
    if info.timestamp:
        createDate = datetime.datetime.fromtimestamp(info.timestamp)
    else:
        stat = os.stat(file)
        createDate = datetime.datetime.fromtimestamp(stat.st_mtime)
    newName = createDate.isoformat()
    newName = newName.replace("T"," ")
    newName = newName.replace(":",".")
    newName = newName + "." + ext
    return newName
    
def renamer(directory):
    os.chdir(directory)
    listOfDir = os.listdir("./")
    listOfDir.sort()
    for i in listOfDir:
        if os.path.isfile(i):
            newName = getNewName(i)
            n = 0
            while os.path.isfile(newName):
                name, ext = os.path.splitext(newName)
                if n == 0:
                    newName = name + "(" + str(n) + ")" + ext
                else:
                    newName = name[:-2] + str(n) + ")" + ext
                n += 1
            os.rename(i, newName)
            print "%s renamed to %s"% (i, newName)
        elif os.path.isdir(i):
            renamer(i)
            os.chdir("..")
    print "%s directory is finished"% directory
    
if __name__ == "__main__":
    argv = sys.argv
    print "%s is starting to renaming"% argv[0]

    argv.pop(0)
    directory = " ".join(argv)
    if directory == "":
        directory = "./"

    renamer(directory)
