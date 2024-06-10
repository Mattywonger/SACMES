from WaitTime import WaitTime
from Track import Track
from Init_cont_canvas import InitializeContinuousCanvas
from DataNormalization import DataNormalization
from PostAnalysis import PostAnalysis
from ContinuousManipulationFrame import ContinuousScanManipulationFrame
from init_freq_canvas import InitializeFrequencyMapCanvas
from FrequencyManipulation import FrequencyMapManipulationFrame
from helper import _retrieve_file
import os
import tkinter as tk
from tkinter import ttk
#from GlobalVariables import *

class CheckPoint():
    def __init__(self, parent, controller,GUI_variables):
        global total_columns

        #-- Check to see if the user's settings are accurate
        #-- Search for the presence of the files. If they exist,
        #-- initialize the functions and frames for Real Time Analysis
        print("Entered CheckPoint")
        self.win = tk.Toplevel()
        self.win.wm_title("CheckPoint")

        title = ttk.Label(self.win, text = 'Searching for files...',font=('Verdana', 18)).grid(row=0,column=0,columnspan=2,pady=10,padx=10,sticky='news')

        self.parent = parent
        self.win.transient(self.parent)
        self.win.attributes('-topmost', 'true')
        self.controller = controller


        
        #Unpacking GUI variables list:
        method,electrode_list, mypath, frequency_list, e_var, electrode_count, InjectionVar, XaxisOptions, NormalizationVault, HighLowList, SampleRate, frequency_dict, q, SelectedOptions, electrode_dict, numFiles, InjectionPoint, resize_interval,byte_limit,handle_variable,extension,delimiter, current_column, spacing_index,ShowFrames,SaveVar = GUI_variables
        self.method = method
        self.electrode_list = electrode_list
        self.mypath = mypath
        self.frequency_list = frequency_list
        self.e_var = e_var
        self.electrode_count = electrode_count
        self.InjectionVar = InjectionVar
        self.XaxisOptions = XaxisOptions
        self.NormalizationVault = NormalizationVault
        self.HighLowList = HighLowList
        self.SampleRate = SampleRate
        self.frequency_dict = frequency_dict
        self.q = q
        self.SelectedOptions = SelectedOptions
        self.electrode_dict = electrode_dict
        self.numFiles = numFiles
        self.InjectionPoint = InjectionPoint
        self.resize_interval = resize_interval
        self.byte_limit = byte_limit
        self.handle_variable = handle_variable
        self.extension = extension
        self.delimiter = delimiter
        self.current_column = current_column
        self.spacing_index = spacing_index
        self.ShowFrames = ShowFrames
        self.SaveVar = SaveVar








        print(self.method)

        row_value = 1
        self.frame_dict = {}
        self.label_dict = {}
        self.already_verified = {}
        for electrode in electrode_list:
            electrode_label = ttk.Label(self.win, text = 'E%s' % electrode,font=('Verdana', 11)).grid(row=row_value,column=0,pady=5,padx=5)
            frame = tk.Frame(self.win, relief='groove',bd=5)
            frame.grid(row = row_value,column=1,pady=5,padx=5)
            self.frame_dict[electrode] = frame
            self.label_dict[electrode] = {}
            self.already_verified[electrode] = {}
            row_value += 1

            column_value = 0
            if self.method == 'Continuous Scan':
                for frequency in frequency_list:
                    label = ttk.Label(frame, text = '%sHz' % str(frequency), foreground = 'red')
                    label.grid(row=0,column=column_value,padx=5,pady=5)
                    self.label_dict[electrode][frequency] = label
                    self.already_verified[electrode][frequency] = False
                    column_value += 1

            elif self.method == 'Frequency Map':
                electrode_label = ttk.Label(frame, text = 'E%s' % electrode,font=('Verdana', 18))
                electrode_label.grid(row=row_value,column=column_value,pady=5,padx=5)
                self.label_dict[electrode][frequency_list[0]] = electrode_label
                self.already_verified[electrode][frequency_list[0]] = False

                if column_value == 1:
                    column_value = 0
                    row_value += 1
                else:
                    column_value = 1
        
        self.stop = ttk.Button(self.win, text = 'Stop', command = self.stop)
        self.stop.grid(row=row_value, column=0,columnspan=2,pady=5)
        self.StopSearch = False

        self.num = 0
        self.count = 0
        self.analysis_count = 0
        self.analysis_limit = self.electrode_count * len(self.frequency_list)
        self.electrode_limit = self.electrode_count - 1
        self.frequency_limit = len(self.frequency_list) - 1

        self.controller.after(50,self.verify)

    def verify(self):

        print("Entered verify")

        self.electrode = self.electrode_list[self.num]
        
        if not self.StopSearch:
        
            if self.method == 'Continuous Scan':
                for frequency in self.frequency_list:
                    print('e_var ' + str(self.e_var))
                    filename, filename2, filename3, filename4 = _retrieve_file(1,self.electrode,frequency,self.method,self.e_var,self.handle_variable,self.extension)
                    print('The file names are\n')
                    print(filename, filename2, filename3, filename4)
                    
                    myfile = self.mypath + filename               ### path of your file
                    myfile2 = self.mypath + filename2
                    myfile3 = self.mypath + filename3
                    myfile4 = self.mypath + filename4

                    try:
                        ### retrieves the size of the file in bytes
                        mydata_bytes = os.path.getsize(myfile)
                    except:
                        try:
                            mydata_bytes = os.path.getsize(myfile2)
                            myfile = myfile2
                        except:
                            try:
                                mydata_bytes = os.path.getsize(myfile3)
                                myfile = myfile3
                            except:
                                try:
                                    mydata_bytes = os.path.getsize(myfile4)
                                    myfile = myfile4
                                except Exception as e:
                                    print(f"An exception occurred: {e}")
                                    mydata_bytes = 1
                    
                    print('Searching for file %s' % myfile)

                    print("my data bytes : " + str(mydata_bytes))
                    print("byte limit : " + str(self.byte_limit))
                    if mydata_bytes > self.byte_limit:

                        if self.e_var == 'single':
                            check_ = self.verify_multi(myfile)
                        else:
                            check_ = True

                        print('the value for _check is ' + str(check_))
                        if check_:
                            if not self.already_verified[self.electrode][frequency]:
                                self.already_verified[self.electrode][frequency] = True
                                if not self.StopSearch:
                                    self.label_dict[self.electrode][frequency]['foreground'] = 'green'
                                    self.analysis_count += 1
                        
                        print('the self analysis count is ' + str(self.analysis_count))

                        print ('the self analysis_limit is ' + str(self.analysis_limit))

                        if self.analysis_count == self.analysis_limit:
                            if not self.StopSearch:
                                self.StopSearch = True
                                self.win.destroy()

                                self.controller.after(10,self.proceed)

                if self.num < self.electrode_limit:
                    self.num += 1

                else:
                    self.num = 0

                if self.analysis_count < self.analysis_limit:
                    if not self.StopSearch:
                        self.controller.after(100,self.verify)


            elif self.method == 'Frequency Map':

                frequency = self.frequency_list[0]

                filename, filename2, filename3, filename4, filename5, filename6 = _retrieve_file(1,self.electrode,frequency)

                myfile = self.mypath + filename               ### path of your file
                myfile2 = self.mypath + filename2
                myfile3 = self.mypath + filename3
                myfile4 = self.mypath + filename4
                myfile5 = self.mypath + filename5
                myfile6 = self.mypath + filename6

                try:
                     ### retrieves the size of the file in bytes
                    mydata_bytes = os.path.getsize(myfile)
                except:
                    try:
                        mydata_bytes = os.path.getsize(myfile2)
                        myfile = myfile2
                    except:
                        try:
                            mydata_bytes = os.path.getsize(myfile3)
                            myfile = myfile3
                        except:
                            try:
                                mydata_bytes = os.path.getsize(myfile4)
                                myfile = myfile4
                            except:
                                try:
                                    mydata_bytes = os.path.getsize(myfile5)
                                    myfile = myfile5
                                except:
                                    try:
                                        mydata_bytes = os.path.getsize(myfile6)
                                        myfile = myfile6
                                    except:
                                        mydata_bytes = 1

                if mydata_bytes > self.byte_limit:

                    if self.e_var == 'single':
                        check_ = self.verify_multi(myfile)
                    else:
                        check_ = True

                    if check_:
                        if not self.already_verified[self.electrode][frequency]:
                            self.already_verified[self.electrode][frequency] = True
                            if not self.StopSearch:
                                self.label_dict[self.electrode][frequency]['foreground'] = 'green'
                                self.analysis_count += 1

                    if self.analysis_count == self.electrode_count:
                        if not self.StopSearch:
                            self.StopSearch = True
                            self.win.destroy()

                            self.controller.after(10,self.proceed)

                if self.num < self.electrode_limit:
                    self.num += 1
                else:
                    self.num = 0

                if self.analysis_count < self.analysis_limit:
                    if not self.StopSearch:
                        self.controller.after(200,self.verify)


    def verify_multi(self, myfile):
        global total_columns

        print('entered verify_multi')
        # changing the column index
        #---Set the electrode index value---#
        check_ = False
        try:
            #---Preallocate Potential and Current lists---#
            with open(myfile,'r',encoding='utf-8') as mydata:
                encoding = 'utf-8'

        except:

            #---Preallocate Potential and Current lists---#
            with open(myfile,'r',encoding='utf-16') as mydata:
                encoding = 'utf-16'


        with open(myfile,'r',encoding=encoding) as mydata:

            for line in mydata:
                # delete any spaces that may come before the first value #
                check_split_list = line.split(self.delimiter)
                while True:
                    if check_split_list[0] == '':
                        del check_split_list[0]
                    else:
                        break

                # delete any tabs that may come before the first value #
                while True:
                    if check_split_list[0] == ' ':
                        del check_split_list[0]
                    else:
                        break

                check_split = check_split_list[0]
                check_split = check_split.replace(',','')
                try:
                    check_split = float(check_split)
                    check_split = True
                except:
                    check_split = False

                if check_split:
                    total_columns = len(check_split_list)
                    check_ = True
                    break

        print('the value for _check is:' + str(check_))                 
        if check_:
            list_val = self.current_column + (self.electrode-1)*self.spacing_index

            if list_val > total_columns:
                return False

            else:
                return True

        else:
            print('\nverify_multi: could not find a line\nthat began with an integer\n')
            return False



    def proceed(self):
        global wait_time, track, initialize, data_normalization, post_analysis
        print("Entered proceed")
        self.win.destroy()

        ##############################
        ### Syncronization Classes ###
        ##############################
        wait_time = WaitTime()
        track = Track(self.numFiles,self.electrode_count,self.method,self.HighLowList,self.SaveVar)

        ######################################################
        ### Matplotlib Canvas, Figure, and Artist Creation ###
        ######################################################
        if self.method == 'Continuous Scan':
            initialize = InitializeContinuousCanvas()

            #################################
            ### Data Normalization Module ###
            #################################
            data_normalization = DataNormalization()

            ############################
            ### Post Analysis Module ###
            ############################
            post_analysis = PostAnalysis(self.parent, self.controller)
            self.ShowFrames[PostAnalysis] = post_analysis
            post_analysis.grid(row=0, column=0, sticky = 'nsew')

            ################################################
            ### Initialize the RealTimeManipulationFrame ###
            ################################################
            frame = ContinuousScanManipulationFrame(self.controller,self.container, self)
            self.ShowFrames[self.method] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        elif self.method == 'Frequency Map':

            initialize = InitializeFrequencyMapCanvas()

            ################################################
            ### Initialize the RealTimeManipulationFrame ###
            ################################################
            frame = FrequencyMapManipulationFrame(self.controller,self.container, self)
            self.ShowFrames[self.method] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        #---When initliazed, raise the Start Page and the plot for electrode one---#
        self.show_frame(self.method)   
        print("The length of plotvalues is" + str(len(PlotValues)))           # raises the frame for real-time data manipulation
        self.show_plot(PlotValues[0])           # raises the figure for electrode 1



    def stop(self):
        self.StopSearch = True
        self.win.destroy()

    #--- Function to switch between visualization frames ---#
    def show_plot(self, frame):
        frame.tkraise()

    def show_frame(self, cont):

        frame = self.ShowFrames[cont]
        frame.tkraise()




