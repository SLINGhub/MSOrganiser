from MSRawData import AgilentMSRawData
from MSRawData import SciexMSRawData
from MSCalculate import ISTD_Operations
import os

#TODO 
#One function to output everything
#One function perhaps to report everything
#Get different dfs
#Calculate vs get ...

class MSAnalysis():
    """To describe the analysis being done"""

    def __init__(self, MS_FilePath, createReport=False ,logger=None, ingui=True, testing=False):
        self.MS_FilePath = MS_FilePath
        self.logger = logger
        self.ingui = ingui
        self.testing = testing

        #Check if file is from Agilent or Sciex
        if MS_FilePath.endswith('.csv'):
            self.RawData = AgilentMSRawData(filepath=MS_FilePath,logger=logger)
        elif MS_FilePath.endswith('.txt'):
            self.RawData = SciexMSRawData(filepath=MS_FilePath,logger=logger)

        #For analysis then depends on other analysis
        self.norm_Area_df = None
        self.ISTD_map_df = None
        self.Sample_Annot_df = None

    def get_Normalised_Area(self,analysis_name,Annotation_FilePath):
        #Perform normalisation using ISTD
        ##Get Area Table
        Area_df = self.RawData.get_table('Area',is_numeric=True)
        
        #Get ISTD map df
        ISTD_map_df = ISTD_Operations.read_ISTD_map(Annotation_FilePath,analysis_name,self.logger,ingui=self.ingui)
        
        #Perform normalisation using ISTD
        [norm_Area_df,ISTD_Area,ISTD_Report] = ISTD_Operations.normalise_by_ISTD(Area_df,ISTD_map_df,self.logger,ingui=self.ingui)

        self.norm_Area_df = norm_Area_df
        self.ISTD_map_df = ISTD_map_df

        return([norm_Area_df,ISTD_Area,ISTD_Report])

    def get_Analyte_Concentration(self,analysis_name,Annotation_FilePath):
        #Perform concentration calculation, we need norm_Area_df, ISTD_map_df and Sample_Annot_df
        Sample_Annot_df = ISTD_Operations.read_Sample_Annot(Annotation_FilePath,[os.path.basename(self.MS_FilePath)],analysis_name,self.logger,ingui=self.ingui)
        [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df] = ISTD_Operations.getConc_by_ISTD(norm_Area_df,ISTD_map_df,Sample_Annot_df,logger,ingui=self.ingui)
