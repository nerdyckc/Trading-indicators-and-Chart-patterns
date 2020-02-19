# -*- coding: utf-8 -*-
"""
@author: techietrader

enhancement by nerdyckc, 31 Jan 2020
utilise talib package, replace all FOR loops with DF internal functions to improve performance
"""

import numpy as np
import pandas as pd
import talib


#SuperTrend
def ST(df,f,n): #df is the dataframe, n is the period, f is the factor; f=3, n=7 are commonly used.
    # calculation of ATR using TALIB function
    df['H-L']=abs(df['high']-df['low'])
    df['H-PC']=abs(df['high']-df['close'].shift(1))
    df['L-PC']=abs(df['low']-df['close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1)
    df['ATR']=talib.ATR(df['high'], df['low'], df['close'], timeperiod=n)

    #Calculation of SuperTrend
    df['Upper Basic']=(df['high']+df['low'])/2+(f*df['ATR'])
    df['Lower Basic']=(df['high']+df['low'])/2-(f*df['ATR'])
    df['Upper Band']=df['Upper Basic']
    df['Lower Band']=df['Lower Basic']
    df['SuperTrend']=np.nan

    # calculate the bands: 
    # in an UPTREND, lower band does not decrease
    # in a DOWNTREND, upper band does not increase
    for i, row in df[n+1:].iterrows():    # begin from row "n"
        # if currently in DOWNTREND (i.e. price is below upper band)
        prevClose = df['close'].loc[i-1]
        prevUpperBand = df['Upper Band'].loc[i-1]
        currUpperBasic = row['Upper Basic']
        if prevClose <= prevUpperBand:
            # upper band will DECREASE in value only
            df.loc[i, 'Upper Band'] = min(currUpperBasic, prevUpperBand)
        
        # if currently in UPTREND (i.e. price is above lower band)
        prevLowerBand = df['Lower Band'].loc[i-1]
        currLowerBasic = row['Lower Basic']
        if prevClose >= prevLowerBand:
            # lower band will INCREASE in value only
            df.loc[i, 'Lower Band'] = max(currLowerBasic, prevLowerBand)
            
        # >>>>>>>> previous period SuperTrend <<<<<<<<
        if prevClose <= prevUpperBand:
            df.loc[i-1, 'SuperTrend'] = prevUpperBand
        else:
            df.loc[i-1, 'SuperTrend'] = prevLowerBand
        prevSuperTrend = df['SuperTrend'].loc[i-1]

    for i, row in df[n+1:].iterrows():    # begin from row "n"
        prevClose = df['close'].loc[i-1]
        prevUpperBand = df['Upper Band'].loc[i-1]
        currUpperBand = row['Upper Band']
        prevLowerBand = df['Lower Band'].loc[i-1]
        currLowerBand = row['Lower Band']
        prevSuperTrend = df['SuperTrend'].loc[i-1]
        
        # >>>>>>>>> current period SuperTrend <<<<<<<<<
        if prevSuperTrend == prevUpperBand and row.close <= currUpperBand:
            df.loc[i, 'SuperTrend'] = currUpperBand        # remain in DOWNTREND
        elif prevSuperTrend == prevUpperBand and row.close > currUpperBand:
            df.loc[i, 'SuperTrend'] = currLowerBand        # switch to UPTREND
        elif prevSuperTrend == prevLowerBand and row.close >= currLowerBand:
            df.loc[i, 'SuperTrend'] = currLowerBand        # remain in UPTREND
        elif prevSuperTrend == prevLowerBand and row.close < currLowerBand:
            df.loc[i, 'SuperTrend'] = currUpperBand        # switch to DOWNTREND
            
    return df
