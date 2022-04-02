#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
from pathlib import Path
import time
import datetime
from decimal import Decimal
import math



class Storage:
    # Variables:
    saveFolder= "/storage/"
    fileName = ''
    
    #Variables in initPath:
    savePath = ''
    fileLocation = ''
    
    #Table
    indexName = 'ID'
    # 
    
    
    def __init__(self,fileName = ''):
        self.fileName = fileName
        self.initPath()
        
    def initPath(self):
        self.currentPath = os.getcwd()
        self.savePath = str(Path(self.currentPath).parent.absolute()) + self.saveFolder
        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath) 
            
        self.fileLocation = self.savePath + self.fileName 
        return 
   
    # Saving
    def saveFilecsv(self): 
        self.table.to_csv(self.fileLocation)
    
    def openFile(self):
        try: 
            self.file = open(self.fileLocation,'a')
            return self.file
        except:
            print(f'no file opened at {self.fileLocation}')
            self.file = ''
            
    def closeFile(self):
        self.file.close()
        
    def loadFilecsv(self):
        try: 
            self.table = pd.read_csv(self.fileLocation)          
            #print(f'File {self.fileLocation} loaded')
        except:
            self.createTable()
            
            
    def createTable(self):
        self.table = pd.DataFrame(columns=self.tableHeader)
        self.table.index.name = self.indexName
    

class DataManipulation(Storage):

    fileNameBase= "Tracked_Tradings_"
    
    def __init__(self, ID_Strategy):
        # Init variables
        fileName = self.fileNameBase + ID_Strategy + '.csv' 
        super().__init__(fileName)
         
        self.tableHeader = {"date","status", "role", "assetPairId", "type", "side", "price", "volume","filledVolume","baseVolume",  "cost","quoteVolume","tradeCompl","tradeSet"}  
        self.ID_Strategy = ID_Strategy
        
        # load file
        self.loadFile()
        
    def initID(self):
        self.currentId = 0
    
    def initPath(self):
        self.currentPath = os.getcwd()
        self.savePath = str(Path(self.currentPath).parent.absolute()) + self.saveFolder
        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath) 
            
        self.fileLocation = self.savePath+self.fileName
        return 
    
    def getHeaders(self):
        return self.tableHeader;
    
    def saveFile(self): 
        self.table.to_csv(self.fileLocation)
        
    def loadFile(self):
        try: 
            self.table = pd.read_csv(self.fileLocation,index_col='ID') 
            #print(f'File {self.fileLocation} loaded')
        except:
            self.createTable()
        
    def createColumn(assetPairId,side,volume,price,total,completed):
        pass
    
    def addOrder(self,order):
        self.loadFile()
        self.addObjectToTable(order)
        self.saveFile()
        
        
    def getRow(self,order):
        rowDict = {}
        for  prop in self.tableHeader:
            if(hasattr(order,prop)):
                rowDict[prop] = getattr(order,prop)
        rowDict['date'] = order.timestamp.seconds
        return rowDict
    
    def getSideBuy(self):
        return self.getRowsCriterias({'side':0})
    
    def getSideSell(self):
        return self.getRowsCriterias({'side':1})
    
    def getLastComnpletedBuy(self):
        table = self.getRowsCriterias({'side':0,'status':''})
        table_sorted = self.sortTableBy(table,'date')
        if len(table):
            return table[0]
        else:
            return ''
    
    def getRowsCriterias(self,criterias):
        # Pass criterias as a dict with key = name of column head, value = fitered criteria
        self.loadFile()
        filtered_table = self.table
        for crit_name in criterias:
            filtered_table = filtered_table.loc[filtered_table[crit_name] == criterias[crit_name]]
        return filtered_table
        
    def sortTableBy(self,table, column_head):
        return table.sort_values(by = [column_head])
    
        
    def updateOrAddOrder(self,order):
            self.loadFile()
            self.addObjectToTable(order)
            self.saveFile()
        
    def addObjectToTable(self, objectToAdd):
        #print(f'Object to add {objectToAdd}')
        header = self.table.head()
        row = {}
        row['date'] = str(datetime.datetime.now())
        if(hasattr(objectToAdd,'id')):
           orderId = getattr(objectToAdd,'id')
        elif (hasattr(objectToAdd,'orderId')):
            orderId = getattr(objectToAdd,'orderId')
        else:
            print(f'{objectToAdd} has no id')
            return
        if (orderId):
            for columnhead in header:
                if(hasattr(objectToAdd,columnhead)):
                    row[columnhead] = getattr(objectToAdd,columnhead)
            
            #print(f'Row: {row}')
            try:
                if(orderId in self.table.index):
                    for col_index in row:
                        self.table.loc[orderId,col_index] = row[col_index]
                else:
                    self.table.loc[orderId] = row
            except Exception as e:
                
                print(f'caused error during saving table: {e}')
                print(f'row: {row}')
                print(f'key: {orderId}')
                print(f'table: {self.table}')
        else:
            return

    
    # TODO: CHange these    
    def getPropertiesDict(self):
        self.rowDict = {}
        for  prop in self.properties:
            self.rowDict[prop] = [getattr(self,prop)]
        return self.rowDict
            
    def getDFRow(self):
        return pd.DataFrame(self.getPropertiesDict())
        

class Order:
    # Side: buy: 0: sell: 1
    properties = {"orderId","date","assetPairId","side","volume","price","total","tradeCompl","tradeSet"}    
    init_properties = {"_side","_assetPairId","_volume","_price"}
    minVolume = 0.001

    @property
    def side(self):
        if self._side == 0 or self._side == '0':
            return 0
        elif self._side == 1 or self._side == '1':
            return 1
        elif self._side == 'Buy':
            return 0
        elif self._side == 'Sell':
            return 1
        else:
            return False
    @side.setter
    def side(self,a):
        self._side = a
        
    @property
    def assetPairId(self):
        return str(self._assetPairId)
    @assetPairId.setter
    def assetPairId(self,a):
        self._assetPairId = a
        
    @property
    def volume(self):
        return "{:.4f}".format(float(self._volume))
    @volume.setter
    def volume(self,a):
        self._volume = a
        
    @property
    def price(self):
        return "{:.2f}".format(float(self._price)) 
    @price.setter
    def price(self,a):
        self._price = a
        
    @property
    def total(self):
        if(self._price and self._volume):
            return "{:.4f}".format(float(self._price)*float(self._volume)) 
        else:
            return "{:.4f}".format(float(self._total)) 
    @total.setter
    def total(self,a):
        self._total = a
        
    def maxParts(volumeTotal,minVolume= 0.001):
        return math.floor(volumeTotal/minVolume)

    def __init__(self):     
        # Add properties
        for prop in self.init_properties:
            setattr(prop, '')
    def __init__(self,assetPairId,side,volume,price):  
        # Add properties
        self.create(assetPairId,side,volume,price)
        
    def transformLykkeOrder(self,order):
        self.assetPairId = order.assetPairId
        self.price = order.price
        self.volume = order.volume
        self.orderId = order.id
            
    def create(self,assetPairId,side,volume,price):
        self.updateTime()
        self.assetPairId = assetPairId
        self.side = side
        self.volume = volume
        self.price = price
        try:
            self.total = float(volume) * float(price)
        except:
            self.total = '-'
        self.tradeCompl = False
        self.tradeSet = False
        
    def calculateVolume(price, total):
        return  total / (float (price))
    
    def printOrder(self):
        print('Order')
        for prop in self.properties:
            try:
                attr = getattr(self,prop)
                print(f'{prop}: {attr} ')
            except:
                print(f'{prop}: not available ')
        
    def updateTime(self):
        self.date = time.localtime()
    
    def put(self,orderId):
        self.orderId = orderId
        self.tradeSet = True
        self.updateTime()
    
    def getPropertiesDict(self):
        self.rowDict = {}
        for  prop in self.properties:
            self.rowDict[prop] = [getattr(self,prop)]
        return self.rowDict
            
    def getDFRow(self):
        return pd.DataFrame(self.getPropertiesDict())
        
        
n = DataManipulation("Alpha_0")
n.saveFile()

# timestamp {
#   seconds: 1636917416
#   nanos: 656000000
# }
# lastTradeTimestamp {
#   seconds: 1636928228
#   nanos: 628000000
# }
# status: "Matched"
# assetPairId: "ETHEUR"
# type: "Limit"
# side: sell
# price: "4012.64"
# volume: "0.001"
# filledVolume: "0.001"
# remainingVolume: "0"
# cost: "4.01264"