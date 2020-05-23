# -*- coding: utf-8 -*-
"""
Created on Thu May 21 11:37:55 2020

@author: tomw1
"""

import numpy as np
import pandas as pd


def get_libor(returns):
    
    rfr = pd.read_csv("Data/USD1MTD156N.csv")
    rfr['Date'] = [x[6:] + "-" + x[3:5] + "-" +x[:2] for x in rfr['DATE']]
    rfr = rfr.drop(['DATE'], axis=1).set_index("Date")
    rfr = rfr.replace('.', np.nan)
    rfr = rfr.fillna(method ='ffill') 
    
    short = [date for date in rfr.index]
    long = [x for x in returns.index]
    test = [float(rfr['VALUE'][l])/(100*365) if l in short else float(rfr['VALUE'][short[0]])/(100*365) for l in long]


    libor = pd.DataFrame({'Date':long, 'rfr':test}).set_index("Date")
    
    libor.to_csv("Data/libor.csv")
    
    return libor
    