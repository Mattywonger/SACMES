from GlobalVariables import *
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import PostAnalysis
import DataNormalization
import WaitTime

import Electrochemical_animation
class ContinuousScanManipulationFrame(tk.Frame):

    def __init__(self, controller, parent, controller_):
        global PlotValues, container, LowFrequencyEntry, high_xstart_entry, low_xstart_entry, high_xend_entry, low_xend_entry, HighFrequencyEntry, NormWarning, ShowFrames, FileLabel, RealTimeSampleLabel, SetPointNorm, NormalizationPoint, NormalizationVar

        tk.Frame.__init__(self,parent)         # Initialize the frame
        

        #######################################
        #######################################
        ### Pack the widgets into the frame ###
        #######################################
        #######################################

        #--- Display the file number ---#
        self.controller = controller
        FileTitle = ttk.Label(self, text = 'File Number', font=('Verdana', 10),)
        FileTitle.grid(row=0,column=0,padx=5,pady=5)
        FileLabel = ttk.Label(self, text = '1', style="LARGE_FONT,Fun.TButton")
        FileLabel.grid(row=1,column=0,padx=5,pady=5)

        #--- Display the experiment duration as a function of the user-inputted Sample Rate ---#
        SampleTitle = ttk.Label(self, text = 'Experiment Time (h)', font=('Verdana', 10))
        SampleTitle.grid(row=0,column=1,padx=5,pady=5)
        RealTimeSampleLabel = ttk.Label(self, text = '0', style='Fun.TButton')
        RealTimeSampleLabel.grid(row=1,column=1,padx=5,pady=5)

        #--- Real-time Normalization Variable ---#
        SetPointNormLabel = ttk.Label(self, text = 'Set Normalization Point', font=('Verdana', 10))
        NormalizationVar = tk.StringVar()
        NormString = str(3)
        NormalizationVar.set(NormString)
        self.SetPointNorm = tk.Entry(self, textvariable = NormalizationVar, width=8)
        SetPointNorm = self.SetPointNorm

        #--- Button to apply any changes to the normalization variable ---#
        NormalizeButton = ttk.Button(self, text='Apply Norm', command = lambda: self.RealTimeNormalization(), width=10)
        self.NormWarning = ttk.Label(self,text='',foreground='red',font=('Verdana', 10))
        NormWarning = self.NormWarning

        if InjectionVar:
            SetPointNormLabel.grid(row=2,column=0,pady=2,sticky='nsew')
            self.SetPointNorm.grid(row=3,column=0,pady=2,padx=2)
            NormalizeButton.grid(row=4,column=0,pady=2,padx=2)
            self.NormWarning.grid(row=5,column=0,pady=0)

        elif not InjectionVar:
            SetPointNormLabel.grid(row=2,column=0,columnspan=4,pady=2,sticky='nsew')
            self.SetPointNorm.grid(row=3,column=0,columnspan=4,pady=2,padx=2)
            NormalizeButton.grid(row=4,column=0,columnspan=4,pady=2,padx=2)
            self.NormWarning.grid(row=5,column=0,columnspan=4,pady=0)



        #--- Real-time Injection tracking ---#
        SetInjectionLabel = ttk.Label(self, text = 'Set Injection Range', font=('Verdana', 10))
        InjectionButton = ttk.Button(self, text='Apply Injection', command = lambda: self.RealTimeInjection(), width=10)
        self.SetInjectionPoint = tk.Entry(self, width=8)


        ## If this is an injection experiment, grid the widgets ##
        if InjectionVar:
            self.SetInjectionPoint.grid(row=3,column=1,pady=2,padx=5)
            InjectionButton.grid(row=4,column=1,pady=2,padx=2)
            SetInjectionLabel.grid(row=2,column=1,pady=2,sticky='nsew')


        row_value = 6
        if len(frequency_list) > 1:

            self.FrequencyFrame = tk.Frame(self, relief = 'groove', bd=3)
            self.FrequencyFrame.grid(row=row_value,column=0,columnspan=4,pady=2,padx=3,ipady=2)

            #--- Drift Correction Title ---#
            self.KDM_title = ttk.Label(self.FrequencyFrame, text = 'Drift Correction', font=('Verdana', 11))
            self.KDM_title.grid(row=0,column=0,columnspan=3,pady=1,padx=5)

            #--- High Frequency Selection for KDM and Ratiometric Analysis ---#
            self.HighFrequencyLabel = ttk.Label(self.FrequencyFrame, text='High Frequency',font=('Verdana', 10))
            self.HighFrequencyLabel.grid(row=1,column=1,pady=5,padx=5)

            HighFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            HighFrequencyEntry.insert('end', HighFrequency)
            HighFrequencyEntry.grid(row=2,column=1,padx=5)

            #--- Low Frequency Selection for KDM and Ratiometric Analysis ---#
            self.LowFrequencyLabel = ttk.Label(self.FrequencyFrame, text='Low Frequency',font=('Verdana', 10))
            self.LowFrequencyLabel.grid(row=1,column=0,pady=5,padx=5)

            LowFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            LowFrequencyEntry.insert('end', LowFrequency)
            LowFrequencyEntry.grid(row=2,column=0,padx=5)

            self.LowFrequencyOffsetLabel = ttk.Label(self.FrequencyFrame, text = 'Low Frequency\n Offset', font=('Verdana', 10)).grid(row=3,column=0,pady=2,padx=2)
            self.LowFrequencyOffset = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencyOffset.insert('end',LowFrequencyOffset)
            self.LowFrequencyOffset.grid(row=4,column=0,padx=2,pady=2)

            self.LowFrequencySlopeLabel = ttk.Label(self.FrequencyFrame, text = 'Low Frequency\n Slope Manipulation', font=('Verdana', 10)).grid(row=3,column=1,pady=2,padx=2)
            self.LowFrequencySlope = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencySlope.insert('end',LowFrequencySlope)
            self.LowFrequencySlope.grid(row=4,column=1,padx=2,pady=2)


            self.ApplyFrequencies = ttk.Button(self.FrequencyFrame, text='Apply Frequencies', command = lambda: self.RealTimeKDM())
            self.ApplyFrequencies.grid(row=5,column=0,columnspan=4,pady=5,padx=5)

            row_value += 1


        #################################################
        ### Nested Frame for Real-Time adjustment     ###
        ### of voltammogram and polynomial regression ###
        #################################################

        RegressionFrame = tk.Frame(self,relief='groove',bd=5)
        RegressionFrame.grid(row=row_value,column=0,columnspan=4,pady=5,padx=5,ipadx=3, sticky='ns')
        RegressionFrame.rowconfigure(0, weight=1)
        RegressionFrame.rowconfigure(1, weight=1)
        RegressionFrame.rowconfigure(2, weight=1)
        RegressionFrame.columnconfigure(0, weight=1)
        RegressionFrame.columnconfigure(1, weight=1)
        row_value += 1

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
        if frequency_list[-1] > cutoff_frequency:
            self.High = True
        else:
            self.High = False

        if frequency_list[0] <= cutoff_frequency:
            self.Low = True
        else:
            self.Low = False

        ##########################################################
        ### If a frequency <= cutoff_frequency exists, grid    ###
        ### a frame for low frequency data manipulation        ###
        ##########################################################
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

        #########################################################
        ### If a frequency > cutoff_frequency exists, grid    ###
        ### a frame for high frequency data manipulation      ###
        #########################################################
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
                self.SelectLowParameters = ttk.Button(RegressionFrame, style = 'Off.TButton', text = 'f <= %dHz' % cutoff_frequency, command = lambda: self.show_frame('LowParameterFrame'))
                self.SelectLowParameters.grid(row=4,column=0,pady=5,padx=5)

                self.SelectHighParameters = ttk.Button(RegressionFrame, style = 'On.TButton', text = 'f > %dHz' % cutoff_frequency, command = lambda: self.show_frame('HighParameterFrame'))
                self.SelectHighParameters.grid(row=4,column=1,pady=5,padx=5)


        #--- Button to apply adjustments ---#
        self.AdjustParameterButton = ttk.Button(RegressionFrame, text = 'Apply Adjustments', command = lambda: self.AdjustParameters())
        self.AdjustParameterButton.grid(row=5,column=0,columnspan=4,pady=10,padx=10)


        #---Buttons to switch between electrode frames---#
        frame_value = 0
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



    #####################################
    ### Manipulation of the Injection ###
    ### Point for visualization       ###
    #####################################
    def RealTimeInjection(self):
        global InjectionPoint

        InjectionPoint = int(self.SetInjectionPoint.get())

        print('\nNew Injection Point: %s\n' % str(InjectionPoint))

    #################################################
    ### Adjustment of points discarded at the     ###
    ### beginning and 'end' of Regression Analysis  ###
    #################################################
    def AdjustParameters(self):
        global low_xstart, high_xstart, low_xend, high_xend, sg_window

        ###############################################
        ### Polynomical Regression Range Parameters ###
        ###############################################

        if self.Low:

            #--- parameters for frequencies equal or below cutoff_frequency ---#
            low_xstart = float(self.low_xstart_entry.get())          # xstart/xend adjust the points at the start and end of the voltammogram/smoothed currents, respectively
            low_xend = float(self.low_xend_entry.get())


        if self.High:

            #--- parameters for frequencies above cutoff_frequency ---#
            high_xstart = float(self.high_xstart_entry.get())
            high_xend = float(self.high_xend_entry.get())

        #######################################
        ### Savitzky-Golay Smoothing Window ###
        #######################################
        sg_window = float(self.SmoothingEntry.get())
        print('\n\n\nAdjustParamaters: SG_Window (mV) %d\n\n\n' % sg_window)


    #########################################################
    ### Real-time adjustment of High and Low frequencies  ###
    ### used for KDM and ratiometric analysis             ###
    #########################################################
    def RealTimeKDM(self):
        global HighFrequency, LowFrequencyOffset, LowFrequencySlope, LowFrequency, HighLowList, LowFrequencyEntry, HighFrequencyEntry, ExistVar, WrongFrequencyLabel, RatioMetricCheck

        TempHighFrequency = int(HighFrequencyEntry.get())
        TempLowFrequency = int(LowFrequencyEntry.get())

        LowFrequencyOffset = float(self.LowFrequencyOffset.get())
        LowFrequencySlope = float(self.LowFrequencySlope.get())

        #--- Reset the variable for the Warning Label (WrongFrequencyLabel) ---#
        CheckVar = 0

        if int(HighFrequency) not in frequency_list:
            CheckVar += 3

        if int(LowFrequency) not in frequency_list:
            CheckVar += 1

        #--- if only the HighFrequency does not exist ---#
        if CheckVar == 3:
            if ExistVar:
                WrongFrequencyLabel.grid_forget()
            WrongFrequencyLabel = ttk.Label(self.FrequencyFrame, text='High Frequency Does Not Exist', foreground='red')
            WrongFrequencyLabel.grid(row=6,column=0,columnspan=4)
            if not ExistVar:
                ExistVar = True

        #--- if only the LowFrequency does not exist ---#
        elif CheckVar == 1:
            if ExistVar:
                WrongFrequencyLabel.grid_forget()
            WrongFrequencyLabel = ttk.Label(self.FrequencyFrame, text='Low Frequency Does Not Exist', foreground='red')
            WrongFrequencyLabel.grid(row=6,column=0,columnspan=4)
            if not ExistVar:
                ExistVar = True

        #--- if both the HighFrequency and LowFrequency do not exist ---#
        elif CheckVar == 4:
            if ExistVar:
                WrongFrequencyLabel.grid_forget()
            WrongFrequencyLabel = ttk.Label(self.FrequencyFrame, text='High and Low Frequencies Do Not Exist', foreground='red')
            WrongFrequencyLabel.grid(row=6,column=0,columnspan=4)
            if not ExistVar:
                ExistVar = True

        #--- else, if they both exist, remove the warning label ---#
        else:
            HighLowList['High'] = TempHighFrequency
            HighLowList['Low'] = TempLowFrequency

            DataNormalization.ResetRatiometricData()

            #--- if a warning label exists, forget it ---#
            if ExistVar:
                WrongFrequencyLabel.grid_forget()

            #--- Tells RawVoltammogramVisualization to revisualize data for new High and Low frequencies ---#
            if not RatioMetricCheck:
                RatioMetricCheck = True

            if analysis_complete:
                PostAnalysis._adjust_data()


    #--- Function for Real-time Normalization ---#
    def RealTimeNormalization(self):
        global NormWarningExists, InitializedNormalization, NormalizationPoint, analysis_complete

        NormalizationPoint = int(self.SetPointNorm.get())
        file = int(FileLabel['text'])
        index = file - 1

        if file >= NormalizationPoint:
            WaitTime.NormalizationWaitTime()

        elif NormalizationPoint > file:
            NormWarning['foreground'] = 'red'
            NormWarning['text'] = 'File %s has \nnot been analyzed' % str(NormalizationPoint)

        if analysis_complete:
            PostAnalysis._adjust_data()


    ########################################################
    ### Function to Reset and raise the user input frame ###
    ########################################################
    def Reset(self):
        from Mainwindow import InputFrame
        global key, PoisonPill, analysis_complete, AlreadyInitiated, LowAlreadyReset, HighAlreadyReset

        key = 0
        PoisonPill = True
        AlreadyInitiated = False # reset the start variable

        if self.High:
            HighAlreadyReset = True

        if self.Low:
            LowAlreadyReset = True

        # Raise the initial user input frame
        self.show_frame(InputFrame)
        self.close_frame(method)

        PostAnalysis._reset()

        ## Take resize weight away from the Visualization Canvas
        container.columnconfigure(1, weight=0)

        analysis_complete = False



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
        global key, PoisonPill, data_analysis, extrapolate, AlreadyInitiated

        if not AlreadyInitiated:

            ######################################################################
            ### Initialize Animation (Visualization) for each electrode figure ###
            ######################################################################
            fig_count = 0    
            print("The type for figures is")
            print(figures)               # index value for the frame
            for figure in figures:
                fig, self.ax = figure
                electrode = electrode_list[fig_count]
                anim.append(Electrochemical_animation(self.controller, fig, electrode, resize_interval = resize_interval, fargs=None))
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

        # close all matplotlib figures
        plt.close('all')

        # destory the frames holding the figures
        for frame in PlotValues:
            frame.destroy()

        # destory the container holding those frames
        PlotContainer.destroy()
