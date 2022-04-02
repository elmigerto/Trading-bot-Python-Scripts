#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 15:19:53 2021

@author: Tobias Elmiger

TODO:
    - Add money


"""

import time
import connectionHandling as ch
import sched
import time
import DataManipulation as dm
import numpy as np
import threading
from PrintFunction import PrintText
from strategy_alpha_BASE import Strategy_alpha
from strategy_alpha_BASE import SellStrategy
from strategy_alpha_BASE import ThreadClass
import strategy_alpha_BASE




    
# **** End of Thread *****


class Strategy_alpha_BTC(Strategy_alpha):
    
    def __init__(self,initialBuy = False):
        
        # Time
        self.startTime = time.time()
        self.nextTriggerTime = []
        self.avgSpacingBetweenTriggerEventsSec = 60*60*24
        self.sdtDevTriggerEvents = 0.1
        self.tradingEventNr = 0
        self.updateTime = 5 # Updates the orders every x seconds
        
        # Parameter
        self.ConnectionHandling = ch.ConnectionHandling() 
        self.schedule = sched.scheduler(time.time,time.sleep)
        self.assetPairId = ['BTCEUR']
        self.assetId = ['BTC']
        self.strategyName = 'alpha_0_BTC'
        self.sellStrategy = SellStrategy.initialize()
        self.buyAmount = 30      
        
        # Init Variables
        self.activeOrders = {}
        #self.updateActiveOrders()
        
        # StartStrategie
        self.data = dm.DataManipulation(self.strategyName)
        self.startStrategie(initialBuy) 
    
    def startStrategie(self,initialBuy = False):
        
        # Thread managment
        self.runPeriodicBuyEvent(initialBuy)
        self.runPeriodiTradeEvent()
        self.runPeriodicCheckEvent()   
        
    

       




