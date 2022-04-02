#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 10:31:11 2021

@author: OldMac
"""

import time
import PrintFunction as log
from MailHandling import MailHandling as Mail
    
   
def ExceptionHandling(function,tries=3,cooldownInSec = 0.2,textInfo=''):
    
    currentTry = 0
    while (currentTry < tries):
        try:
            returnValue = function()
            if(returnValue):
                if(currentTry > 0):
                    Mail(f'success {textInfo}, current try: {currentTry}')
                return returnValue
            else:
                currentTry += 1
                continue
        except Exception as e:
            text = f'{str(e)} with {textInfo}, current try: {currentTry}'
            Mail(text)
            log.PrintText(text,'Exception')
            time.sleep(cooldownInSec)
            currentTry += 1
    return False
             
