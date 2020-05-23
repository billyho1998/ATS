# -*- coding: utf-8 -*-
"""
Created on Sun May 17 19:25:15 2020

@author: tomw1
"""

import datetime as dt
import matplotlib.pyplot as plt    
import numpy as np
import pandas as pd
import random
import sys

def PerformStatistics(returns, rfr, label=None, BUS_DAYS = 252):
    
    
    if label is None:
        stats = pd.DataFrame(index=[0])
    else:
        stats = pd.DataFrame(index=[label])

    try:
        col = returns.columns[0]
        cumReturns = (((returns+1).cumprod()-1))[col]
        ret = returns[col]
    except AttributeError:
        cumReturns = (((returns+1).cumprod()-1))
        ret = returns
            
    cumReturns.plot(title=label, linewidth=1)
    plt.show()
    plt.close()

    stats['Tot Ret (%)']        = cumReturns.iloc[-1] * 100
    stats['Avg Ret (%)']        = ret.mean() * BUS_DAYS * 100
    
    stats['rfr']                = rfr['rfr'].mean() * 365 * 100
    
    stats['Std (%)']            = ret.std()*np.sqrt(BUS_DAYS)*100
    stats['Skewness']           = ret.skew()
    stats["Kurtosis"]           = ret.kurt()
    
    stats["HWM"]                = cumReturns.max() * 100
    stats["HWM Date"]           = cumReturns.idxmax()
    DD                          = cumReturns.cummax() - cumReturns
    end_mdd                     = DD.idxmax()
    start_mdd                   = (cumReturns[:end_mdd]).idxmax()
    stats['MDD']                = (1 - cumReturns[end_mdd]/cumReturns[start_mdd]) * 100
    stats['Peak date']          = start_mdd
    stats['Trough date']        = end_mdd
    
    stats['SR']                 = ( stats['Avg Ret (%)']-stats['rfr'] ) / stats['Std (%)']
    stats['Inv. Calmar Ratio']  = stats['MDD'] / stats['Avg Ret (%)']
    bool_P                      = cumReturns[end_mdd:] > cumReturns[start_mdd]
    
#    if (bool_P.idxmax() > bool_P.idxmin()):
#        stats['Rec date']    = bool_P.idxmax()
#        a = dt.datetime.strptime(stats['Rec date'].values[0], '%Y-%m-%d').date()
#        b = dt.datetime.strptime(stats['Peak date'].values[0], '%Y-%m-%d').date()
#        stats['MDD dur']     = (a - b).days
#    else:
#        stats['Rec date']    = stats['MDD dur']  ='Yet to recover'

    print(stats.T)
    
    return
    
    
    
    
    
    


