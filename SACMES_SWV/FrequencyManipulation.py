import tkinter as tk
from tkinter import ttk
from GlobalVariables import *

import Electrochemical_animation
class FrequencyMapManipulationFrame(tk.Frame):

    def __init__(self, controller, parent, controller_):
        global PlotValues, container, high_xstart_entry, low_xstart_entry, high_xend_entry, low_xend_entry, ShowFrames

        tk.Frame.__init__(self, parent)         # Initialize the frame
        self.controller = controller

        #######################################
        #######################################
        ### Pack the widgets into the frame ###
        #######################################
        #######################################

        #################################################
        ### Nested Frame for Real-Time adjustment     ###
        ### of voltammogram, polynomial regression,   ###
        ### and savitzky-golay Smoothing              ###
        #################################################

        RegressionFrame = tk.Frame(self,relief='groove',bd=5)
        RegressionFrame.grid(row=7,column=0,columnspan=4,pady=5,padx=5,ipadx=3, sticky='ns')
        RegressionFrame.rowconfigure(0, weight=1)
        RegressionFrame.rowconfigure(1, weight=1)
        RegressionFrame.rowconfigure(2, weight=1)
        RegressionFrame.columnconfigure(0, weight=1)
        RegressionFrame.columnconfigure(1, weight=1)

        #--- Title ---#
        self.RegressionLabel = ttk.Label(RegressionFrame, text = 'Real Time Analysis Manipulation', font=('Verdana', 11))
        self.RegressionLabel.grid(row=0,column=0,columnspan=4,pady=5,padx=5)


        ###################################################################
        ### Real Time Manipulation of Savitzky-Golay Smoothing Function ###
        ###################################################################
        self.SmoothingLabel = ttk.Label(RegressionFrame, text = 'Savitzky-Golay Window (mV)', font = LARGE_FONT)
        self.SmoothingLabel.grid(row=1,column=0,columnspan=4,pady=1)
        self.SmoothingEntry = tk.Entry(RegressionFrame, width=10)
        self.SmoothingEntry.grid(row=2,column=0,columnspan=4,pady=3)
        self.SmoothingEntry.insert('end', sg_window)

        #--- Check for the presence of high and low frequencies ---#
        if frequency_list[-1] > 50:
            self.High = True
        else:
            self.High = False
        if frequency_list[0] <= 50:
            self.Low = True
        else:
            self.Low = False
        ###################################################
        ### If a frequency <= 50Hz exists, grid a frame ###
        ### for low frequency data manipulation         ###
        ###################################################
        if self.Low is True:
            LowParameterFrame = tk.Frame(RegressionFrame)
            LowParameterFrame.grid(row=3,column=0,columnspan=4, sticky='nsew')
            LowParameterFrame.rowconfigure(0, weight=1)
            LowParameterFrame.rowconfigure(1, weight=1)
            LowParameterFrame.rowconfigure(2, weight=1)
            LowParameterFrame.columnconfigure(0, weight=1)
            LowParameterFrame.columnconfigure(1, weight=1)
            ShowFrames['LowParameterFrame'] = LowParameterFrame

            #--- points discarded at the beginning of the voltammogram, xstart ---#
            self.low_xstart_label = ttk.Label(LowParameterFrame, text = 'xstart (V)', font=('Verdana', 10)).grid(row=0,column=0)
            self.low_xstart_entry = tk.Entry(LowParameterFrame, width=7)
            self.low_xstart_entry.insert('end', str(low_xstart))
            self.low_xstart_entry.grid(row=1,column=0)
            low_xstart_entry = self.low_xstart_entry

            #--- points discarded at the beginning of the voltammogram, xend ---#
            self.low_xend_label = ttk.Label(LowParameterFrame, text = 'xend (V)', font=('Verdana', 10)).grid(row=0,column=1)
            self.low_xend_entry = tk.Entry(LowParameterFrame, width=7)
            self.low_xend_entry.insert('end', str(low_xend))
            self.low_xend_entry.grid(row=1,column=1)
            low_xend_entry = self.low_xend_entry

        ##################################################
        ### If a frequency > 50Hz exists, grid a frame ###
        ### for high frequency data manipulation       ###
        ##################################################
        if self.High is True:
            HighParameterFrame = tk.Frame(RegressionFrame)
            HighParameterFrame.grid(row=3,column=0,columnspan=4, sticky='nsew')
            HighParameterFrame.rowconfigure(0, weight=1)
            HighParameterFrame.rowconfigure(1, weight=1)
            HighParameterFrame.rowconfigure(2, weight=1)
            HighParameterFrame.columnconfigure(0, weight=1)
            HighParameterFrame.columnconfigure(1, weight=1)
            ShowFrames['HighParameterFrame'] = HighParameterFrame

            #--- points discarded at the beginning of the voltammogram, xstart ---#
            self.high_xstart_label = ttk.Label(HighParameterFrame, text = 'xstart (V)', font=('Verdana', 10)).grid(row=0,column=0)
            self.high_xstart_entry = tk.Entry(HighParameterFrame, width=7)
            self.high_xstart_entry.insert('end', str(high_xstart))
            self.high_xstart_entry.grid(row=1,column=0)
            high_xstart_entry = self.high_xstart_entry

            #--- points discarded at the beginning of the voltammogram, xend ---#
            self.high_xend_label = ttk.Label(HighParameterFrame, text = 'xend (V)', font=('Verdana', 10)).grid(row=0,column=1)
            self.high_xend_entry = tk.Entry(HighParameterFrame, width=7)
            self.high_xend_entry.insert('end', str(high_xend))
            self.high_xend_entry.grid(row=1,column=1)
            high_xend_entry = self.high_xend_entry

        ############################################################
        ### If both high and low frequencies are being analyzed, ###
        ### create Buttons to switch between the two             ###
        ############################################################
        if self.High is True:
            if self.Low is True:
                self.SelectLowParameters = ttk.Button(RegressionFrame, style = 'Off.TButton', text = 'f <= 50Hz', command = lambda: self.show_frame('LowParameterFrame'))
                self.SelectLowParameters.grid(row=4,column=0,pady=5,padx=5)

                self.SelectHighParameters = ttk.Button(RegressionFrame, style = 'On.TButton', text = 'f > 50Hz', command = lambda: self.show_frame('HighParameterFrame'))
                self.SelectHighParameters.grid(row=4,column=1,pady=5,padx=5)


        #--- Button to apply adjustments ---#
        self.AdjustParameterButton = ttk.Button(RegressionFrame, text = 'Apply Adjustments', command = lambda: self.AdjustParameters())
        self.AdjustParameterButton.grid(row=5,column=0,columnspan=4,pady=10,padx=10)


        #---Buttons to switch between electrode frames---#
        frame_value = 0
        row_value = 8
        column_value = 0
        for value in PlotValues:
            Button = ttk.Button(self, text=frame_list[frame_value], command = lambda frame_value=frame_value: self.show_plot(PlotValues[frame_value]))
            Button.grid(row=row_value,column=column_value,pady=2,padx=5)

            ## allows .grid() to alternate between
            ## packing into column 1 and column 2
            if column_value == 1:
                column_value = 0
                row_value += 1

            ## if gridding into the 1st column,
            ## grid the next into the 2nd column
            else:
                column_value += 1
            frame_value += 1
        row_value += 1


        #--- Start ---#
        StartButton = ttk.Button(self, text='Start', style='Fun.TButton', command = lambda: self.SkeletonKey())
        StartButton.grid(row=row_value, column=0, pady=5, padx=5)

        #--- Reset ---#
        Reset = ttk.Button(self, text='Reset', style='Fun.TButton', command = lambda: self.Reset())
        Reset.grid(row=row_value, column=1,pady=5, padx=5)
        row_value += 1

        #--- Quit ---#
        QuitButton = ttk.Button(self, text='Quit Program',command=lambda: quit())
        QuitButton.grid(row=row_value,column=0,columnspan=4,pady=5)

        for row in range(row_value):
            row += 1
            self.rowconfigure(row, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)



                                        ###################################################
                                        ###################################################
                                        ###### Real Time Data Manipulation Functions ######
                                        ###################################################
                                        ###################################################



    #################################################
    ### Adjustment of points discarded at the     ###
    ### beginning and 'end' of Regression Analysis  ###
    #################################################
    def AdjustParameters(self):
        #--- Adjusts the parameters used to visualize the raw voltammogram, smoothed currents, and polynomial fit
        global low_xstart, high_xstart, low_xend, high_xend, sg_window

        ###############################################
        ### Polynomical Regression Range Parameters ###
        ###############################################

        if self.Low:
            #--- parameters for frequencies equal or below 50Hz ---#
            low_xstart = float(self.low_xstart_entry.get())          # xstart/xend adjust the points at the start and 'end' of the voltammogram/smoothed currents, respectively
            low_xend = float(self.low_xend_entry.get())
        if self.High:
            #--- parameters for frequencies above 50Hz ---#
            high_xstart = float(self.high_xstart_entry.get())
            high_xend = float(self.high_xend_entry.get())

        #######################################
        ### Savitzky-Golay Smoothing Window ###
        #######################################
        sg_window = float(self.SmoothingEntry.get())
        print('\n\n\nAdjustParamaters: SG_Window (mV) %d\n\n\n' % sg_window)


    ########################################################
    ### Function to Reset and raise the user input frame ###
    ########################################################
    def Reset(self):
        from Mainwindow import InputFrame
        global key, PoisonPill, AlreadyInitiated, AlreadyReset

        key = 0
        PoisonPill = True
        AlreadyInitiated = False # reset the start variable
        AlreadyReset = True

        # Raise the initial user input frame
        self.show_frame(InputFrame)
        self.close_frame(method)

    ##########################################################
    ### Function to raise frame to the front of the canvas ###
    ##########################################################
    def show_frame(self, cont):

        frame = ShowFrames[cont]            # Key: frame handle / Value: tk.Frame object
        frame.tkraise()                     # raise the frame objext

        if cont == 'LowParameterFrame':
            self.SelectLowParameters['style'] = 'On.TButton'
            self.SelectHighParameters['style'] = 'Off.TButton'

        elif cont == 'HighParameterFrame':
            self.SelectLowParameters['style'] = 'Off.TButton'
            self.SelectHighParameters['style'] = 'On.TButton'

    ###################################################
    ### Function to start returning visualized data ###
    ###################################################
    def SkeletonKey(self):
        global key, PoisonPill, AlreadyInitiated

        if not AlreadyInitiated:

            ######################################################################
            ### Initialize Animation (Visualization) for each electrode figure ###
            ######################################################################
            fig_count = 0                   # index value for the frame
            for figure in figures:
                fig, self.ax = figure
                electrode = electrode_list[fig_count]
                anim.append(Electrochemical_animation(self.controller, fig, electrode, resize_interval = None, fargs=None))
                fig_count += 1

            AlreadyInitiated = True

            #--- reset poison pill variables --#
            PoisonPill = False

            if key == 0:                                # tells Generate() to start data analysis
                key += 100
        else:
            print('\n\nProgram has already been initiaed\n\n')



    ######################################################
    ### Function to raise frame for specific electrode ###
    ######################################################
    def show_plot(self, frame):
        frame.tkraise()

    #####################################
    ### Destory the frames on Reset() ###
    #####################################
    def close_frame(self, cont):
        frame = ShowFrames[cont]
        frame.grid_forget()

        for value in PlotValues:
            value.destroy()

        PlotContainer.destroy()