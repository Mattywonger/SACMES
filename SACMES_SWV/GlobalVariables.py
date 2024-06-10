import Config

handle_variable,e_var,PHE_method,InputFrequencies,electrodes = Config.globalvar_config()
high_xstart = None
high_xend = None
low_xstart = None
low_xend = None
sg_window,sg_degree,polyfit_deg,cutoff_frequency = Config.regressionvar_config()
key,search_lim,PoisonPill,FoundFilePath,ExistVar,AlreadyInitiated,HighAlreadyReset,LowAlreadyReset,analysis_complete= Config.checkpoint_parameter()
delimiter,extension,current_column,current_column_index,voltage_column,voltage_column_index,spacing_index,byte_limit,byte_index = Config.data_extraction_parameter()


LowFrequencyOffset,LowFrequencySlope = Config.low_freq_parameter()
HUGE_FONT,LARGE_FONT,MEDIUM_FONT,SMALL_FONT = Config.font_specification()

#Retrieved from GUI

normalized_ratiometric_data_list = None
anim = None
plot_list = None
ratiometric_plots = None
PlotContainer = None
starting_file = None
EmptyPlots = None
FileLabel = None
DataFolder = None
FileHandle = None
ExportFilePath = None
RealTimeSampleLabel = None
ExportPath = None
ShowFrames = None
frame_list = None
PlotValues = None
figures = None
ratiometric_figures = None
NormalizationPoint = None
data_list = None
normalized_data_list = None
file_list = None
offset_normalized_data_list = None
NormWarning = None
KDM_list = None






