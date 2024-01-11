def globalvar_config():
    handle_variable = ''    # default handle variable is nothing
    e_var = 'single'        # default input file is 'Multichannel', or a single file containing all electrodes
    PHE_method = 'Abs'      # default PHE Extraction is difference between absolute max/min

    #------------------------------------------------------------#

    InputFrequencies = [30,80,240]  # frequencies initially displayed in Frequency Listbox
    electrodes = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

    return handle_variable,e_var,PHE_method,InputFrequencies,electrodes

def regressionvar_config():
    sg_window = 5           ### Savitzky-Golay window (in mV range), must be odd number (increase signal:noise)
    sg_degree = 1           ### Savitzky-Golay polynomial degree
    polyfit_deg = 15        ### degree of polynomial fit

    cutoff_frequency = 50          ### frequency that separates 'low' and 'high'
                                ### frequencies for regression analysis and
                                ### smoothing manipulation
    return sg_window,sg_degree,polyfit_deg,cutoff_frequency


def checkpoint_parameter():
    key = 0                 ### SkeletonKey
    search_lim = 15         ### Search limit (sec)
    PoisonPill = False      ### Stop Animation variable
    FoundFilePath = False   ### If the user-inputted file is found
    ExistVar = False        ### If Checkpoints are not met ExistVar = True
    AlreadyInitiated = False    ### indicates if the user has already initiated analysis
    HighAlreadyReset = False    ### If data for high frequencies has been reset
    LowAlreadyReset = False      ### If data for low frequencies has been reset
    analysis_complete = False    ### If analysis has completed, begin PostAnalysis

    return key,search_lim,PoisonPill,FoundFilePath,ExistVar,AlreadyInitiated,HighAlreadyReset,LowAlreadyReset,analysis_complete

def data_extraction_parameter():
    delimiter = 1               ### default delimiter is a space; 2 = tab
    extension = 1
    current_column = 4           ### column index for list_val.
    current_column_index = 3
                                # list_val = column_index + 3
                                # defauly column is the second (so index = 1)
    voltage_column = 1
    voltage_column_index = 0
    spacing_index = 3

    #-- set the initial limit in bytes to filter out preinitialized files < 3000b
    byte_limit = 3000
    #- set the initial bite index to match the checkButton
    #- index in the toolbar menu MainWindow.byte_menu
    byte_index = 2
    return delimiter,extension,current_column,current_column_index,voltage_column,voltage_column_index,spacing_index,byte_limit,byte_index

def low_freq_parameter():
    LowFrequencyOffset = 0         ### Vertical offset of normalized data for
                                ### user specified 'Low Frequency'
    LowFrequencySlope = 0          ### Slope manipulation of norm data for user
                                ### specified 'Low Frequency'
    return LowFrequencyOffset,LowFrequencySlope

def font_specification():
    HUGE_FONT = ('Verdana', 18)
    LARGE_FONT = ('Verdana', 11)
    MEDIUM_FONT = ('Verdana', 10)
    SMALL_FONT = ('Verdana', 8)
    return HUGE_FONT,LARGE_FONT,MEDIUM_FONT,SMALL_FONT
