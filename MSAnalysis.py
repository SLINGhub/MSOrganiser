from MSRawData import AgilentMSRawData
from MSRawData import SciexMSRawData
from MSCalculate import ISTD_Operations
import os

class MS_Analysis():
    """To describe the analysis being done"""

    def __init__(self, MS_FilePath,OutputFormat,logger=None, ingui=True, testing=False):
        self.MS_FilePath = MS_FilePath
        self.OutputFormat = OutputFormat
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

    def get_from_Input_Data(self,column_name):
        #We extract the data directly from the file and output accordingly
        Output_df = self.RawData.get_table(column_name,is_numeric=True)
        return Output_df

    def get_Normalised_Area(self,analysis_name,Annotation_FilePath,outputdata=True):
        #Perform normalisation using ISTD
        ##Get Area Table
        Area_df = self.RawData.get_table('Area',is_numeric=True)
        
        #Get ISTD map df
        ISTD_map_df = ISTD_Operations.read_ISTD_map(Annotation_FilePath,analysis_name,self.logger,ingui=self.ingui)
        self.ISTD_map_df = ISTD_map_df

        #Perform normalisation using ISTD
        [norm_Area_df,ISTD_Area,ISTD_Report] = ISTD_Operations.normalise_by_ISTD(Area_df,self.ISTD_map_df,self.logger,ingui=self.ingui)
        self.norm_Area_df = norm_Area_df

        if outputdata:
            return([norm_Area_df,ISTD_Area,ISTD_map_df,ISTD_Report])

    def get_Analyte_Concentration(self,analysis_name,Annotation_FilePath,outputdata=True):

        #Perform normalisation using ISTD if it is not done earlier
        if(self.norm_Area_df is None or self.ISTD_map_df is None):
            self.get_Normalised_Area(analysis_name,Annotation_FilePath,outputdata=False)

        #Perform concentration calculation, we need norm_Area_df, ISTD_map_df and Sample_Annot_df
        Sample_Annot_df = ISTD_Operations.read_Sample_Annot(Annotation_FilePath,[os.path.basename(self.MS_FilePath)],analysis_name,self.logger,ingui=self.ingui)
        self.Sample_Annot_df = Sample_Annot_df

        [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df] = ISTD_Operations.getConc_by_ISTD(self.norm_Area_df,self.ISTD_map_df,self.Sample_Annot_df,self.logger,ingui=self.ingui)

        if outputdata:
            return([norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df])