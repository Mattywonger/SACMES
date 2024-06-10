import tkinter as tk
from Cont_visualization import ContinuousScanVisualizationFrame
from TextFileExport import TextFileExport
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from helper import _get_listval
from helper import _retrieve_file
from helper import ReadData
import Config
import os
import numpy as np
from scipy.signal import *
from GlobalVariables import *

handle_variable,e_var,PHE_method,InputFrequencies,electrodes = Config.globalvar_config()
high_xstart, high_xend, low_xstart, low_xend = None, None, None, None
sg_window,sg_degree,polyfit_deg,cutoff_frequency = Config.regressionvar_config()
key,search_lim,PoisonPill,FoundFilePath,ExistVar,AlreadyInitiated,HighAlreadyReset,LowAlreadyReset,analysis_complete= Config.checkpoint_parameter()
delimiter,extension,current_column,current_column_index,voltage_column,voltage_column_index,spacing_index,byte_limit,byte_index = Config.data_extraction_parameter()
LowFrequencyOffset,LowFrequencySlope = Config.low_freq_parameter()
HUGE_FONT,LARGE_FONT,MEDIUM_FONT,SMALL_FONT = Config.font_specification()

class InitializeContinuousCanvas():
    def __init__(self):
        global text_file_export, electrode_count, offset_normalized_data_list, anim, Frame, FrameReference, FileHandle, PlotContainer, KDM_list, empty_ratiometric_plots, ratiometric_plots, ratiometric_figures, normalized_ratiometric_data_list, normalized_data_list,frequency_list, data_list, plot_list, EmptyPlots, file_list, figures, frame_list, sample_list, Plot, PlotFrames, PlotValues

        ##############################################
        ### Generate global lists for data storage ###
        ##############################################

        self.length = len(frequency_list)
        electrode_count = int(electrode_count)

        #--- Animation list ---#
        anim = []

        #--- Figure lists ---#
        figures = []
        ratiometric_figures = []

        ############################################
        ### Create global lists for data storage ###
        ############################################
        data_list = [0]*electrode_count                             # Peak Height/AUC data (after smoothing and polynomial regression)
        avg_data_list = []                                          # Average Peak Height/AUC across all electrodes for each frequency
        std_data_list = []                                          # standard deviation between electrodes for each frequency
        normalized_data_list = [0]*electrode_count                  # normalized data
        offset_normalized_data_list = [0]*electrode_count           # to hold data with low frequency offset
        normalized_ratiometric_data_list = []                       # uses ratio of normalized peak heights
        KDM_list = []                                               # hold the data for kinetic differential measurements

        for num in range(electrode_count):
            data_list[num] = [0]*self.length                        # a data list for each eletrode
            normalized_data_list[num] = [0]*self.length
            offset_normalized_data_list[num] = [0]*numFiles
            for count in range(self.length):                        # a data list for each frequency for that electrode
                data_list[num][count] = [0]*numFiles                # use [0]*numFiles to preallocate list space
                normalized_data_list[num][count] = [0]*numFiles


        for num in range(electrode_count):
            normalized_ratiometric_data_list.append([])
            KDM_list.append([])

        #--- Lists of Frames and Artists ---#
        plot_list = []
        ratiometric_plots = []
        empty_ratiometric_plots = []
        frame_list = []

        #--- Misc Lists ---#
        file_list = []          # Used for len(file_list)
        sample_list = []        # For plotting Peak Height vs. sample rate


        ######################################################
        ### Create a figure and artists for each electrode ###
        ######################################################

        print("The electrode_count is" + str(electrode_count))
        for num in range(electrode_count):
            electrode = electrode_list[num]
            figure = self.MakeFigure(electrode,frame_list)
            figures.append(figure)

            if len(frequency_list) > 1:
                ratio_figure = self.MakeRatiometricFigure(electrode)
                ratiometric_figures.append(ratio_figure)
        
        print("Framelist right after for loop is\n :" + str(len(frame_list)))


        #####################################################
        ### Create a frame for each electrode and embed   ###
        ### within it the figure containing its artists   ###
        #####################################################

        PlotFrames = {}                # Dictionary of frames for each electrode
        PlotValues = []                # create a list of frames

        #--- Create a container that can be created and destroyed when Start() or Reset() is called, respectively ---#
        PlotContainer = tk.Frame(container, relief = 'groove', bd = 3)
        PlotContainer.grid(row=0,column=1, sticky = 'nsew')
        PlotContainer.rowconfigure(0, weight=1)
        PlotContainer.columnconfigure(0, weight=1)

        frame_count = 0
        FileLabelList = []
        for electrode_frame in frame_list:                # Iterate through the frame of each electrode

            #--- create an instance of the frame and append it to the global frame dictionary ---#
            FrameReference = ContinuousScanVisualizationFrame(electrode_frame, frame_count, PlotContainer, self)            # PlotContainer is the 'parent' frame
            FrameReference.grid(row=0,column=0,sticky='nsew')      # sticky must be 'nsew' so it expands and contracts with resize
            PlotFrames[electrode_frame] = FrameReference

            frame_count += 1
        
        print("The framecount is" + str(frame_count))

        #--- Create a list containing the Frame objects for each electrode ---#
        for reference, frame in PlotFrames.items():
            PlotValues.append(frame)
        
        print("Immediately after the for loop, the length is :" + str(len(PlotValues)))


        #################################
        ### Initiate .txt File Export ###
        #################################

        #--- If the user has indicated that text file export should be activated ---#
        if SaveVar:
            print('Initializing Text File Export')
            text_file_export = TextFileExport()

        else:
            text_file_export = None
            print('Text File Export Deactivated')


    ############################################
    ### Create the figure and artist objects ###
    ############################################
    def MakeFigure(self, electrode,frame_list):
        global list_val, EmptyPlots, plot_list, SampleRate, numFiles

        print('Make Figure: Continuous Scan')
        try:
            ########################
            ### Setup the Figure ###
            ########################
            length = self.length
            fig, ax = plt.subplots(nrows=3,ncols=length,squeeze=False,figsize=(9,4.5))    ## figsize=(width, height)
            plt.subplots_adjust(bottom=0.1,hspace=0.6,wspace=0.3)         ### adjust the spacing between subplots


            # changing the column index
            #---Set the electrode index value---#
            if e_var == 'single':
                list_val = current_column_index + (electrode-1)*spacing_index
                ## changing
            elif e_var == 'multiple':
                list_val = current_column_index

            #######################
            ### Set axis labels ###
            #######################

            ax[0,0].set_ylabel('Current\n(µA)',fontweight='bold')
            if SelectedOptions == 'Peak Height Extraction':
                ax[1,0].set_ylabel('Peak Height\n(µA)',fontweight='bold')
            elif SelectedOptions == 'Area Under the Curve':
                ax[1,0].set_ylabel('AUC (a.u.)',fontweight='bold')
            ax[2,0].set_ylabel('Normalized', fontweight='bold')

            ##########################################
            ### Set suplot axes for each frequency ###
            ##########################################
            electrode_plot = []
            subplot_count = 0
            for freq in range(length):
                frequency = frequency_list[freq]
                ax[0,subplot_count].set_xlabel('Potential (V)')

                #--- if the resize interval is larger than the number of files, ---#
                #--- make the x lim the number of files (& vice versa)          ---#
                if resize_interval > numFiles:
                    xlim_factor = numFiles
                elif resize_interval is None:
                    xlim_factor = numFiles
                elif resize_interval <= numFiles:
                    xlim_factor = resize_interval

                if XaxisOptions == 'Experiment Time':
                    ax[1,subplot_count].set_xlim(0,(xlim_factor*SampleRate)/3600+(SampleRate/7200))
                    ax[2,subplot_count].set_xlim(0,(xlim_factor*SampleRate)/3600+(SampleRate/7200))
                    ax[2,subplot_count].set_xlabel('Time (h)')

                elif XaxisOptions == 'File Number':
                    ax[1,subplot_count].set_xlim(-0.05,xlim_factor+0.1)
                    ax[2,subplot_count].set_xlim(-0.05,xlim_factor+0.1)
                    ax[2,subplot_count].set_xlabel('File Number')


            #################################################################################
            #################################################################################
            ###       Analyze the first file and create the Y limits of the subplots      ###
            ###               depending on the data range of the first file               ###
            #################################################################################
                self.InitializeSubplots(ax, frequency, electrode, subplot_count)

            #################################################################################
            #################################################################################


                #---Set Subplot Title---#
                frequency = str(frequency)
                ax[0,subplot_count].set_title(''.join(frequency+' Hz'),fontweight='bold')

                #---Initiate the subplots---#
                # this assigns a Line2D artist object to the artist object (Axes)
                smooth, = ax[0, subplot_count].plot([], [], 'ko', markersize=2)
                regress, = ax[0,subplot_count].plot([],[],'r-')
                linear, = ax[0,subplot_count].plot([],[],'r-')

                peak, = ax[1,subplot_count].plot([],[],'ko',markersize=1)
                peak_injection, = ax[1,subplot_count].plot([],[],'bo',markersize=1)
                normalization, = ax[2,subplot_count].plot([],[],'ko',markersize=1)
                norm_injection, = ax[2,subplot_count].plot([],[],'ro',markersize=1)

                #--- shading for AUC ---#
                verts = [(0,0),*zip([],[]),(0,0)]
                poly = Polygon(verts, alpha = 0.5)
                ax[0,subplot_count].add_patch(poly)


                #####################################################
                ### Create a list of the primitive artists        ###
                ### (Line2D objects) that will be returned        ###
                ### to ElectrochemicalAnimation to be visualized  ###
                #####################################################

                # this is the list that will be returned as _drawn_artists to the Funcanimation class
                plots = [smooth,regress,peak,peak_injection,normalization,norm_injection,poly,linear]

                #--- And append that list to keep a global reference ---#
                electrode_plot.append(plots)        # 'plots' is a list of artists that are passed to animate
                electrode_frame = 'Electrode %s' % str(electrode)
                if electrode_frame not in frame_list:
                    frame_list.append(electrode_frame)

                #--- Create empty plots to return to animate for initializing---#
                EmptyPlots = [smooth,regress,peak,normalization]

                subplot_count += 1

            plot_list.append(electrode_plot)        # 'plot_list' is a list of lists containing 'plots' for each electrode

            #-- Return both the figure and the axes to be stored as global variables --#
            return fig, ax


        except:
            print('Error in MakeFigure')

    #################################################################
    ### Make Figures for Ratiometric Data                         ###
    ### (e.g. Kinetic Differential Measurement, Normalized Ratio) ###
    #################################################################
    def MakeRatiometricFigure(self, electrode):
        global EmptyRatioPlots, ratiometric_plots

        try:
            figure, axes = plt.subplots(nrows=1,ncols=2,squeeze=False,figsize=(8.5,1.85))
            plt.subplots_adjust(bottom=0.3,hspace=0.6,wspace=0.3)         ### adjust the spacing between subplots


            ###############################################################################
            ### If the number of files is less than the resize interval, make           ###
            ### the x-axis the length of numFiles. Elif the resize_interval is          ###
            ### smaller than numFiles, make the x-axis the length of the first interval ###
            ###############################################################################
            if resize_interval > numFiles:
                xlim_factor = numFiles
            elif resize_interval <= numFiles:
                xlim_factor = resize_interval

            ################################################
            ## Set the X and Y axes for the Ratriometric  ##
            ## Plots (KDM and Norm Ratio)                 ##
            ################################################
            axes[0,0].set_ylabel('% Signal', fontweight='bold')
            axes[0,1].set_ylabel('% Signal', fontweight='bold')


            if XaxisOptions == 'Experiment Time':
                axes[0,0].set_xlim(0,(xlim_factor*SampleRate)/3600+(SampleRate/7200))
                axes[0,1].set_xlim(0,(xlim_factor*SampleRate)/3600+(SampleRate/7200))
                axes[0,0].set_xlabel('Time (h)')
                axes[0,1].set_xlabel('Time (h)')

            elif XaxisOptions == 'File Number':
                axes[0,0].set_xlim(0,xlim_factor+0.1)
                axes[0,1].set_xlim(0,xlim_factor+0.1)
                axes[0,0].set_xlabel('File Number')
                axes[0,1].set_xlabel('File Number')

            axes[0,0].set_ylim(100*min_norm,100*max_norm)
            axes[0,1].set_ylim(100*ratio_min,100*ratio_max)
            axes[0,0].set_title('Normalized Ratio')
            axes[0,1].set_title('KDM')

            #####################################################
            ### Create the primitive artists (Line2D objects) ###
            ### that will contain the data that will be       ###
            #### visualized by ElectrochemicalAnimation       ###
            #####################################################
            norm_ratiometric_plot, = axes[0,0].plot([],[],'ro',markersize=1)            # normalized ratio of high and low freq's
            KDM, = axes[0,1].plot([],[],'ro',markersize=1)

            # if InjectionPoint =! None, these will
            # visualize the points after the injection
            norm_injection, = axes[0,0].plot([],[],'bo',markersize=1)
            KDM_injection, = axes[0,1].plot([],[],'bo',markersize=1)

            ratio_plots = [norm_ratiometric_plot,norm_injection,KDM,KDM_injection]
            ratiometric_plots.append(ratio_plots)

            empty_norm_ratiometric, = axes[0,0].plot([],[],'ro',markersize=1)
            empty_KDM, = axes[0,1].plot([],[],'ro',markersize=1)
            EmptyRatioPlots = [norm_ratiometric_plot,norm_injection,KDM,KDM_injection]

            return figure, axes

        except:
            print('\n ERROR IN MAKE RATIOMETRIC FIGURES \n')


    #####################################################################################
    ### Initalize Y Limits of each figure depending on the y values of the first file ###
    #####################################################################################
    def InitializeSubplots(self,ax,frequency,electrode,subplot_count):

        print('Initialize Subplots: Continuous Scan')

        self.list_val = _get_listval(electrode)

        frequency = int(frequency)

        try:

            filename, filename2, filename3, filename4 = _retrieve_file(1,electrode,frequency)

            myfile = mypath + filename               ### path of your file
            myfile2 = mypath + filename2
            myfile3 = mypath + filename3
            myfile4 = mypath + filename4

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
                            mydata_bytes = 1

            if mydata_bytes > byte_limit:
                print('Found File %s' % myfile)
                self.RunInitialization(myfile,ax,subplot_count, electrode, frequency)

            else:
                return False


        except:
            print('could not find file for electrode %d' % electrode)
            #--- If search time has not met the search limit keep searching ---#
            self.controller.after(1000, self.InitializeSubplots, ax, frequency, electrode, subplot_count)


    def RunInitialization(self, myfile, ax, subplot_count, electrode, frequency):
        global high_xstart, high_xend, low_xstart, low_xend

        try:
            #########################
            ### Retrieve the data ###
            #########################

            potentials, currents, data_dict = ReadData(myfile, electrode)

            ##########################################
            ### Set the x axes of the voltammogram ###
            ##########################################
            MIN_POTENTIAL = min(potentials)
            MAX_POTENTIAL = max(potentials)
            #-- Reverse voltammogram to match the 'Texas' convention --#
            ax[0,subplot_count].set_xlim(MAX_POTENTIAL,MIN_POTENTIAL)


            #######################################
            ### Get the high and low potentials ###
            #######################################

            if int(frequency) > cutoff_frequency:

                if not HighAlreadyReset:
                    high_xstart = max(potentials)
                    high_xend = min(potentials)

                #-- set the local variables to the global ---#
                xend = high_xend
                xstart = high_xstart

            elif int(frequency) <= cutoff_frequency:

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

            adjusted_potentials = [value for value in potentials if xend <= value <= xstart]

            #########################################
            ### Savitzky-Golay smoothing          ###0----89
            #########################################
            smooth_currents = savgol_filter(currents, 15, sg_degree)
            data_dict = dict(zip(potentials,smooth_currents))


            #######################################
            ### adjust the smooth currents to   ###
            ### match the adjusted potentials   ###
            #######################################
            adjusted_currents = []
            for potential in adjusted_potentials:
                adjusted_currents.append(data_dict[potential])

            ######################
            ### Polynomial fit ###
            ######################
            polynomial_coeffs = np.polyfit(adjusted_potentials,adjusted_currents,polyfit_deg)
            eval_regress = np.polyval(polynomial_coeffs,adjusted_potentials).tolist()
            regression_dict = dict(zip(eval_regress, adjusted_potentials))      # dictionary with current: potential

            fit_half = round(len(eval_regress)/2)
            min1 = min(eval_regress[:-fit_half])
            min2 = min(eval_regress[fit_half:])
            max1 = max(eval_regress[:-fit_half])
            max2 = max(eval_regress[fit_half:])

            linear_fit = np.polyfit([regression_dict[min1],regression_dict[min2]],[min1,min2],1)
            linear_regression = np.polyval(linear_fit,[regression_dict[min1],regression_dict[min2]]).tolist()

            if SelectedOptions == 'Peak Height Extraction':
                Peak_Height = max(max1,max2)-min(min1,min2)
                data = Peak_Height

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

            #--- calculate the baseline current ---#
            minimum_current = min(min1,min2)
            maximum_current = max(max1,max2)

            #- Voltammogram -#
            ax[0,subplot_count].set_ylim(minimum_current-abs(min_raw*minimum_current),maximum_current+abs(max_raw*maximum_current))

            #- PHE/AUC Data -#
            ax[1,subplot_count].set_ylim(data-abs(min_data*data),data+abs(max_data*data))

            #- Normalized Data -#
            ax[2,subplot_count].set_ylim(min_norm,max_norm)

            print('RunInitialization Complete')

            return True

        except:
            print('\n\nError in RunInitialization\n\n')