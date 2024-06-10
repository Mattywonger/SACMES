from GlobalVariables import *
import tkinter as tk
from tkinter import *
import os
import numpy as np
from helper import _get_listval,_retrieve_file,ReadData
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.signal import *
import Freq_visualization
import TextFileExport

class InitializeFrequencyMapCanvas():
    def __init__(self):
        global text_file_export, SaveVar, file_list, electrode_count, anim, Frame, FrameReference, FileHandle, PlotContainer,frequency_list, data_list, plot_list, EmptyPlots, figures, frame_list, Plot, PlotFrames, PlotValues

        ##############################################
        ### Generate global lists for data storage ###
        ##############################################

        self.length = len(frequency_list)
        electrode_count = int(electrode_count)

        #--- Animation list ---#
        anim = []

        #--- file list ---#
        file_list = [0]*numFiles

        #--- Figure lists ---#
        figures = []

        ############################################
        ### Create global lists for data storage ###
        ############################################
        data_list = [0]*electrode_count                             # Peak Height/AUC data (after smoothing and polynomial regression)

        for num in range(electrode_count):
            data_list[num] = [0]*self.length                        # a data list for each eletrode
            for count in range(self.length):                        # a data list for each frequency for that electrode
                data_list[num][count] = [0]*numFiles


        #--- Lists of Frames and Artists ---#
        plot_list = []
        frame_list = []

        ######################################################
        ### Create a figure and artists for each electrode ###
        ######################################################
        for num in range(electrode_count):
            electrode = electrode_list[num]
            figure = self.MakeFigure(electrode)
            figures.append(figure)


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
        for electrode_frame in frame_list:                # Iterate through the frame of each electrode

            #--- create an instance of the frame and append it to the global frame dictionary ---#
            FrameReference = Freq_visualization(electrode_frame, frame_count, PlotContainer, self)            # PlotContainer is the 'parent' frame
            FrameReference.grid(row=0,column=0,sticky='nsew')      # sticky must be 'nsew' so it expands and contracts with resize
            PlotFrames[electrode_frame] = FrameReference
            print("This is what's stored in\n")
            print(FrameReference)

            frame_count += 1

        #--- Create a list containing the Frame objects for each electrode ---#
        for reference, frame in PlotFrames.items():
            PlotValues.append(frame)


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
    def MakeFigure(self, electrode):
        global EmptyPlots, plot_list, frame_list

        try:
            ##########################################
            ### Setup the Figure for voltammograms ###
            ##########################################
            fig, ax = plt.subplots(nrows=2,ncols=1,squeeze=False,figsize=(9,4.5))    ## figsize=(width, height)
            plt.subplots_adjust(bottom=0.2,hspace=0.6,wspace=0.3)         ### adjust the spacing between subplots

            #---Set the electrode index value---#
            if e_var == 'single':
                list_val = current_column_index + (electrode-1)*spacing_index
            elif e_var == 'multiple':
                list_val = current_column_index

            #######################
            ### Set axis labels ###
            #######################
            ax[0,0].set_ylabel('Current (µA)',fontweight='bold')
            ax[0,0].set_xlabel('Voltage (V)',fontweight='bold')

            ax[1,0].set_ylabel('Charge (uC)',fontweight='bold')
            ax[1,0].set_xlabel('Frequency (Hz)',fontweight='bold')
            ##########################################
            ### Set suplot axes for each frequency ###
            ##########################################
            electrode_plot = []

            max_frequency = frequency_list[-1]
            ax[1,0].set_xscale('log')
            #################################################################################
            #################################################################################
            ###       Analyze the first file and create the Y limits of the subplots      ###
            ###               depending on the data range of the first file               ###
            #################################################################################

            self.InitializeSubplots(ax, electrode)

            #################################################################################
            #################################################################################

            #---Initiate the subplots---#
            # this assigns a Line2D artist object to the artist object (Axes)
            smooth, = ax[0,0].plot([],[],'ko',Markersize=2)
            regress, = ax[0,0].plot([],[],'r-')
            charge, = ax[1,0].plot([],[],'ko',MarkerSize=1)

            #--- shading for AUC ---#
            verts = [(0,0),*zip([],[]),(0,0)]
            poly = Polygon(verts, alpha = 0.5)
            ax[0,0].add_patch(poly)

            #####################################################
            ### Create a list of the primitive artists        ###
            ### (Line2D objects) that will be returned        ###
            ### to ElectrochemicalAnimation to be visualized  ###
            #####################################################

            # this is the list that will be returned as _drawn_artists to the Funcanimation class
            plots = [smooth,regress,charge,poly]

            #--- And append that list to keep a global reference ---#
            electrode_plot.append(plots)        # 'plots' is a list of artists that are passed to animate
            electrode_frame = 'Electrode %s' % str(electrode)
            if electrode_frame not in frame_list:
                frame_list.append(electrode_frame)
                print("Entered 2996 for loop")

            #--- Create empty plots to return to animate for initializing---#
            EmptyPlots = [smooth,regress,charge]

            plot_list.append(plots)        # 'plot_list' is a list of lists containing 'plots' for each electrode

            #-- Return both the figure and the axes to be stored as global variables --#
            return fig, ax


        except:
            print('Error in MakeFigure')


    #####################################################################################
    ### Initalize Y Limits of each figure depending on the y values of the first file ###
    #####################################################################################
    def InitializeSubplots(self,ax,electrode):

        self.list_val = _get_listval(electrode)

        try:
            frequency = frequency_list[0]
            filename, filename2, filename3, filename4, filename5, filename6 = _retrieve_file(1,electrode,frequency)

            myfile = mypath + filename               ### path of your file
            myfile2 = mypath + filename2
            myfile3 = mypath + filename3
            myfile4 = mypath + filename4
            myfile5 = mypath + filename5
            myfile6 = mypath + filename6
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

            if mydata_bytes > byte_limit:
                print('Found File %s' % myfile)
                self.RunInitialization(myfile,ax,electrode)

            else:
                return False


        except:
            print('could not find file for electrode %d' % electrode)
            #--- If search time has not met the search limit keep searching ---#
            self.controller.after(1000, self.InitializeSubplots, ax, electrode)


    def RunInitialization(self, myfile, ax, electrode):
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
            ax[0,0].set_xlim(MAX_POTENTIAL,MIN_POTENTIAL)

            #######################################
            ### Get the high and low potentials ###
            #######################################

            #-- set the local variables to the global ---#
            xstart = max(potentials)
            xend = min(potentials)

            low_xstart = xstart
            high_xstart = xstart
            low_xend = xend
            high_xend = xend

            cut_value = 0
            for value in potentials:
                if value == 0:
                    cut_value += 1


            if cut_value > 0:
                potentials = potentials[:-cut_value]
                currents = currents[:-cut_value]

            adjusted_potentials = [value for value in potentials if xend <= value <= xstart]

            #########################################
            ### Savitzky-Golay smoothing          ###
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

            Peak_Height = max(max1,max2)-min(min1,min2)


            if SelectedOptions == 'Area Under the Curve':
                AUC_index = 1
                AUC = 0

                AUC_potentials = [abs(potential) for potential in adjusted_potentials]
                AUC_min = min(adjusted_currents)
                AUC_currents = [Y - AUC_min for Y in adjusted_currents]

                while AUC_index <= len(AUC_currents) - 1:
                    AUC_height = (AUC_currents[AUC_index] + AUC_currents[AUC_index - 1])/2
                    AUC_width = AUC_potentials[AUC_index] - AUC_potentials[AUC_index - 1]
                    AUC += (AUC_height * AUC_width)
                    AUC_index += 1

            #--- calculate the baseline current ---#
            minimum_current = min(min1,min2)
            maximum_current = max(max1,max2)
            peak_current = maximum_current - minimum_current
            charge = peak_current/(frequency_list[0])

            ## Reverse voltammogram to match the 'Texas' convention ##
            ax[0,0].set_xlim(MAX_POTENTIAL,MIN_POTENTIAL)
            ax[0,0].set_ylim(minimum_current-abs(min_raw*minimum_current),maximum_current+abs(max_raw*maximum_current))         # voltammogram

            ## set the limits of the lovric plot ##
            ax[1,0].set_ylim(charge-abs(min_data*charge),charge+abs(max_data*charge))
            ax[1,0].set_xlim(int(frequency_list[0]),int(frequency_list[-1]))

            return True

        except:
            print('\n\nError in RunInitialization\n\n')
