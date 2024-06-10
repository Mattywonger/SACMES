import tkinter as tk
from tkinter import *
from GlobalVariables import *
import WaitTime
class DataNormalization():
    def __init__(self):
        pass

    def Normalize(self, file, data, num, count, index):
        global InitializedNormalization

        sample = len(file_list)*SampleRate/3600
        #######################################################
        ## Check the frequency and apply the baseline offset ##
        #######################################################
        frequency = frequency_list[count]
        if frequency == HighLowList['Low']:
            if XaxisOptions == 'Experiment Time':
                Offset = (sample*LowFrequencySlope) + LowFrequencyOffset
            elif XaxisOptions == 'File Number':
                Offset = (file*LowFrequencySlope) + LowFrequencyOffset
        else:
            Offset = 0

        NormalizationIndex = int(NormalizationPoint) - 1

        #--- If the file being used as the standard has been analyzed, normalize the data to that point ---#
        if file >= NormalizationPoint:

            if NormalizationPoint not in NormalizationVault:
                NormalizationVault.append(NormalizationPoint)

            #-- if the software has still been normalizing to the first file, start normalizing to the normalization point --#
            if not InitializedNormalization:
                InitializedNormalization = True

            ###########################################################
            ### If the rest of the data has already been normalized ###
            ### to this point, continue to normalize the data for   ###
            ### the current file to the normalization point         ###
            ###########################################################
            normalized_data_list[num][count][index] = data/data_list[num][count][NormalizationIndex]

            ###########################################################################
            ### If this is a low frequency, apply the offset to the normalized data ###
            ###########################################################################
            if frequency == HighLowList['Low']:
                offset_normalized_data_list[num][index] = normalized_data_list[num][count][index] + Offset

        #######################################################################
        ### Elif the chosen normalization point is greater than the current ###
        ### file, continue to normalize to the previous normalization point ###
        #######################################################################
        elif InitializedNormalization:

            ### Acquire the normalization point that was previously selected ###
            TempNormalizationPoint = NormalizationVault[-1]
            TempNormalizationIndex = TempNormalizationPoint - 1

            normalized_data_list[num][count][index] = data/data_list[num][count][TempNormalizationIndex]

            ###########################################################################
            ### If this is a low frequency, apply the offset to the normalized data ###
            ###########################################################################
            if frequency_list[count] == HighLowList['Low']:
                offset_normalized_data_list[num][index] = normalized_data_list[num][count][index] + Offset


        #--- Else, if the initial normalization point has not yet been reached, normalize to the first file ---#
        elif not InitializedNormalization:
            normalized_data_list[num][count][index] = data/data_list[num][count][0]

            ###########################################################################
            ### If this is a low frequency, apply the offset to the normalized data ###
            ###########################################################################
            if frequency_list[count] == HighLowList['Low']:
                offset_normalized_data_list[num][index] = normalized_data_list[num][count][index] + Offset

    ################################################################
    ### If the normalization point has been changed, renormalize ###
    ### the data list to the new normalization point             ###
    ################################################################
    def RenormalizeData(self, file):

        ##############################################################
        ## If the normalization point equals the current file,      ##
        ## normalize all of the data to the new normalization point ##
        #############################################################
        if file == NormalizationPoint:
            index = file - 1
            NormalizationIndex = NormalizationPoint - 1
            for num in range(electrode_count):
                for count in range(len(frequency_list)):

                    normalized_data_list[num][count][:index] = [(idx/data_list[num][count][NormalizationIndex]) for idx in data_list[num][count][:index]]

                    ##################################################
                    ## If the frequency is below cutoff_frequency, ###
                    ## add the baseline Offset                     ###
                    ##################################################
                    if frequency_list[count] == HighLowList['Low']:
                        for index in range(len(file_list)):


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

            ################################################
            ### Analyze KDM using new normalization data ###
            ################################################
            if len(frequency_list) > 1:
                self.ResetRatiometricData()

            ###############################
            ### GUI Normalization Label ###
            ###############################
            NormWarning['foreground'] = 'green'
            NormWarning['text'] = 'Normalized to file %s' % str(NormalizationPoint)


            ########################################################################
            ### If .txt file export has been activated, update the exported data ###
            ########################################################################
            if SaveVar:
                text_file_export.TxtFileNormalization()

        #########################################################################
        ## If the Normalization Point has been changed and the current file is ##
        ## greater than the new point, renormalize the data to the new point   ##
        #########################################################################
        if NormalizationWaiting:
            index = file - 1
            NormalizationIndex = NormalizationPoint - 1
            for num in range(electrode_count):
                for count in range(len(frequency_list)):

                    ##########################
                    ## Renormalize the data ##
                    ##########################
                    normalized_data_list[num][count][:index] = [idx/data_list[num][count][NormalizationIndex] for idx in data_list[num][count][:index]]
                    ##################################################
                    ## If the frequency is below cutoff_frequency,  ##
                    ## add the baseline Offset                      ##
                    ##################################################
                    if frequency_list[count] == HighLowList['Low']:
                        for index in range(len(file_list)):

                            ##########################
                            ## Calculate the offset ##
                            ##########################
                            sample = sample_list[index]
                            file = index + 1

                            if XaxisOptions == 'Experiment Time':
                                Offset = (sample*LowFrequencySlope) + LowFrequencyOffset
                            elif XaxisOptions == 'File Number':
                                Offset = (file*LowFrequencySlope) + LowFrequencyOffset

                            offset_normalized_data_list[num][index] = normalized_data_list[num][count][index] + Offset

            ################################################
            ## Using the newly normalized data, calculate ##
            ## the Normalized Ratio and KDM               ##
            ## for each file that has been analyzed       ##
            ################################################
            if len(frequency_list) > 1:
                self.ResetRatiometricData()


            #--- Indicate that the data has been normalized to the new NormalizationPoint ---#
            NormWarning['foreground'] = 'green'
            NormWarning['text'] = 'Normalized to file %s' % str(NormalizationPoint)
            wait_time.NormalizationProceed()


            #-- if .txt file export has been activated, update the exported data ---#
            if SaveVar:
                text_file_export.TxtFileNormalization()

    #############################################################
    ### Readjust the data to the new user-inputted parameters ###
    #############################################################
    def ResetRatiometricData(self):

        ############################################
        ### Readjust Low Frequencies with Offset ###
        ############################################

        #-- Iterate through every frequency --#
        for frequency in frequency_list:

            #-- Only apply the offset if the frequency is below cutoff_frequency --#
            if frequency == HighLowList['Low']:
                count = frequency_dict[frequency]

                #-- Apply the offset to every file --#
                for index in range(len(file_list)):

                    sample = sample_list[index]
                    file = file_list[index]

                    if XaxisOptions == 'Experiment Time':
                        Offset = (sample*LowFrequencySlope) + LowFrequencyOffset
                    elif XaxisOptions == 'File Number':
                        Offset = (file*LowFrequencySlope) + LowFrequencyOffset

                    for num in range(electrode_count):
                        offset_normalized_data_list[num][index] = normalized_data_list[num][count][index] + float(Offset)

        ####################################################
        ### Readjust KDM with newly adjusted frequencies ###
        ####################################################
        for file in file_list:
            index = file - 1
            for num in range(electrode_count):

                # grab the index value for the current high and low frequencies used for ratiometric analysis #
                HighCount = frequency_dict[HighFrequency]

                HighPoint = normalized_data_list[num][HighCount][index]
                LowPoint = offset_normalized_data_list[num][index]

                NormalizedDataRatio = HighPoint/LowPoint
                normalized_ratiometric_data_list[num][index] = NormalizedDataRatio

                #-- KDM ---#
                KDM = (HighPoint - LowPoint) + 1
                KDM_list[num][index] = KDM

        #-- if .txt file export has been activated, update the exported data ---#
        if SaveVar:
            if not analysis_complete:
                text_file_export.TxtFileNormalization()