# -*- coding: utf-8 -*-
"""
Created on Sun May 17 11:33:03 2020

@author: tomw1
"""

import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import libor_rate as lr
import data_summary as ds
import performance_statistics as ps
import risk_parity as rp

import sys

###############################################################################
##############################DATA COLLECTION##################################
###############################################################################    


"""
    Get data from file
"""
data = pd.read_excel("Data/Commodity Data.xlsx", sheet_name = "Return indices").set_index("date")
asset_sector = pd.read_excel("Data/Commodity Data.xlsx", sheet_name = "Assets")
try:
    returns = pd.read_csv("Commodity_Returns.csv").set_index("date")
except FileNotFoundError:
    returns = data.pct_change()
    returns.to_csv("Commodity_Returns.csv")
    
"""
    Get libor rate from file 'USD1MTD156N.csv' and back date it to get a daily libor
"""    
try:
    rfr = pd.read_csv("Date/libor.csv")
except FileNotFoundError:
    rfr = lr.get_libor(returns)
    
    
###############################################################################
##############################DATA SUMMARY#####################################
###############################################################################    
    
"""
    Get list of commodities in each sector
"""
agri_livestock = [asset_sector["Commodity"][i] for i in range(asset_sector.shape[0]) if asset_sector["Sector"][i]=="Agri & livestock"]
energy = [asset_sector["Commodity"][i] for i in range(asset_sector.shape[0]) if asset_sector["Sector"][i]=="Energy"]
metals = [asset_sector["Commodity"][i] for i in range(asset_sector.shape[0]) if asset_sector["Sector"][i]=="Metals"]
commodities = agri_livestock + energy + metals

"""
    Summarize commodity data
"""
ds.summarize_data(data, commodities)

"""
    Create commodity market factor
"""
ones = np.ones(shape=(len(data),len(commodities)))
signals = pd.DataFrame(ones, columns=commodities)
signals.index = data.index

market_factor = pd.DataFrame({"Benchmark":(signals*returns).mean(axis=1)})

###############################################################################
##############################STRATEGIES#######################################
###############################################################################    
    
"""
    Response Speed to Signal
"""
lag = 1

"""
    Moving Average Signal:
"""
# MA Parameters
slow = 50
fast = 20
MA_signal = data.apply(lambda x: x.rolling(fast).mean()>x.rolling(slow).mean(), axis=0).astype(int) * 2 - 1

try:
    strategy_MA = pd.read_csv("MA_{}_{}.csv".format(slow, fast)).set_index("date")
except FileNotFoundError:

    rolling_slow = data.rolling(window=slow).mean()
    rolling_fast = data.rolling(window=fast).mean()
    
    strategy_MA = pd.DataFrame({"Strategy": (MA_signal.shift(lag)*returns).mean(axis=1)})

    strategy_MA.to_csv("MA_{}_{}.csv".format(slow, fast))
 
    
"""
    Exponentially Weighted Moving Average Signal:
"""

EWMA_signal = data.apply(lambda x: x.ewm(span=fast).mean()>x.ewm(span=slow).mean(), axis=0).astype(int) * 2 - 1
try:
    strategy_EWMA = pd.read_csv("EWMA_{}_{}.csv".format(slow, fast)).set_index("date")
except FileNotFoundError:
    
    exponential_slow = data.ewm(span=slow).mean()
    exponential_fast = data.ewm(span=fast).mean()
    
    strategy_EWMA = pd.DataFrame({"Strategy": (EWMA_signal.shift(lag)*returns).mean(axis=1)})

    strategy_EWMA.to_csv("EWMA_{}_{}.csv".format(slow, fast))





# Breakout paramters
mu = 100
lam = 50


def breakout(x):
    
    # Set the first mu signals to zero
    sig = [0 for i in range(mu)]
    
    n = commodities.index(x.name) + 1
    # Progress report
    print("\n (", n, "/24): ", x.name, "\n")
    
    # Loop through all dates, starting from the mu-th day
    for d in x.index[mu:]:
        
        # If commodity breaches mu-day high go long
        if x.loc[d] == x.rolling(mu).max()[d] or sig[-1] == 1:
            # If commodity goes below lambda-day low exit long position, else stay long
            if x.loc[d] == x.rolling(lam).min()[d]:
                sig.append(0)
#                print("Exit: {}".format(d.date()))
            else:
#                if sig[-1] != 1:
#                    print("Long: {}".format(d.date()))
                sig.append(1)
                
        # If commodity breaches mu-day low go short        
        elif x.loc[d] == x.rolling(mu).min()[d] or sig[-1] == -1:
            # If commodity goes above lambda-day high exit short position, else stay short
            if x.loc[d] == x.rolling(lam).max()[d]:
                sig.append(0)
#                print("Exit: {}".format(d.date()))
            else:
#                if sig[-1] != -1:
#                    print("Short: {}".format(d.date()))
                sig.append(-1)
                
        # Stay out of market       
        else:
            sig.append(0)
            
    print("Long: {} \n Neutral: {} \n Short: {}".format(sig.count(1), sig.count(0), sig.count(-1)))
    
    return sig

"""
    Breakout Signal:
"""

try:
    breakout_signal = pd.read_csv("breakout_{}_{}.csv".format(mu,lam)).set_index("date")
except FileNotFoundError:
    breakout_signal = data.apply(breakout, axis=0)
    breakout_signal.to_csv("breakout_{}_{}.csv".format(mu, lam))
            


"""
    Volotility Scaling: - Needs to be normalized
"""           

rolling_vol = returns.rolling(window=126).std()
vol_parity = np.sqrt(12/10000) / rolling_vol

vol_breakout = (breakout_signal*vol_parity) #/ ((vol_parity*(breakout_signal.abs())).sum(axis=1))



"""
    Risk Parity Scaling
"""

risk_par = pd.DataFrame((1-ones), columns=commodities)
risk_par.index = data.index

for period in range(0, returns.shape[0], 252):
    if period == 0:
        weights = list( [1/ ( len(commodities) - returns.iloc[1].isna().sum() ) for x in range(len(commodities))] * np.array([0 if math.isnan(returns.iloc[1][i]) else 1 for i in range(len(commodities))]) )
    else:
        weights = rp.rb_p_weights(returns.iloc[:period].fillna(0)).x * np.array([0 if math.isnan(returns.iloc[period][i]) else 1 for i in range(len(commodities))])
        weights = list(weights / weights.sum())
    risk_par.iloc[period] = weights
risk_par = risk_par.replace(0, np.nan)
risk_par = risk_par.ffill(axis=0).fillna(0)
















strategy_breakout = pd.DataFrame({"Strategy": (breakout_signal.shift(lag)*returns).mean(axis=1)})       

strategy_vp = pd.DataFrame({"Strategy": (vol_parity.shift(lag) * returns).sum(axis=1)/24})
strategy_vp_breakout = pd.DataFrame({"Strategy": (breakout_signal.shift(lag) * vol_parity.shift(lag) * returns).sum(axis=1)/24})       

strategy_rp = pd.DataFrame({"Strategy": (risk_par.shift(lag) * returns).sum(axis=1)})
strategy_vp_rp_breakout = pd.DataFrame({"Strategy": (risk_par.shift(lag) * breakout_signal.shift(lag) * vol_parity.shift(lag) * returns).sum(axis=1)})       

strategy_all = pd.DataFrame({"Strategy": ((MA_signal.shift(lag) + breakout_signal.shift(lag)) * 0.5 * risk_par.shift(lag) * vol_parity.shift(lag) * returns).sum(axis=1)}) 




























#sp500 = pd.read_csv(r'Data\^GSPC.csv',index_col=0, parse_dates=True,
#                    date_parser = lambda dates: [pd.datetime.strptime(d, '%d/%m/%Y') for d in dates])
#
#
#
#Ret = sp500.loc["1986":, 'Adj Close'][1:].pct_change()
#
#
#ps.PerformStatistics(Ret, rfr, "Test") 
#
#
#
#ps.PerformStatistics(returns['Wheat'], rfr, "Wheat")
#

###############################################################################
###########################STRATEGY PERFORMANCE################################
###############################################################################    


"""
    Performance Statistics - Sharpe Ratio to be added once Risk Free Rate Found - Have Libor from 1986, what to do for period 1970-86
"""


ps.PerformStatistics(market_factor, rfr, "Benchmark")

ps.PerformStatistics(strategy_MA, rfr, "Strategy MA")
ps.PerformStatistics(strategy_EWMA, rfr, "Strategy EWMA")
ps.PerformStatistics(strategy_breakout, rfr, "Strategy Breakout")
ps.PerformStatistics(strategy_vp, rfr, "Strategy Volatility Scaling")
ps.PerformStatistics(strategy_rp, rfr, "Strategy Risk Parity")

ps.PerformStatistics(strategy_vp_breakout, rfr, "Strategy Vol. Parity Breakout")
ps.PerformStatistics(strategy_vp_rp_breakout, rfr, "Strategy Vol. And Risk Parity Breakout")

ps.PerformStatistics(strategy_all, rfr, "Strategy MA with Breakout, Vol and Risk Parity")



"""
    Things to be added:
        - Rolling Sharpe
        - Add drawdown curve to strategy plots
        
        - Separate signals and weightings into different .py files
        - Export Findings to Excel file
        - Export signals to Excel file for speed of execution
        
        - Comment code
        
        - Add different signals/weightings to compare e.g. index signal for gold hedge (useful for FC2008)
        
        - Normalize vol scaling and see how it interacts with Risk Parity (figure out inner workings of risk parity)
"""


