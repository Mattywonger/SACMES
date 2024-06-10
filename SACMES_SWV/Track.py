from GlobalVariables import *
import tkinter as tk
from tkinter import *
import DataNormalization
import TextFileExport

def _update_global_lists(self,file):
        global file_list, sample_list

        if file not in file_list:
            file_list.append(file)

            sample = round(len(file_list)*SampleRate/3600,3)
            sample_list.append(sample)
            RealTimeSampleLabel['text'] = sample

            if file != numFiles:
                FileLabel['text'] = file + 1

class Track():
    
    def __init__(self,numFiles,electrode_count,method,HighLowList,SaveVar):
        self.track_list = [1]*numFiles
        self.electrode_count = electrode_count
        self.method = method
        self.HighLowList = HighLowList
        self.SaveVar = SaveVar

    def tracking(self, file, frequency):
        global RatioMetricCheck


        index = file - 1

        if self.track_list[index] == self.electrode_count:

            if self.method == 'Continuous Scan':

                ### Global File List
                _update_global_lists(file)

                HighFrequency = self.HighLowList['High']
                LowFrequency = self.HighLowList['Low']

                DataNormalization.RenormalizeData(file)


                if self.SaveVar:
                    TextFileExport.ContinuousScanExport(file)


                #--- if the high and low frequencies have been changed, adjust the data ---#
                if RatioMetricCheck:

                    DataNormalization.ResetRatiometricData()

                    #-- if the data is being exported, reset the exported data file --#
                    if self.SaveVar:
                        TextFileExport.TxtFileNormalization()

                    RatioMetricCheck = False

            elif self.method == 'Frequency Map':

                if self.track_list[index] == self.electrode_count:

                    if self.SaveVar:
                        TextFileExport.FrequencyMapExport(file,frequency)


            self.track_list[index] = 1

        else:
            self.track_list[index] += 1
    