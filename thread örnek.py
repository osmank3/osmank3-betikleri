#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import time
from threading import Thread

#For using unicode utf-8
reload(sys).setdefaultencoding("utf-8")

class progress(object):
    def __init__(self):
        self.sayi = 100
        self.simdiki = 0
        
    def artir(self):
        self.simdiki += 1
        
    def artirici(self):
        while self.simdiki != 100:
            time.sleep(2)
            self.artir()
            
    def getPercent(self):
        return self.simdiki
        
class surec(Thread):
    def __init__(self, Progress):
        Thread.__init__(self)
        self.progress = Progress
        
    def run(self):
        while self.progress.getPercent() != 100:
            time.sleep(1)
            print self.progress.getPercent()
            
ilerleme = progress()
thrSurec = surec(ilerleme)

thrSurec.start()
ilerleme.artirici()

print "bakak nolcek!"