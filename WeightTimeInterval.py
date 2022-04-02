#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 11:21:42 2021

@author: OldMac
"""

# API: 854ba3cf36829a354b2835b87df055bbf0e4d39bc1de1aadc431a838dc54d7d2


class WeightTimeInterval:
    def week_p(std_dev = 0.3):
        '''
        std_dev: Standard deviation around 1

        Returns
        -------
        float
           A probabibility using values of the week. 1 is the standard value. Higher values than one means that it is more useful to buy the stock,
           where lower values means the contrary. 

        '''

        return 1
    def month_p(std_dev = 0.2):
        '''
        std_dev: Standard deviation around 1

        Returns
        -------
        float
           A probabibility using values of the month. 1 is the standard value. Higher values than one means that it is more useful to buy the stock,
           where lower values means the contrary

        '''
        return 1

    def year_p(std_dev = 0.1):
        '''
        std_dev: Standard deviation around 1

        Returns
        -------
        float
           A probabibility using values of the year. 1 is the standard value. Higher values than one means that it is more useful to buy the stock,
           where lower values means the contrary

        '''
        return 1
    
    def day_p():
        '''
        std_dev: Standard deviation around 1

        Returns
        -------
        float
           A probabibility using values of the year. 1 is the standard value. Higher values than one means that it is more useful to buy the stock,
           where lower values means the contrary

        '''
        return 1