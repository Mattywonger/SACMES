from GlobalVariables import *
class WaitTime():

    def __init__(self):
        global NormalizationWaiting

        NormalizationWaiting = False


    def NormalizationWaitTime(self):
        global NormalizationWaiting

        NormalizationWaiting = True

    def NormalizationProceed(self):
        global NormalizationWaiting

        NormalizationWaiting = False