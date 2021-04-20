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
        Annotation_FilePath (str): The file path to the MS Template Creator annotation file if provided
        logger (object): logger object created by start_logger in MSOrganiser
        ingui (bool): if True, print analysis status to screen
        longtable (bool): if True, prepare a dataframe to store results in long table
    """

    def __init__(self, MS_FilePath , MS_FileType ,Annotation_FilePath=None, logger=None, ingui=True,  longtable = False, longtable_annot = False):
        self.MS_FilePath = MS_FilePath
        self.logger = logger
        self.ingui = ingui

        #Check if file is from Agilent or Sciex
        if MS_FileType in ['Agilent Wide Table in csv', 'Agilent Compound Table in csv']:
            if MS_FilePath.endswith('.csv'):
                self.RawData = AgilentMSRawData(filepath=MS_FilePath,logger=logger)
            else:
                if self.ingui:
                    print('Filepath ' + str(MS_FilePath) + ' must have a .csv extention',flush=True)
                if self.logger:
                    self.logger.error('Filepath %s must have a .csv extention',MS_FilePath)
                sys.exit(-1)
        elif MS_FileType in ['Multiquant Long Table in txt']:
            if MS_FilePath.endswith('.txt'):
                self.RawData = SciexMSRawData(filepath=MS_FilePath,logger=logger)
            else:
                if self.ingui:
                    print('Filepath ' + str(MS_FilePath) + ' must have a .txt extention',flush=True)
                if self.logger:
                    self.logger.error('Filepath %s must have a .txt extention',MS_FilePath)
                sys.exit(-1)

        #Annotation File Path
        self.Annotation_FilePath = Annotation_FilePath

        #Initialise the data in long table starting with an empty dataframe
        self.LongTable_df = pd.DataFrame()

        self.LongTable = longtable
        self.LongTable_Annot = longtable_annot


        #For analysis that depends on other analysis

        self.norm_Area_df = pd.DataFrame()
        self.ISTD_map_df = pd.DataFrame()
        self.Sample_Annot_df = pd.DataFrame()

    def _add_to_LongTable_df(self,wide_df,column_name,allow_multiple_istd = False):

        if allow_multiple_istd:
            wide_df = pd.melt(wide_df,id_vars=["Sample_Name"],
                              var_name= ["Transition_Name","Transition_Name_ISTD"],
                              value_name=column_name)
            if self.LongTable_df.empty:
                self.LongTable_df = wide_df
            else:
                self.LongTable_df = pd.merge(self.LongTable_df, wide_df , 
                                             on=["Sample_Name","Transition_Name","Transition_Name_ISTD"], 
                                             how='left')
        else:
            wide_df = pd.melt(wide_df,id_vars=["Sample_Name"],var_name="Transition_Name", value_name=column_name)
            if self.LongTable_df.empty:
                self.LongTable_df = wide_df
            else:
                self.LongTable_df = pd.merge(self.LongTable_df, wide_df , on=["Sample_Name","Transition_Name"], how='left')

    def get_Long_Table(self, allow_multiple_istd = False):
        """Function to get the long table of the extracted or calculated MRM transition name data.

        Args:
            allow_multiple_istd (bool): if True, allow Transition_Annot data by to have mulitple internal standards (in development)

        Returns:
            Output_df (pandas DataFrame): A long data frame of with column name Sample_Name, Transition_Name and other relevant data

        """

        #Check if the Long Table has data
        if self.LongTable_df.empty:
            if self.logger:
                self.logger.warning("Long Table has no data")
            if self.ingui:
                print("Long Table has no data",flush=True)
            return self.LongTable_df

        #If we ask for the Sample Type and Transition Name ISTD to be present in the Long Table and an annotation file is given
        if self.LongTable_Annot and self.Annotation_FilePath:
            #To handle the case when no normalization is required but we still need to read the annotation file
            if self.ISTD_map_df.empty:
                self.ISTD_map_df = ISTD_Operations.read_ISTD_map(self.Annotation_FilePath,"LongTable",logger=self.logger,
                                                                 ingui=self.ingui, doing_normalization = False, 
                                                                 allow_multiple_istd = allow_multiple_istd)
            if self.Sample_Annot_df.empty:
                self.Sample_Annot_df = ISTD_Operations.read_Sample_Annot(self.Annotation_FilePath,[os.path.basename(self.MS_FilePath)],"LongTable",
                                                                         logger = self.logger, ingui = self.ingui)
            #self.LongTable can never be empty as it must have at least one output option e.g "Area"
            #It could be the case that the df is empty after reading the file
            if not self.ISTD_map_df.empty:
                #No merging is required for the case of allow_multiple_istd
                #if allow_multiple_istd:
                if not allow_multiple_istd:
                    merge_column = ["Transition_Name","Transition_Name_ISTD"]
                    self.LongTable_df = pd.merge(self.LongTable_df, self.ISTD_map_df[[item for item in merge_column if item in self.ISTD_map_df.columns.tolist()]] , 
                                                 on=["Transition_Name"], how='left')
            if not self.Sample_Annot_df.empty:
                merge_column = ["Sample_Name","Sample_Type","Concentration_Unit"]
                self.LongTable_df = pd.merge(self.LongTable_df, self.Sample_Annot_df[[item for item in merge_column if item in self.Sample_Annot_df.columns.tolist()]] , 
                                             on=["Sample_Name"], how='left')

        #Reorder the columns
        col_order = self.LongTable_df.columns.tolist()
        if self.LongTable_Annot and self.Annotation_FilePath:
            first_few_column = ["Transition_Name","Transition_Name_ISTD","Sample_Name","Sample_Type","Concentration_Unit"]
            col_order =  [item for item in first_few_column if item in col_order]  + [item for item in col_order if item not in first_few_column]
        else:
            if allow_multiple_istd  and "Transition_Name_ISTD" in self.LongTable_df.columns.tolist():
                col_order = ["Transition_Name","Transition_Name_ISTD","Sample_Name"] + [item for item in col_order if item not in ["Transition_Name","Transition_Name_ISTD","Sample_Name"]]
            else:
                col_order = ["Transition_Name","Sample_Name"] + [item for item in col_order if item not in ["Sample_Name","Transition_Name"]]

        self.LongTable_df = self.LongTable_df[col_order] 

        return self.LongTable_df

    def get_from_Input_Data(self,column_name,allow_multiple_istd = False):
        """Function to get a specific column from the input MRM transition name data.

        Args:
            column_name (str): The name of the column given in the Output_Options.
            allow_multiple_istd (bool): if True, allow normalisation of peak area by mulitple internal standards which leads to an expansion of the Output_df

        Returns:
            Output_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with values from the chosen column name

        """

        #We extract the data directly from the file and output accordingly
        Output_df = self.RawData.get_table(column_name,is_numeric=True)

        if allow_multiple_istd:
            #Get ISTD map df
            ISTD_map_df = ISTD_Operations.read_ISTD_map(self.Annotation_FilePath,column_name,
                                                        logger=self.logger,ingui=self.ingui, 
                                                        doing_normalization = False, 
                                                        allow_multiple_istd = allow_multiple_istd)
            self.ISTD_map_df = ISTD_map_df
            
            # We set the ingui to False by now to avoid multiple printing of errors such as
            # There are Transition_Names in data set mentioned in the Transition_Name_Annot sheet 
            # but have a blank Transition_Name_ISTD.
            # We only need to print it once during the normalisation stage.
            [ISTD_report,Transition_Name_dict] = ISTD_Operations.create_Transition_Name_dict(Output_df,self.ISTD_map_df,
                                                                                             logger=self.logger,ingui=False,
                                                                                             allow_multiple_istd = allow_multiple_istd)
            Output_df = ISTD_Operations.expand_Transition_Name_df(Output_df,Transition_Name_dict,
                                                                  logger=self.logger,ingui=self.ingui)

        if self.LongTable:
            MS_Analysis._add_to_LongTable_df(self,Output_df,column_name,allow_multiple_istd)

        return Output_df

    def get_Normalised_Area(self,analysis_name,outputdata=True,allow_multiple_istd = False):
        """Function to calculate the normalised area from the input MRM transition name data and MS Template Creator annotation file.

        Args:
            analysis_name (str): The name of the column given in the Output_Options. Should be "normArea by ISTD"
            outputdata (bool): if True, return the results as a pandas dataframe. Else, the dataframe is stored in the class and nothing is returned
            allow_multiple_istd (bool): if True, allow normalisation of peak area by mulitple internal standards (in development)
        
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
        ISTD_map_df = ISTD_Operations.read_ISTD_map(self.Annotation_FilePath,analysis_name,
                                                    logger=self.logger,ingui=self.ingui, 
                                                    doing_normalization = True, 
                                                    allow_multiple_istd = allow_multiple_istd)
        self.ISTD_map_df = ISTD_map_df


        [ISTD_report,Transition_Name_dict] = ISTD_Operations.create_Transition_Name_dict(Area_df,self.ISTD_map_df,
                                                                                         logger=self.logger,ingui=self.ingui,
                                                                                         allow_multiple_istd = allow_multiple_istd)

        ##Update the Area_df so that it can be normalised by multiple ISTD
        if allow_multiple_istd:
            Area_df = ISTD_Operations.expand_Transition_Name_df(Area_df,Transition_Name_dict,
                                                logger=self.logger,ingui=self.ingui)

        #Perform normalisation using ISTD
        [norm_Area_df,ISTD_Area] = ISTD_Operations.normalise_by_ISTD(Area_df,Transition_Name_dict,
                                                                     logger=self.logger,ingui=self.ingui,
                                                                     allow_multiple_istd = allow_multiple_istd)
        self.norm_Area_df = norm_Area_df

        #Create the Long Table dataframe
        if self.LongTable:
            MS_Analysis._add_to_LongTable_df(self,norm_Area_df,"normArea",allow_multiple_istd)

        if outputdata:
            return([norm_Area_df,ISTD_Area,ISTD_map_df,ISTD_report])

    def get_Analyte_Concentration(self,analysis_name,outputdata=True,allow_multiple_istd = False):
        """Function to calculate the transition names concentration from the input MRM transition name data and MS Template Creator annotation file.

        Args:
            analysis_name (str): The name of the column given in the Output_Options. Should be "normConc by ISTD"
            outputdata (bool): if True, return the results as a pandas dataframe. Else, the dataframe is stored in the class and nothing is returned
            allow_multiple_istd (bool): if True, allow normalisation of peak area by mulitple internal standards
        
        When outputdata is set to True,

        Returns:
            (list): list containing:

                * norm_Conc_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with the transition name concentration as values
                * ISTD_Conc_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with the ISTD concentration as values
                * ISTD_Samp_Ratio_df (pandas DataFrame): A data frame of with transition names, its corresponding ISTD and ISTD to Sample ratio as columns
                * Sample_Annot_df (pandas DataFrame): A data frame showing the samples annotation

        """

        #Perform normalisation using ISTD if it is not done earlier
        if(self.norm_Area_df.empty or self.ISTD_map_df.empty):
            self.get_Normalised_Area(analysis_name,
                                     outputdata=False,allow_multiple_istd = allow_multiple_istd)

        #Perform concentration calculation, we need norm_Area_df, ISTD_map_df and Sample_Annot_df
        Sample_Annot_df = ISTD_Operations.read_Sample_Annot(self.Annotation_FilePath,[os.path.basename(self.MS_FilePath)],analysis_name,
                                                            logger= self.logger, ingui=self.ingui)
        self.Sample_Annot_df = Sample_Annot_df

        [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df] = ISTD_Operations.getConc_by_ISTD(self.norm_Area_df,self.ISTD_map_df,self.Sample_Annot_df,
                                                                                         logger=self.logger,ingui=self.ingui,
                                                                                         allow_multiple_istd = allow_multiple_istd)

        #Create the Long Form dataframe
        if self.LongTable:
            MS_Analysis._add_to_LongTable_df(self,norm_Conc_df,"normConc",allow_multiple_istd)

        if outputdata:
            return([norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df])