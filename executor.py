
#!/usr/bin/python
"""
Created on Thu Nov 11 10:22:42 2021

@author: OldMac
"""

import time
from PrintFunction import PrintText

from strategy_alpha_ETH import Strategy_alpha_ETH
from strategy_alpha_BTC import Strategy_alpha_BTC
from strategy_alpha_BASE import Strategy_alpha
from ExceptionHandling import ExceptionHandling 
from MailHandling import MailHandling
try:
    bot = Strategy_alpha()
    TradingBot = {}
    TradingBot['Alpha ETH'] = Strategy_alpha_ETH()
    bot1 = TradingBot['Alpha ETH']
    time.sleep(0.5)
    TradingBot['Alpha BTC'] = Strategy_alpha_BTC()
    bot2 = TradingBot['Alpha BTC']
except Exception as e:
    
    PrintText(str(e),'Exception')
    MailHandling(str(e))