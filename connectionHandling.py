import grpc
import common_pb2
import common_pb2_grpc
import privateService_pb2
import privateService_pb2_grpc
import publicService_pb2
import publicService_pb2_grpc
import google.protobuf
import DataManipulation
from PrintFunction import PrintText
import time
import ExceptionHandling
from ExceptionHandling import ExceptionHandling as tryOrMail

class ConnectionHandling(object):
    
    @property
    def private_api(self):
        currentTry = 0
        maxTries = 3
        while (currentTry < maxTries):
            try:
                API_KEY = self.API_KEY
                token_credentials = grpc.access_token_call_credentials(API_KEY)
                ssl_credentials = grpc.ssl_channel_credentials()
                credentials = grpc.composite_channel_credentials(ssl_credentials, token_credentials)
                channel = grpc.secure_channel("hft-apiv2-grpc.lykke.com:443", credentials)
                pa = privateService_pb2_grpc.PrivateServiceStub(channel)
                self._private_api = pa
                return pa
            except:
                time.sleep(0.5)
                currentTry += 1
        return False
            
    @private_api.setter
    def private_api(self,a):
         self._private_api = a     
         
    @property
    def public_api(self):
        currentTry = 0
        maxTries = 3
        while (currentTry < maxTries):
            try:
                API_KEY = self.API_KEY
                token_credentials = grpc.access_token_call_credentials(API_KEY)
                ssl_credentials = grpc.ssl_channel_credentials()
                credentials = grpc.composite_channel_credentials(ssl_credentials, token_credentials)
                channel = grpc.secure_channel("hft-apiv2-grpc.lykke.com:443", credentials)
                pa = publicService_pb2_grpc.PublicServiceStub(channel)
                self._public_api = pa
                return pa
            except:
                time.sleep(0.5)
                currentTry += 1
        return False
            
    @public_api.setter
    def public_api(self,a):
         self._public_api = a
         
    @property
    def API_KEY(self):
        if(hasattr(self,'_API_KEY')):
            return self._API_KEY
        else:
           API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IndhbGxldCIsImF1ZCI6ImhmdC1hcGl2Mi5seWtrZS5jb20iLCJrZXktaWQiOiJlZTVkM2IxNC1hNjJlLTQ1YTMtOTliMS1lOTMyOTY3ZTM0YzkiLCJjbGllbnQtaWQiOiJkNmM5YWRhMS1kMjIzLTQ2ZDktOWVlZS0wZTdkMjJlNGY5ZTQiLCJ3YWxsZXQtaWQiOiI5NTQxNDg1Yi0xMmRiLTQxNTItOGRiZi1jM2EyMWZjODI5ODAiLCJhcGl2Mk9ubHkiOiI5NTQxNDg1Yi0xMmRiLTQxNTItOGRiZi1jM2EyMWZjODI5ODAiLCJuYmYiOjE2MzEzODMyMTksImV4cCI6MTk0NjkxNjAxOSwiaWF0IjoxNjMxMzgzMjE5fQ.QAVIkz17okRQP4241Zgw_AbbEXL3XUab0N9TRQDs9Zw'
           self._API_KEY = API_KEY
           return API_KEY
            
    @API_KEY.setter
    def API_KEY(self,a):
         self._API_KEY = a
        
    
    def __init__(self):
        self.createConnection()
        #Init Parameter
        self.usedAssetPairIdList = ['ETHEUR','BTCEUR']
        self.status = {0:'Placed',1:'Cancelled',2:'Matched'}
        self.maxTries = 3
        
    
    def createConnection(self):
        # use ssl creds
        self.ssl_credentials = grpc.ssl_channel_credentials()
        # use auth creds
        self.token_credentials = grpc.access_token_call_credentials(self.API_KEY)
        # aggregate creds
        self.credentials = grpc.composite_channel_credentials(self.ssl_credentials, self.token_credentials)
        #create a channel
        channel = grpc.secure_channel("hft-apiv2-grpc.lykke.com:443", self.credentials)
        self.private_api = privateService_pb2_grpc.PrivateServiceStub(channel)
        #init public connection
        self.public_api = publicService_pb2_grpc.PublicServiceStub(channel)
        

    def get_balances(self,assetId =''):
      balances = tryOrMail(lambda : self.private_api.GetBalances(google.protobuf.empty_pb2.Empty()))
      maxTries = self.maxTries
      currentTry = 0
      success = False
      while(currentTry < maxTries):
          if(hasattr(balances,'payload')):
              balances = balances.payload
              success = True
              break
          else:
              time.sleep(0.5)
              balances = tryOrMail(lambda : self.private_api.GetBalances(google.protobuf.empty_pb2.Empty()))
              currentTry += 1
         
      if(success == False):
          PrintText('Error in connectionHandling: get_balance: no success')
          return False

      if assetId:
          for balance in balances:
              if balance.assetId == assetId:
                  return balance
          return
      else:
          return balances
      

    def get_volume(self,assetId=''):
        request = tryOrMail(lambda : privateService_pb2.OrdersRequest())
        if(assetId):
            # TODO: Not yet implemented
            return tryOrMail(lambda : self.private_api.GetBalances(request))
        else:
            return tryOrMail(lambda : self.private_api.GetBalances(request))
    
    
    # ****** Orders********
    def place_order(self,order):
      #**************
      request = tryOrMail(lambda : privateService_pb2.LimitOrderRequest())
      request.assetPairId = order.assetPairId
      request.side = order.side
      request.volume = order.volume 
      request.price =  order.price
      
      #order.printOrder()
      response = tryOrMail(lambda : self.private_api.PlaceLimitOrder(request))
      order = response.payload
      orderId = order.orderId
     
      if(orderId):
          
          time.sleep(2)
          recOrder = self.getOrder(orderId).payload
          if(recOrder.id == orderId):
              #print(f'We got an order {recOrder}')
              try:
                  total = float(recOrder.volume) * float(recOrder.price)
                  PrintText(f"{recOrder.status}: {recOrder.assetPairId}, {recOrder.side}, $: {recOrder.price}, v: {recOrder.volume}, cost: {total}, id: {orderId}")
              except Exception as e:
                  PrintText(f"Order placed! orderId: {orderId}, failure {e}")
              return recOrder
          else:
              print(f'We got no order for orderId {orderId}')
              print(f'Order is the following: {order}')
              return order
      else:
          PrintText(f"Order placement unsuccessful, status: {response} ")
          return False
      
        # ***  Cancel orders ******
    def cancel_order(self,orderId):
    
      cancel_request = privateService_pb2.CancelOrderRequest()
      cancel_request.orderId = orderId  
      cancel_response = self.private_api.CancelOrder(cancel_request)
    
      PrintText(f"Order cancel response: {cancel_response.payload}")
      
    def cancelAllOrders(self,assetPairId =0,side='None'):
        request = tryOrMail(lambda : privateService_pb2.CancelOrdersRequest())
        if side == 'None':
            cancelBuy = self.cancelAllOrders(side=0)
            cancelSell = self.cancelAllOrders(side=1)
            return cancelBuy + cancelSell
        else:
            request.side = side
            if(assetPairId):
                request.assetPairId = assetPairId
                cancel_response = self.private_api.CancelAllOrders(request)
                PrintText(f"Order cancel response: {cancel_response.payload}")
            else:
                cancel_response = []
                for assetPairId in self.usedAssetPairIdList:
                    request.assetPairId = assetPairId
                    cancel_response.append(self.private_api.CancelAllOrders(request))
                    PrintText(f"Order cancel response: {cancel_response[-1].payload}")     
            return cancel_response
        
    # ***  Information  ******
    # Note: All the orders are not tested yet  
    def getActiveOrders(self,assetPairId = 0):
        return self.getOrders(assetPairId,active = True)
    
    def getCompletedOrders(self,assetPairId = 0):
        return self.getOrders(assetPairId,active = False)
    
    def getMatchedOrders(self,assetPairId = 0):
        return self.getOrders(assetPairId,active = False, status='Matched')
            
    def getAllOrders(self,assetPairId = 0):
        return self.getOrders(assetPairId,active = 'All')
    
    def getOrders(self,i_assetPairId = 0, active = True, status = 0):
        # Note: Works and is tested
        # @Param: request returns a variable having a attribute payload with a array containing the stuff
        # Access the variables by using it as property, e.g. request[0].id
        # Format: 
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
        request = tryOrMail(lambda : privateService_pb2.OrdersRequest())
        orders = []   
        if (i_assetPairId):
            assetPairIds= []
            assetPairIds.append(i_assetPairId)
        else:
            assetPairIds = self.usedAssetPairIdList     
        for assetPairId in assetPairIds:
            request.assetPairId = assetPairId
            if(active == True):
                receive = self.private_api.GetActiveOrders(request)
                receive = receive.payload
                for order in receive:      
                    orders.append(order)
            elif  (active == False):
                receive = self.private_api.GetClosedOrders(request)
                receive = receive.payload
                for order in receive:      
                    orders.append(order)
            else:
                receive = self.private_api.GetActiveOrders(request)
                receive = receive.payload
                for order in receive:      
                    orders.append(order)
                receive = self.private_api.GetClosedOrders(request)
                receive = receive.payload
                for order in receive:      
                    orders.append(order)
                    
        if status == 0:
            return orders
        else:
            filteredOrders = []
            for order in orders:
                if order.status == status:
                    filteredOrders.append(order)
            return filteredOrders
               
    def getOrder(self, orderId):
        request = tryOrMail(lambda : privateService_pb2.OrderRequest())
        request.orderId = orderId
        order = tryOrMail(lambda : self.private_api.GetOrder(request))
        return order
    
    def get24HoursStatistics(self, assetPairId, currentTry=0, maxTries = 3):
        if(currentTry >= maxTries):
            PrintText('Failure during get24HourseStatistics: File:ConnectionHandling')
            return False
        request = tryOrMail(lambda : publicService_pb2.TickersRequest(assetPairIds = [assetPairId]))
        function = lambda : self.public_api.GetTickers(request)
        info = tryOrMail(function)
        
        returnValue = tryOrMail(lambda : info.payload[0])
        if (returnValue):
            return returnValue
        else:
            self.get24HoursStatistics(assetPairId,currentTry+1)            
    def orderIsCompletedOrCancelled(self, orderId):
        # Note: Not completed : Status could be different
        order = self.getOrder(orderId)
        if (order.status == 'completed'or order == False):
            return True
        else:
            return False
                   
    def streamCompletedTrades(self,assetPairId=0,side='None'):
        PrintText('Stream started')
        request = privateService_pb2.OrdersRequest()
        self.trade_stream = []
        if (assetPairId):
            request.assetPairId = assetPairId
            stream = self.private_api.GetTradeUpdates(request)
            self.trade_stream.append(stream)
        else:
            for aPI in self.usedAssetPairIdList:
                request.assetPairId = aPI
                stream = self.private_api.GetTradeUpdates(request)
                self.trade_stream.append(stream)            
        return self.trade_stream     
    
    def get_price_updates(self, assetPairId):
      request = publicService_pb2.PriceUpdatesRequest()
      request.assetPairIds.extend([assetPairId]) # or [] for all asset pairs
      stream = self.public_api.GetPriceUpdates(request)
      try:
        for price in stream:
          PrintText(f"{price.assetPairId} bid: {price.bid}, ask: {price.ask}, timestamp: {price.timestamp.ToDatetime()}")
      except KeyboardInterrupt:
        stream.cancel()
    def get_price(self, assetPairId=''):
      #PrintText('get prices')
      request = publicService_pb2.PriceUpdatesRequest()
      if assetPairId:
          request.assetPairIds.extend([assetPairId]) # or [] for all asset pairs
      else:
          request.assetPairIds.extend([]) 
     
      prices = self.public_api.GetPrices(request)
      #for price in prices.payload:
      #    PrintText(f"{price.assetPairId} bid: {price.bid}, ask: {price.ask}, timestamp: {price.timestamp.ToDatetime()}")
      return prices

    def get_trades_stream(self):
      stream = self.private_api.GetTradeUpdates(google.protobuf.empty_pb2.Empty())
      return stream

    def get_assets(self,assetId = ''):
        request = publicService_pb2.AssetRequest()
        if assetId:
            request.assetId = assetId
            asset = self.public_api.GetAsset(request)
        else:
            asset = self.public_api.GetAssets(request)
        return asset
        # Returns;
        # assetId	string	Asset unique identifier.
        # name	string	Asset name.
        # symbol	string	Asset symbol.
        # accuracy	uint	Maximum number of digits after the decimal point which are supported by the asset.
        
    def getAssetPairs(self,assetId = ''):
        request = publicService_pb2.AssetRequest()
        if assetId:
            request.assetId = assetId
            asset = self.public_api.GetAssetPair(request)
        else:
            asset = self.public_api.GetAssetPairs(request)
        return asset
        # Returns;
        # assetId	string	Asset unique identifier.
        # name	string	Asset name.
        # symbol	string	Asset symbol.
        # accuracy	uint	Maximum number of digits after the decimal point which are supported by the asset.
    

        
#ch = ConnectionHandling()
#get_balances()
#a = ConnectionHandling()
#a.place_order("ETHEUR",0,"0.001","2000")       
#place_cancel_order
#get_quotes()
#get_trades()