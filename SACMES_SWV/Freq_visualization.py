from GlobalVariables import *
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
class FrequencyMapVisualizationFrame(tk.Frame):
    def __init__(self, electrode, count, parent, controller):
        global FrameFileLabel

        tk.Frame.__init__(self, parent)

        #--- for resize ---#
        self.columnconfigure(0, weight = 2)
        self.columnconfigure(1, weight = 1)
        self.rowconfigure(2, weight=2)

        ElectrodeLabel = ttk.Label(self, text='%s' % electrode ,font=('Verdana', 18))
        ElectrodeLabel.grid(row=0,column=0,pady=5,sticky='n')

        FrameFileLabel = ttk.Label(self, text = '', font=('Verdana', 10))
        FrameFileLabel.grid(row=0,column=1,pady=3,sticky='ne')

        #--- Voltammogram, Raw Peak Height, and Normalized Figure and Artists ---#
        fig, ax = figures[count]                                                # Call the figure and artists for the electrode
        canvas = FigureCanvasTkAgg(fig, self)                                         # and place the artists within the frame
        canvas.draw()                                                           # initial draw call to create the artists that will be blitted
        canvas.get_tk_widget().grid(row=1,columnspan=2,pady=6,ipady=5,sticky='news')   