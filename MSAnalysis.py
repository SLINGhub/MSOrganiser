from MSRawData import AgilentMSRawData
from MSRawData import SciexMSRawData
from MSCalculate import ISTD_Operations
import os
import sys
import pandas as pd

class MS_Analysis():
    """
    A class to set up the right configurations before performing data analysis

    Args:
        MS_FilePath (str): File path of the input MRM transition name file
        logger (object): logger object created by start_logger in MSOrganiser
        ingui (bool): if True, print analysis status to screen
        longform (bool): if True, prepare a dataframe to store results in long form
    """

    def __init__(self, MS_FilePath , logger=None, ingui=True,  longform = False):
        self.MS_FilePath = MS_FilePath
        self.logger = logger
        self.ingui = ingui

        #Check if file is from Agilent or Sciex
        if MS_FilePath.endswith('.csv'):
            self.RawData = AgilentMSRawData(filepath=MS_FilePath,logger=logger)
        elif MS_FilePath.endswith('.txt'):
            self.RawData = SciexMSRawData(filepath=MS_FilePath,logger=logger)

        #Initialise the data in long form starting with an empty dataframe
        self.LongForm_df = pd.DataFrame()
        self.LongForm = False
        if longform:
            self.LongForm = True

        #For analysis that depends on other analysis
        self.norm_Area_df = None
        self.ISTD_map_df = None
        self.Sample_Annot_df = None

    def _add_to_LongForm_df(self,wide_df,column_name):
        wide_df = pd.melt(wide_df,id_vars=["Sample_Name"],var_name="Transition_Name", value_name=column_name)
        if self.LongForm_df.empty:
            self.LongForm_df = wide_df
        else:
            self.LongForm_df = pd.merge(self.LongForm_df, wide_df , on=["Sample_Name","Transition_Name"], how='left')
        print(self.LongForm_df.columns)

    def get_Long_Form(self):
        """Function to get the long form of the extracted or calculated MRM transition name data.

        Returns:
            Output_df (pandas DataFrame): A long data frame of with column name Sample_Name, Transition_Name and other relevant data

        """
        return self.LongForm_df

    def get_from_Input_Data(self,column_name):
        """Function to get a specific column from the input MRM transition name data.

        Args:
            column_name (str): The name of the column given in the Output_Options.

        Returns:
            Output_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with values from the chosen column name

        """

        #We extract the data directly from the file and output accordingly
        Output_df = self.RawData.get_table(column_name,is_numeric=True)

        if self.LongForm:
            MS_Analysis._add_to_LongForm_df(self,Output_df,column_name)

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

        #Create the Long Form dataframe
        if self.LongForm:
            if self.LongForm_df.empty:
                self.LongForm_df = ISTD_map_df[["Transition_Name","Transition_Name_ISTD"]]
            else:
                self.LongForm_df = pd.merge(self.LongForm_df, ISTD_map_df[["Transition_Name","Transition_Name_ISTD"]] , on=["Transition_Name"], how='left')
            MS_Analysis._add_to_LongForm_df(self,norm_Area_df,"normArea")

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

        #Create the Long Form dataframe
        if self.LongForm:
            if self.LongForm_df.empty:
                self.LongForm_df = Sample_Annot_df[["Sample_Name","Sample_Type"]]
            else:
                self.LongForm_df = pd.merge(self.LongForm_df, Sample_Annot_df[["Sample_Name","Sample_Type"]] , on=["Sample_Name"], how='left')
            MS_Analysis._add_to_LongForm_df(self,norm_Conc_df,"normConc")

        if outputdata:
            return([norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df])