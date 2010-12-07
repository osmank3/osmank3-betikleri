#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Author: Osman Karagöz
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.
#
# For mounting and umounting casper-rw file
# Usage:
#     mount:
#         python mountCasper.py mount
#     umount:
#         python mountCasper.py umount

import os
import sys

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

mountTo = "%s/casper-rw"% (os.environ["HOME"])

def foundCasperRw():
    listOfMounted = os.listdir("/media")
    for i in listOfMounted:
        if os.path.isdir("/media/%s"% i):
            listOfI = os.listdir("/media/%s"% i)
            if "casper-rw" in listOfI:
                return "/media/%s/casper-rw"% i
    return False

def mount():
    mountPoint = foundCasperRw()
    if mountPoint:
        if not os.path.isdir(mountTo):
            os.mkdir(mountTo)
        if len(os.listdir(mountTo)) == 0:
            os.system("sudo mount -o loop %s %s"% (mountPoint, mountTo))
        else:
            print "mount directory is not free or casper-rw mounted to directory"
    else:
        print "casper-rw can't found anywhere"

def umount():
    if os.path.isdir(mountTo):
        os.system("sudo umount %s"% mountTo)
        if len(os.listdir(mountTo)) == 0:
            os.rmdir(mountTo)
        else:
            print "directory is not free"
    else:
        print "%s is not directory"% mountTo
        
if __name__ == "__main__":
    if "mount" in sys.argv:
        mount()
    elif "umount" in sys.argv:
        umount()
    elif "help" in sys.argv:
        print "mount    -   mounting founded casper-rw"
        print "umount   -   umounting casper-rw"
        print "help     -   printing this help"
