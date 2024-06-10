import SACMES_PYTHON_PACKAGE.Config as Config
import os
import matplotlib
import sys
import time
import datetime
matplotlib.use('TkAgg') # To use the TkAGG backend for matplotlib
os.system("clear && printf '\e[3J'")

import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import *
from tkinter import filedialog, Menu
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

import SACMES_PYTHON_PACKAGE.helper as helper
style.use('ggplot')

#---Filter out error warnings---#
import warnings
warnings.simplefilter('ignore', np.RankWarning)         #numpy polyfit_deg warning
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd") #RuntimeWarning


handle_variable,e_var,PHE_method,InputFrequencies,electrodes = Config.globalvar_config()
high_xstart = None
high_xend = None
low_xstart = None
low_xend = None
sg_window,sg_degree,polyfit_deg,cutoff_frequency = Config.regressionvar_config()
key,search_lim,PoisonPill,FoundFilePath,ExistVar,AlreadyInitiated,HighAlreadyReset,LowAlreadyReset,analysis_complete= Config.checkpoint_parameter()
delimiter,extension,current_column,current_column_index,voltage_column,voltage_column_index,spacing_index,byte_limit,byte_index = Config.data_extraction_parameter()
LowFrequencyOffset,LowFrequencySlope = Config.low_freq_parameter()
HUGE_FONT,LARGE_FONT,MEDIUM_FONT,SMALL_FONT = Config.font_specification()
method=""

from CheckPoint import CheckPoint
from ContinuousManipulationFrame import ContinuousScanManipulationFrame
from GlobalVariables import *


class MainWindow(tk.Tk):

    #--- Initialize the GUI ---#
    def __init__(self,master=None,*args, **kwargs):
        global container, Plot, frame_list, PlotValues, ShowFrames, HighLowList


        #tk.Tk.__init__(self, *args, **kwargs)
        self.master = master
        self.master.wm_title('SACMES')

        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        #--- Create a frame for the UI ---#
        container = tk.Frame(self.master,relief='flat',bd=5)
        container.grid(row=0,rowspan=11,padx=10, sticky = 'nsew')         ## container object has UI frame in column 0
        container.rowconfigure(0, weight=1)              ## and PlotContainer (visualization) in column 1
        container.columnconfigure(0, weight=1)


        #--- Raise the frame for initial UI ---#
        ShowFrames = {}                                 # Key: frame handle / Value: tk.Frame object
        frame = InputFrame(container, self.master,method)
        ShowFrames[InputFrame] = frame
        frame.grid(row=0, column=0, sticky = 'nsew')
        self.show_frame(InputFrame)


        self._create_toolbar()

        #--- High and Low Frequency Dictionary ---#
        HighLowList = {}

    #--- Function to visualize different frames ---#
    def _create_toolbar(self):

        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        #################
        ### Edit Menu ###
        #################
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_separator()
        editmenu.add_command(label="Customize File Format", command=lambda: self.extraction_adjustment_frame())
        self.delimiter_value = IntVar()
        self.delimiter_value.set(1)

        self.extension_value = IntVar()
        self.extension_value.set(1)

        self.byte_menu = tk.Menu(menubar)
        self.onethousand = self.byte_menu.add_command(label = "   1000", command = lambda: self.set_bytes('1000',0))
        self.twothousand = self.byte_menu.add_command(label = "   2000", command = lambda: self.set_bytes('2000',1))
        self.threethousand = self.byte_menu.add_command(label="✓ 3000", command = lambda: self.set_bytes('3000',2))
        self.fourthousand = self.byte_menu.add_command(label = "   4000", command = lambda: self.set_bytes('4000',3))
        self.fivethousand = self.byte_menu.add_command(label = "   5000", command = lambda: self.set_bytes('5000',4))
        self.fivethousand = self.byte_menu.add_command(label = "   7500", command = lambda: self.set_bytes('7500',5))

        editmenu.add_cascade(label='Byte Limit', menu=self.byte_menu)

        menubar.add_cascade(label="Settings", menu=editmenu)

    def extraction_adjustment_frame(self):
        global delimiter, extension

        win = tk.Toplevel()
        win.wm_title("Customize File Format")

        #-- new frame --#
        row_value = 0
        container = tk.Frame(win, relief='groove',bd=2)
        container.grid(row=row_value,column=0,columnspan=2,padx=5,pady=5,ipadx=3)

        container_value = 0
        l = ttk.Label(container, text="Current is in Column:")
        l.grid(row=container_value, column=0)

        container_value += 1
        self.list_val_entry = tk.Entry(container, width=5)
        self.list_val_entry.insert(END,current_column)
        self.list_val_entry.grid(row=container_value,column=0,pady=5)

        container_value = 0
        l = ttk.Label(container, text="Voltage is in Column:")
        l.grid(row=container_value, column=1)

        container_value += 1
        self.voltage_column = tk.Entry(container, width=5)
        self.voltage_column.insert(END,voltage_column)
        self.voltage_column.grid(row=container_value,column=1,pady=5)

        container_value += 1
        l = ttk.Label(container, text="Multipotentiostat Settings\nSpace Between Current Columns:")
        l.grid(row=container_value, column=0,columnspan=2)

        #-- frameception --#
        container_value += 1
        inner_frame = tk.Frame(container)
        inner_frame.grid(row=container_value,column=0,columnspan=2)
        self.spacing_label = ttk.Label(inner_frame, text = '\t         Columns').grid(row=0,column=0)

        self.spacing_val_entry = tk.Entry(inner_frame, width=4)
        self.spacing_val_entry.insert(END,3)
        self.spacing_val_entry.grid(row=0,column=0,pady=1)

        #-- new frame --#

        row_value += 1
        box = tk.Frame(win, relief='groove',bd=2)
        box.grid(row=row_value,column=0,columnspan=2,pady=7)

        box_value = 0
        l = ttk.Label(box, text="Delimiter between\ndata columns:")
        l.grid(row=box_value, column=0)

        box_value += 1
        self.space_delimiter = tk.RadioButton(box, text='Space',variable = self.delimiter_value, value = 1)
        self.space_delimiter.grid(row=box_value,column=0,pady=5)

        box_value += 1
        self.tab_delimiter = tk.RadioButton(box, text = 'Tab',variable = self.delimiter_value, value = 2)
        self.tab_delimiter.grid(row=box_value, column=0,pady=3)

        box_value += 1
        self.tab_delimiter = tk.RadioButton(box, text = 'Comma',variable = self.delimiter_value, value = 3)
        self.tab_delimiter.grid(row=box_value, column=0,pady=3)

        box_value = 0
        l = ttk.Label(box, text="File Extension")
        l.grid(row=box_value, column=1)

        box_value += 1
        self.txt_value = tk.RadioButton(box, text='txt',variable = self.extension_value, value = 1)
        self.txt_value.grid(row=box_value,column=1,pady=5)

        box_value += 1
        self.csv_value = tk.RadioButton(box, text = 'csv',variable = self.extension_value, value = 2)
        self.csv_value.grid(row=box_value, column=1,pady=3)

        box_value += 1
        self.dta_value = tk.RadioButton(box, text = 'dta',variable = self.extension_value, value = 3)
        self.dta_value.grid(row=box_value, column=1,pady=3)


        row_value += 1
        apply_list_val = ttk.Button(win, text="Apply", command=lambda: self.get_list_val())
        apply_list_val.grid(row=row_value, column=0,pady=6)

        exit = ttk.Button(win, text="Exit", command= lambda: win.destroy())
        exit.grid(row=row_value, column=1,pady=3)

    def get_list_val(self):
        global current_column, current_column_index,voltage_column, voltage_column_index, spacing_index, delimiter, extension, total_columns

        current_column = int(self.list_val_entry.get())
        current_column_index = current_column - 1

        spacing_index = int(self.spacing_val_entry.get())

        voltage_column = int(self.voltage_column.get())
        voltage_column_index = voltage_column - 1

        ### Set the delimiter and extension ###
        delimiter = self.delimiter_value.get()
        extension = self.extension_value.get()

    def set_bytes(self, bytes, index):
        global byte_limit, byte_index

        #-- reset the self.byte_menu widgets --#
        self.byte_menu.entryconfigure(index, label='✓%s' % bytes)
        self.byte_menu.entryconfigure(byte_index, label='   %s' % str(byte_limit))

        #-- now change the current data being used --#
        byte_limit = int(bytes)
        byte_index = index


    def show_frame(self, cont):

        frame = ShowFrames[cont]
        frame.tkraise()

    def onExit(self):
        self.master.destroy()
        self.master.quit()
        quit()

class InputFrame(tk.Frame):
                             # first frame that is displayed when the program is initialized
    def __init__(self, parent, controller,method):
        global figures, StartNormalizationVar, SaveBox, ManipulateFrequenciesFrame

        self.parent = parent
        self.controller = controller
        self.method=method

        tk.Frame.__init__(self, parent)             # initialize the frame

        row_value = 0

        ##############################################
        ### Pack all of the widgets into the frame ###
        ##############################################

        self.SelectFilePath = ttk.Button(self, style = 'Off.TButton', text = 'Select File Path', command = lambda: self.FindFile(parent))
        self.SelectFilePath.grid(row=row_value,column=0,columnspan=4)
        row_value += 2

        self.NoSelectedPath = ttk.Label(self, text = 'No File Path Selected', foreground = 'red')
        self.PathWarningExists = False               # tracks the existence of a warning label

        #ImportFileLabel = ttk.Label(self, text='Import File Label', font=('Verdana', 11))
        #ImportFileLabel.grid(row=row_value, column=0, columnspan=2)

        self.ImportFileEntry = tk.Entry(self)
        self.ImportFileEntry.grid(row=row_value+1,column=0,columnspan=2,pady=5)
        self.ImportFileEntry.insert(END, handle_variable)

        #--- File Handle Input ---#



        HandleLabel = ttk.Label(self, text='Exported File Handle:', font=('Verdana', 10))
        HandleLabel.grid(row=row_value,column=2,columnspan=2)
        self.filehandle = tk.Entry(self)
        now = datetime.datetime.now()
        hour = str(now.hour)
        day = str(now.day)
        month = str(now.month)
        year = str(now.year)
        self.filehandle.insert(END, 'DataExport_%s_%s_%s.txt' % (year, month, day))
        self.filehandle.grid(row=row_value+1,column=2,columnspan=2,pady=5)

        row_value += 2

        EmptyLabel = ttk.Label(self, text = '',font=('Verdana', 11)).grid(row=row_value,rowspan=2,column=0,columnspan=10)
        row_value += 1

        #---File Limit Input---#
        numFileLabel = ttk.Label(self, text='Number of Files:', font=('Verdana', 11))
        numFileLabel.grid(row=row_value,column=0,columnspan=2,pady=4)
        self.numfiles = tk.Entry(self, width=7)
        self.numfiles.insert(END, '50')
        self.numfiles.grid(row=row_value+1,column=0,columnspan=2,pady=6)

        #--- Analysis interval for event callback in ElectrochemicalAnimation ---#
        IntervalLabel = ttk.Label(self, text='Analysis Interval (ms):', font=('Verdana', 11))
        IntervalLabel.grid(row=row_value,column=2,columnspan=2,pady=4)
        self.Interval = tk.Entry(self, width=7)
        self.Interval.insert(END, '10')
        self.Interval.grid(row=row_value+1,column=2,columnspan=2,pady=6)

        row_value += 2

        #---Sample Rate Variable---#
        SampleLabel = ttk.Label(self, text='Sampling Rate (s):', font=('Verdana', 11))
        SampleLabel.grid(row=row_value,column=0,columnspan=2)
        self.sample_rate = tk.Entry(self, width=7)
        self.sample_rate.insert(END, '20')
        self.sample_rate.grid(row=row_value+1,column=0,columnspan=2)

        self.resize_label = ttk.Label(self, text='Resize Interval', font = LARGE_FONT)
        self.resize_label.grid(row=row_value,column=2,columnspan=2)
        self.resize_entry = tk.Entry(self, width = 7)
        self.resize_entry.insert(END,'200')
        self.resize_entry.grid(row=row_value+1,column=2,columnspan=2)

        row_value += 2

        ##################################
        ### Select and Edit Electrodes ###
        ##################################

        self.ElectrodeListboxFrame = tk.Frame(self)                   # create a frame to pack in the Electrode box and
        self.ElectrodeListboxFrame.grid(row=row_value,column=0,columnspan=2,padx=10,pady=10,ipady=5, sticky = 'nsew')

        #--- parameters for handling resize ---#
        self.ElectrodeListboxFrame.rowconfigure(0, weight=1)
        self.ElectrodeListboxFrame.rowconfigure(1, weight=1)
        self.ElectrodeListboxFrame.columnconfigure(0, weight=1)
        self.ElectrodeListboxFrame.columnconfigure(1, weight=1)

        self.ElectrodeListExists = False
        self.ElectrodeLabel = ttk.Label(self.ElectrodeListboxFrame, text='Select Electrodes:', font=('Verdana', 11))
        self.ElectrodeLabel.grid(row=0,column=0,columnspan=2, sticky = 'nswe')
        self.ElectrodeCount = Listbox(self.ElectrodeListboxFrame, relief='groove', exportselection=0, width=10, font=('Verdana', 11), height=6, selectmode = 'multiple', bd=3)
        self.ElectrodeCount.bind('<<ListboxSelect>>',self.ElectrodeCurSelect)
        self.ElectrodeCount.grid(row=1,column=0,columnspan=2,sticky='nswe')
        for electrode in electrodes:
            self.ElectrodeCount.insert(END, electrode)

        self.scrollbar = Scrollbar(self.ElectrodeListboxFrame, orient="vertical")
        self.scrollbar.config(width=10,command=self.ElectrodeCount.yview)
        self.scrollbar.grid(row=1,column=1,sticky='nse')
        self.ElectrodeCount.config(yscrollcommand=self.scrollbar.set)

        #--- Option to have data for all electrodes in a single file ---#
        self.SingleElectrodeFile = ttk.Button(self.ElectrodeListboxFrame, text='Multichannel', style = 'On.TButton', command =  lambda: self.ElectrodeSelect('Multichannel'))
        self.SingleElectrodeFile.grid(row=2,column=0)

        #--- Option to have data for each electrode in a separate file ---#
        self.MultipleElectrodeFiles = ttk.Button(self.ElectrodeListboxFrame,  text='Multiplex', style = 'Off.TButton',command = lambda: self.ElectrodeSelect('Multiplex'))
        self.MultipleElectrodeFiles.grid(row=2,column=1)


        #--- Frame for editing electrodes ---#
        self.ElectrodeSettingsFrame = tk.Frame(self, relief = 'groove', bd=3)
        self.ElectrodeSettingsFrame.grid(row=10,column=0,columnspan=2,padx=10,pady=10, sticky = 'nsew')
        self.ElectrodeSettingsFrame.columnconfigure(0,weight=1)
        self.ElectrodeSettingsFrame.rowconfigure(0,weight=1)
        self.ElectrodeSettingsFrame.rowconfigure(1,weight=1)
        self.ElectrodeSettingsFrame.rowconfigure(2,weight=1)


        #####################################################
        ### Select and Edit Frequencies for Data Analysis ###
        #####################################################

        self.ListboxFrame = tk.Frame(self)                   # create a frame to pack in the frequency box and scrollbar
        self.ListboxFrame.grid(row=row_value,column=2,columnspan=2,padx=10,pady=10, sticky='nsew')
        frequencies = InputFrequencies

        #-- resize ---#
        self.ListboxFrame.rowconfigure(0, weight=1)
        self.ListboxFrame.rowconfigure(1, weight=1)
        self.ListboxFrame.columnconfigure(0, weight=1)

        self.FrequencyLabel = ttk.Label(self.ListboxFrame, text='Select Frequencies', font= LARGE_FONT)
        self.FrequencyLabel.grid(row=0,padx=10)

        #--- If more than 5 frequencies are in the listbox, add a scrollbar as to not take up too much space ---#
        if len(InputFrequencies) > 5:
            self.ScrollBarVal = True
        else:
            self.ScrollBarVal = False

        #--- Variable to check if the frequency_list contains frequencies ---#
        self.FrequencyListExists = False

        #--- ListBox containing the frequencies given on line 46 (InputFrequencies) ---#
        self.FrequencyList = Listbox(self.ListboxFrame, relief='groove', exportselection=0, width=5, font=('Verdana', 11), height = 6, selectmode='multiple', bd=3)
        self.FrequencyList.bind('<<ListboxSelect>>',self.FrequencyCurSelect)
        self.FrequencyList.grid(row=1,padx=10,sticky='nswe')
        for frequency in frequencies:
            self.FrequencyList.insert(END, frequency)

        #--- Scroll Bar ---#
        if self.ScrollBarVal:
            self.scrollbar = Scrollbar(self.ListboxFrame, orient="vertical")
            self.scrollbar.config(width=10,command=self.FrequencyList.yview)
            self.scrollbar.grid(row=1,sticky='nse')
            self.FrequencyList.config(yscrollcommand=self.scrollbar.set)

        ManipulateFrequencies = ttk.Button(self.ListboxFrame, text = 'Edit', command = lambda: ManipulateFrequenciesFrame.tkraise()).grid(row=2,column=0,columnspan=4)

        ###########################################################
        ### Frame for adding/deleting frequencies from the list ###
        ###########################################################

        ManipulateFrequenciesFrame = tk.Frame(self, width=10, bd = 3, relief = 'groove')
        ManipulateFrequenciesFrame.grid(row=row_value,column=2,columnspan=2,padx=10,pady=10, sticky='nsew')

        ManipulateFrequencyLabel = ttk.Label(ManipulateFrequenciesFrame, text = 'Enter Frequency(s)')
        ManipulateFrequencyLabel.grid(row=0,column=0,columnspan=4)

        self.FrequencyEntry = tk.Entry(ManipulateFrequenciesFrame, width=8)
        self.FrequencyEntry.grid(row=1,column=0,columnspan=4)

        AddFrequencyButton = ttk.Button(ManipulateFrequenciesFrame, text='Add', command = lambda: self.AddFrequency()).grid(row=2,column=0)
        DeleteFrequencyButton = ttk.Button(ManipulateFrequenciesFrame, text='Delete', command = lambda: self.DeleteFrequency()).grid(row=2,column=1)
        ClearFrequencyButton = ttk.Button(ManipulateFrequenciesFrame, text='Clear', command = lambda: self.Clear()).grid(row=3,column=0,columnspan=2)

        ReturnButton = ttk.Button(ManipulateFrequenciesFrame, text = 'Return', command = lambda: self.Return()).grid(row=4,column=0,columnspan=2)

        ManipulateFrequenciesFrame.rowconfigure(0, weight=1)
        ManipulateFrequenciesFrame.rowconfigure(1, weight=1)
        ManipulateFrequenciesFrame.rowconfigure(2, weight=1)
        ManipulateFrequenciesFrame.rowconfigure(3, weight=1)
        ManipulateFrequenciesFrame.rowconfigure(4, weight=1)
        ManipulateFrequenciesFrame.columnconfigure(0, weight=1)
        ManipulateFrequenciesFrame.columnconfigure(1, weight=1)

        row_value += 1

        #--- Select Analysis Method---#
        Methods = ['Continuous Scan','Frequency Map']
        MethodsLabel = ttk.Label(self, text='Select Analysis Method', font=('Verdana', 11))
        self.MethodsBox = Listbox(self, relief='groove', exportselection=0, font=('Verdana', 11), height=len(Methods), selectmode='single', bd=3)
        self.MethodsBox.bind('<<ListboxSelect>>', self.SelectMethod)
        MethodsLabel.grid(row=row_value,column=0,columnspan=4)
        row_value += 1
        self.MethodsBox.grid(row=row_value,column=0,columnspan=4)
        row_value += 1
        for method in Methods:
            self.MethodsBox.insert(END, method)

        # Select SWV and CA
        Analysis_methods = ['SWV','CA']
        AnalysisLabel = ttk.Label(self, text='Select data-Analysis Method', font=('Verdana', 11))
        self.AnalysisBox = Listbox(self, relief='groove', exportselection=0, font=('Verdana', 11), height=len(Analysis_methods), selectmode='single', bd=3)
        self.AnalysisBox.bind('<<ListboxSelect>>', self.SelectDataAnalysis)
        AnalysisLabel.grid(row=row_value,column=0,columnspan=4)
        row_value += 1
        self.AnalysisBox.grid(row=row_value,column=0,columnspan=4)
        row_value += 1
        for method in Analysis_methods:
            self.AnalysisBox.insert(END, method)


        #--- Select Data to be Plotted ---#
        Options = ['Peak Height Extraction','Area Under the Curve']
        OptionsLabel = ttk.Label(self, text='Select Data to be Plotted', font=('Verdana', 11))
        self.PlotOptions = Listbox(self, relief='groove', exportselection=0, font=('Verdana', 11), height=len(Options), selectmode='single', bd=3)
        self.PlotOptions.bind('<<ListboxSelect>>', self.SelectPlotOptions)
        OptionsLabel.grid(row=row_value,column=0,columnspan=2)
        self.PlotOptions.grid(row=row_value+1,column=0,columnspan=2)

        for option in Options:
            self.PlotOptions.insert(END, option)

        #--- Warning label for if the user does not select an analysis method ---#
        self.NoOptionsSelected = ttk.Label(self, text = 'Select a Data Analysis Method', foreground='red')   # will only be added to the grid (row 16) if they dont select an option
        self.NoSelection = False


        #--- Select units of the X-axis ---#
        PlotOptions = ['Experiment Time','File Number']
        PlotLabel = ttk.Label(self, text='Select X-axis units', font=('Verdana', 11))
        self.XaxisOptions = Listbox(self, relief='groove', exportselection=0, font=('Verdana', 11), height=len(PlotOptions), selectmode='single', bd=3)
        self.XaxisOptions.bind('<<ListboxSelect>>', self.SelectXaxisOptions)
        PlotLabel.grid(row=row_value,column=2,columnspan=2)
        self.XaxisOptions.grid(row=row_value+1,column=2,columnspan=2)
        for option in PlotOptions:
            self.XaxisOptions.insert(END, option)

        row_value += 2
        ############################################################
        ### Adjustment of Visualization Parameters: xstart, xend ###
        ############################################################

        #--- Create a frame that will contain all of the widgets ---#
        AdjustmentFrame = tk.Frame(self, relief = 'groove', bd=3)
        AdjustmentFrame.grid(row=row_value,column=0,columnspan=4,pady=15)
        row_value += 1
        AdjustmentFrame.rowconfigure(0, weight=1)
        AdjustmentFrame.rowconfigure(1, weight=1)
        AdjustmentFrame.rowconfigure(2, weight=1)
        AdjustmentFrame.rowconfigure(3, weight=1)
        AdjustmentFrame.rowconfigure(4, weight=1)
        AdjustmentFrame.columnconfigure(0, weight=1)
        AdjustmentFrame.columnconfigure(1, weight=1)
        AdjustmentFrame.columnconfigure(2, weight=1)
        AdjustmentFrame.columnconfigure(3, weight=1)

        #--- Y Limit Adjustment Variables ---#
        self.y_limit_parameter_label = ttk.Label(AdjustmentFrame, text = 'Select Y Limit Parameters',font=('Verdana', 11))
        self.y_limit_parameter_label.grid(row=0,column=0,columnspan=4,pady=5,padx=5)

        #--- Raw Data Minimum Parameter Adjustment ---#
        self.raw_data_min_parameter_label = ttk.Label(AdjustmentFrame, text = 'Raw Min. Factor',font=('Verdana', 10))
        self.raw_data_min_parameter_label.grid(row=1,column=0)
        self.raw_data_min = tk.Entry(AdjustmentFrame, width=5)
        self.raw_data_min.insert(END, '2')                   # initial minimum is set to 0.5*minimum current (baseline) of file 1
        self.raw_data_min.grid(row=2,column=0,padx=5,pady=2,ipadx=2)

        #--- Raw Data Maximum Parameter Adjustment ---#
        self.raw_data_max_parameter_label = ttk.Label(AdjustmentFrame, text = 'Raw Max. Factor',font=('Verdana', 10))
        self.raw_data_max_parameter_label.grid(row=3,column=0)
        self.raw_data_max = tk.Entry(AdjustmentFrame, width=5)
        self.raw_data_max.insert(END, '2')                      # initial adjustment is set to 2x the max current (Peak Height) of file 1
        self.raw_data_max.grid(row=4,column=0,padx=5,pady=2,ipadx=2)

        #--- Raw Data Minimum Parameter Adjustment ---#
        self.data_min_parameter_label = ttk.Label(AdjustmentFrame, text = 'Data Min. Factor',font=('Verdana', 10))
        self.data_min_parameter_label.grid(row=1,column=1)
        self.data_min = tk.Entry(AdjustmentFrame, width=5)
        self.data_min.insert(END, '2')                   # initial minimum is set to 0.5*minimum current (baseline) of file 1
        self.data_min.grid(row=2,column=1,padx=5,pady=2,ipadx=2)

        #--- Raw Data Maximum Parameter Adjustment ---#
        self.data_max_parameter_label = ttk.Label(AdjustmentFrame, text = 'Data Max. Factor',font=('Verdana', 10))
        self.data_max_parameter_label.grid(row=3,column=1)
        self.data_max = tk.Entry(AdjustmentFrame, width=5)
        self.data_max.insert(END, '2')                      # initial adjustment is set to 2x the max current (Peak Height) of file 1
        self.data_max.grid(row=4,column=1,padx=5,pady=2,ipadx=2)

        #--- Normalized Data Minimum Parameter Adjustment ---#
        self.norm_data_min_parameter_label = ttk.Label(AdjustmentFrame, text = 'Norm. Min.',font=('Verdana', 10))
        self.norm_data_min_parameter_label.grid(row=1,column=2)
        self.norm_data_min = tk.Entry(AdjustmentFrame, width=5)
        self.norm_data_min.insert(END, '0')                      # initial minimum is set to 0
        self.norm_data_min.grid(row=2,column=2,padx=5,pady=2,ipadx=2)

        #--- Normalized Data Maximum Parameter Adjustment ---#
        self.norm_data_max_parameter_label = ttk.Label(AdjustmentFrame, text = 'Norm. Max.',font=('Verdana', 10))
        self.norm_data_max_parameter_label.grid(row=3,column=2)
        self.norm_data_max = tk.Entry(AdjustmentFrame, width=5)
        self.norm_data_max.insert(END, '2')                      # initial maximum is set to 2
        self.norm_data_max.grid(row=4,column=2,padx=5,pady=2,ipadx=2)

        #--- Raw Data Minimum Parameter Adjustment ---#
        self.KDM_min_label = ttk.Label(AdjustmentFrame, text = 'KDM Min.',font=('Verdana', 10))
        self.KDM_min_label.grid(row=1,column=3)
        self.KDM_min = tk.Entry(AdjustmentFrame, width=5)
        self.KDM_min.insert(END, '0')                   # initial minimum is set to 0.5*minimum current (baseline) of file 1
        self.KDM_min.grid(row=2,column=3,padx=5,pady=2,ipadx=2)

        #--- Raw Data Maximum Parameter Adjustment ---#
        self.KDM_Max_label = ttk.Label(AdjustmentFrame, text = 'KDM Max. ',font=('Verdana', 10))
        self.KDM_Max_label.grid(row=3,column=3)
        self.KDM_max = tk.Entry(AdjustmentFrame, width=5)
        self.KDM_max.insert(END, '2')                      # initial adjustment is set to 2x the max current (Peak Height) of file 1
        self.KDM_max.grid(row=4,column=3,padx=5,pady=2,ipadx=2)


        #--- Ask the User if they want to export the data to a .txt file ---#
        self.SaveVar = BooleanVar()
        self.SaveVar.set(False)
        #self.SaveBox = CheckButton(self, variable=self.SaveVar, onvalue=True, offvalue=False, text="Export Data").grid(row=row_value,column=0,columnspan=2)
        self.SaveBox = Checkbutton(self, variable=self.SaveVar, onvalue=True, offvalue=False, text="Export Data")
        self.SaveBox.grid(row=row_value, column=0, columnspan=2)

        #--- Ask the User if they want to export the data to a .txt file ---#
        self.InjectionVar = BooleanVar()
        self.InjectionVar.set(False)
        self.InjectionCheck = Checkbutton(self, variable=self.InjectionVar, onvalue=True, offvalue=False, text="Injection Experiment?")
        self.InjectionCheck.grid(row=row_value, column=2, columnspan=2)

        row_value += 1


        #--- Quit Button ---#
        self.QuitButton = ttk.Button(self, width=9, text='Quit Program',command=lambda: quit())
        self.QuitButton.grid(row=row_value,column=0,columnspan=2,pady=10,padx=10)

        #--- Button to Initialize Data Analysis --#
        StartButton = ttk.Button(self, width=9, text='Initialize', command = lambda: self.CheckPoint())
        StartButton.grid(row=row_value,column=2,columnspan=2, pady=10, padx=10)
        row_value += 1

        for row in range(row_value):
            row += 1
            self.rowconfigure(row, weight = 1)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(3, weight = 1)

        ### Raise the initial frame for Electrode and Frequency Selection ###
        self.ListboxFrame.tkraise()
        self.ElectrodeListboxFrame.tkraise()


    #################################################
    ### Functions to track Selections and Entries ###
    #################################################

    def AddFrequency(self):
        Frequencies = self.FrequencyEntry.get()
        self.FrequencyEntry.delete(0,END)

        if Frequencies is not None:
            FrequencyList = Frequencies.split(' ')
            for frequency in FrequencyList:
                if int(frequency) not in InputFrequencies:
                    InputFrequencies.append(int(frequency))
            InputFrequencies.sort()

            self.FrequencyList.delete(0,1)
            self.FrequencyList.delete(0,END)

            for frequency in InputFrequencies:
                self.FrequencyList.insert(END,frequency)


    def DeleteFrequency(self):
        Frequencies = self.FrequencyEntry.get()
        self.FrequencyEntry.delete(0,END)

        if Frequencies is not None:
            FrequencyList = Frequencies.split(' ')

            for Frequency in FrequencyList:

                Frequency = int(Frequency)
                if Frequency in InputFrequencies:
                    InputFrequencies.remove(Frequency)

                self.FrequencyList.delete(0,END)

                for frequency in InputFrequencies:
                    self.FrequencyList.insert(END,int(frequency))

    def Clear(self):
        global InputFrequencies

        self.FrequencyList.delete(0, tk.END)
        InputFrequencies = []

    def Return(self):
        self.ListboxFrame.tkraise()
        self.FrequencyEntry.delete(0,tk.END)

    def ElectrodeSettings(self):
        self.ElectrodeSettingsFrame.tkraise()

    def ElectrodeSelect(self, variable):
        global e_var

        if variable == 'Multiplex':
            e_var = 'multiple'

            self.SingleElectrodeFile['style'] = 'Off.TButton'
            self.MultipleElectrodeFiles['style'] = 'On.TButton'

        elif variable == 'Multichannel':
            e_var = 'single'

            self.SingleElectrodeFile['style'] = 'On.TButton'
            self.MultipleElectrodeFiles['style'] = 'Off.TButton'


    def FindFile(self, parent):
        global FilePath, ExportPath, FoundFilePath, DataFolder

        try:

            ### prompt the user to select a  ###
            ### directory for  data analysis ###
            FilePath = filedialog.askdirectory(parent = parent)
            FilePath = ''.join(FilePath + '/')

            ### Path for directory in which the    ###
            ### exported .txt file will be placed  ###
            ExportPath = FilePath.split('/')

            #-- change the text of the find file Button to the folder the user chose --#
            DataFolder = '%s/%s' % (ExportPath[-3],ExportPath[-2])

            self.SelectFilePath['style'] = 'On.TButton'
            self.SelectFilePath['text'] = DataFolder

            del ExportPath[-1]
            del ExportPath[-1]
            ExportPath = '/'.join(ExportPath)
            ExportPath = ''.join(ExportPath + '/')

            ## Indicates that the user has selected a File Path ###
            FoundFilePath = True

            if self.PathWarningExists:
                self.NoSelectedPath['text'] = ''
                self.NoSelectedPath.grid_forget()

        except Exception as e:
            print('\n\nInputPage.FindFile: Could Not Find File Path\n\n')
            print(e)

    #--- Analysis Method ---#
    def SelectMethod(self, event):
        global method
        selection = self.MethodsBox.curselection()
        if selection:
            method = str(self.MethodsBox.get(selection))
        else:
            # Handle the case when no item is selected
            method = "No selection"
        print(f'Chose method {method}')

    #-- Data-Analysis Method --#
    def SelectDataAnalysis(self,event):
        global data_method
        selection = self.AnalysisBox.curselection()
        if selection:
            data_method = str(self.AnalysisBox.get(selection))
        else:
            # Handle the case when no item is selected
            data_method = "No selection"
        print(f'Chose method {data_method}')

    #--- Analysis method ---#
    def SelectPlotOptions(self,event):
        global SelectedOptions
        SelectedOptions = str((self.PlotOptions.get(self.PlotOptions.curselection())))
        print(SelectedOptions)


    def SelectXaxisOptions(self,event):
        global XaxisOptions
        XaxisOptions = str((self.XaxisOptions.get(self.XaxisOptions.curselection())))

    #--- Electrode Selection ---#
    def ElectrodeCurSelect(self,event):
        ###################################################
        ## electrode_list: list; ints                    ##
        ## electrode_dict: dict; {electrode: index}      ##
        ## electrode_count: int                          ##
        ###################################################
        global electrode_count, electrode_list, electrode_dict, frame_list, PlotValues

        electrode_list = [self.ElectrodeCount.get(idx) for idx in self.ElectrodeCount.curselection()]
        electrode_list = [int(electrode) for electrode in electrode_list]
        electrode_count = len(electrode_list)

        index = 0
        electrode_dict = {}
        for electrode in electrode_list:
            electrode_dict[electrode] = index
            index += 1

        if electrode_count == 0:
            self.ElectrodeListExists = False
            self.ElectrodeLabel['foreground'] = 'red'

        elif electrode_count != 0:
            self.ElectrodeListExists = True
            self.ElectrodeLabel['foreground'] = 'black'

    #--- Frequency Selection ---#
    def FrequencyCurSelect(self,event):
        global frequency_list, frequency_dict, LowFrequency, HighFrequency, HighLowList

        frequency_list = [self.FrequencyList.get(idx) for idx in self.FrequencyList.curselection()]


        if len(frequency_list) != 0:

            self.FrequencyListExists = True
            self.FrequencyLabel['foreground'] = 'black'

            for var in frequency_list:
                var = int(var)

            LowFrequency = min(frequency_list)          # Initial Low Frequency for KDM/Ratiometric analysis
            HighFrequency = max(frequency_list)         # Initial High Frequency for KDM/Ratiometric analysis

            HighLowList['High'] = HighFrequency
            HighLowList['Low'] = LowFrequency

            #--- Frequency Dictionary ---#
            frequency_dict = {}
            count = 0
            for frequency in frequency_list:
                frequency = int(frequency)
                frequency_dict[frequency] = count
                count += 1

        elif len(frequency_list) == 0:
            self.FrequencyListExists = False
            self.FrequencyLabel['foreground'] = 'red'


    #--- Functions to switch frames and plots ---#
    def show_frame(self, cont):

        frame = ShowFrames[cont]
        frame.tkraise()

    #--- Function to switch between visualization frames ---#
    def show_plot(self, frame):
        frame.tkraise()

    #####################################################################
    ### Check to see if the user has filled out all  required fields: ###
    ### Electrodes, Frequencies, Analysis Method, and File Path. If   ###
    ### they have, initialize the program                             ###
    #####################################################################
    def CheckPoint(self):
        global mypath, Option, FileHandle, SelectedOptions, ExportFilePath, AlreadyInitiated, delimeter
        print("Successfully initialized")
        try:
            #--- check to see if the data analysis method has been selected by the user ---#
            Option = SelectedOptions

            #--- If a data analysis method was selected and a warning label was already created, forget it ---#
            if self.NoSelection:
                self.NoSelection = False
                self.NoOptionsSelected.grid_forget()
        except:
            #--- if no selection was made, create a warning label telling the user to select an analysis method ---#
            self.NoSelection = True
            self.NoOptionsSelected.grid(row=14,column=0,columnspan=2)


        #########################################################
        ### Initialize Canvases and begin tracking animation  ###
        #########################################################
        try:
            mypath = FilePath
            print(mypath)                       # file path
            FileHandle = str(self.filehandle.get()) # handle for exported .txt file
            ExportFilePath = ''.join(ExportPath + FileHandle)

            if self.PathWarningExists:
                self.NoSelectedPath.grid_forget()
                self.PathWarningExists = False

        except:
            #-- if the user did not select a file path for data analysis, raise a warning label ---#
            if not FoundFilePath:
                self.NoSelectedPath.grid(row=1,column=0,columnspan=4)
                self.PathWarningExists = True

        if not self.FrequencyListExists:
            self.FrequencyLabel['foreground'] = 'red'
        elif self.FrequencyListExists:
            self.FrequencyLabel['foreground'] = 'black'

        if not self.ElectrodeListExists:
            self.ElectrodeLabel['foreground'] = 'red'
        elif self.ElectrodeListExists:
            self.ElectrodeLabel['foreground'] = 'black'

        if not self.PathWarningExists:
            if not self.NoSelection:
                if self.FrequencyListExists:
                    self.StartProgram()

                else:
                    print('Could Not Start Program')


    ########################################################################
    ### Function To Initialize Data Acquisition, Analysis, and Animation ###
    ########################################################################

    def StartProgram(self):
        global FileHandle, starting_file,extension, post_analysis, handle_variable, track, Interval, PlotContainer, e_var, data_normalization, resize_interval, InjectionPoint, InjectionVar, ratio_min, ratio_max, min_norm, max_norm, min_raw, max_raw, min_data, max_data, HighLowList, HighFrequency, LowFrequency, InitializedNormalization, RatioMetricCheck, NormWarningExists, NormalizationVault, mypath, electrode_count, wait_time, SaveVar, track, numFiles, SampleRate, ratiometricanalysis, frames, generate, figures, Plot, frame_list, PlotValues, anim, NormalizationPoint, q, delimiter

        #---Get the User Input and make it globally accessible---#

        print("Entered StartProgram")
        SampleRate = float(self.sample_rate.get())  # sample rate for experiment in seconds

        if method == 'Continuous Scan':
            numFiles = int(self.numfiles.get())     # file limit
        elif method == 'Frequency Map':
            numFiles = 1

        q = Queue()

        if delimiter == 1:
            delimiter = ' '
        elif delimiter == 2:
            delimiter = '\t'
        elif delimiter == 3:
            delimiter = ','

        if extension == 1:
            extension = '.txt'
        elif extension == 2:
            extension = '.csv'
        elif extension == 3:
            extension = '.DTA'

        InjectionPoint = None                   # None variable if user has not selected an injection point
        InitializedNormalization = False        # tracks if the data has been normalized to the starting normalization point
        RatioMetricCheck = False                # tracks changes to high and low frequencies
        NormWarningExists = False               # tracks if a warning label for the normalization has been created

        NormalizationPoint = 3
        starting_file = 1

        SaveVar = self.SaveVar.get()            # tracks if text file export has been activated
        InjectionVar = self.InjectionVar.get()  # tracks if injection was selected
        resize_interval = int(self.resize_entry.get())      # interval at which xaxis of plots resizes
        handle_variable = self.ImportFileEntry.get()        # string handle used for the input file


        #--- Y Limit Adjustment Parameters ---#
        min_norm = float(self.norm_data_min.get())          # normalization y limits
        max_norm = float(self.norm_data_max.get())
        min_raw = float(self.raw_data_min.get())            # raw data y limit adjustment variables
        max_raw = float(self.raw_data_max.get())
        min_data = float(self.data_min.get())               # raw data y limit adjustment variables
        max_data = float(self.data_max.get())
        ratio_min = float(self.KDM_min.get())               # KDM min and max
        ratio_max = float(self.KDM_max.get())

        #############################################################
        ### Interval at which the program searches for files (ms) ###
        #############################################################
        Interval = self.Interval.get()

        ## set the resizeability of the container ##
        ## frame to handle PlotContainer resize   ##
        container.columnconfigure(1, weight=1)

        #--- High and Low Frequency Selection for Drift Correction (KDM) ---#
        HighFrequency = max(frequency_list)
        LowFrequency = min(frequency_list)
        HighLowList['High'] = HighFrequency
        HighLowList['Low'] = LowFrequency

        #--- Create a timevault for normalization variables if the chosen normalization point has not yet been analyzed ---#
        NormalizationVault = []                           # timevault for Normalization Points
        NormalizationVault.append(NormalizationPoint)     # append the starting normalization point

        ################################################################
        ### If all checkpoints have been met, initialize the program ###
        ################################################################
        if not self.NoSelection:
            if FoundFilePath:
                GUI_variables = (method,electrode_list, mypath, frequency_list, e_var, electrode_count, InjectionVar, XaxisOptions, NormalizationVault, HighLowList, SampleRate, frequency_dict, q, SelectedOptions, electrode_dict, numFiles, InjectionPoint, resize_interval,byte_limit,handle_variable,extension,delimiter,current_column,spacing_index, ShowFrames,SaveVar )



                checkpoint = CheckPoint(self.parent, self.controller,GUI_variables),
