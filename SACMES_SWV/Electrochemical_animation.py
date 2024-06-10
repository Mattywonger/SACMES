from GlobalVariables import *
import tkinter as tk
from tkinter import *
import os
import numpy as np
from scipy.signal import *
from helper import *
import PostAnalysis
import DataNormalization
import Track
import threading
import time
from helper import _retrieve_file


class ElectrochemicalAnimation():
    def __init__(self, controller, fig, electrode, generator = None, func = None, resize_interval = None, fargs = None):
        
        self.controller = controller
        self.electrode = electrode                               # Electrode for this class instance
        self.num = electrode_dict[self.electrode]                # Electrode index value
        self.spacer = ''.join(['       ']*self.electrode)        # Spacer value for print statements
        self.file = starting_file                                # Starting File
        self.index = 0                                           # File Index Value
        self.count = 0                                           # Frequency index value
        self.frequency_limit = len(frequency_list) - 1           # ' -1 ' so it matches the index value

        ### Lists for sample rate (time passed)  ###
        ### and file count for each electrode    ###
        self.sample_list = []
        self.file_list = []

        self.frequency_axis = []
        self.charge_axis = []

        ##############################
        ## Set the generator object ##
        ##############################
        if generator is not None:
            self.generator = generator
        else:
            self.generator = self._raw_generator

        ################################
        ## Set the animation function ##
        ################################
        if func is not None:
            self._func = func
        elif method == 'Continuous Scan':
            self._func = self._continuous_func
        elif method == 'Frequency Map':
            self._func = self._frequency_map_func

        if resize_interval is not None:
            self.resize_interval = resize_interval
        else:
            self.resize_interval = None

        self.resize_limit = self.resize_interval        # set the first limit


        if fargs:
            self._args = fargs
        else:
            self._args = ()

        self._fig = fig

        # Disables blitting for backends that don't support it.  This
        # allows users to request it if available, but still have a
        # fallback that works if it is not.
        self._blit = fig.canvas.supports_blit


        # Instead of starting the event source now, we connect to the figure's
        # draw_event, so that we only start once the figure has been drawn.
        self._first_draw_id = fig.canvas.mpl_connect('draw_event', self._start)

        # Connect to the figure's close_event so that we don't continue to
        # fire events and try to draw to a deleted figure.
        self._close_id = self._fig.canvas.mpl_connect('close_event', self._stop)

        self._setup_blit()


    def _start(self, *args):


        # Starts interactive animation. Adds the draw frame command to the GUI
        # andler, calls show to start the event loop.

        # First disconnect our draw event handler
        self._fig.canvas.mpl_disconnect(self._first_draw_id)
        self._first_draw_id = None  # So we can check on save

        # Now do any initial draw
        self._init_draw()

        ### Create a thread to analyze obtain the file from a Queue
        ### and analyze the data.

        class _threaded_animation(threading.Thread):

            def __init__(self, controller,Queue):
                #global PoisonPill
                self.controller = controller
                threading.Thread.__init__(self)     # initiate the thread

                self.q = Queue

                #-- set the poison pill event for Reset --#
                self.PoisonPill = Event()
                PoisonPill = self.PoisonPill             # global reference

                self.file = 1

                self.controller.after(10,self.start)                       # initiate the run() method

            def run(self):

                while True:
                    try:
                        task = self.q.get(block=False)

                    except:
                        break
                    else:
                        if not PoisonPill:
                            self.controller.after(Interval,task)

                if not analysis_complete:
                    if not PoisonPill:
                        self.controller.after(10, self.run)


        threaded_animation = _threaded_animation(self.controller,Queue = q)

        self._step()


    def _stop(self, *args):
        # On stop we disconnect all of our events.
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._fig.canvas.mpl_disconnect(self._close_id)

    def _setup_blit(self):
        # Setting up the blit requires: a cache of the background for the
        # axes
        self._blit_cache = dict()
        self._drawn_artists = []
        self._resize_id = self._fig.canvas.mpl_connect('resize_event',
                                                       self._handle_resize)
        self._post_draw(True)

    def _blit_clear(self, artists, bg_cache):
        # Get a list of the axes that need clearing from the artists that
        # have been drawn. Grab the appropriate saved background from the
        # cache and restore.
        axes = {a.axes for a in artists}
        for a in axes:
            if a in bg_cache:
                a.figure.canvas.restore_region(bg_cache[a])


    #######################################################################
    ### Initialize the drawing by returning a sequence of blank artists ###
    #######################################################################
    def _init_draw(self):

        self._drawn_artists = EmptyPlots

        for a in self._drawn_artists:
            a.set_animated(self._blit)

    def _redraw_figures(self):
        print('\nREDRAWING FIGURES\nRESIZE LIMIT = %d' % self.resize_limit)

        ############################################
        ### Resize raw and normalized data plots ###
        ############################################
        fig, ax = figures[self.num]
        for count in range(len(frequency_list)):

            if XaxisOptions == 'Experiment Time':
                ax[1,count].set_xlim(0,(self.resize_limit*SampleRate)/3600+(SampleRate/7200))
                ax[2,count].set_xlim(0,(self.resize_limit*SampleRate)/3600+(SampleRate/7200))

            elif XaxisOptions == 'File Number':
                ax[1,count].set_xlim(0,self.resize_limit+0.1)
                ax[2,count].set_xlim(0,self.resize_limit+0.1)

        ##################################
        ### Readjust Ratiometric Plots ###
        ##################################
        if len(frequency_list) > 1:
            fig, ax = ratiometric_figures[self.num]

            if XaxisOptions == 'File Number':
                ax[0,0].set_xlim(0,self.resize_limit+0.1)
                ax[0,1].set_xlim(0,self.resize_limit+0.1)

            elif XaxisOptions == 'Experiment Time':
                ax[0,0].set_xlim(0,(self.resize_limit*SampleRate)/3600+(SampleRate/7200))
                ax[0,1].set_xlim(0,(self.resize_limit*SampleRate)/3600+(SampleRate/7200))

        #####################################################
        ### Set up the new canvas with an idle draw event ###
        #####################################################
        self._post_draw(True)


    def _handle_resize(self, *args):
        # On resize, we need to disable the resize event handling so we don't
        # get too many events. Also stop the animation events, so that
        # we're paused. Reset the cache and re-init. Set up an event handler
        # to catch once the draw has actually taken place.

        #################################################
        ### Stop the event source and clear the cache ###
        #################################################
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._blit_cache.clear()
        self._init_draw()
        self._resize_id = self._fig.canvas.mpl_connect('draw_event',
                                                       self._end_redraw)


    def _end_redraw(self):
        # Now that the redraw has happened, do the post draw flushing and
        # blit handling. Then re-enable all of the original events.
        self._post_draw(True)
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._resize_id = self._fig.canvas.mpl_connect('resize_event',
                                                       self._handle_resize)

    def _draw_next_frame(self, framedata, fargs = None):
        # Breaks down the drawing of the next frame into steps of pre- and
        # post- draw, as well as the drawing of the frame itself.
        self._pre_draw(framedata)
        self._draw_frame(framedata, fargs)
        self._post_draw(False)


    def _pre_draw(self, framedata):
        # Perform any cleaning or whatnot before the drawing of the frame.
        # This default implementation allows blit to clear the frame.
        self._blit_clear(self._drawn_artists, self._blit_cache)

    ###########################################################################
    ### Retrieve the data from _animation and blit the data onto the canvas ###
    ###########################################################################
    def _draw_frame(self, framedata, fargs):

        # Ratiometric #
        if fargs:
            if fargs == 'ratiometric_analysis':
                self._drawn_artists = self._ratiometric_animation(framedata, *self._args)
                self._drawn_artists = sorted(self._drawn_artists,
                                             key=lambda x: x.get_zorder())
                for a in self._drawn_artists:
                    a.set_animated(self._blit)

        else:

            self._drawn_artists = self._func(framedata, *self._args)

            if self._drawn_artists is None:
                raise RuntimeError('The animation function must return a '
                                   'sequence of Artist objects.')
            self._drawn_artists = sorted(self._drawn_artists,
                                         key=lambda x: x.get_zorder())

            for a in self._drawn_artists:
                a.set_animated(self._blit)


    def _post_draw(self, redraw):
        # After the frame is rendered, this handles the actual flushing of
        # the draw, which can be a direct draw_idle() or make use of the
        # blitting.

        if redraw:

            # Data plots #
            self._fig.canvas.draw()

            # ratiometric plots
            if method == 'Continuous Scan':
                if len(frequency_list) > 1:
                    ratio_fig, ratio_ax = ratiometric_figures[self.num]
                    ratio_fig.canvas.draw()

        elif self._drawn_artists:

            self._blit_draw(self._drawn_artists, self._blit_cache)


    # The rest of the code in this class is to facilitate easy blitting
    def _blit_draw(self, artists, bg_cache):
        # Handles blitted drawing, which renders only the artists given instead
        # of the entire figure.
        updated_ax = []
        for a in artists:
            # If we haven't cached the background for this axes object, do
            # so now. This might not always be reliable, but it's an attempt
            # to automate the process.
            if a.axes not in bg_cache:
                bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.bbox)
            a.axes.draw_artist(a)
            updated_ax.append(a.axes)

        # After rendering all the needed artists, blit each axes individually.
        for ax in set(updated_ax):
            ax.figure.canvas.blit(ax.bbox)


    ## callback that is called every 'interval' ms ##
    def _step(self):
        global RatioMetricCheck, file_list, sample_list, analysis_complete
        if self.file not in self.file_list:
            self.file_list.append(self.file)
            self.sample_list.append((len(self.file_list)*SampleRate)/3600)

        ### look for the file here ###
        frequency = int(frequency_list[self.count])

        if method == 'Continuous Scan':
            self.electrode = electrode_list[self.num]

            filename, filename2, filename3, filename4 = _retrieve_file(self.file,self.electrode,frequency)

            ### path of your file
            myfile = mypath + filename
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


        elif method == 'Frequency Map':

            filename, filename2, filename3, filename4, filename5, filename6 = _retrieve_file(self.file,self.electrode,frequency)

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
                    filename = filename2
                except:
                    try:
                        mydata_bytes = os.path.getsize(myfile3)
                        myfile = myfile3
                        filename = filename3
                    except:
                        try:
                            mydata_bytes = os.path.getsize(myfile4)
                            myfile = myfile4
                            filename = filename4
                        except:
                            try:
                                mydata_bytes = os.path.getsize(myfile5)
                                myfile = myfile5
                                filename = filename5
                            except:
                                try:
                                    mydata_bytes = os.path.getsize(myfile6)
                                    myfile = myfile6
                                    filename = filename6
                                except:
                                    mydata_bytes = 1


        if mydata_bytes > byte_limit:
            print('%s%d: Queueing %s' % (self.spacer,self.electrode,filename))
            q.put(lambda: self._run_analysis(myfile,frequency))


        else:
            if not PoisonPill:
                self.controller.after(100,self._step)

    def _check_queue(self):

        while True:
            try:
                print('%sChecking Queue' % self.spacer)
                task = q.get(block=False)
            except:
                print('%sQueue Empty' % self.spacer)
                break
            else:
                if not PoisonPill:
                    self.controller.after(1,self.task)

        if not analysis_complete:
            if not PoisonPill:
                self.controller.after(5, self._check_queue)

    def _run_analysis(self,myfile,frequency):

        #######################################################
        ### Perform the next iteration of the data analysis ###
        #######################################################
        try:
            framedata = self.generator(myfile, frequency)
            self._draw_next_frame(framedata)

            if method == 'Frequency Map':
                Track.tracking(self.file, frequency)


        except StopIteration:
            return False

        ##########################################################################
        ### if the resize limit has been reached, resize and redraw the figure ###
        ##########################################################################
        if self.file == self.resize_limit:

            # Dont redraw if this is the already the last file #
            if self.resize_limit < numFiles:

                ###############################################################
                ### If this is the last frequency, move onto the next limit ###
                ###############################################################
                if self.count == self.frequency_limit:
                    self.resize_limit = self.resize_limit + self.resize_interval

                    ### If the resize limit is above the number of files (e.g.
                    ### going out of bounds for the last resize event) then
                    ### readjust the final interval to the number of files
                    if self.resize_limit >= numFiles:
                        self.resize_limit = numFiles

                ############################################################
                ### 'if' statement used to make sure the plots dont get  ###
                ### erased when there are no more files to be visualized ###
                ############################################################
                try:
                    self._redraw_figures()
                except:
                    print('\nCould not redraw figure\n')



        ##################################################################
        ### If the function has analyzed each frequency for this file, ###
        ### move onto the next file and reset the frequency index      ###
        ##################################################################
        if self.count == self.frequency_limit:

            ######################################################
            ### If there are multiple frequencies, perform     ###
            ### ratiometric analysis and visualize the data on ###
            ######################################################
            if method == 'Continuous Scan':
                if len(frequency_list) > 1:
                    try:
                        framedata = self._ratiometric_generator()
                        self._draw_next_frame(framedata, fargs = 'ratiometric_analysis')

                    except StopIteration:
                        return False

                Track.tracking(self.file, None)

            #########################################################################
            ### If the function has analyzed the final final, remove the callback ###
            #########################################################################
            if self.file == numFiles:
                print('\n%sFILE %s.\n%sElectrode %d\n%sData Analysis Complete\n' % (self.spacer,str(self.file),self.spacer,self.electrode,self.spacer))

                if method == 'Continuous Scan':
                    PostAnalysis._analysis_finished()

            else:
                self.file += 1
                self.index += 1
                self.count = 0
                self.controller.after(1, self._step)



        ##########################################################
        ### Elif the function has not analyzed each frequency  ###
        ### for this file, move onto the next frequency        ###
        ##########################################################
        elif self.count < self.frequency_limit:
            self.count += 1

            self.controller.after(1, self._step)


    def _raw_generator(self, myfile, frequency):

        ########################################
        ### Polynomical Regression Range (V) ###
        ########################################
        #--- if the frequency is equal or below cutoff_frequency, use the low freq parameters ---#
        if frequency <= cutoff_frequency:
            xstart = low_xstart
            xend = low_xend

        #--- if the frequency is above cutoff_frequency, use the high freq parameters ---#
        else:
            xstart = high_xstart
            xend = high_xend

        ###################################
        ### Retrieve data from the File ###
        ###################################
        potentials, currents, data_dict = ReadData(myfile, self.electrode)

        cut_value = 0
        for value in potentials:
            if value == 0:
                cut_value += 1

        if cut_value > 0:
            potentials = potentials[:-cut_value]
            currents = currents[:-cut_value]


        ################################################################
        ### Adjust the potentials depending on user-input parameters ###
        ################################################################
        adjusted_potentials = [value for value in potentials if xend <= value <= xstart]

        #########################################
        ### Savitzky-Golay Smoothing          ###
        #########################################
        min_potential = min(potentials)            # find the min potential
        sg_limit = sg_window/1000                  # mV --> V

        # shift all values positive
        sg_potentials = [x - min_potential for x in potentials]

        # find how many points fit within the sg potential window
        # this will be how many points are included in the rolling average
        sg_range = len([x for x in sg_potentials if x <= sg_limit])

        #--- Savitzky-golay Window must be greater than the range ---#
        if sg_range <= sg_degree:
            sg_range = sg_degree + 1

        #-- if the range is even, make it odd --#
        if sg_range % 2 == 0:
            sg_range = sg_range + 1

        # Apply the smoothing function and create a dictionary pairing
        # each potential with its corresponding current
        try:
            smooth_currents = savgol_filter(currents, sg_range, sg_degree)
            data_dict = dict(zip(potentials,smooth_currents))
        except ValueError:
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

        #############################
        ### Polynomial Regression ###
        #############################
        eval_regress = np.polyval(polynomial_coeffs,adjusted_potentials).tolist()
        regression_dict = dict(zip(eval_regress, adjusted_potentials))      # dictionary with current: potential

        ###############################################
        ### Absolute Max/Min Peak Height Extraction ###
        ###############################################
        #-- If the user selects 'Absolute Max/Min' in the 'Peak Height Extraction Settings'
        #-- within the Settings toolbar this analysis method will be used for PHE
        fit_half = round(len(eval_regress)/2)

        min1 = min(eval_regress[:fit_half])
        min2 = min(eval_regress[fit_half:])
        max1 = max(eval_regress[:fit_half])
        max2 = max(eval_regress[fit_half:])


        ################################################################
        ### If the user selected Peak Height Extraction, analyze PHE ###
        ################################################################
        Peak_Height = max(max1,max2)-min(min1,min2)
        if SelectedOptions == 'Peak Height Extraction':
            data = Peak_Height


        ########################################################
        ### If the user selected AUC extraction, analyze AUC ###
        ########################################################

        elif SelectedOptions == 'Area Under the Curve':
            ##################################
            ### Integrate Area Under the   ###
            ### Curve using a Riemmann Sum  ###
            ##################################
            AUC_index = 1
            AUC = 0

            AUC_potentials = adjusted_potentials

            #--- Find the minimum value and normalize it to 0 ---#
            AUC_min = min(adjusted_currents)
            AUC_currents = [Y - AUC_min for Y in adjusted_currents]

            #--- Midpoint Riemann Sum ---#
            while AUC_index <= len(AUC_currents) - 1:
                AUC_height = (AUC_currents[AUC_index] + AUC_currents[AUC_index - 1])/2
                AUC_width = AUC_potentials[AUC_index] - AUC_potentials[AUC_index - 1]
                AUC += (AUC_height * AUC_width)
                AUC_index += 1

            data = AUC

        #######################################
        ### Save the data into global lists ###
        #######################################
        data_list[self.num][self.count][self.index] = data

        if method == 'Continuous Scan':
            DataNormalization.Normalize(self.file, data, self.num, self.count, self.index)

        elif method == 'Frequency Map':
            frequency = frequency_list[self.count]
            self.frequency_axis.append(int(frequency))

            charge = (Peak_Height/frequency) * 100000
            self.charge_axis.append(Peak_Height/frequency)


        #####################################################
        ### Return data to the animate function as 'args' ###
        #####################################################

        return potentials, adjusted_potentials, smooth_currents, adjusted_currents, eval_regress


    def _continuous_func(self, framedata, *args):

        if key > 0:
            while True:

                potentials, adjusted_potentials, smooth_currents, adjusted_currents, regression = framedata

                print('\n%s%d: %dHz\n%s_animate' % (self.spacer,self.electrode,frequency_list[self.count],self.spacer))


                #############################################################
                ### Acquire the current frequency and get the xstart/xend ###
                ### parameters that will manipulate the visualized data   ###
                #############################################################
                frequency = frequency_list[self.count]

                ###################################
                ### Set the units of the X-axis ###
                ###################################
                if XaxisOptions == 'Experiment Time':
                    Xaxis = self.sample_list
                elif XaxisOptions == 'File Number':
                    Xaxis = self.file_list

                ################################################################
                ### Acquire the artists for this electrode at this frequency ###
                ### and get the data that will be visualized                 ###
                ################################################################
                plots = plot_list[self.num][self.count]                              # 'count' is the frequency index value

                ##########################
                ### Visualize the data ###
                ##########################

                #--- Peak Height ---#

                data = data_list[self.num][self.count][:len(self.file_list)]                     # 'num' is the electrode index value

                if frequency_list[self.count] == HighLowList['Low']:
                    NormalizedDataList = offset_normalized_data_list[self.num][:len(self.file_list)]
                else:
                    NormalizedDataList = normalized_data_list[self.num][self.count][:len(self.file_list)]

                ####################################################
                ### Set the data of the artists to be visualized ###
                ####################################################
                if InjectionPoint is None:
                    plots[0].set_data(potentials,smooth_currents)               # Smooth current voltammogram
                    plots[1].set_data(adjusted_potentials, regression)
                    plots[2].set_data(Xaxis,data)                    # Raw Data
                    plots[4].set_data(Xaxis,NormalizedDataList)           # Norm Data

                ##########################################################
                ### If an Injection Point has been set, visualize the  ###
                ### data before and after the injection separately     ###
                ##########################################################
                elif InjectionPoint is not None:

                    if self.file >= InjectionPoint:
                        InjectionIndex = InjectionPoint - 1

                        ####################################################
                        ### Set the data of the artists to be visualized ###
                        ####################################################

                        plots[0].set_data(potentials,smooth_currents)          # Smooth current voltammogram
                        plots[1].set_data(adjusted_potentials,regression)      # Regression voltammogram
                        plots[2].set_data(Xaxis[:InjectionIndex],data[:InjectionIndex])      # Raw Data up until injection point
                        plots[3].set_data(Xaxis[InjectionIndex:],data[InjectionIndex:])      # Raw Data after injection point
                        plots[4].set_data(Xaxis[:InjectionIndex],NormalizedDataList[:InjectionIndex])     # Norm Data before injection point
                        plots[5].set_data(Xaxis[InjectionIndex:],NormalizedDataList[InjectionIndex:])     # Norm Data before injection point

                    elif InjectionPoint > self.file:
                        plots[0].set_data(potentials,smooth_currents)               # Smooth current voltammogram
                        plots[1].set_data(adjusted_potentials, regression)
                        plots[2].set_data(Xaxis,data)                          # Raw Data
                        plots[3].set_data([],[])                                    # Clear the injection artist
                        plots[4].set_data(Xaxis,NormalizedDataList)                  # Norm Data
                        plots[5].set_data([],[])                                    # Clear the injection artist


                if SelectedOptions == 'Area Under the Curve':
                    #--- Shaded region of Area Under the Curve ---#
                    vertices = [(adjusted_potentials[0],adjusted_currents[0]), *zip(adjusted_potentials, adjusted_currents), (adjusted_potentials[-1],adjusted_currents[-1])]
                    plots[6].set_xy(vertices)


                print('returning plots!')
                return plots


        else:
            file = 1
            EmptyPlots = framedata
            time.sleep(0.1)
            print('\n Yielding Empty Plots in Animation \n')
            return EmptyPlots

    def _frequency_map_func(self, framedata, *args):

        if key > 0:
            while True:

                potentials, adjusted_potentials, smooth_currents, adjusted_currents, regression = framedata

                print('\n%s%d: %dHz\n%s_animate' % (self.spacer,self.electrode,frequency_list[self.count],self.spacer))


                ################################################################
                ### Acquire the artists for this electrode at this frequency ###
                ### and get the data that will be visualized                 ###
                ################################################################
                plots = plot_list[self.num]

                ##########################
                ### Visualize the data ###
                ##########################

                #--- Peak Height ---#

                data = data_list[self.num][self.count][:len(self.file_list)]                     # 'num' is the electrode index value

                ####################################################
                ### Set the data of the artists to be visualized ###
                ####################################################
                plots[0].set_data(potentials,smooth_currents)          # Smooth current voltammogram
                plots[1].set_data(adjusted_potentials,regression)      # Regression voltammogram
                plots[2].set_data(self.frequency_axis,self.charge_axis)


                print('returning plots!')
                return plots


        else:
            file = 1
            EmptyPlots = framedata
            time.sleep(0.1)
            print('\n Yielding Empty Plots in Animation \n')
            return EmptyPlots


    ############################
    ### Ratiometric Analysis ###
    ############################
    def _ratiometric_generator(self):

        index = self.file - 1

        HighFrequency = HighLowList['High']
        LowFrequency = HighLowList['Low']

        HighCount = frequency_dict[HighFrequency]
        LowCount = frequency_dict[LowFrequency]

        HighPoint = normalized_data_list[self.num][HighCount][self.index]
        LowPoint = offset_normalized_data_list[self.num][self.index]

        NormalizedRatio = HighPoint/LowPoint
        KDM = (HighPoint - LowPoint) + 1

        #-- save the data to global lists --#
        normalized_ratiometric_data_list[self.num].append(NormalizedRatio)
        KDM_list[self.num].append(KDM)

        return NormalizedRatio, KDM

    def _ratiometric_animation(self, framedata, *args):

        NormalizedRatio, KDM = framedata

        plots = ratiometric_plots[self.num]

        if XaxisOptions == 'Experiment Time':
            Xaxis = self.sample_list
        elif XaxisOptions == 'File Number':
            Xaxis = self.file_list

        norm = [X*100 for X in normalized_ratiometric_data_list[self.num]]
        KDM = [X*100 for X in KDM_list[self.num]]

        ##########################################
        ## If an injection point has not been   ##
        ## chosen, visualize the data as usual  ##
        ##########################################
        if InjectionPoint is None:
            plots[0].set_data(Xaxis,norm)
            plots[2].set_data(Xaxis,KDM)

        ############################################
        ## If an injection point has been chosen  ##
        ## chosen, visualize the injection        ##
        ## points separately                      ##
        ############################################
        elif InjectionPoint is not None:

            #-- list index value for the injection point --#
            InjectionIndex = InjectionPoint - 1

            #-- if the injection point has already been --#
            #-- analyzed, separate the visualized data  --#
            if self.file >= InjectionPoint:
                plots[0].set_data(Xaxis[:InjectionIndex],norm[:InjectionIndex])
                plots[1].set_data(Xaxis[InjectionIndex:],norm[InjectionIndex:])
                plots[2].set_data(Xaxis[:InjectionIndex],KDM[:InjectionIndex])
                plots[3].set_data(Xaxis[InjectionIndex:],KDM[InjectionIndex:])

            #-- if the file is below the injectionpoint, wait until  --#
            #-- the point is reached to visualize the injection data --#
        elif self.file < InjectionPoint:
                plots[0].set_data(Xaxis,norm)
                plots[1].set_data([],[])
                plots[2].set_data(Xaxis,KDM)
                plots[3].set_data([],[])


        return plots