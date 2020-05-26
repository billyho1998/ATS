import pandas as pd
import numpy as np
import os

os.chdir(r'/Users/mihne/Desktop/MSc/Summer Term/ATS/Backtesting') # Change Directory

## Get commodities and sectors data

cmdty = pd.read_excel("Commodity Data.xlsx", sheet_name = "Return indices").set_index("date")
sectors = pd.read_excel("Commodity Data.xlsx", sheet_name = "Assets")

## Calculate daily returns
try:
    returns = pd.read_csv("Commodity_Returns.csv").set_index("date")
except FileNotFoundError:
    returns = cmdty/cmdty.shift(1)
    returns.to_csv("Commodity_Returns.csv")

## Get list of commodities in each sector
agri_livestock = [sectors["Commodity"][i] for i in range(sectors.shape[0]) if sectors["Sector"][i]=="Agri & livestock"]
energy = [sectors["Commodity"][i] for i in range(sectors.shape[0]) if sectors["Sector"][i]=="Energy"]
metals = [sectors["Commodity"][i] for i in range(sectors.shape[0]) if sectors["Sector"][i] == "Metals"]

# Aggregated list of all individual commodities in the dataset
commodities_list = agri_livestock + energy + metals

## Get index number of last observation
lastIndex = cmdty.shape[0] - 1  

## Summary stats

# Create empty dataframe to store results
summary_stats = pd.DataFrame(columns=returns.columns, 
                             index=['Sector','First Obs Date','No Obs','Tot Ret (%)','Avg Ret (%)', \
                                    'SD (%)', 'Sharpe', 'Skew', 'Kurtosis', 'HWM', 'HWM Date', \
                                    'MDD (%)', 'Peak Date', 'Trough Date', 'Inv. Calmar Ratio'])

# Sector map
for i in commodities_list:
    if i in agri_livestock:
        summary_stats.loc['Sector'][i] = 'Agriculture & Livestock'
    elif i in energy:
        summary_stats.loc['Sector'][i] = 'Energy'
    else:
        summary_stats.loc['Sector'][i] = 'Metals'

# Number of Observations
summary_stats.loc['No Obs'] = returns.count()

# Total Return
for i in commodities_list:
    summary_stats.loc['Tot Ret (%)'][i] = \
        (cmdty.iloc[lastIndex][i] - cmdty.iloc[cmdty[i].index.get_loc(cmdty[i].first_valid_index())][i]) / \
        cmdty.iloc[cmdty[i].index.get_loc(cmdty[i].first_valid_index())][i]*100
        
# Date of first observation
for i in commodities_list:
    summary_stats.loc['First Obs Date'][i] = \
        cmdty.loc[cmdty[i].first_valid_index()].name.date()
        
# Average Return
summary_stats.loc['Avg Ret (%)'] = (returns-1).mean()*252*100

# Standard Deviation
summary_stats.loc['SD (%)'] = returns.std() * np.sqrt(252) * 100

# Sharpe (Note: returns are already in excess of the risk free rate)
summary_stats.loc['Sharpe'] = summary_stats.loc['Avg Ret (%)'] / summary_stats.loc['SD (%)']

# Skewness
summary_stats.loc['Skew'] = returns.skew()

# Kurtosis
summary_stats.loc['Kurtosis'] = returns.kurt()

## Calculating cumulative returns per commodity

# Creating empty dataframe to store cumulative returns
cmdty_cum_returns = pd.DataFrame(columns = returns.columns, index = returns.index.copy())

# Get cumulative returns per commodity
for i in commodities_list:
    cmdty_cum_returns[i] = returns[i].cumprod()
    
cmdty_cum_returns.index = cmdty.index
   
# HWM and HWM Date (High Water Mark)
for i in commodities_list:
    summary_stats.loc['HWM'][i] = cmdty_cum_returns[i].max()*100
    HWM_Date = cmdty_cum_returns[i].idxmax()
    summary_stats.loc['HWM Date'][i] = HWM_Date
    
# MDD (Maximum Drawdown)
DD = cmdty.cummax() - cmdty 
end_mdd = DD.idxmax()

for i in commodities_list:
    start_mdd = cmdty[i][:end_mdd[i]].idxmax()
    end_mdd_i = end_mdd[i]
    summary_stats.loc['MDD (%)'][i] = (1 - cmdty_cum_returns.loc[end_mdd_i][i]/cmdty_cum_returns.loc[start_mdd][i])*100
    summary_stats.loc['Peak Date'][i] = start_mdd
    summary_stats.loc['Trough Date'][i] = end_mdd_i

# Inverse Calmar Ratio

for i in commodities_list:
    summary_stats.loc['Inv. Calmar Ratio'][i] = summary_stats.loc['MDD (%)'][i] / summary_stats.loc['Avg Ret (%)'][i]


# Convert Timestamp data to DateTime data in the summary stats final table
for i in commodities_list:
    summary_stats.loc["HWM Date"][i] = summary_stats.loc["HWM Date"][i].date()
    summary_stats.loc["Peak Date"][i] = summary_stats.loc["Peak Date"][i].date()
    summary_stats.loc["Trough Date"][i] = summary_stats.loc["Trough Date"][i].date()
    
# Rounding (float numbers)
summary_stats.loc['Tot Ret (%)'] = summary_stats.loc['Tot Ret (%)'].apply(lambda x : round(x,2))
summary_stats.loc['Avg Ret (%)'] = summary_stats.loc['Avg Ret (%)'].apply(lambda x : round(x,2))
summary_stats.loc['SD (%)'] = summary_stats.loc['SD (%)'].apply(lambda x : round(x,2))
summary_stats.loc['Sharpe'] = summary_stats.loc['Sharpe'].apply(lambda x : round(x,2))
summary_stats.loc['Skew'] = summary_stats.loc['Skew'].apply(lambda x : round(x,2))
summary_stats.loc['HWM'] = summary_stats.loc['HWM'].apply(lambda x : round(x,2))
summary_stats.loc['Kurtosis'] = summary_stats.loc['Kurtosis'].apply(lambda x : round(x,2))
summary_stats.loc['MDD (%)'] = summary_stats.loc['MDD (%)'].apply(lambda x : round(x,2))
summary_stats.loc['Inv. Calmar Ratio'] = summary_stats.loc['Inv. Calmar Ratio'].apply(lambda x : round(x,2))

print(summary_stats.T)
# Export transposed summary stats dataframe to csv
(summary_stats.T).to_csv('Summary_Stats_Final.csv')


