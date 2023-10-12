
def process_continuous_scan(e_var,handle_variable,frequency,file,extension,electrode):
            if e_var == 'single':
                filename = '%s%dHz_%d%s' % (handle_variable, frequency, file,extension)
                filename2 = '%s%dHz__%d%s' % (handle_variable, frequency, file,extension)
                filename3 = '%s%dHz_#%d%s' % (handle_variable, frequency, file,extension)
                filename4 = '%s%dHz__#%d%s' % (handle_variable, frequency, file,extension)

            elif e_var == 'multiple':
                filename = 'E%s_%s%sHz_%d%s' % (electrode,handle_variable,frequency,file,extension)
                filename2 = 'E%s_%s%sHz__%d%s' % (electrode,handle_variable,frequency,file,extension)
                filename3 = 'E%s_%s%sHz_#%d%s' % (electrode,handle_variable,frequency,file,extension)
                filename4 = 'E%s_%s%sHz__#%d%s' % (electrode,handle_variable,frequency,file,extension)

            return filename, filename2, filename3, filename4

def process_Frequencymap(e_var,handle_variable, frequency, file, extension,electrode):
    if e_var == 'single':
                filename = '%s%dHz%s' % (handle_variable, frequency, extension)
                filename2 = '%s%dHz_%s' % (handle_variable, frequency, extension)
                filename3 = '%s%dHz_%d%s' % (handle_variable, frequency, file, extension)
                filename4 = '%s%dHz__%d%s' % (handle_variable, frequency, file, extension)
                filename5 = '%s%dHz_#%d%s' % (handle_variable, frequency, file, extension)
                filename6 = '%s%dHz__#%d%s' % (handle_variable, frequency, file, extension)


    elif e_var == 'multiple':
                filename = 'E%s_%s%sHz%s' % (electrode,handle_variable,frequency, extension)
                filename2 = 'E%s_%s%sHz_%s' % (electrode,handle_variable,frequency, extension)
                filename3 = 'E%s_%s%sHz_%d%s' % (electrode,handle_variable,frequency,file, extension)
                filename4 = 'E%s_%s%sHz__%d%s' % (electrode,handle_variable,frequency,file, extension)
                filename5 = 'E%s_%s%sHz_#%d%s' % (electrode,handle_variable,frequency,file, extension)
                filename6 = 'E%s_%s%sHz__#%d%s' % (electrode,handle_variable,frequency,file, extension)

    return filename, filename2, filename3, filename4, filename5, filename6