# -*- coding: utf-8 -*-
"""
Created on Fri May 22 21:19:12 2020

@author: tomw1
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

# risk budgeting approach optimisation object function
def obj_fun(x, p_cov, rb):
   return np.sum((x * np.dot(p_cov, x) / np.dot(x.transpose(), np.dot(p_cov, x))-rb)**2)

# constraint on sum of weights equal to one
def cons_sum_weight(x):
   return np.sum(x)-1.0

# constraint on weight larger than zero
def cons_long_only_weight(x):
   return x

# calculate risk budgeting portfolio weight give risk budget
def rb_p_weights(asset_rets, rb=1):
   # number of ARP series
   num_arp = asset_rets.shape[1]
   # covariance matrix of asset returns
   p_cov = asset_rets.cov()
   # initial weights
   w0 = 1.0 * np.ones((num_arp, 1)) / num_arp
   # constraints
   cons = ({'type': 'eq', 'fun': cons_sum_weight}, {'type': 'ineq', 'fun': cons_long_only_weight})
   # portfolio optimisation
   return minimize(obj_fun, w0, args=(p_cov, rb), method='SLSQP', constraints=cons)





