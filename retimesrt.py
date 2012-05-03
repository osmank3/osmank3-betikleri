#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Author: Osman Karagöz
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt
#
# For increasing or decreasing time of srt file
#
# Usage:
#     python retimesrt.py [OPTIONS] file or directory
#
# Options:
#     -p --plus           increase time DEFAULT
#     -m --minus          decrease time
#     --minute MINUTE     how many minutes to change
#     --second SECOND     how many seconds to change
#     --microsec MICROSEC how many micro seconds to change
#
# Example:
#     python retimesrt.py -p --minute 15 file
#     python retimesrt.py -m --second 25 file

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

def SetNewTime(TimeText):
    timesstext = TimeText.split(" --> ")
    newtimesstext = []
    for i in timesstext:
        sure, salise = i.split(",")
        saat, dakika, saniye = sure.split(":")
        oldtime = datetime.datetime(1,1,1,int(saat),int(dakika),int(saniye),int(salise)*1000)
        
        delta = datetime.timedelta(minutes=MINUTES, seconds=SECONDS,microseconds=MICROSEC)
        
        if ISPLUS:
            newtime = oldtime + delta
        else:
            try:
                newtime = oldtime - delta
            except OverflowError:
                print("Date value out of range, it does not retime")
                sys.exit(2);
        
        text = "%0.2d:%0.2d:%0.2d,%0.3d"% (newtime.hour, newtime.minute, newtime.second, newtime.microsecond / 1000)
        newtimesstext.append(text)
    
    return(" --> ".join(newtimesstext))
    
def editFile(dosya):
    subtitle = open(dosya, "r")
    lines = subtitle.readlines()
    ceviriler = [[]]
    for i in lines:
        if i == "\r\n" or i == "\n":
            lineEnd = i
            ceviriler.append([])
        else:
            ceviriler[-1].append(i)
            
    for i in ceviriler:
        if len(i) > 0:
            newtime = SetNewTime(i[1].replace("\r\n",""))
            i[1] = newtime + "\r\n"
        
    newsub = open("%s.new.srt"% dosya[:-4], "w")
    for i in ceviriler:
        for j in i:
            newsub.write(j)
        newsub.write(lineEnd)
        
    newsub.close()
    print("%s.new.srt is created"% dosya[:-4])

def usage(returnArg=0):
    msg = "Usage: retimesrt.py [OPTIONS] file\n"
    msg += "Increase or decrease time of srt file.\n\nOptions:\n"
    msg += "-p --plus           increase time DEFAULT\n"
    msg += "-m --minus          decrease time\n"
    msg += "--minute MINUTE     how many minutes to change\n"
    msg += "--second SECOND     how many seconds to change\n"
    msg += "--microsec MICROSEC how many micro seconds to change\n"
    msg += "-h --help           print this help\n"
    print(msg)
    sys.exit(returnArg)
    
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hpm", ["help", "minute=", "second=", "microsec=", "plus", "minus"])
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
            
    editFile(" ".join(args))
