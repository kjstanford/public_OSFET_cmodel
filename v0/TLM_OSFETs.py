# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 14:19:37 2025

@author: koust
"""

from os import system as sys
import fileinput as fi
from numpy.core.multiarray import dtype
import numpy as np
import pandas as pd
import scipy.linalg as la
import scipy.integrate as integrate
import matplotlib.pyplot as plt
from numpy import pi, exp, log, sin, cos, tan, log10, abs, gradient, sinh, cosh, arctan, argmax, argmin
from scipy.special import hyp2f1, erf, erfc, erfcinv, gammainc, erfi, spence
from scipy.optimize import fsolve
from scipy.signal import savgol_filter
from scipy import sparse
from scipy.sparse import linalg as las
from math import ceil, floor
import time
import csv
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import matplotlib.ticker as ticker
import re

import os
from multiprocessing import Pool
from sklearn.linear_model import LinearRegression

import sys as simp
simp.path.append("D:/Stanford Important Docs/")
from helper_funs import *

def calculate_VTON_VTOFF(Vglin, Idlin, Vdlin, PHIT, Id_SS_limits=[2e-11, 1e-8], Vg_limits=None, smoothen_Idlin_lin=False, smoothen_Idlin_log=False, smoothen_gmlin=True, Id_SS_full_range=False):
    # print('X'+'-X'*20)
    # print(f'Start TR extraction.')
    
    Idlin_sf = sf([Idlin], wl=31, order=3)[0] if smoothen_Idlin_lin else Idlin
    Idlin_sf_log10 = sf_log10([Idlin], wl=31, order=3)[0] if smoothen_Idlin_log else Idlin
    
    if Vg_limits == None:
        Vg_limits = [Vglin[0], Vglin[-1]]
    Vgtemp = Vglin
    Vglin = Vglin[ ( Vgtemp >= Vg_limits[0] ) & ( Vgtemp <= Vg_limits[-1] ) ]
    Idlin_sf = Idlin_sf[ ( Vgtemp >= Vg_limits[0] ) & ( Vgtemp <= Vg_limits[-1] ) ]
    Idlin_sf_log10 = Idlin_sf_log10[ ( Vgtemp >= Vg_limits[0] ) & ( Vgtemp <= Vg_limits[-1] ) ]

    ### Analysis when sufficiently ON ###
    Gmlin_raw = gradient(Idlin_sf)/gradient(Vglin)
    Gmlin = sf(y=[Gmlin_raw], wl=31, order=3)[0] if smoothen_gmlin else Gmlin_raw
    reqd_index = argmax(Gmlin)
    Gmlin_max = Gmlin[reqd_index]
    # print(f'Gmlin max index is {reqd_index}, max value is {Gmlin_max} at Vgs={Vglin[reqd_index]}')
    indices = np.arange(max(0, reqd_index - 2), min(len(Vglin), reqd_index + 3))
    # print(f'Indices for ON linear fit are {indices}, corresponding Vgs range is {Vglin[indices[0]]}V to {Vglin[indices[-1]]}V')
    x_points = Vglin[indices]
    y_points = Idlin_sf[indices]
    
    # Perform linear regression
    X = x_points.reshape(-1, 1)
    reg = LinearRegression().fit(X, y_points)
    mslope = reg.coef_[0]
    cintercept = reg.intercept_
    # print("For sufficiently ON", mslope, cintercept)
    # Equation of the best-fit line
    def best_fit_line(x):
        return mslope * x + cintercept
    
    BETA = mslope / Vdlin

    ### Analysis when sufficiently OFF [Lin] ###
    SSlin_raw = 1e3*gradient(Vglin)/gradient(log10(Idlin_sf_log10))
    SSlin = SSlin_raw
    SSlin_min = min( SSlin[ ( Idlin_sf_log10 >= Id_SS_limits[0] ) & ( Idlin_sf_log10 <= Id_SS_limits[-1] ) ] )
    reqd_index_l = np.where(SSlin == SSlin_min)[0][0]
    # print(f'SSlin min index is {reqd_index_l}, min value is {SSlin_min} at Id={Idlin_sf_log10[reqd_index_l]}')
    indices_l = np.arange(max(0, reqd_index_l - 1), min(len(Idlin_sf_log10), reqd_index_l + 2))
    # print(f'Indices [lin] for OFF log-linear fit are {indices_l}, corresponding Id range is {Idlin_sf_log10[indices_l[0]]}A to {Idlin_sf_log10[indices_l[-1]]}A')
    if Id_SS_full_range:
        x_points_l = Vglin[( Idlin_sf_log10 >= Id_SS_limits[0] ) & ( Idlin_sf_log10 <= Id_SS_limits[-1] )]
        y_points_l = log10(Idlin_sf_log10[( Idlin_sf_log10 >= Id_SS_limits[0] ) & ( Idlin_sf_log10 <= Id_SS_limits[-1] )])
        print(x_points_l, 10**y_points_l)
    else:
        x_points_l = Vglin[indices_l]
        y_points_l = log10(Idlin_sf_log10[indices_l])
    
    # Perform log10 linear regression
    X_l = x_points_l.reshape(-1, 1)
    reg_l = LinearRegression().fit(X_l, y_points_l)
    mslope_l = reg_l.coef_[0]
    cintercept_l = reg_l.intercept_
    # print("For sufficiently OFF", mslope_l, cintercept_l)
    # mslope_l, cintercept_l = logle_calc(Vg=Vglin, Id=Idlin_sf_log10, lower_i=1e-10, higher_i=1e-9)
    # print(f'SS = {1e3/mslope_l} mv/Dec')
    
    # Equation of the best-fit line
    def best_fit_line_l(x):
        return mslope_l * x + cintercept_l
    
    nSSlin = 1 / (log(10) * mslope_l * PHIT)
    
    ### final TR width calculation [Lin] ###
    VTONlin = -cintercept / mslope - nSSlin * Vdlin / 2
    VTOFFlin = -cintercept_l / mslope_l + log10( BETA * PHIT * ( 1 - exp(-Vdlin / PHIT) ) / ( log(10) * mslope_l ) ) /  mslope_l
    TRlin = VTONlin - VTOFFlin

    # print(f'Finish TR extraction.')
    # print('X'+'-X'*20)
    return BETA, nSSlin, VTONlin, VTOFFlin, TRlin

def get_Rtotal(Vov, Vglin, Idlin, Vdlin, PHIT, Id_SS_limits=[2e-11, 1e-8], Vg_limits=None, smoothen_Idlin_lin=False, smoothen_Idlin_log=False, smoothen_gmlin=True, Id_SS_full_range=False):
    BETA, nSSlin, VTONlin, VTOFFlin, TRlin = calculate_VTON_VTOFF(Vglin, Idlin, Vdlin, PHIT, Id_SS_limits=Id_SS_limits, Vg_limits=Vg_limits, smoothen_Idlin_lin=smoothen_Idlin_lin, smoothen_Idlin_log=smoothen_Idlin_log, smoothen_gmlin=smoothen_gmlin, Id_SS_full_range=Id_SS_full_range)
    Rtotal = Vdlin / Idlin
    Vg = Vov + VTONlin
    print(f"Vg={Vg} for Vov={Vov}")
    interp_func = interp1d(Vglin, Rtotal, kind='linear', fill_value='extrapolate')
    R_at_Vg = interp_func(Vg)
    return R_at_Vg
    