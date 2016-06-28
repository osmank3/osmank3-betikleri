#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Author: Osman Karagöz
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt
#
# For editing, increasing or decreasing time of srt file
#
# Usage:
#     python retimesrt.py [OPTIONS] file or directory
#
# Options:
#     -p --plus           increase time DEFAULT
#     -m --minus          decrease time
#     -o --overwrite      overwrite original file
#     --minute MINUTE     how many minutes to change
#     --second SECOND     how many seconds to change
#     --microsec MICROSEC how many micro seconds to change
#     --aftertime TIME    change file after time, TIME = h:m:s or m:s
#     --beforetime TIME   change file before time, TIME = h:m:s or m:s
#     -d --delete         deleting for some lines(use with after/beforetime)
#     -a --add            adding for line(use with --text, --start and --length both)
#       --text 'TEXT'     text for adding
#       --start TIME      adding text time start point, TIME = h:m:s or m:s
#       --length SEC.MSEC adding text length, SEC.MSEC = s.S or s
#
# Example:
#     python retimesrt.py -p --minute 15 file
#     python retimesrt.py -m --second 25 file
#     python retimesrt.py -p --second 6 --aftertime 1:12:30 file
#     python retimesrt.py --delete --aftertime 1:12:30 file\n"
#     python retimesrt.py -a --text 'The End' --start 1:32:28 --length 1.750 file\n"

import os
import sys
import datetime
import getopt

#For using unicode utf-8
if sys.version_info.major < 3:
    reload(sys).setdefaultencoding("utf-8")

MINUTES = 0
SECONDS = 0
MICROSEC = 000000
ISPLUS = True
OVERWRITE = False
ATIME = datetime.datetime(1,1,1)
ASTAT = False
BTIME = datetime.datetime(1,1,1)
BSTAT = False
ISDEL = False
ADD = False
TEXT = ""
START = datetime.datetime(1,1,1)
LENGTH = datetime.timedelta()

class oneString(object):
    def __init__(self, time="0:0:0,0 --> 0:0:0,0", text=""):
        self.timeStart, self.timeEnd = self.extractTime(time)
        self.text = text
        self.isDel = False
        self.isPrinted = False
        self.isAdded = True

    def extractTime(self, timeText):
        timeText.replace("\r\n", "").replace("\n", "")
        timesAsText = timeText.split(" --> ")
        times = []
        for text in timesAsText:
            time, millisec = text.split(",")
            hour, minute, second = time.split(":")
            timeAsDatetime = datetime.datetime(1, 1, 1, int(hour), int(minute),
                                               int(second), int(millisec)*1000)
            times.append(timeAsDatetime)
        return(times)

    def changeTime(self, delta, isPlus=True):
        if isPlus:
            self.timeStart += delta
            self.timeEnd += delta
        else:
            try:
                self.timeStart -= delta
                self.timeEnd -= delta
            except OverflowError:
                print("Date value out of range")
                sys.exit(2)

    def delete(self, stat=True):
        self.isDel = stat

    def getDelete(self):
        return(self.isDel)

    def print(self, number):
        timeAsText = "%s --> %s"% (
            "%0.2d:%0.2d:%0.2d,%0.3d"% (self.timeStart.hour, self.timeStart.minute,
                                        self.timeStart.second, self.timeStart.microsecond / 1000),
            "%0.2d:%0.2d:%0.2d,%0.3d"% (self.timeEnd.hour, self.timeEnd.minute,
                                        self.timeEnd.second, self.timeEnd.microsecond / 1000))
        return("%s\r\n%s\r\n%s\r\n"% (number, timeAsText, self.text))

def checkStrings(strings):
    n = 0
    while n + 1 < len(strings):
        if strings[n].timeEnd > strings[n+1].timeStart:
            strings[n].timeEnd = strings[n+1].timeStart
        if strings[n].timeStart > strings[n+1].timeStart:
            print("Strings timing is corrupted.")
            sys.exit(3)
        n += 1

def editFile(subfile):
    subtitle = open(subfile, "r")
    lines = subtitle.readlines()
    subtitle.close()
    transLines = [[]]
    for i in lines:
        if i == "\r\n" or i == "\n":
            lineEnd = i
            transLines.append([])
        else:
            transLines[-1].append(i)

    allStrings = []
    for i in transLines:
        if len(i) > 0:
            allStrings.append(oneString(i[1], "".join(i[2:])))

    isAdding = False
    if ADD and TEXT != "" and START != datetime.datetime(1,1,1) and LENGTH != datetime.timedelta():
        end = START + LENGTH
        addingLine = oneString("%s --> %s"% (
            "%0.2d:%0.2d:%0.2d,%0.3d"% (START.hour, START.minute, START.second,
                                        START.microsecond / 1000),
            "%0.2d:%0.2d:%0.2d,%0.3d"% (end.hour, end.minute, end.second,
                                        end.microsecond / 1000)
            ), TEXT + "\r\n")
        addingLine.isAdded = False
        isAdding = True
    elif ADD:
        print("new text can not adding")

    n = 0
    while n < len(allStrings):
        aString = allStrings[n]
        if ASTAT and BSTAT:
            if ATIME < BTIME:
                if ATIME < aString.timeStart < aString.timeEnd < BTIME:
                    if ISDEL:
                        aString.delete()
                    delta = datetime.timedelta(minutes=MINUTES, seconds=SECONDS,
                                               microseconds=MICROSEC)
                else:
                    delta = datetime.timedelta()
            elif BTIME < ATIME:
                if BTIME < aString.timeStart and aString.timeStart < ATIME:
                    delta = datetime.timedelta()
                else:
                    if ISDEL:
                        aString.delete()
                    delta = datetime.timedelta(minutes=MINUTES, seconds=SECONDS,microseconds=MICROSEC)
            elif BTIME == ATIME:
                delta = datetime.timedelta(minutes=MINUTES, seconds=SECONDS,microseconds=MICROSEC)
        elif ASTAT or BSTAT:
            if (ASTAT and ATIME < aString.timeStart) or (BSTAT and aString.timeEnd < BTIME):
                if ISDEL:
                    aString.delete()
                delta = datetime.timedelta(minutes=MINUTES, seconds=SECONDS,microseconds=MICROSEC)
            else:
                delta = datetime.timedelta()
        else:
            delta = datetime.timedelta(minutes=MINUTES, seconds=SECONDS,microseconds=MICROSEC)

        if ISPLUS:
            aString.changeTime(delta)
        else:
            aString.changeTime(delta, False)

        if isAdding and not addingLine.isAdded:
            if addingLine.timeStart < aString.timeStart:
                addingLine.isAdded = True
                allStrings.insert(n, addingLine)
                n += 1
            if aString.timeStart < addingLine.timeStart < allStrings[n+1].timeStart:
                addingLine.isAdded = True
                allStrings.insert(n+1, addingLine)
                n += 1
        n += 1

    checkStrings(allStrings)

    if OVERWRITE:
        newFileName = subfile
    else:
        newFileName = "%s.new.srt"% subfile[:-4]
    newsub = open(newFileName, "w")
    num = 1
    for i in allStrings:
        if not i.getDelete():
            newsub.write(i.print(num))
            num += 1
        
    newsub.close()
    print("%s is prepared"% newFileName)

def usage(returnArg=0, detail=False):
    msg = "Usage: retimesrt.py [OPTIONS] file\n"
    msg += "Edit, Increase or decrease time of srt file.\n\nOptions:\n"
    msg += "-p --plus           increase time DEFAULT\n"
    msg += "-m --minus          decrease time\n"
    msg += "-o --overwrite      overwrite original file\n"
    msg += "--minute MINUTE     how many minutes to change\n"
    msg += "--second SECOND     how many seconds to change\n"
    msg += "--microsec MICROSEC how many micro seconds to change\n"
    msg += "--aftertime TIME    change file after time, TIME = h:m:s or m:s\n"
    msg += "--beforetime TIME   change file before time, TIME = h:m:s or m:s\n"
    msg += "-d --delete         deleting for some lines(use with after/beforetime)\n"
    msg += "-a --add            adding for line(use with --text, --start and --length both)\n"
    msg += "  --text 'TEXT'     text for adding\n"
    msg += "  --start TIME      adding text time start point, TIME = h:m:s or m:s\n"
    msg += "  --length SEC.MSEC adding text length, SEC.MSEC = s.S or s\n"
    msg += "-u --usage          print detailed usage\n"
    msg += "-h --help           print this help\n\nExamples:\n"
    msg += "  retimesrt.py -p --minute 15 file\n"
    msg += "  retimesrt.py -m --second 25 file\n"
    msg += "  retimesrt.py -p --second 6 --aftertime 1:12:30 file\n"
    msg += "  retimesrt.py --delete --aftertime 1:12:30 file\n"
    msg += "  retimesrt.py -a --text 'The End' --start 1:32:28 --length 1.750 file\n"
    if detail == True:
        msg += "\nDetailed Usage:\n"
        msg += "  --aftertime TIME => A\n  --beforetime TIME => B\n  changing 'x' times\n"
        msg += "    A only    ------Axxxxx\n"
        msg += "    B only    xxxxxB------\n"
        msg += "    A<B       ---AxxxxB---\n"
        msg += "    A>B       xxxB----Axxx\n"
        msg += "    A=B       xxxxxABxxxxx\n\n"
        msg += "  -a --add          this parameter needs these:\n"
        msg += "    --text TEXT         text for adding\n"
        msg += "    --start TIME        adding text time start point, TIME = h:m:s or m:s\n"
        msg += "    --length SEC.MSEC   adding text length, SEC.MSEC = s.S or s\n"
    print(msg)
    sys.exit(returnArg)
    
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt( sys.argv[1:], "hpmouda",
                                    ["help", "minute=", "second=", "microsec=",
                                    "plus", "minus", "overwrite", "aftertime=",
                                    "beforetime=", "text=", "start=", "length=",
                                    "usage"])
    except getopt.GetoptError:
        usage(2)
        
    for o, a in opts:
        if o in ("-h", "--help"):
            usage(0)
        if o in ("-u", "--usage"):
            usage(0, True)
        if o in ("-m", "--minus"):
            ISPLUS = False
        if o in ("-p", "--plus"):
            ISPLUS = True
        if o in ("-o", "--overwrite"):
            OVERWRITE = True
        if o in ("-d", "--delete"):
            ISDEL = True
        if o in ("--minute") and o not in ("-m"):
            MINUTES = int(a)
        if o in ("--second"):
            SECONDS = int(a)
        if o in ("--microsec") and o not in ("-m"):
            if int(a) < 1000:
                MICROSEC = int(a) * 1000
            elif 1000 <= int(a) < 1000000:
                MICROSEC = int(a)
            else:
                pass
        if o in ("--aftertime", "--beforetime") and o not in ("-a"):
            if o == "--aftertime":
                ASTAT = True
            if o == "--beforetime":
                BSTAT = True
            time = a.split(":")
            if len(time) == 3:
                hour, minute, second = time
                second = int(second)
                minute = int(minute)
                minute += int(hour) * 60
            elif len(time) == 2:
                minute, second = time
                second = int(second)
                minute = int(minute)
            else:
                usage(2)
            delta = datetime.timedelta(minutes=minute, seconds=second)
            if o == "--aftertime":
                ATIME += delta
            if o == "--beforetime":
                BTIME += delta
        if o in ("-a", "--add"):
            ADD = True
        if o in ("--text"):
            TEXT = a
        if o in ("--start"):
            time = a.split(":")
            if len(time) == 3:
                hour, minute, second = time
                second = int(second)
                minute = int(minute)
                minute += int(hour) * 60
            elif len(time) == 2:
                minute, second = time
                second = int(second)
                minute = int(minute)
            else:
                usage(2)
            START += datetime.timedelta(minutes=minute, seconds=second)
        if o in ("--length"):
            time = a.split(".")
            if len(time) == 2:
                second, millisec = time
                second = int(second)
                microsec = int(millisec) * 1000
                LENGTH = datetime.timedelta(seconds=second, microseconds=microsec)
            elif len(time) == 1:
                LENGTH = datetime.timedelta(seconds=int(time[0]))
            else:
                usage(2)
    
    if args == []:
        usage(2)
    
    editFile(" ".join(args))
