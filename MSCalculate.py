import pandas as pd
import numpy as np
import sys
import os
import logging

from openpyxl import load_workbook
from Annotation import MS_Template

class ISTD_Operations():
    """A collection of functions to perform calculation relating to ISTD"""

    #def __init__( logger=None,ingui=True):
        #logger = logger
        #ingui = ingui
        #Transition_Name_dict = {}
        #ISTD_report = []

    #def remove_whiteSpaces(df):
        ##Strip the whitespaces for each string columns of a df
        #df[df.select_dtypes(['object']).columns] = df.select_dtypes(['object']).apply(lambda x: x.str.strip())
        #return df

    def read_ISTD_map(filepath,column_name,logger=None,ingui=False,
                      doing_normalization = False, allow_multiple_istd = False):
        """Function to get the transition names annotation dataframe from the MS Template Creator annotation file.

        Args:
            filepath (str): The file path to the MS Template Creator annotation file
            column_name (str): The name of the column given in the Output_Options.
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen
            doing_normalization (bool): if True, check if input file has data. If no data, throws an error
            allow_multiple_istd (bool): if True, allow normalization of data by mulitple internal standards

        Returns:
            Transition_Name_Annot_df (pandas DataFrame): A data frame of showing the transition names annotation

        """

        AnnotationList = MS_Template(filepath=filepath,column_name=column_name, logger=logger,ingui=ingui,
                                     doing_normalization = doing_normalization, allow_multiple_istd = allow_multiple_istd)
        Transition_Name_Annot_df = AnnotationList.Read_Transition_Name_Annot_Sheet()
        ISTD_Annot_df = AnnotationList.Read_ISTD_Annot_Sheet()
        
        if not ISTD_Annot_df.empty:
            #Additional check to ensure each Transition_Name_ISTD in Transition_Name_Annot sheet has 
            #Also appears in  the ISTD_Annot sheet
            ISTD_list_in_Transition_Name_Annot_sheet = list(filter(None,Transition_Name_Annot_df['Transition_Name_ISTD'].unique()))
            ISTD_list_in_Annot_sheet = list(filter(None,ISTD_Annot_df['Transition_Name_ISTD'].unique()))
            missing_ISTD = set(ISTD_list_in_Transition_Name_Annot_sheet) - set(ISTD_list_in_Annot_sheet)
            if missing_ISTD:
                if logger:
                    logger.warning('There are Transition_Name_ISTD in Transition_Name_Annot not mentioned in ISTD_Annot.')
                if ingui:
                    print('There are Transition_Name_ISTD in Transition_Name_Annot not mentioned in ISTD_Annot.',flush=True)
                for Transition_Name in missing_ISTD:
                    if logger:
                        logger.warning('/"%s/"',Transition_Name)
                    if ingui:
                        print('\"' + Transition_Name + '\"',flush=True)
            #Merge the two data frame by common ISTD
            Transition_Name_Annot_df = pd.merge(Transition_Name_Annot_df, ISTD_Annot_df, on='Transition_Name_ISTD', how='outer')

        if not Transition_Name_Annot_df.empty:
            #Remove Rows with ISTD with no Transition_Names
            Transition_Name_Annot_df = Transition_Name_Annot_df.dropna(subset=['Transition_Name'])

        return Transition_Name_Annot_df

    def read_Sample_Annot(filepath,MS_FilePathList,column_name,logger=None,ingui=False):
        """Function to get the sample names annotation dataframe from the MS Template Creator annotation file.

        Args:
            filepath (str): The file path to the MS Template Creator annotation file
            MS_FilePathList (list): A list of MRM transition name file names.
            column_name (str): The name of the column given in the Output_Options.
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen

        Note:
            The list of MRM transition name file names names is to help the program properly filter 
            the Sample annotation such that we only pick rows whose Data_File_Name values is in the list. 
            Currently, our input is set as [os.path.basename(self.MS_FilePath)] from MSAnalysis.

        Returns:
            Sample_Annot_df (pandas DataFrame): A data frame of showing the sample names annotation

        """
        AnnotationList = MS_Template(filepath=filepath,column_name=column_name, logger=logger,ingui=ingui)
        Sample_Annot_df = AnnotationList.Read_Sample_Annot_Sheet(MS_FilePathList)
        return Sample_Annot_df

    def _validate_Transition_Name_df(Transition_Name_df,logger=None,ingui=False):
        if "Sample_Name" not in Transition_Name_df:
            if logger:
                logger.error("The input data frame does not contain the column Sample_Name")
                logger.error("If input raw file is from MassHunter, make sure the column Data File is present")
                logger.error("If input raw file is from Sciex, make sure the column Sample Name is present")
            if ingui:
                print("The input data frame does not contain the Sample_Name",flush=True)
                print("If input raw file is from MassHunter, make sure the column Data File is present",flush=True)
                print("If input raw file is from Sciex, make sure the column Sample Name is present")
            sys.exit(-1)

    def _validate_Sample_Annot_df(Sample_Annot_df,logger=None,ingui=False):
        if "Sample_Name" not in Sample_Annot_df:
            if logger:
                logger.error("The sample annotation file does not contain the column Sample_Name")
            if ingui:
                print("The sample annotation file does not contain the Sample_Name",flush=True)
            sys.exit(-1)

    def _create_ISTD_data_from_Transition_Name_df(Transition_Name_df,Transition_Name_Annot_df,
                                                  logger=None,ingui=False,
                                                  allow_multiple_istd = False):
        """
        Create the ISTD data from Transition_Name df and ISTD map file

        Args:
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            Transition_Name_Annot_df (pandas DataFrame): A data frame of showing the transition names annotation
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen
            allow_multiple_istd (bool): if True, ISTD data can have mulitple internal standards for one transition

        Returns:
            (list): list containing:

                * ISTD_report (pandas DataFrame): A data frame of with transition names, its corresponding ISTD as columns. This will be converted to a pdf file page
                * ISTD_data (pandas DataFrame): A data frame of sample as rows and transition names as columns with the ISTD area as values. Output as excel only at testing mode
        """

        #Create a dictionary to map the Transition_Name to the Transition_Name_ISTD and an ISTD report to map Transition_Name_ISTD to Transition_Name
        #We start a new Transition_Name_dict and ISTD_report
        Transition_Name_dict = {}
        ISTD_report = []

        #Create the Transition_Name_dict and ISTD_report
        Transition_Name_df.iloc[:,1:].apply(lambda x: ISTD_Operations._update_Transition_Name_dict(x=x,Transition_Name_Annot_df=Transition_Name_Annot_df,
                                                                                                   Transition_Name_dict=Transition_Name_dict,
                                                                                                   ISTD_report_list = ISTD_report,
                                                                                                   logger=logger,ingui=ingui,
                                                                                                   allow_multiple_istd = allow_multiple_istd)
                                            ,axis=0)
        #print(Transition_Name_dict)

        #Create empty dataframe with a preset column name and index
        if allow_multiple_istd:
            # Initialize empty list
            tuples=[("Sample_Name","Sample_Name")]
            for Transition_Name in Transition_Name_dict:
                for Transition_Name_ISTD in Transition_Name_dict[Transition_Name]:
                    tuples.append((Transition_Name, Transition_Name_ISTD))
            column_index = pd.MultiIndex.from_tuples(tuples, names=["Transition_Name", "Transition_Name_ISTD"])
            ISTD_data = pd.DataFrame(columns=column_index, index=Transition_Name_df["Sample_Name"])
        else:
            ISTD_data = pd.DataFrame(columns=Transition_Name_df.columns, index=Transition_Name_df.index)

        #Sample_Name must be present
        ISTD_Operations._validate_Transition_Name_df(Transition_Name_df,logger,ingui)
        ISTD_data["Sample_Name"] = Transition_Name_df["Sample_Name"]    

        #Create a ISTD table from the Transition_Name df
        ISTD_data.iloc[:,1:].apply(lambda x: ISTD_Operations._update_ISTD_data_from_Transition_Name_df(x=x,
                                                                                                       Transition_Name_dict=Transition_Name_dict,
                                                                                                       Transition_Name_df=Transition_Name_df,
                                                                                                       ISTD_report_list = ISTD_report,
                                                                                                       logger=logger,ingui=ingui,
                                                                                                       allow_multiple_istd = allow_multiple_istd),
                                   axis=0)

        #Convert ISTD report from list to dataframe and report any warnings if any
        ISTD_report = pd.DataFrame(ISTD_report)
        ISTD_report.columns=(['Transition_Name_ISTD','Transition_Name'])
        ISTD_report = ISTD_report.sort_values(by=['Transition_Name_ISTD','Transition_Name'])

        #Check ISTD_report for any problems
        if "!Missing Transition_Name in map file" in ISTD_report['Transition_Name_ISTD'].unique():
            if ingui:
                print("There are Transition_Names in data set not mentioned in the Transition_Name_Annot sheet.",flush=True)
                for things in ISTD_report.loc[ ISTD_report['Transition_Name_ISTD'] == "!Missing Transition_Name in map file" , 'Transition_Name' ]:
                    print('\"' + things + '\"',flush=True)

        if "!Duplicate Transition_Name_ISTD in map file" in ISTD_report['Transition_Name_ISTD'].unique():
            if ingui:
                print("There are Transition_Names in data set with more than one Transition_Name_ISTDs mentioned in the Transition_Name_Annot sheet.",flush=True)
                for things in ISTD_report.loc[ ISTD_report['Transition_Name_ISTD'] == "!Duplicate Transition_Name_ISTD in map file" , 'Transition_Name' ]:
                    print('\"' + things + '\"',flush=True)

        if "!Blank Transition_Name_ISTD in map file" in ISTD_report['Transition_Name_ISTD'].unique():
            if ingui:
                print("There are Transition_Names in data set mentioned in the Transition_Name_Annot sheet but have a blank Transition_Name_ISTD.",flush=True)
                for things in ISTD_report.loc[ ISTD_report['Transition_Name_ISTD'] == "!Blank Transition_Name_ISTD in map file" , 'Transition_Name' ]:
                    print('\"' + things + '\"',flush=True)

        if "!Missing Transition_Name_ISTD in data" in ISTD_report['Transition_Name_ISTD'].unique():
            if ingui:
                print("There are Transition_Name_ISTDs in the Transition_Name_Annot sheet that cannot be found in data set.",flush=True)
                for things in ISTD_report.loc[ ISTD_report['Transition_Name_ISTD'] == "!Missing Transition_Name_ISTD in data" , 'Transition_Name' ]:
                    print('\"' + things + '\"',flush=True)

        if "!Duplicate Transition_Name_ISTD in data" in ISTD_report['Transition_Name_ISTD'].unique():
            if ingui:
                print("There are Transition_Name_ISTDs in the Transition_Name_Annot sheet that are duplicated in data set. Please check input file",flush=True)
                for things in ISTD_report.loc[ ISTD_report['Transition_Name_ISTD'] == "!Duplicate Transition_Name_ISTD in data" , 'Transition_Name' ]:
                    print('\"' + things + '\"',flush=True)

        #Make ISTD column to be the index
        ISTD_report = ISTD_report.set_index(['Transition_Name_ISTD'])

        return [ISTD_report,ISTD_data]

    def _update_Transition_Name_dict(x,Transition_Name_Annot_df,Transition_Name_dict,ISTD_report_list,
                                     logger=None,ingui=False,
                                     allow_multiple_istd = False):
        """Updating the Transition_Name dict to map Transition_Name to their Transition_Name_ISTD

        Args:
            x (pandas Series): A column from the ISTD_data to obtain the transition name
            Transition_Name_Annot_df (pandas DataFrame): A data frame of showing the transition names annotation
            Transition_Name_dict (dict): A dictionary to map each transition name to its ISTD. To be updated by each x
            ISTD_report_list (list): A list of tuples showing (ISTD name or reason why there is no ISTD,Transition name)
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen
            allow_multiple_istd (bool): if True, Transition_Name_dict can have mulitple internal standards for one transition

        """

        #Get the mapping of one Transition_Name to exactly one ISTD
        ISTD_list = Transition_Name_Annot_df.loc[Transition_Name_Annot_df['Transition_Name']==x.name,"Transition_Name_ISTD"].tolist()

        #print(x.name)
        #print(ISTD_list)

        if not ISTD_list:
            #ISTD_list None
            if logger:
                logger.warning("%s is not found in the Transition_Name_Annot sheet. Please check ISTD map file",x.name)
            Transition_Name_dict[x.name] = None
            ISTD_report_list.append(("!Missing Transition_Name in map file",x.name))
            return

        if allow_multiple_istd:
            #Check if each ISTD in the ISTD_List is valid
            valid_ISTD = []
            for ISTD_index,ISTD in enumerate(ISTD_list):
                if ISTD is None:
                    #ISTD may be None
                    if logger:
                        logger.warning("%s number %s has a blank internal standard. Please check ISTD map file",
                                       x.name, str(ISTD_index+1))
                    if ingui:
                        print(x.name + " number " +  str(ISTD_index+1) +
                              " has a blank internal standard. Please check ISTD map file", flush=True)
                    ISTD_report_list.append(("!Blank Transition_Name_ISTD in map file", x.name))
                elif not isinstance(ISTD,float):
                    #When we have a valid ISTD
                    valid_ISTD.append(ISTD)
                    ISTD_report_list.append((ISTD,x.name))
                elif np.isnan(ISTD):
                    #Value may be nan which is a type float
                    if logger:
                        logger.warning("%s number %s has a blank internal standard. Please check ISTD map file",
                                       x.name, str(ISTD_index+1))
                    ISTD_report_list.append(("!Blank Transition_Name_ISTD in map file",x.name))
                else:
                    if logger:
                        logger.warning("%s has an invalid Transition_Name_ISTD of %s. Please check ISTD map file",x.name,str(ISTD))
                    if ingui:
                        print(x.name + " has an invalid Transition_Name_ISTD of " + str(ISTD) + ". Please check ISTD map file",flush=True)
                    sys.exit(-1)
            Transition_Name_dict[x.name] = valid_ISTD
            return

        if len(ISTD_list) > 1:
            #If do not allow this, give a warning and do not set the dict entry to be None to prevent
            #this transition from being normalised
            if logger:
                logger.warning("%s has duplicates or multiple internal standards. %s Please check ISTD map file",x.name," ".join(ISTD_list))
            if ingui:
                print(x.name + " has duplicates or multiple internal standards. " + " ".join(ISTD_list) + " Please check ISTD map file",flush=True)
            ISTD_report_list.append(("!Duplicate Transition_Name_ISTD in map file",x.name))
            Transition_Name_dict[x.name] = None
        elif ISTD_list[0] is None:
            #ISTD_list may be [None]
            if logger:
                logger.warning("%s has a blank internal standard. Please check ISTD map file",x.name)
            Transition_Name_dict[x.name] = None
            ISTD_report_list.append(("!Blank Transition_Name_ISTD in map file",x.name))
        elif not isinstance(ISTD_list[0],float):
            #When we have only one valid ISTD
            Transition_Name_dict[x.name] = ISTD_list[0]
            ISTD_report_list.append((ISTD_list[0],x.name))
        elif np.isnan(ISTD_list[0]):
            #Value may be [nan]
            if logger:
                logger.warning("%s has a blank internal standard. Please check ISTD map file",x.name)
            Transition_Name_dict[x.name] = None
            ISTD_report_list.append(("!Blank Transition_Name_ISTD in map file",x.name))
        else:
            if logger:
                logger.warning("%s has an invalid Transition_Name_ISTD of %s. Please check ISTD map file",x.name,str(ISTD_list[0]))
            if ingui:
                print(x.name + " has an invalid Transition_Name_ISTD of " + str(ISTD_list[0]) + ". Please check ISTD map file",flush=True)
            sys.exit(-1)

    def _update_ISTD_data_from_Transition_Name_df(x,Transition_Name_dict,Transition_Name_df,ISTD_report_list,
                                                  logger=None,ingui=False,
                                                  allow_multiple_istd = False):
        """Update the ISTD data for each Transition_Name. Value remains as NAN when there is an issue

        Args:
            x (pandas Series): A column from the ISTD_data to be updated with its corresponding ISTD values
            Transition_Name_dict (dict): A dictionary to map each transition name to its ISTD
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            ISTD_report_list (list): A list of tuples showing (ISTD name or reason why there is no ISTD,Transition name)
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen
            allow_multiple_istd (bool): if True, Transition_Name_dict can have mulitple internal standards for one transition
        
        """

        #When a Transition_Name name has no/duplicate Transition_Name_ISTD or not found in the map file, just leave the funtion
        #A warning is already given in update_Transition_Name_dict so we do not need to write this again

        #IF we do not allow multiple istd, Transition_Name_dict[x.name] will be a string or None
        if not allow_multiple_istd:
            if not Transition_Name_dict[x.name]:
                return
            if list(Transition_Name_df.columns.values).count(Transition_Name_dict[x.name]) == 1:
                x.update(Transition_Name_df.loc[:, Transition_Name_dict[x.name] ])
            elif list(Transition_Name_df.columns.values).count(Transition_Name_dict[x.name]) > 1 :
                if logger:
                    logger.warning("%s appears more than once in the input data frame. Ignore normalisation in column %s", Transition_Name_dict[x.name],x.name)
                #if ingui:
                    #print(Transition_Name_dict[x.name] + " appears more than once in the input data frame. Ignore normalisation in this column " + x.name)
                ISTD_report_list.append(("!Duplicate Transition_Name_ISTD in data",x.name + " -> " + Transition_Name_dict[x.name] ))
            else:
                if logger:
                    logger.warning("%s cannot be found in the input data frame. Ignore normalisation in this column %s",Transition_Name_dict[x.name],x.name)
                #if ingui:
                    #print(Transition_Name_dict[x.name] + " cannot be found in the input data frame. Ignore normalisation in this column " + x.name)
                ISTD_report_list.append(("!Missing Transition_Name_ISTD in data", x.name + " -> " + Transition_Name_dict[x.name] ))


        #When a Transition_Name name has nan Transition_Name_ISTD, just leave the funtion

        #If the Transition_Name_df has presence of duplicate Transition_Name_ISTD for the given Transition_Names 
        #or do not have the Transition_Name_ISTD indicated in the map file 
        #we will give a warning and will not update ISTD data
        #print(Transition_Name_dict)
        #print(Transition_Name_df.columns)
        #print(Transition_Name_df.columns.values)
        #print(list(Transition_Name_df.columns.values))
        #exit(0)

    def normalise_by_ISTD(Transition_Name_df,Transition_Name_Annot_df,
                          logger=None,ingui=False,
                          allow_multiple_istd = False):
        """Perform normalisation using the values from the Transition_Name_ISTD

        Args:
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            Transition_Name_Annot_df (pandas DataFrame): A data frame of showing the transition names annotation
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen
            allow_multiple_istd (bool): if True, allow normalisation of Transition_Name_df mulitple internal standards (in development)

        Returns:
            (list): list containing:
                * norm_Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with the normalised values
                * ISTD_data (pandas DataFrame): A data frame of sample as rows and transition names as columns with the ISTD area as values. Output as excel only at testing mode
                * ISTD_Report (pandas DataFrame): A data frame of with transition names, its corresponding ISTD as columns. This will be converted to a pdf file page

        """
        #If the Transition_Name table or Transition_Name_Annot df is empty, return an empty data frame
        if Transition_Name_df.empty:
            if logger:
                logger.warning("The input Transition_Name data frame has no data. Skipping normalisation by Transition_Name_ISTD")
            if ingui:
                print("The input Transition_Name data frame has no data. Skipping normalisation by Transition_Name_ISTD",flush=True)
            return [pd.DataFrame(),pd.DataFrame(),pd.DataFrame()]

        #Create empty dataframe with a preset column name and index
        ISTD_data = pd.DataFrame(columns=Transition_Name_df.columns, index=Transition_Name_df.index)
        norm_Transition_Name_df = pd.DataFrame(columns=Transition_Name_df.columns, index=Transition_Name_df.index)

        #Sample_Name must be present
        ISTD_Operations._validate_Transition_Name_df(Transition_Name_df,logger,ingui)
        norm_Transition_Name_df["Sample_Name"] = Transition_Name_df["Sample_Name"]

        #Create the ISTD data from Transition_Name df and ISTD map file
        [ISTD_report,ISTD_data] = ISTD_Operations._create_ISTD_data_from_Transition_Name_df(Transition_Name_df,Transition_Name_Annot_df,
                                                                                            logger=logger,ingui=ingui,
                                                                                            allow_multiple_istd = allow_multiple_istd)

        #Perform an elementwise normalisation so that it is easy to debug.
        #To prevent Division by zero error, use astype
        norm_Transition_Name_df.iloc[:,1:] = Transition_Name_df.iloc[:,1:].astype('float64') / ISTD_data.iloc[:,1:].astype('float64')

        #Convert relevant columns to numeric
        ISTD_data = ISTD_data.apply(pd.to_numeric,errors='ignore')
        norm_Transition_Name_df = norm_Transition_Name_df.apply(pd.to_numeric,errors='ignore')

        return [norm_Transition_Name_df,ISTD_data,ISTD_report]

    def _create_ISTD_data_from_Transition_Name_Annot(Transition_Name_df,ISTD_Annot_df,ISTD_column,logger,ingui):
        """Perform normalisation using the values from the Transition_Name_ISTD

        Args:
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            ISTD_Annot_df (pandas DataFrame): A panda data frame containing the ISTD Annotation
            ISTD_column (str): The column from ISTD Annotation that needs to be map to ISTD_data
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen

        Returns:
            ISTD_data (pandas DataFrame): A data frame of sample as rows and transition names as columns with the corresponding ISTD_column values. Output as excel only at testing mode

        """

        #Create an empty data frame
        ISTD_data = pd.DataFrame(columns=Transition_Name_df.columns, index=Transition_Name_df.index)

        #Sample_Name must be present
        ISTD_Operations._validate_Transition_Name_df(Transition_Name_df,logger,ingui)
        ISTD_data["Sample_Name"] = Transition_Name_df["Sample_Name"]

        #Compulsory columns Transition_Name and Transition_Name_ISTD and verified when reading the Transition_Name_Annot file
        #We do not need to check for these columns again

        #Check if ISTD_column is a column in the ISTD_Annot_df
        if ISTD_column not in ISTD_Annot_df.columns:
            if logger:
                logger.warning("\"%s\" is not a column in the ISTD_Annot sheet. Returning an empty data frame",ISTD_column)
            if ingui:
                print("\"" + ISTD_column + "\" is not a column in the ISTD_Annot file. Returning an empty data frame",flush=True)
            return [ISTD_data]

        for index, row in ISTD_Annot_df.iterrows():
            if row['Transition_Name'] in ISTD_data.columns:
                ISTD_data[row['Transition_Name']] = row[ISTD_column]
        
        return(ISTD_data)

    def getConc_by_ISTD(Transition_Name_df,ISTD_Annot_df,Sample_Annot_df,logger=None,ingui=False):
        """Perform calculation of analyte concentration using values from Transition_Name_Annot_ISTD
        
        Args:
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            ISTD_Annot_df (pandas DataFrame): A data frame showing the ISTD annotation
            Sample_Annot_df (pandas DataFrame): A data frame showing the sample name annotation
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen

        Returns:
            (list): list containing:

                * Conc_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with the transition name concentration as values
                * ISTD_Conc_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with the ISTD concentration as values
                * ISTD_Samp_Ratio_df (pandas DataFrame): A data frame of with transition names, its corresponding ISTD and ISTD to Sample ratio as columns
 
        """
        #If the Transition_Name_df or Sample_Annot_df is empty, return an empty data frame
        if Transition_Name_df.empty:
            if logger:
                logger.warning("Skipping step to get normConc. The input Transition_Name data frame has no data.")
            if ingui:
                print("Skipping step to get normConc. The input Transition_Name data frame has no data.",flush=True)
            return [pd.DataFrame(),pd.DataFrame(),pd.DataFrame()]

        if ISTD_Annot_df.empty:
            if logger:
                logger.warning("Skipping step to get normConcThe input ISTD_Annot data frame has no data.")
            if ingui:
                print("Skipping step to get normConc. The input ISTD_Annot data frame has no data.",flush=True)
            return [pd.DataFrame(),pd.DataFrame(),pd.DataFrame()]

        if Sample_Annot_df.empty:
            if logger:
                logger.warning("Skipping step to get normConc. The Sample Annotation data frame has no data.")
            if ingui:
                print("Skipping step to get normConc .The Sample Annotation data frame has no data.",flush=True)
            return [pd.DataFrame(),pd.DataFrame(),pd.DataFrame()]

        #Sample_Name must be present
        ISTD_Operations._validate_Transition_Name_df(Transition_Name_df,logger,ingui)
        ISTD_Operations._validate_Sample_Annot_df(Sample_Annot_df,logger,ingui)

        #Creating the normConc dataframe
        Conc_df = pd.DataFrame(columns=Transition_Name_df.columns, index=Transition_Name_df.index)
        Conc_df["Sample_Name"] = Transition_Name_df["Sample_Name"]
        
        #Creating the ISTD_Conc_df
        ISTD_Annot_Columns = list(ISTD_Annot_df.columns.values)
        ISTD_Conc_Column = [col for col in ISTD_Annot_df if col.startswith("ISTD_Conc")]

        #if "ISTD_Conc_[nM]" in ISTD_Annot_Columns:
        if len(ISTD_Conc_Column) == 1:
            #Some values may be missing because some transition names have no ISTD, logging it may be unnecessary 
            ISTD_Conc_Column = ISTD_Conc_Column[0]
            #ISTD_Conc_df = ISTD_Operations._create_ISTD_data_from_Transition_Name_Annot(Transition_Name_df,ISTD_Annot_df,"ISTD_Conc_[nM]",logger,ingui)
            ISTD_Conc_df = ISTD_Operations._create_ISTD_data_from_Transition_Name_Annot(Transition_Name_df,ISTD_Annot_df,ISTD_Conc_Column,logger,ingui)
        else:
            #Return empty data set
            if len(ISTD_Conc_Column) == 0:
                if logger:
                    logger.warning("Skipping step to get normConc. ISTD_Annot sheet does not have a column that contains ISTD_Conc")
                if ingui:
                    print("Skipping step to get normConc. ISTD_Annot sheet does not have a column that contains ISTD_Conc",flush=True)
            elif len(ISTD_Conc_Column) > 1:
                if logger:
                    logger.warning("Skipping step to get normConc. ISTD_Annot sheet has more than one column that contains ISTD_Conc")
                if ingui:
                    print("Skipping step to get normConc. ISTD_Annot sheet has more than one column that contains ISTD_Conc",flush=True)
            return [Conc_df,Conc_df,Conc_df]

        #Creating the ISTD_Samp_Ratio_df
          
        #Ensure that the necessary columns are there
        Sample_Annot_Columns = list(Sample_Annot_df.columns.values)
        if not all(things in Sample_Annot_Columns for things in ["Data_File_Name","Sample_Name","Sample_Amount",
                                                                 "Sample_Amount_Unit","ISTD_Mixture_Volume_[uL]",
                                                                 "Concentration_Unit"]):
            #Return empty data set
            if logger:
                logger.warning("Skipping step to get normConc. Sample Annotation data frame is missing column %s" , 
                               ', '.join(["Data_File_Name","Sample_Name","Sample_Amount",
                                          "Sample_Amount_Unit","ISTD_Mixture_Volume_[uL]",
                                          "Concentration_Unit"]) )
            if ingui:
                print("Skipping step to get normConc. Sample Annotation data frame is missing column " 
                      , ', '.join(["Data_File_Name","Sample_Name","Sample_Amount",
                                   "Sample_Amount_Unit","ISTD_Mixture_Volume_[uL]",
                                   "Concentration_Unit"]),flush=True)
            return [Conc_df,Conc_df,Conc_df]

        #We cannot accept duplicated Data_File_path
        #By right Data_File_Name should be uniquely one value since it has been filtered in ISTD_Operations.read_Sample_Annot
        if(len(Sample_Annot_df.Data_File_Name.unique()) > 1):
            #Return empty data set
            if logger:
                logger.error('Skipping step to get normConc. Sample Annotation data frame has more than one Data_File_Name.')
            if ingui:
                print('Skipping step to get normConc. Sample Annotation data frame has more than one Data_File_Name.' ,flush=True)
            for things in Sample_Annot_df.Data_File_Name.unique():
                if logger:
                    logger.warning('/"%s/"',things)
                if ingui:
                    print('\"' + things + '\"',flush=True)
            return [Conc_df,Conc_df,Conc_df]

        #We cannot accept duplicated Data_File_Name and Sample Name
        #By right Data_File_Name should be uniquely one value since it has been filtered in ISTD_Operations.read_Sample_Annot
        if(len(Sample_Annot_df[["Data_File_Name","Sample_Name"]][Sample_Annot_df[["Data_File_Name","Sample_Name"]].duplicated(keep=False)]) > 0):
            #Return empty data set
            if logger:
                logger.warning('Skipping step to get normConc. Sample Annotation data frame has non-unique Sample_Name.')
                logger.warning('\n{}'.format( Sample_Annot_df[["Data_File_Name","Sample_Name"]][Sample_Annot_df[["Data_File_Name","Sample_Name"]].duplicated(keep=False)] ) )
            if ingui:
                print('Skipping step to get normConc. Sample Annotation data frame has non-unique Sample_Name.' ,flush=True)
                print(Sample_Annot_df[["Data_File_Name","Sample_Name"]][Sample_Annot_df[["Data_File_Name","Sample_Name"]].duplicated(keep=False)], flush =True)
            return [Conc_df,Conc_df,Conc_df]

        #Calculate the dilution factor or "ISTD_to_Sample_Amount_Ratio"
        Sample_Annot_df["ISTD_to_Sample_Amount_Ratio"] = Sample_Annot_df["ISTD_Mixture_Volume_[uL]"].astype('float64') / Sample_Annot_df["Sample_Amount"].astype('float64')
        #Sample_Annot_df["ISTD_to_Sample_Amount_Ratio"] = Sample_Annot_df["ISTD_to_Sample_Amount_Ratio"].replace([np.inf, -np.inf], np.nan)

        #Filter the Transition_Name_df to get the Sample_Name column
        merged_df = Transition_Name_df.loc[:, Transition_Name_df.columns == 'Sample_Name']

        #Merge it with the Sample_Annot_df so that the order of the Sample_name follows Transition_Name_df
        merged_df = pd.merge(merged_df, Sample_Annot_df.loc[:, ["Sample_Name","ISTD_to_Sample_Amount_Ratio"]], on="Sample_Name")

        ISTD_Samp_Ratio_df = pd.DataFrame(index=Transition_Name_df.index, columns=Transition_Name_df.columns,dtype='float64')
        ISTD_Samp_Ratio_df.apply(lambda x: x.update(merged_df["ISTD_to_Sample_Amount_Ratio"]) ,axis=0)

        #Assignment of string must come after df apply
        ISTD_Samp_Ratio_df['Sample_Name'] = Transition_Name_df['Sample_Name']
        #print(ISTD_Samp_Ratio_df,flush=True)
        #print(ISTD_Samp_Ratio_df.info())

        #Perform an elementwise multiplication so that it is easy to debug.
        Conc_df.iloc[:,1:] = Transition_Name_df.iloc[:,1:].astype('float64') * ISTD_Conc_df.iloc[:,1:].astype('float64') * ISTD_Samp_Ratio_df.iloc[:,1:].astype('float64')

        return [Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df]