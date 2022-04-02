#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 15:19:53 2021

@author: Tobias Elmiger

TODO:

# ETH

- TODO:
    TradeStream: Empty stream, not working yet
    
    
TOTEST:
    
"""

import time
import connectionHandling as ch
import sched
import time
import DataManipulation as dm
import numpy as np
import pandas as pd
import threading
import math
import random
from PrintFunction import PrintText
from MailHandling import MailHandling as Mail
import ExceptionHandling
from ExceptionHandling import ExceptionHandling as tryOrMail
import WeightTimeInterval as wti # WeightTimeInterval
    
def getSchedule(delay, function):
    schedule = sched.scheduler(time.time,time.sleep)
    schedule.enter(delay = delay, priority= 0, action = function)
    schedule.run()
    return schedule
    
class SellStrategy:
    
    def initialize(parts = 12, c = 0.004, base=1.8, equal = True):
        """
        description:
            Returns a dict of n = parts entries
            All values together are equal to 1
        
        
        math: 
            key (n):  1 + c * base^n
            value: 1/parts
            
        """
        ss = {}
        if not parts:
            return
        percentil = 1/parts
        if(equal == True):
            for index in range(0,parts):
                multiplier = 1 + c * pow(base,index)
                ss[multiplier] = percentil
        return ss

# *** Thread class ***   
class ThreadClass(threading.Thread):
    def __init__(self, threadID, name, function):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.function = function
        
    def run(self):
        PrintText(f"Start thread ID: {self.threadID}, name: {self.name}")
        threadLock.acquire(0)
        self.function()
        threadLock.release()
            
threadLock = threading.Lock()
threads = []

    
class CalculationHelper:
    ''' 
    static class with methods to calculate and return models
    '''
    
    def sellStrategyPartDict(parts = 12, c = 0.006, base=1.4, equal = True):
        """
        description:
            Retunrs a dict of n = parts entries
            All values together are equal to 1
        
        
        math: 
            key (n):  1 + c * base^n
            value: 1/parts
            
         """
        ss = {}
        if not parts:
            return
        percentil = 1/parts
        if(equal == True):
            for index in range(0,parts):
                multiplier = 1 + c * pow(base,index)
                ss[multiplier] = percentil
        return ss
# **** End of Thread *****

class Strategy_alpha:
    
    assetId = []
    
    
    # Used Variables
    activeOrders = {}
    recentCompletedTrades = []
    initalBuy = False
    assetPair = ['EUR']
    reRunThreads = True
    baseClass = False
    
    #Placing Orders
    setPriceBidAskRatio = 0.5 # 0.5 will choose the placed price in the middle between bid and ask, where 0 is bid (lower value) and 1 is ask
    incompletedTrades = False
    
    
    # Strategies
    sellStrategy = SellStrategy.initialize(parts=7,c=0.005,base=1.4)
    #DayStrat
    dayStrat_Multiplicator =  3.5
    dayStrat_Power = 3.5
    dayStrat_hours = 24
    
    # Only for testing:
    placedOrders = []
    def __init__(self):
        self.baseClass = True
        
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
        self.assetPairId = ['ETHEUR']
        self.assetPair = ['EUR']
        self.assetId = ['ETH']
        self.strategyName = 'alpha_0'
        self.buyAmount = 35
        
        # Strategies
        self.sellStrategy = SellStrategy.initialize(parts=10,c=0.005,base=1.4)
        #DayStrat
        self.dayStrat_Multiplicator =  4
        self.dayStrat_Power = 3.5
        self.dayStrat_hours = 24
                
        # Init Variables
        self.activeOrders = {}
        self.recentCompletedTrades = []
        #self.updateActiveOrders()
        
        # StartStrategie
        self.data = dm.DataManipulation(self.strategyName)
        self.startStrategie()       
        
        # General infos
        self.getBalance()
      
    # Info: will be frequently called
    def isBaseClass(self):
        return self.baseClass
    
    
    def timeEvent(self):
        self.evaluateStrategie()    
    
    def running(self):
        self.continueRunning = True         
            
    def evaluateStrategie(self):
        pass
    
    def startStrategie(self):
        #self.ConnectionHandling.cancelAllOrders()

        if(self.isBaseClass()):
            self.runPeriodicInfoMailEvent()
        else:
            # Thread managment
            self.runPeriodicBuyEvent(False)
            self.runPeriodiTradeEvent()
        self.runPeriodicCheckEvent()
            
    
    def runPeriodicBuyEvent(self,initalBuy=False):
        self.initalBuy = initalBuy
        self.buyEvent = ThreadClass(threading.activeCount() + 1,self.strategyName + ' : periodic buy event', self.periodicBuyEventLoop)
        self.buyEvent.start()
    
    def runPeriodiTradeEvent(self):
        self.tradeStream = ThreadClass(threading.activeCount() + 1,self.strategyName + ' : periodic trade stream', self.periodicTradeStream)
        self.tradeStream.start()
        
    def runPeriodicCheckEvent(self):
        self.threadChecker = ThreadClass(threading.activeCount() + 1,self.strategyName + ' : periodic run inactive threads', self.periodicRunInactiveThreadsLoop)
        self.threadChecker.start()

    def runPeriodicInfoMailEvent(self):
        self.infoMailEvent = ThreadClass(threading.activeCount() + 1,self.strategyName + ' : periodic sending info mail', self.periodicInfoMailEvent)
        self.infoMailEvent.start()          
        
    def stopThreads(self):
        self.reRunThreads = False
    
    def periodicRunInactiveThreadsLoop(self,updateFrequencyInSeconds=60):
        checkConnectionCountdown = 5
        while(self.reRunThreads):
             time.sleep(updateFrequencyInSeconds)
             if(checkConnectionCountdown < 1 ):
                 tryOrMail(lambda : self.ConnectionHandling.createConnection())
                 checkConnectionCountdown = 5    
                 if(self.hasFreeVolumeHigherThanLimit(self.assetId[0],self.assetPairId[0])):
                    time.sleep(updateFrequencyInSeconds)
                    if(self.hasFreeVolumeHigherThanLimit(self.assetId[0],self.assetPairId[0])):
                        self.performSellStrategyLastBuyOrderOrCurrentPrice(self.assetId[0],self.assetPairId[0])
                    
             else:
                 checkConnectionCountdown -= 1
             if(self.isBaseClass()):
                 if(not self.infoMailEvent.is_alive() and self.isBaseClass()):
                     self.runPeriodicInfoMailEvent()
             else:
                 if(not self.buyEvent.is_alive() and not self.isBaseClass()):
                     self.initalBuy=False
                     self.runPeriodicBuyEvent()
                 if(not self.tradeStream.is_alive() and not self.isBaseClass()):
                     self.runPeriodiTradeEvent()

                 
    def periodicInfoMailEvent(self,updateFrequencyInSeconds=86400):
        while(self.reRunThreads):
            message = self.getInfo()
            mail = Mail(message)
            time.sleep(updateFrequencyInSeconds)
    
    def orderStream(self,assetPairId = 0):
        self.ConnectionHandling.streamCompletedTrades(assetPairId)


    #  --- Periodical Functions --- 
    def periodicBuyEventLoop(self,repeat_sec= 3600, skip_interval_after_buy = 8):
        '''
        Runs every repeat_sec a probability test and buys new cryptocurrency, if the test returns true. Has higher buy chances on low values

        Returns
        -------
        None.

        '''
        order = False
        maxTries = 3
        currentTry = 0
        while(self.reRunThreads):
            self.ConnectionHandling = ch.ConnectionHandling() 
            if(self.strat_24h_buyLowNow(self.assetPairId[0])):
                # Try to buy new stocks as long as not succesful. If initialBuy is false, just wait and do it after the cooldown
                while(currentTry < maxTries ):
                    if (not order):
                        order = self.periodicBuyEvent()
                    time.sleep(0.1)
                    if(order):
                        self.addOrUpdateOrder(order)
                        triggerWaitTime = np.abs(np.random.normal(repeat_sec,repeat_sec*0.3)) + skip_interval_after_buy*repeat_sec
                        self.nextTriggerTime.append(triggerWaitTime + time.time())          
                        self.tradingEventNr += 1
                        time.sleep(triggerWaitTime)
                        order = False
                        currentTry = 0
                    else:
                        time.sleep(10)
                        currentTry += 1
            else:
                triggerWaitTime = np.abs(np.random.normal(repeat_sec,repeat_sec*0.3))
                self.nextTriggerTime.append(triggerWaitTime + time.time())          
                self.tradingEventNr += 1
                time.sleep(triggerWaitTime)
                order = False
                currentTry = 0
            
    def periodicBuyEvent(self):
        price = self.ConnectionHandling.get_price(self.assetPairId[0])
        bid = float(price.payload[0].bid)
        ask = float(price.payload[0].ask)
        difference = ask - bid
        medium = (bid + ask)/2
        if(self.setPriceBidAskRatio):
            tradingPrice = self.setPriceBidAskRatio * difference + bid
        else:
            tradingPrice = medium
        total = self.buyAmount
        volume = dm.Order.calculateVolume(tradingPrice,total)
        order = dm.Order(self.assetPairId[0],0,volume, tradingPrice)
        order = self.placeOrder(order)
        return order
        
    def periodicTradeStream(self):
        restart = True
        while(restart):
            
            self.tradeEvents = self.ConnectionHandling.get_trades_stream()
            try:
                for tradeEvent in self.tradeEvents:
                    if(not str(tradeEvent) == ''):
                        self.ConnectionHandling = ch.ConnectionHandling()
                        if(hasattr(tradeEvent,'side')):
                            if(tradeEvent.side == 0):
                                if(tradeEvent.assetPairId in self.assetPairId):
                                    self.recentCompletedTrades.append(tradeEvent)
                        self.perfomSellStrategyForCompletedTrades()
                    else:       
                        pass
                        #PrintText('No trade news')
                        
            except Exception as e:
                PrintText(f'Periodic trade event error of {self.strategyName}: {e} - restart periodicTradeStream')
                self.ConnectionHandling = ch.ConnectionHandling()
                if(len(self.recentCompletedTrades)):
                    self.perfomSellStrategyForCompletedTrades()
                    
                    
############################################################         
############## --- Perform Trade Strategies --- ###############    
############################################################

    def performSellStrategyOrder(self,order,strategy = 0):
        #Just pass the matched order
        self.performSellStrategy(order.assetPairId,float(order.price),float(order.volume),strategy)
              
    def performSellStrategyAllAssets(self):
        balances = self.getBalance()
        currency = self.assetPair[0]
        
        for balance in balances:
            assetId = balance.assetId
            if(assetId == currency):
                pass
            else:
                assetPairId = assetId + currency
                self.performSellStrategyCurrentPriceMaxVolume(assetId, assetPairId)

    def performSellStrategyCurrentPriceMaxVolume(self,assetId, assetPairId,strategy = 0):
        freeVolume = self.getFreeVolume(assetId)
        self.performSellStrategyCurrentPrice(assetPairId,freeVolume)
        
    def performSellStrategyMaxVolume(self,assetId, assetPairId, price, strategy = 0):
        freeVolume = self.getFreeVolume(assetId)
        self.performSellStrategy(assetPairId, price, freeVolume)
        
    def performSellStrategyCurrentPrice(self,assetPairId,volume,strategy = 0):
        prices = self.ConnectionHandling.get_price(assetPairId)
        ask = prices.payload[0].ask
        
        price = float(ask)
        self.performSellStrategy(assetPairId, price, volume)

    def performSellStrategy(self,assetPairId,price,volume,strategy = 0):
        if(strategy):
            sellStrategy = strategy
        else:
            sellStrategy = self.sellStrategy
        # Check whether sell strategy workds
        try:
            minVolume = float(self.getMinVolume(assetPairId))
            maxParts = math.floor(float(volume)/minVolume)
            if maxParts > 0:
                if len(sellStrategy) > maxParts:
                    sellStrategy = SellStrategy.initialize(maxParts)
                
                # The safety margin helps that the last order still will be able to be performed.
                safetyMargin = 0.90
                while ((volume/len(sellStrategy))*safetyMargin < minVolume and safetyMargin < 1):
                    safetyMargin += 0.01
                # Places an order for each multiplier in the strategy, whereas a fraction of the volume is used.
                for multiplier in sellStrategy:
                    priceNewOrder = price * multiplier
                    volumeNewOrder = volume * sellStrategy[multiplier] * safetyMargin
                    newOrder = dm.Order(assetPairId, 'Sell', volumeNewOrder, priceNewOrder)
                    self.placeOrder(newOrder)
                    time.sleep(0.1)
            return True
        except Exception as e:
            PrintText(f'Exception in performSellStrategy: {e}')
            return False            
            
    def performSellStrategyLastBuyOrderOrCurrentPrice(self,assetId,assetPairId):
        '''
        Uses the higher price of either the last buy order or the current price to perform buy order

        '''
        order = self.getLastBuyOrder(assetPairId=assetPairId)
        order_price = float(order.price)
        current_price = self.getPriceBidAskAvarage(assetPairId)
        if (current_price > order_price):
            self.performSellStrategyMaxVolume(assetId,assetPairId,current_price)
        else:
            self.performSellStrategyOrder(order)     
            
    def perfomSellStrategyForCompletedTrades(self, maxTries = 3):
        currentTry = 1
        success = False
        while(len(self.recentCompletedTrades) and currentTry <= maxTries):
            recentTradeEvent = self.recentCompletedTrades[0].trades
            for completedTrade in recentTradeEvent:
                self.addOrUpdateOrder(completedTrade)
                # Only perform sell strategy for buy crypto currency order, not for sell cryptocurrency orders
                if(hasattr(completedTrade,'side')):
                    if(completedTrade.side == 0):
                        assetPairId = completedTrade.assetPairId
                        volume = float(completedTrade.baseVolume)
                        price = float(completedTrade.price)
                        if(assetPairId in self.assetPairId):
                            try:
                                PrintText(f'{self.strategyName}: TradeEvent: {assetPairId}, vol: {volume}, price: {price}')
                            except Exception as e:
                                PrintText(f'{self.strategyName} : Trade event {assetPairId}: failed to print text. Error: {e}')
                            success = self.performSellStrategy(assetPairId, price, volume)
            if(len(self.recentCompletedTrades)):
                if(success):
                    self.recentCompletedTrades.pop(0)
                    currentTry = 1
                else:
                    time.sleep(10)
                    currentTry += 1
            
    def handleAndCheckIncompletedTrades(self):
        pass
            
    # Orders
    def getActiveOrders(self):
        return self.ConnectionHandling.getActiveOrders()
    
    def getOrderById(self, orderId):
        return self.ConnectionHandling.getOrder(orderId)
    
    # Active Orders
    def getAllOrders(self):
        return self.ConnectionHandling.getAllOrders()

    def getMatchedOrders(self,assetPairId = 0):
        return self.ConnectionHandling.getMatchedOrders(assetPairId)
            
    def getLastBuyOrder(self,assetPairId= ''):
        orders = self.getMatchedOrders(assetPairId)
        for order in orders:
            # This should return the first buy order
            if order.side== 0:
                return order
        return ''
    
    def placeOrderVolPrice(self,assetPairId,volume,tradingPrice,side='Buy'):
        # side: 'Buy' or 'Sell'
        order = dm.Order(assetPairId,side,volume, tradingPrice)
        placedOrder = self.placeOrder(order)
        return placedOrder   
    
    def placeOrder(self,orderToPlace):
        # Format of orderToPlace: DataManipulation
        order = self.ConnectionHandling.place_order(orderToPlace)
        # If successful, save order
        if (order):
            self.placedOrders.append(order)
            self.addOrUpdateOrder(order)
        return order
    
    def cancelOrder(self,orderId):
        self.ConnectionHandling.cancel_order(orderId)
             
    def updateActiveOrders(self):
        activeOrders = self.getActiveOrders()
        self.activeOrders = {}
        for activeOrder in activeOrders:
            self.activeOrders[activeOrder.id] = activeOrder
            
    def getAllCompletedActiveOrders(self,side='all'):
        # SIDE: either sell, buy, or all
        currentActiveOrders = self.activeOrders
        newlyCompletedOrders = {}
        for orderId in currentActiveOrders:
            maxAttempts= 3
            attempt = 1
            successful = False
            while(attempt <= maxAttempts and not successful):
                try:
                    order =  self.ConnectionHandling.getOrder(orderId)
                    successful = True
                except:
                    time.sleep(10)
                    attempt += 1
            if(not successful):
                PrintText('getOrder not succesful for {orderId}')
                continue
            order = order.payload
            if(order.status == 'Matched' and order.assetPairId == self.assetPairId[0] and self.checkSide(order,side)):
                newlyCompletedOrders[order.id] = order
                PrintText('Order comleted:')
                PrintText(order)
        self.updateActiveOrders()
        return newlyCompletedOrders
    
    def checkSide(self,order,side):
        #SIDE: either sell, buy, or all
        if side == 'all':
            return True
        elif side =='sell':
            if(hasattr(order, side)):
                return order.side == side
        elif side == 'buy':
            if(hasattr(order, side)):
                return order.side == side
            else:
                return True
            
    def getInfo(self,assetID=''):
        text = str(self.getBalance(assetID)) 
        text += '\n' + str(self.getValueofAll())
        PrintText(text)
        return text
        
    def getBalance(self,assetID=''):
        return self.ConnectionHandling.get_balances(assetID)
    
    def getValueofAll(self, currency = 'EUR'):
        balances = self.getBalance()
        valueSet = {}
        total = 0
        header = {'price', 'volume','value (in CHF)'}
        table = pd.DataFrame(columns=header)
        # text = 'assetP :  price  : volume : value (in CHF)'
        for balance in balances:
            if(balance.assetId == 'EUR'):
                assetPairId = balance.assetId + 'CHF'
            else:
                assetPairId = balance.assetId + currency
            assetPairIdCHF = balance.assetId + 'CHF'
            priceInfosCurrency = self.getPrice(assetPairId)
            priceInfosCHF = self.getPrice(assetPairIdCHF)
            price = (float(priceInfosCurrency.payload[0].bid) + float(priceInfosCurrency.payload[0].ask))/2            
            priceCHF = (float(priceInfosCHF.payload[0].bid) + float(priceInfosCHF.payload[0].ask))/2
            volume = float(balance.available)
            value = priceCHF * volume
            total += value
            valueS = "{:.2f}".format(value)
            priceS = "{:.2f}".format(price)
            volumeS = "{:.4f}".format(volume)
            table.loc[assetPairId] = {'volume' : volumeS, 'price' : priceS, 'value (in CHF)' : valueS}
            # text += f'\n{assetPairId} : {priceS} : {volumeS} : {valueS} '
            valueSet[assetPairId] = valueS
        totalS = "{:.2f}".format(total)
        # valueSet['CHFSUM'] = totalS
        table.loc['CHFSUM'] = {'value (in CHF)' : totalS}
        return table
    
    def hasFreeVolumeHigherThanLimit(self,assetId,assetPairId):
        freeVolume = self.getFreeVolume(assetId)
        minVolume = self.getMinVolume(assetPairId)
        if(freeVolume > minVolume):
            return True
        else:
            return False
        
    def getFreeVolume(self,assetId):
        balance = self.getBalance(assetId)
        freeVolume = float(balance.available) - float(balance.reserved)
        return freeVolume
    
    def getMinVolume(self,assetPairId):
        assetPair = self.getAssetPairs(assetPairId)
        return float(assetPair.payload.minVolume)
    
    def getPrice(self,assetID = ''):
        return self.ConnectionHandling.get_price(assetID)
    
    def getPriceBidAskAvarage(self,assetPairId = ''):
        priceInfo = self.ConnectionHandling.get_price(assetPairId)
        bid = float(priceInfo.payload[0].bid) 
        ask = float(priceInfo.payload[0].ask) 
        priceAvarage = (bid+ask)/2
        return priceAvarage
    
    def get24HoursInfo(self,assetPairId=''):
        if(assetPairId == ''):
            assetPairId = self.assetPairId[0]   
        return self.ConnectionHandling.get24HoursStatistics(assetPairId)
    
    def strat_24h_buyLowNow(self,assetPairId, ):
        ''' 
        Description: 
            Uses min and max of 24 hours. Dependent on current value of the currency, it either returns true or false dependent on probability,
        Math:
            Chances (1 - (current $ - min $ 24h) < 0.5 are set to zero
            P($) = P_t * {(1 - (current $ - min $ 24h))/(max $ 24h - min $ 24 h)}^power
            P(h) = chance_multiplicator*P($) / hours
            P_t = P-week * P-month * P-year
            
            returns true with a P(h) probability
        '''
        
        # Time Interval adjustments of probability. Each factor has 1 at mean.
        W_T = wti.WeightTimeInterval
        w_d = W_T.day_p()
        w_w = W_T.week_p()
        w_m = W_T.month_p()
        w_y = W_T.year_p()
        
        P_t = w_d * w_w * w_m * w_y
        
        hours =  self.dayStrat_hours
        chance_multiplicator = self.dayStrat_Multiplicator
        power = self.dayStrat_Power
        
        returnValue = tryOrMail(lambda : self.get24HoursInfo(assetPairId=assetPairId))
        if(returnValue== False):
            raise Exception            
        info24 = returnValue
        lowPrice = float(info24.low)
        highPrice = float(info24.high)
        difference = (highPrice - lowPrice)
        
        currentInfo = self.getPrice(assetPairId)
        bid = float(currentInfo.payload[0].bid)
        ask = float(currentInfo.payload[0].ask)
        currentPrice = (bid + ask)/2
        
        chance_LIP = (1- (currentPrice-lowPrice)/difference)
        if(chance_LIP  < 0.5):
            chance_time_power_adjusted = 0
        else:
            chance_time_power_adjusted = chance_multiplicator * P_t * math.pow(max(0,chance_LIP),power)/hours
        rand_chance = random.random()
        PrintText(f'{self.strategyName}: chance: {chance_time_power_adjusted} P: {rand_chance}')
        if(rand_chance < chance_time_power_adjusted):
            return True
        else:
            return False
        
    def tradeInfoConversion(self, receive):
        # Returns a converted dict from a received order
        # @Param: receive: an order
        # @return: a dictionary
        convertedReturnOrder = {}
        convertedReturnOrder['id'] = receive.id
        convertedReturnOrder['assetPairId'] = receive.assetPairId
        convertedReturnOrder['volume'] = receive.volume
    
    def addOrUpdateOrder(self,order):
        try:
            if(hasattr(order,'id')):
                orderId = order.id
            elif(hasattr(order,'orderId')):
                orderId = order.orderId
            else:
                orderId = 'No order id found'
            txt = f'update for order with id {orderId}'
            
        except Exception as e:
           txt = f'failure during order update: {e}'
        #PrintText(txt)
        self.data.updateOrAddOrder(order)
        
    def orderCompletedEvent(self):
        pass
    
    def checkPrice(self,assetPairId):
        self.ConnectionHandling.get_price(assetPairId)
        
    def getAsset(self, assetID = ''):
        # assetID = e.g. ETH
        return self.ConnectionHandling.get_assets(assetID)
    
    
    def getAssetPairs(self, assetID = ''):
        return self.ConnectionHandling.getAssetPairs(assetID)

    # ***** Strategy *****

    # ***** Helpers *****
        
    # ***** Test Functions *****

# ***** Information *****
# ExampleOrder: 
# Returns a converted dict from a received order
# @Param: receive: an order
# @return: a dictionary

# id: "abeae4f1-b0e7-43c5-a86b-ce15c02d84b2"
# timestamp {
#   seconds: 1634457448
#   nanos: 576000000
# }
# status: "Placed"
# assetPairId: "ETHEUR"
# type: "Limit"
# price: "2100"
# volume: "0.001"
# filledVolume: "0.000"
# remainingVolume: "0.001"
# cost: "0.000"

# ---  Placed buy order ---

#  status: "Placed"
#  assetPairId: "ETHEUR"
#  type: "Limit"
#  price: "3804.8582"
#  volume: "0.0092"
#  filledVolume: "0.0000"
#  remainingVolume: "0.0092"
#  cost: "0.00000000",
#  id: "7be8d899-5450-4774-9f25-9a52c53a26ef"
#  timestamp {
#    seconds: 1636064955
#    nanos: 749000000
#  }

# --- Placed Sell Order ---

#  status: "Placed"
#  assetPairId: "ETHEUR"
#  type: "Limit"
#  side: sell
#  price: "5760.2643"
#  volume: "0.0013"
#  filledVolume: "0.0000"
#  remainingVolume: "0.0013"
#  cost: "0.00000000",
#  id: "08c67a4c-54b2-4b09-aac6-d0ec04639334"
#  timestamp {
#    seconds: 1636064955
#    nanos: 529000000
#  }
