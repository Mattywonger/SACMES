import config_m,helper_m
import os
import matplotlib
import sys
import time
import datetime
matplotlib.use('TkAgg') # To use the TkAGG backend for matplotlib
os.system("clear && printf '\e[3J'")

import tkinter as tk
from tkinter import *
from tkinter import *
from tkinter import filedialog, Menu
from tkinter import ttk
from tkinter.messagebox import showinfo


from matplotlib import style
import scipy.integrate as integrate
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import csv
from pylab import *
from numpy import *
from scipy.interpolate import *
from scipy.integrate import simps
from scipy.signal import *
from itertools import *
from math import log10, floor
from decimal import Decimal
from operator import truediv
import threading
from threading import Thread
from queue import Queue

import helper_m
style.use('ggplot')

#---Filter out error warnings---#
import warnings
warnings.simplefilter('ignore', np.RankWarning)         #numpy polyfit_deg warning
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd") #RuntimeWarning



#data_method is a global variable gotten from the SelectDataAnalysis method

def data_analysis(data_method,SelectedOptions,frequency,currents,potentials,max1,max2,min1,min2):
    if data_method == "SWV":
        print("SWV")
        SWV_Analysis=(SelectedOptions,frequency)
    if data_method == "CA":
        print("CA")

def SWV_Analysis(SelectedOptions,frequency,currents,potentials,max1,max2,min1,min2):
    xstart,xend = get_high_low_potential(frequency)
    adjusted_potentials = [value for value in potentials if xend <= value <= xstart]
    data_dict = Savitzky_smoothing(currents,potentials)
    adjusted_currents=adjust_smooth(adjusted_potentials,data_dict)
    data = ProcessSelectedOptions(SelectedOptions,max1,max2,min1,min2,adjusted_potentials,adjusted_currents) #arguments
    return data





def ProcessSelectedOptions(SelectedOptions,max1,max2,min1,min2,adjusted_potentials,adjusted_currents):
    if (SelectedOptions == "Peak Height Extraction"):
        Peak_Height = max(max1,max2)-min(min1,min2)
        data = Peak_Height
        return data
    if SelectedOptions == 'Area Under the Curve':
        AUC_index = 1
        AUC = 0

        AUC_potentials = adjusted_potentials
        AUC_min = min(adjusted_currents)
        AUC_currents = [Y - AUC_min for Y in adjusted_currents]

        while AUC_index <= len(AUC_currents) - 1:
                    AUC_height = (AUC_currents[AUC_index] + AUC_currents[AUC_index - 1])/2
                    AUC_width = AUC_potentials[AUC_index] - AUC_potentials[AUC_index - 1]
                    AUC += (AUC_height * AUC_width)
                    AUC_index += 1
        data = AUC
        return data

def Savitzky_smoothing(currents,potentials,sg_degree):
    smooth_currents = savgol_filter(currents, 15, sg_degree)
    data_dict = dict(zip(potentials,smooth_currents))
    return data_dict

def adjust_smooth(adjusted_potentials,data_dict):
    adjusted_currents = []
    for potential in adjusted_potentials:
        adjusted_currents.append(data_dict[potential])
    return adjusted_currents

def get_high_low_potential(frequency,cutoff_frequency,HighAlreadyReset,LowAlreadyReset):
    if int(frequency) > cutoff_frequency:

        if not HighAlreadyReset:
            high_xstart = max(potentials)
            high_xend = min(potentials)

    #-- set the local variables to the global ---#
    xend = high_xend
    xstart = high_xstart
    if int(frequency) <= cutoff_frequency:
        if not LowAlreadyReset:
            low_xstart = max(potentials)
            low_xend = min(potentials)

        #-- set the local variables to the global ---#
        xstart = low_xstart
        xend = low_xend


    cut_value = 0
    for value in potentials:
        if value == 0:
            cut_value += 1

    if cut_value > 0:
        potentials = potentials[:-cut_value]
        currents = currents[:-cut_value]
    return xstart,xend

def analyze_regression(adjusted_potentials, adjusted_currents, polyfit_deg):
    # Perform polynomial regression
    polynomial_coeffs = np.polyfit(adjusted_potentials, adjusted_currents, polyfit_deg)
    eval_regress = np.polyval(polynomial_coeffs, adjusted_potentials).tolist()
    
    # Create a dictionary mapping fitted currents to potentials
    regression_dict = dict(zip(eval_regress, adjusted_potentials))
    
    # Find minima and maxima of the fitted currents
    fit_half = round(len(eval_regress) / 2)
    min1 = min(eval_regress[:-fit_half])
    min2 = min(eval_regress[fit_half:])
    max1 = max(eval_regress[:-fit_half])
    max2 = max(eval_regress[fit_half:])
    
    # Fit a linear polynomial to the minimum points
    linear_fit = np.polyfit([regression_dict[min1], regression_dict[min2]], [min1, min2], 1)
    
    # Evaluate the linear fit at the potential points corresponding to the minimum currents
    linear_regression = np.polyval(linear_fit, [regression_dict[min1], regression_dict[min2]]).tolist()
    
    return {
        'polynomial_coeffs': polynomial_coeffs,
        'eval_regress': eval_regress,
        'regression_dict': regression_dict,
        'min1': min1,
        'min2': min2,
        'max1': max1,
        'max2': max2,
        'linear_fit': linear_fit,
        'linear_regression': linear_regression
    }








    

        




