# -*- coding: utf-8 -*-
"""
Created on Sun May 17 11:53:57 2020

@author: tomw1
"""
import numpy as np
import pandas as pd
from tabulate import tabulate

class Commodities:
    
    def __init__(self, data):
        
        self.commodity = data.name
        self.data = data
        self.returns = np.log(self.data/self.data.shift(1))
    
    def _numObs(self):
        return self.data.count()
    
    def _firstObs(self):
        return (self.data.first_valid_index()).date()
    
    def _lastObs(self):
        return (self.data.last_valid_index()).date()
    
    def _meanReturns(self):
        return round(self.returns.mean()*100, 3)
    
    def _stdReturns(self):
        return round(self.returns.std()*100, 3)
    
    def _averagePrice(self):
        return round(self.data.mean(), 2)
    
    def _minPrice(self):
        return self.data.min()
    
    def _maxPrice(self):
        return self.data.max()
    
    def _whenMin(self):
        return self.data.idxmin().date()
    
    def _whenMax(self):
        return self.data.idxmax().date()
    
    def summarizeData(self):
        return [self.commodity, self._numObs(), self._firstObs(), 
                self._lastObs(), self._meanReturns(), self._stdReturns(), 
                self._averagePrice(), self._minPrice(), self._whenMin(), 
                self._maxPrice(), self._whenMax()]
        
def summarize_data(data, commodities):
    headers = ["Commodity", "Num Obs.", "First Obs.", 
               "Last Obs.", "Mean (%)", "StD (%)", 
               "Average Price", "Min. Price", "Date of Min.", 
               "Max. Price", "Date of Max."]
    
    try: 
        table = pd.read_csv("Data_Summary.csv", usecols=headers).set_index("Commodity")
        
    except FileNotFoundError as _:
        
        table=[]
        
        for asset in commodities:
            table.append(Commodities(data[asset]).summarizeData())
        
        df = pd.DataFrame(data = table, columns=headers)  
        df.to_csv("Data_Summary.csv")
    
    print(tabulate(table, headers=headers)) 
    
    return
        




