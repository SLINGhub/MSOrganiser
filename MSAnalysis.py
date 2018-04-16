from MSRawData import AgilentMSRawData
from MSRawData import SciexMSRawData
from MSCalculate import ISTD_Operations
import os

class MS_Analysis():
    """
    A class to set up the right configurations before performing data analysis

    Args:
        MS_FilePath (str): File path of the input MRM transition name file
        logger (object): logger object created by start_logger in MSOrganiser
        ingui (bool): if True, print analysis status to screen
    """

    def __init__(self, MS_FilePath,logger=None, ingui=True):
        self.MS_FilePath = MS_FilePath
        self.logger = logger
        self.ingui = ingui

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
        """Function to get a specific column from the input MRM transition name data.

        Args:
            column_name (str): The name of the column given in the Output_Options.

        Returns:
            Output_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with values from the chosen column name

        """

        #We extract the data directly from the file and output accordingly
        Output_df = self.RawData.get_table(column_name,is_numeric=True)
        return Output_df

    def get_Normalised_Area(self,analysis_name,Annotation_FilePath,outputdata=True):
        """Function to calculate the normalised area from the input MRM transition name data and MS Template Creator annotation file.

        Args:
            analysis_name (str): The name of the column given in the Output_Options. Should be "normArea by ISTD"
            Annotation_FilePath (str): The file path to the MS Template Creator annotation file
            outputdata (bool): if True, return the results as a pandas dataframe. Else, the dataframe is stored in the class and nothing is returned
        
        When outputdata is set to True,

        Returns:
            (list): list containing:

                * norm_Area_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with the normalised area as values
                * ISTD_Area (pandas DataFrame): A data frame of sample as rows and transition names as columns with the ISTD area as values. Output as excel only at testing mode
                * ISTD_map_df (pandas DataFrame): A data frame of showing the transition names annotation
                * ISTD_Report (pandas DataFrame): A data frame of with transition names, its corresponding ISTD as columns. This will be converted to a pdf file page

        """

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
        """Function to calculate the transition names concentration from the input MRM transition name data and MS Template Creator annotation file.

        Args:
            analysis_name (str): The name of the column given in the Output_Options. Should be "normConc by ISTD"
            Annotation_FilePath (str): The file path to the MS Template Creator annotation file
            outputdata (bool): if True, return the results as a pandas dataframe. Else, the dataframe is stored in the class and nothing is returned
        
        When outputdata is set to True,

        Returns:
            (list): list containing:

                * norm_Conc_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with the transition name concentration as values
                * ISTD_Conc_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with the ISTD concentration as values
                * ISTD_Samp_Ratio_df (pandas DataFrame): A data frame of with transition names, its corresponding ISTD and ISTD to Sample ratio as columns
                * Sample_Annot_df (pandas DataFrame): A data frame showing the samples annotation

        """

        #Perform normalisation using ISTD if it is not done earlier
        if(self.norm_Area_df is None or self.ISTD_map_df is None):
            self.get_Normalised_Area(analysis_name,Annotation_FilePath,outputdata=False)

        #Perform concentration calculation, we need norm_Area_df, ISTD_map_df and Sample_Annot_df
        Sample_Annot_df = ISTD_Operations.read_Sample_Annot(Annotation_FilePath,[os.path.basename(self.MS_FilePath)],analysis_name,self.logger,ingui=self.ingui)
        self.Sample_Annot_df = Sample_Annot_df

        [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df] = ISTD_Operations.getConc_by_ISTD(self.norm_Area_df,self.ISTD_map_df,self.Sample_Annot_df,self.logger,ingui=self.ingui)

        if outputdata:
            return([norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df])