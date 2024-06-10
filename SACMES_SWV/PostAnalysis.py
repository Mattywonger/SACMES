from GlobalVariables import *
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import DataNormalization
import WaitTime
import TextFileExport
from tkinter import Listbox
import PostAnalysis
from tkinter import filedialog

class PostAnalysis(tk.Frame):
    def __init__(self, parent, container):
        global analysis_complete

        ############################
        ### Class-wide variables ###
        ############################
        self.parent = parent
        self.container = container

        #-- global boolean to control activation of this class --#
        analysis_complete = False
        self.ExportTopLevelExists = False

        #-- once completion value == electrode_count, analysis_complete --#
        #-- will be changed from False to True                          --#
        self.completion_value = 0

        #--- Check for the presence of high and low frequencies ---#
        if frequency_list[-1] > cutoff_frequency:
            self.High = True
        else:
            self.High = False

        if frequency_list[0] <= cutoff_frequency:
            self.Low = True
        else:
            self.Low = False

        ##########################################
        ### Initialize the Post Analysis Frame ###
        ##########################################
        self._initialize_frame()

    def _initialize_frame(self):

        ###################################################
        ### Initialize the Frame and create its Widgets ###
        ###################################################
        tk.Frame.__init__(self, self.parent)             # initialize the frame

        self.Title = ttk.Label(self, text = 'Post Analysis', font=('Verdana', 18)).grid(row=0,column=0,columnspan=2)

        DataAdjustmentFrame = tk.Frame(self, relief='groove',bd=3)
        DataAdjustmentFrame.grid(row=1,column=0,columnspan=2,pady=5, ipadx=50, padx=2, sticky = 'ns')

        NormalizationFrame = tk.Frame(DataAdjustmentFrame)
        NormalizationFrame.grid(row=1,column=0,pady=5)

        #--- Real-time Normalization Variable ---#
        SetPointNormLabel = ttk.Label(NormalizationFrame, text = 'Set Normalization Point', font=('Verdana', 10)).grid(row=0,column=0,pady=5)
        NormalizationVar = tk.StringVar()
        NormString = str(NormalizationPoint)
        NormalizationVar.set(NormString)
        self.SetPointNorm = tk.Entry(NormalizationFrame, textvariable = NormalizationVar, width=8)
        self.SetPointNorm.grid(row=1,column=0,pady=5)
        SetPointNorm = self.SetPointNorm

        #--- Button to apply any changes to the normalization variable ---#
        NormalizeButton = ttk.Button(NormalizationFrame, text='Apply Norm', command = lambda: self.PostAnalysisNormalization(), width=10)
        NormalizeButton.grid(row=2,column=0)
        self.NormWarning = ttk.Label(NormalizationFrame,text='',foreground='red',font=('Verdana', 10))
        NormWarning = self.NormWarning

        if len(frequency_list) > 1:

            self.FrequencyFrame = tk.Frame(DataAdjustmentFrame, relief = 'groove', bd=3)
            self.FrequencyFrame.grid(row=2,column=0,pady=10,padx=3,ipady=2)

            #--- Drift Correction Title ---#
            self.KDM_title = ttk.Label(self.FrequencyFrame, text = 'Drift Correction', font=('Verdana', 11))
            self.KDM_title.grid(row=0,column=0,columnspan=3,pady=1,padx=5)

            #--- High Frequency Selection for KDM and Ratiometric Analysis ---#
            self.HighFrequencyLabel = ttk.Label(self.FrequencyFrame, text='High Frequency',font=('Verdana', 10))
            self.HighFrequencyLabel.grid(row=1,column=1,pady=5,padx=5)

            self.HighFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            self.HighFrequencyEntry.insert('end', HighFrequency)
            self.HighFrequencyEntry.grid(row=2,column=1,padx=5)

            #--- Low Frequency Selection for KDM and Ratiometric Analysis ---#
            self.LowFrequencyLabel = ttk.Label(self.FrequencyFrame, text='Low Frequency',font=('Verdana', 10))
            self.LowFrequencyLabel.grid(row=1,column=0,pady=5,padx=5)

            self.LowFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencyEntry.insert('end', LowFrequency)
            self.LowFrequencyEntry.grid(row=2,column=0,padx=5)

            self.LowFrequencyOffsetLabel = ttk.Label(self.FrequencyFrame, text = 'Low Frequency\n Offset', font=('Verdana', 10)).grid(row=3,column=0,pady=2,padx=2)
            self.LowFrequencyOffset = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencyOffset.insert('end',LowFrequencyOffset)
            self.LowFrequencyOffset.grid(row=4,column=0,padx=2,pady=2)

            self.LowFrequencySlopeLabel = ttk.Label(self.FrequencyFrame, text = 'Low Frequency\n Slope Manipulation', font=('Verdana', 10)).grid(row=3,column=1,pady=2,padx=2)
            self.LowFrequencySlope = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencySlope.insert('end',LowFrequencySlope)
            self.LowFrequencySlope.grid(row=4,column=1,padx=2,pady=2)

            self.ApplyFrequencies = ttk.Button(self.FrequencyFrame, text='Apply Frequencies', command = lambda: self.PostAnalysisKDM())
            self.ApplyFrequencies.grid(row=5,column=0,columnspan=2,pady=5,padx=5)


        self.RedrawButton = ttk.Button(DataAdjustmentFrame, text = 'Redraw Figures', command = lambda: self._draw(), width=12)
        self.RedrawButton.grid(row=3,column=0,pady=7)


        DataAdjustmentFrame.columnconfigure(0,weight=1)
        row_value = 3

        self.DataExportFrame = tk.Frame(self,relief='groove',bd=2)
        self.DataExportFrame.grid(row=row_value,column=0,pady=5,ipady=5)

        self.DataExportSettings = ttk.Button(self.DataExportFrame, text = 'Data Export Settings', command = lambda: self.DataExportTopLevel)

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

        ExportSettings = tk.Frame(self)
        ExportSettings.grid(row=row_value,column=0,columnspan=2,pady=5,ipady=10)

        ExportSettingsButton = ttk.Button(ExportSettings, text = 'Post Analysis Data Export', command = self.DataExportTopLevel)
        ExportSettingsButton.grid(row=0, column=0,padx=5)

        ExportSettings.columnconfigure(1,weight=1)
        ExportSettings.rowconfigure(1,weight=1)

        row_value += 1

        #--- Reset ---#
        Reset = ttk.Button(self, text='Reset', style='Fun.TButton', command = lambda: self._reset())
        Reset.grid(row=row_value, column=1,pady=5, padx=5)

        #--- Quit ---#
        QuitButton = ttk.Button(self, text='Quit Program',command=lambda: quit())
        QuitButton.grid(row=row_value,column=0,pady=5)

        for row in range(row_value):
            row += 1
            self.rowconfigure(row, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)



    def _analysis_finished(self):
        global analysis_complete

        self.completion_value += 1

        if self.completion_value == electrode_count:
            analysis_complete = True

            #####################################
            ### Raise the Post Analysis Frame ###
            #####################################
            ShowFrames[PostAnalysis].tkraise()

    def _adjust_data(self):

        ###################################
        ### Renormalize all of the data ###
        ###################################
        NormalizationIndex = NormalizationPoint - 1

        if NormalizationPoint <= numFiles:
            for num in range(electrode_count):
                for count in range(len(frequency_list)):
                    normalized_data_list[num][count] = [(idx/data_list[num][count][NormalizationIndex]) for idx in data_list[num][count]]
                    ##################################################
                    ## If the frequency is below cutoff_frequency,  ##
                    ## add the baseline Offset                      ##
                    ##################################################
                    if frequency_list[count] == HighLowList['Low']:
                        for index in range(numFiles):

                            ##########################
                            ## Calculate the offset ##
                            ##########################
                            sample = sample_list[index]
                            file = file_list[index]

                            if XaxisOptions == 'Experiment Time':
                                Offset = (sample*LowFrequencySlope) + LowFrequencyOffset
                            elif XaxisOptions == 'File Number':
                                Offset = (file*LowFrequencySlope) + LowFrequencyOffset

                            offset_normalized_data_list[num][index] = normalized_data_list[num][count][index] + Offset

        DataNormalization.ResetRatiometricData()

        self.NormWarning['foreground'] = 'green'
        self.NormWarning['text'] = 'Normalized to File %d' % NormalizationPoint

        if SaveVar:
            TextFileExport.TxtFileNormalization()

        ### Draw the readjusted data
        self._draw()


    def _draw(self):
        global peak, norm

        for num in range(electrode_count):

            ## get the figure for the electrode ##
            fig, ax = figures[num]

            subplot_count = 0
            for count in range(len(frequency_list)):

                frequency = frequency_list[count]

                ###################################
                ### Set the units of the X-axis ###
                ###################################
                if XaxisOptions == 'Experiment Time':
                    Xaxis = sample_list
                elif XaxisOptions == 'File Number':
                    Xaxis = file_list

                ################################################################
                ### Acquire the artists for this electrode at this frequency ###
                ### and get the data that will be visualized                 ###
                ################################################################
                plots = plot_list[num][count]                              # 'count' is the frequency index value

                ##########################
                ### Visualize the data ###
                ##########################

                #--- Peak Height ---#

                data = data_list[num][count]                     # 'num' is the electrode index value

                if frequency_list[count] == HighLowList['Low']:
                    NormalizedDataList = offset_normalized_data_list[num]
                else:
                    NormalizedDataList = normalized_data_list[num][count]

                ### Draw new data ###
                ax[1,subplot_count].clear()
                peak = ax[1,subplot_count].plot(Xaxis,data,'bo',markersize=1)

                ax[2,subplot_count].clear()
                norm = ax[2,subplot_count].plot(Xaxis,NormalizedDataList,'ko',markersize=1)

                #####################
                ## Set the Y Label ##
                #####################
                ax[0,0].set_ylabel('Current\n(µA)',fontweight='bold')
                if SelectedOptions == 'Peak Height Extraction':
                    ax[1,0].set_ylabel('Peak Height\n(µA)',fontweight='bold')
                elif SelectedOptions == 'Area Under the Curve':
                    ax[1,0].set_ylabel('AUC (a.u.)',fontweight='bold')
                ax[2,0].set_ylabel('Normalized', fontweight='bold')


                ### If necessary, redraw ratiometric data ###
                if len(frequency_list) > 1:
                    ratio_fig, ratio_ax = ratiometric_figures[num]

                    norm = [X*100 for X in normalized_ratiometric_data_list[num]]
                    KDM = [X*100 for X in KDM_list[num]]

                    #-- Clear the Plots --#
                    ratio_ax[0,0].clear()
                    ratio_ax[0,1].clear()

                    #-- Redraw the titles --#
                    ratio_ax[0,0].set_title('Normalized Ratio')
                    ratio_ax[0,1].set_title('KDM')
                    ratio_ax[0,0].set_ylabel('% Signal', fontweight='bold')
                    ratio_ax[0,1].set_ylabel('% Signal', fontweight='bold')

                    #-- Plot the Data --#
                    ratio_ax[0,0].plot(Xaxis,norm,'ro',markersize=1)            # normalized ratio of high and low freq'
                    ratio_ax[0,1].plot(Xaxis,KDM,'ro',markersize=1)

                subplot_count += 1

            fig.canvas.draw_idle()

            if len(frequency_list) > 1:

                ratio_fig.canvas.draw_idle()

    #########################################################
    ### Post Analysis adjustment of High and Low          ###
    ### frequencies used for KDM and ratiometric analysis ###
    #########################################################
    def PostAnalysisKDM(self):
        global HighFrequency, LowFrequencyOffset, LowFrequencySlope, LowFrequency, HighLowList, LowFrequencyEntry, HighFrequencyEntry, ExistVar, WrongFrequencyLabel, RatioMetricCheck

        HighFrequency = int(self.HighFrequencyEntry.get())
        LowFrequency = int(self.LowFrequencyEntry.get())

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
            HighLowList['High'] = HighFrequency
            HighLowList['Low'] = LowFrequency

            DataNormalization.ResetRatiometricData()

            #--- if a warning label exists, forget it ---#
            if ExistVar:
                WrongFrequencyLabel.grid_forget()

            #--- Tells RawVoltammogramVisualization to revisualize data for new High and Low frequencies ---#
            if not RatioMetricCheck:
                RatioMetricCheck = True

            self._adjust_data()


    #--- Function for Real-time Normalization ---#
    def PostAnalysisNormalization(self):
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


    ######################################################
    ### Data Export TopWindow and Associated Functions ###
    ######################################################

    def DataExportTopLevel(self):

        self.win = tk.Toplevel()
        self.win.wm_title("Post Analysis Data Export")

        self.ExportTopLevelExists = True

        ##############################################
        ### Pack all of the widgets into the frame ###
        ##############################################

        #--- File Path ---#
        self.SelectFilePath = ttk.Button(self.win, style = 'On.TButton', text = '%s' % DataFolder, command = lambda: self.FindFile(self.parent))
        self.SelectFilePath.grid(row=0,column=0,columnspan=2)

        self.NoSelectedPath = ttk.Label(self.win, text = 'No File Path Selected', foreground = 'red')
        self.PathWarningExists = False               # tracks the existence of a warning label

        #--- File Handle Input ---#
        HandleLabel = ttk.Label(self.win, text='Exported File Handle:', font=('Verdana', 11))
        HandleLabel.grid(row=4,column=0,columnspan=2)
        self.filehandle = tk.Entry(self.win)
        self.filehandle.insert('end', FileHandle)
        self.filehandle.grid(row=5,column=0,columnspan=2,pady=5)

        self.ElectrodeLabel = ttk.Label(self.win, text='Select Electrodes:', font=('Verdana', 11))
        self.ElectrodeLabel.grid(row=10,column=0, sticky = 'nswe')
        self.ElectrodeCount = Listbox(self.win, relief='groove', exportselection=0, width=10, font=('Verdana', 11), height=6, selectmode = 'multiple', bd=3)
        self.ElectrodeCount.bind('<<ListboxSelect>>',self.ElectrodeCurSelect)
        self.ElectrodeCount.grid(row=11,column=0,padx=10,sticky='nswe')
        for electrode in electrode_list:
            self.ElectrodeCount.insert('end', electrode)

        #--- ListBox containing the frequencies given on line 46 (InputFrequencies) ---#

        self.FrequencyLabel = ttk.Label(self.win, text='Select Frequencies', font= LARGE_FONT)
        self.FrequencyLabel.grid(row=10,column=1,padx=10)
        self.FrequencyList = Listbox(self.win, relief='groove', exportselection=0, width=5, font=('Verdana', 11), height = 5, selectmode='multiple', bd=3)
        self.FrequencyList.bind('<<ListboxSelect>>',self.FrequencyCurSelect)
        self.FrequencyList.grid(row=11,column=1,padx=10,sticky='nswe')
        for frequency in frequency_list:
            self.FrequencyList.insert('end', frequency)

        ExportData = ttk.Button(self.win, text = 'Export Data', command = lambda: self.PostAnalysisDataExport())
        ExportData.grid(row=15,column=0,columnspan=2)

        CloseButton = ttk.Button(self.win, text = 'Close', command = lambda: self.win.destroy())
        CloseButton.grid(row=16,column=0,columnspan=2,pady=10)


    # def ElectrodeCurSelect(self,event):

    #     ###################################################
    #     ## electrode_list: list; ints                    ##
    #     ## electrode_dict: dict; {electrode: index}      ##
    #     ## electrode_count: int                          ##
    #     ###################################################
    #     print(event)
        
    #     self.electrode_list = [self.ElectrodeCount.get(idx) for idx in self.ElectrodeCount.curselection()]
    #     self.electrode_list = [int(electrode) for electrode in self.electrode_list]

    #     if electrode_count is 0:
    #         self.ElectrodeListExists = False
    #         self.ElectrodeLabel['foreground'] = 'red'

    #     elif electrode_count is not 0:
    #         self.ElectrodeListExists = True
    #         self.ElectrodeLabel['foreground'] = 'black'

    #--- Frequency Selection ---#
    # def FrequencyCurSelect(self):
    #     global frequency_list, frequency_dict, LowFrequency, HighFrequency

    #     self.frequency_list = [self.FrequencyList.get(idx) for idx in self.FrequencyList.curselection()]

    #     if len(frequency_list) is not 0:

    #         self.FrequencyListExists = True
    #         self.FrequencyLabel['foreground'] = 'black'

    #         for var in frequency_list:
    #             var = int(var)

    #     elif len(frequency_list) is 0:
    #         self.FrequencyListExists = False
    #         self.FrequencyLabel['foreground'] = 'red'


    def FindFile(self, parent):
        global FilePath, ExportPath, FoundFilePath

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
            ExportPath = '/'.join(ExportPath)
            ExportPath = ''.join(ExportPath + '/')
            ## Indicates that the user has selected a File Path ###
            FoundFilePath = True

            if self.PathWarningExists:
                self.NoSelectedPath['text'] = ''
                self.NoSelectedPath.grid_forget()

        except:
            FoundFilePath = False
            self.NoSelectedPath.grid(row=1,column=0,columnspan=4)
            self.PathWarningExists = True
            self.SelectFilePath['style'] = 'Off.TButton'
            self.SelectFilePath['text'] = ''


    def PostAnalysisDataExport(self):
        global ExportFilePath

        FileHandle = str(self.filehandle.get())
        ExportFilePath = ''.join(ExportPath + FileHandle)

        post_analysis_export = TextFileExport(electrodes=self.electrode_list, frequencies=self.frequency_list)
        post_analysis_export.TxtFileNormalization(electrodes=self.electrode_list, frequencies=self.frequency_list)


    def _reset(self):
        global HighAlreadyReset, LowAlreadyReset, AlreadyInitiated, PoisonPill, key, container, analysis_complete
        from Mainwindow import InputFrame
        self.completion_value = 0
        analysis_complete = False

        if self.ExportTopLevelExists is True:
            self.win.destroy()

        key = 0
        PoisonPill = True
        AlreadyInitiated = False # reset the start variable

        if self.High:
            HighAlreadyReset = True

        if self.Low:
            LowAlreadyReset = True

        # Raise the initial user input frame
        self.show_frame(InputFrame)
        self.close_frame(PostAnalysis)

        ## Take resize weight away from the Visualization Canvas
        container.columnconfigure(1, weight=0)


    #--- Function to switch between visualization frames ---#
    def show_plot(self, frame):
        frame.tkraise()

    def show_frame(self, cont):

        frame = ShowFrames[cont]
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