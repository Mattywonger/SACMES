from Mainwindow import MainWindow
import tkinter as tk
from tkinter import ttk

method=""
root = tk.Tk()
app = MainWindow(root)
style = ttk.Style()
style.configure('On.TButton', foreground = 'blue', font = ('Verdana', 11), relief = 'raised', border = 100)
style.configure('Off.TButton', foreground = 'black', relief = 'sunken', border = 5)
style.configure('LARGE_FONT', font=('Verdana', 11))
style.configure('HUGE_FONT',font=('Verdana', 18))
style.configure('MEDIUM_FONT',font=('Verdana', 10))
style.configure('SMALL_FONT',font=('Verdana', 8))

while True:
        #--- initiate the mainloop ---#
        try:
            root.mainloop()
            
        #--- escape scrolling error ---#
        except UnicodeDecodeError:
            pass


                    #*########################################*#
                    #*############ End of Program ############*#
                    #*########################################*#