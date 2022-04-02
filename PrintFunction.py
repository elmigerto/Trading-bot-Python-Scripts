#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 19:38:43 2021

@author: OldMac
"""

import time
import datetime 

from DataManipulation import Storage

class PrintText(Storage):
    def __init__(self,text,LogType=''):
        try:
            name = 'log' + str(LogType)
        except Exception as e:
            name = 'logUnknown'
            PrintText(str(e),'Exception')
            
        super().__init__(name)
        print(text)
        f = self.openFile()
        f.write('\n')
        f.write(str(datetime.datetime.now()) + ': ' + text)
        f.close()
        
    
    
       