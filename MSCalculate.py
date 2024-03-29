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

        AnnotationList = MS_Template(filepath=filepath,column_name=column_name, 
                                     logger=logger,ingui=ingui,
                                     doing_normalization = doing_normalization, 
                                     allow_multiple_istd = allow_multiple_istd)
        Transition_Name_Annot_df = AnnotationList.Read_Transition_Name_Annot_Sheet()
        ISTD_Annot_df = AnnotationList.Read_ISTD_Annot_Sheet()

        if not ISTD_Annot_df.empty:
            # Additional check to ensure each Transition_Name_ISTD in Transition_Name_Annot sheet 
            # also appears in the ISTD_Annot sheet
            ISTD_list_in_Transition_Name_Annot_sheet = list(filter(None,Transition_Name_Annot_df['Transition_Name_ISTD'].unique()))
            ISTD_list_in_Annot_sheet = list(filter(None,ISTD_Annot_df['Transition_Name_ISTD'].unique()))

            missing_ISTD = sorted(list(set(ISTD_list_in_Transition_Name_Annot_sheet).difference(ISTD_list_in_Annot_sheet)))
            if missing_ISTD:
                if logger:
                    logger.warning('There are Transition_Name_ISTD in Transition_Name_Annot not mentioned in ISTD_Annot.\n' +
                                   "\n".join(missing_ISTD) + '\n' +
                                   'Check that these ISTD are in the ISTD_Annot sheet.'
                                   )
                if ingui:
                    print('There are Transition_Name_ISTD in Transition_Name_Annot not mentioned in ISTD_Annot.\n' + 
                          "\n".join(missing_ISTD) + '\n' +
                          'Check that these ISTD are in the ISTD_Annot sheet.',
                          flush=True)

            excess_ISTD = sorted(list(set(ISTD_list_in_Annot_sheet).difference(ISTD_list_in_Transition_Name_Annot_sheet)))
            if excess_ISTD:
                if logger:
                    logger.warning('There are Transition_Name_ISTD in ISTD_Annot not used in Transition_Name_Annot.\n' +
                                   "\n".join(excess_ISTD) + '\n' +
                                   'Check that these ISTD are truly not needed.'
                                   )
                if ingui:
                    print('There are Transition_Name_ISTD in ISTD_Annot not used in Transition_Name_Annot.\n' + 
                          "\n".join(excess_ISTD) + '\n' +
                          'Check that these ISTD are truly not needed.',
                          flush=True)

            Transition_Name_Annot_df = pd.merge(Transition_Name_Annot_df, ISTD_Annot_df, 
                                                on = 'Transition_Name_ISTD', 
                                                how = 'outer')

            # Remove rows with no transition name, even though it has an transition name istd
            Transition_Name_Annot_df.dropna(subset = ['Transition_Name'], 
                                            inplace = True)

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
        """Function to validate if the input Transition_Name_df is valid.

        Args:
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen

        Note:
            Check if the column "Sample_Name" exists, otherwise, throw an error.

        """

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
        """Function to validate if the input Transition_Name_df is valid.

        Args:
            Sample_Annot_df (pandas DataFrame): A data frame showing the sample name annotation
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen

        Note:
            Check if the column "Sample_Name" exists, otherwise, throw an error.

        """

        if "Sample_Name" not in Sample_Annot_df:
            if logger:
                logger.error("The sample annotation file does not contain the column Sample_Name")
            if ingui:
                print("The sample annotation file does not contain the Sample_Name",flush=True)
            sys.exit(-1)

    def create_Transition_Name_dict(Transition_Name_df,Transition_Name_Annot_df,
                                    logger=None,ingui=False,
                                    allow_multiple_istd = False):

        """
        Create a dictionary to map the Transition_Name to the Transition_Name_ISTD and an ISTD report to map Transition_Name_ISTD to Transition_Name

        Args:
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            Transition_Name_Annot_df (pandas DataFrame): A data frame of showing the transition names annotation
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen
            allow_multiple_istd (bool): if True, ISTD data can have mulitple internal standards for one transition

        Returns:
            (list): list containing:

                * ISTD_report_list (pandas DataFrame): An updated ISTD report to map Transition_Name_ISTD to Transition_Name
                * Transition_Name_dict (dict): An updated python dictionary to map the Transition_Name to the Transition_Name_ISTD
        """

        #Create a dictionary to map the Transition_Name to the Transition_Name_ISTD and an ISTD report to map Transition_Name_ISTD to Transition_Name
        #We start a new Transition_Name_dict and ISTD_report
        Transition_Name_dict = {}
        ISTD_report = []
        Transition_Name_df_column_list = list(Transition_Name_df.columns.values)

        #Create the Transition_Name_dict and ISTD_report
        for Transition_Name in Transition_Name_df_column_list:
            if Transition_Name != 'Sample_Name':
                [ISTD_report,Transition_Name_dict] = ISTD_Operations._update_Transition_Name_dict(
                    Transition_Name = Transition_Name,
                    Transition_Name_Annot_df=Transition_Name_Annot_df,
                    Transition_Name_dict=Transition_Name_dict,
                    Transition_Name_df_column_list = Transition_Name_df_column_list,
                    ISTD_report_list = ISTD_report,
                    logger=logger,ingui=ingui,
                    allow_multiple_istd = allow_multiple_istd
                    )

        #Convert ISTD report from list to dataframe and report any warnings if any
        ISTD_report = pd.DataFrame(ISTD_report)
        ISTD_report.columns=(['Transition_Name_ISTD','Transition_Name'])
        ISTD_report = ISTD_report.sort_values(by=['Transition_Name_ISTD','Transition_Name'])

        #Check ISTD_report for any problems
        if "!Missing Transition_Name in Transition_Name_Annot sheet" in ISTD_report['Transition_Name_ISTD'].unique():
            bad_input_list = ISTD_report.loc[ ISTD_report['Transition_Name_ISTD'] == "!Missing Transition_Name in Transition_Name_Annot sheet" , 
                                             'Transition_Name']
            if logger:
                logger.warning('There are transitions in the input data set not mentioned' + 
                               'in the Transition_Name column of the Transition_Name_Annot sheet.\n' +
                               '\n'.join(f'"{bad_input}"' for bad_input in bad_input_list))
            if ingui:
                print('There are transitions in the input data set not mentioned ' + 
                      'in the Transition_Name column of the Transition_Name_Annot sheet.\n' +
                      '\n'.join(f'"{bad_input}"' for bad_input in bad_input_list),
                      flush=True)

        if "!Blank Transition_Name_ISTD in Transition_Name_Annot sheet" in ISTD_report['Transition_Name_ISTD'].unique():
            bad_input_list = ISTD_report.loc[ ISTD_report['Transition_Name_ISTD'] == "!Blank Transition_Name_ISTD in Transition_Name_Annot sheet" , 
                                             'Transition_Name' ]
            if logger:
                logger.warning('There are Transition_Names mentioned ' + 
                               'in the Transition_Name_Annot sheet but have a blank Transition_Name_ISTD.\n' + 
                               '\n'.join(f'"{bad_input}"' for bad_input in bad_input_list))
            if ingui:
                print('There are Transition_Names mentioned ' + 
                      'in the Transition_Name_Annot sheet but have a blank Transition_Name_ISTD.\n' + 
                      '\n'.join(f'"{bad_input}"' for bad_input in bad_input_list),
                      flush=True)

        if "!Missing Transition_Name_ISTD in input data" in ISTD_report['Transition_Name_ISTD'].unique():
            bad_input_list = ISTD_report.loc[ ISTD_report['Transition_Name_ISTD'] == "!Missing Transition_Name_ISTD in input data" , 
                                             'Transition_Name' ]
            if logger:
                logger.warning('There are Transition_Names mentioned ' + 
                               'in the Transition_Name_Annot sheet ' +
                               'whose Transition_Names_ISTD does not exists ' +
                               'in the input dataset.\n' +
                               '\n'.join(f'"{bad_input}"' for bad_input in bad_input_list))
            if ingui:
                print('There are Transition_Names mentioned ' + 
                      'in the Transition_Name_Annot sheet ' +
                      'whose Transition_Names_ISTD does not exists ' +
                      'in the input dataset.\n' +
                      '\n'.join(f'"{bad_input}"' for bad_input in bad_input_list),
                      flush=True)

        # Duplicate Transition_Name_ISTD in input data has been taken care
        # by DuplicateCheck.py

        #Make ISTD column to be the index
        ISTD_report = ISTD_report.set_index(['Transition_Name_ISTD'])

        return [ISTD_report,Transition_Name_dict]

            
    def _create_ISTD_data_from_Transition_Name_df(Transition_Name_df,Transition_Name_dict,
                                                  logger=None,ingui=False,
                                                  allow_multiple_istd = False):
        """
        Create the ISTD data from Transition_Name df and ISTD map file

        Args:
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            Transition_Name_dict (dict): A python dictionary to map the Transition_Name to the Transition_Name_ISTD and an ISTD report to map Transition_Name_ISTD to Transition_Name
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen
            allow_multiple_istd (bool): if True, ISTD data can have mulitple internal standards for one transition

        Notes:
            It is actually one of the internal function of normalise_by_ISTD. An empty data frame of the same dimension as
            Transition_Name_df is created, then, the first column "Sample_Name" is filled in. For the subsequent columns,
            the ISTD area is placed based on what is provided in Transition_Name_dict

        Returns:
            (list): list containing:

                * ISTD_data (pandas DataFrame): A data frame of sample as rows and transition names as columns with the ISTD area as values. Output as excel only at testing mode
        """

        ISTD_data = pd.DataFrame(columns=Transition_Name_df.columns, index=Transition_Name_df.index)

        #Sample_Name must be present
        ISTD_Operations._validate_Transition_Name_df(Transition_Name_df,logger,ingui)
        
        #Create a ISTD table from the Transition_Name df
        ISTD_data["Sample_Name"] = Transition_Name_df["Sample_Name"]

        ISTD_data = ISTD_data.apply(
            lambda x: ISTD_Operations._update_ISTD_data_from_Transition_Name_df(
                ISTD_data_column_data = x,
                Transition_Name_dict=Transition_Name_dict,
                Transition_Name_df=Transition_Name_df,
                logger=logger,ingui=ingui,
                allow_multiple_istd = allow_multiple_istd)
                if x.name != 'Sample_Name' else x,
                axis=0)

        return [ISTD_data]

    def _update_Transition_Name_dict(Transition_Name,Transition_Name_Annot_df,Transition_Name_dict,
                                     Transition_Name_df_column_list, ISTD_report_list,
                                     logger=None,ingui=False,
                                     allow_multiple_istd = False):
        """Updating the Transition_Name dict and ISTD_report_list to map Transition_Name to their Transition_Name_ISTD given a Transition_Name

        Args:
            Transition_Name (str): Input transition name
            Transition_Name_Annot_df (pandas DataFrame): A data frame of showing the transition names annotation
            Transition_Name_dict (dict): A dictionary to map each transition name to its ISTD. To be updated by each x
            Transition_Name_df_column_list (list): A list of column names of Transition_Name_df
            ISTD_report_list (list): A list of tuples showing (ISTD name or reason why there is no ISTD,Transition name)
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen
            allow_multiple_istd (bool): if True, Transition_Name_dict can have mulitple internal standards for one transition

        Notes:
            It is actually one of the internal function of create_Transition_Name_dict. It is meant to be interated over each transition in the
            Transition_Name_df_column_list

        Returns:
            (list): list containing:

                * ISTD_report_list (pandas DataFrame): An updated ISTD report to map Transition_Name_ISTD to Transition_Name
                * Transition_Name_dict (dict): An updated python dictionary to map the Transition_Name to the Transition_Name_ISTD

        """

        # Get the mapping of one Transition_Name to exactly one ISTD
        ISTD_list = Transition_Name_Annot_df.loc[Transition_Name_Annot_df['Transition_Name']==Transition_Name,"Transition_Name_ISTD"].tolist()

        if allow_multiple_istd:
            # Check if each ISTD in the ISTD_List is valid
            valid_ISTD = []
            # There is no need to get the index as cases
            # Transtion_Name Transition_Name_ISTD
            #       LPC 18:0
            #       LPC 18:0
            # Will give an error because of duplicate rows in
            # Annotation.py __validate_Transition_Name_Annot_sheet function

            if ISTD_list is None:
                # ISTD_list is None
                #Append an empty ISTD, this is not done if we do not allow multiple ISTD
                valid_ISTD.append("")
                ISTD_report_list.append(("!Missing Transition_Name in Transition_Name_Annot sheet", Transition_Name))
                Transition_Name_dict[Transition_Name] = valid_ISTD
                return [ISTD_report_list,Transition_Name_dict] 

            if len(ISTD_list) == 0:
                # ISTD_list is []
                #Append an empty ISTD, this is not done if we do not allow multiple ISTD
                valid_ISTD.append("")
                ISTD_report_list.append(("!Missing Transition_Name in Transition_Name_Annot sheet", Transition_Name))
                Transition_Name_dict[Transition_Name] = valid_ISTD
                return [ISTD_report_list,Transition_Name_dict] 

            for ISTD in ISTD_list:

                if ISTD is None:
                    # ISTD may be None
                    #Append an empty ISTD, this is not done if we do not allow multiple ISTD
                    valid_ISTD.append("")
                    ISTD_report_list.append(("!Blank Transition_Name_ISTD in Transition_Name_Annot sheet", Transition_Name))
                    continue
                elif pd.isna(ISTD):
                    # Value may be [nan] which is a type float
                    # Unfortunately, np.isnan must be the last condition
                    # else it gives an error
                    # TypeError: ufunc 'isnan' not supported for the input types, and the inputs could not 
                    # be safely coerced to any supported types according to the casting rule ''safe''
                    ISTD_report_list.append(("!Blank Transition_Name_ISTD in Transition_Name_Annot sheet",Transition_Name))
                    continue

                if not isinstance(ISTD,float):
                    if Transition_Name_df_column_list.count(ISTD) == 0:
                        # ISTD is used in Annotation File but not present in the input data
                        ISTD_report_list.append(("!Missing Transition_Name_ISTD in input data", Transition_Name))
                        valid_ISTD.append(ISTD)
                        continue
                    elif Transition_Name_df_column_list.count(ISTD) > 1:
                        # ISTD is used in Annotation File but has duplicates in the input data
                        # This check may be redundant because the
                        # duplicate Transition_Name_ISTD in input data has been taken care
                        # by DuplicateCheck.py
                        if logger:
                            logger.error(str(ISTD) + ' has duplicates in the input data. ' + 
                                 'Please check the Transition_Name_Annot sheet')
                        if ingui:
                            print(str(ISTD) + ' has duplicates in the input data. ' + 
                                  'Please check the Transition_Name_Annot sheet',
                                  flush=True)
                        sys.exit(-1)
                    else:
                        # When we have a valid ISTD
                        valid_ISTD.append(ISTD)
                        ISTD_report_list.append((ISTD,Transition_Name))
                else:
                    if logger:
                        logger.error(Transition_Name + ' has an invalid Transition_Name_ISTD of ' + 
                                     str(ISTD) + '. Please check ISTD map file')
                    if ingui:
                        print(Transition_Name + ' has an invalid Transition_Name_ISTD of ' + 
                              str(ISTD) + '. Please check ISTD map file',
                              flush=True)
                    sys.exit(-1)

            Transition_Name_dict[Transition_Name] = valid_ISTD
            return [ISTD_report_list,Transition_Name_dict]

        # Case of not using multiple ISTD
        if ISTD_list is None:
            # ISTD_list None
            Transition_Name_dict[Transition_Name] = None
            ISTD_report_list.append(("!Missing Transition_Name in Transition_Name_Annot sheet",Transition_Name))
            return [ISTD_report_list,Transition_Name_dict]

        if len(ISTD_list) == 0:
            # ISTD_list is []
            Transition_Name_dict[Transition_Name] = None
            ISTD_report_list.append(("!Missing Transition_Name in Transition_Name_Annot sheet",Transition_Name))
            return [ISTD_report_list,Transition_Name_dict]

        if ISTD_list[0] is None:
            # ISTD_list may be [None]
            Transition_Name_dict[Transition_Name] = None
            ISTD_report_list.append(("!Blank Transition_Name_ISTD in Transition_Name_Annot sheet",Transition_Name))
            return [ISTD_report_list,Transition_Name_dict] 
        elif pd.isna(ISTD_list[0]):
            # Value may be [np.NaN] which is a type float
            # Unfortunately, np.isnan must be the last condition
            # else it gives an error
            # TypeError: ufunc 'isnan' not supported for the input types, and the inputs could not 
            # be safely coerced to any supported types according to the casting rule ''safe''
            Transition_Name_dict[Transition_Name] = None
            ISTD_report_list.append(("!Blank Transition_Name_ISTD in Transition_Name_Annot sheet",Transition_Name))
            return [ISTD_report_list,Transition_Name_dict] 

        if not isinstance(ISTD_list[0],float):
            # When we have only one valid ISTD
            # Check if the ISTD is valid in the input data set
            if Transition_Name_df_column_list.count(ISTD_list[0]) == 0:
                # ISTD is used in Annotation File but not present in the input data
                Transition_Name_dict[Transition_Name] = ISTD_list[0]
                ISTD_report_list.append(("!Missing Transition_Name_ISTD in input data", Transition_Name))
                return [ISTD_report_list,Transition_Name_dict] 
            elif Transition_Name_df_column_list.count(ISTD_list[0]) > 1:
                # ISTD is used in Annotation File but has duplicates in the input data
                # This check may be redundant because the
                # duplicate Transition_Name_ISTD in input data has been taken care
                # by DuplicateCheck.py
                if logger:
                    logger.error(str(ISTD_list[0]) + ' has duplicates in the input data. ' + 
                                 'Please check the Transition_Name_Annot sheet')
                if ingui:
                    print(str(ISTD_list[0]) + ' has duplicates in the input data. ' + 
                          'Please check the Transition_Name_Annot sheet',
                          flush=True)
                sys.exit(-1)
            else:
                # When we have a valid ISTD
                Transition_Name_dict[Transition_Name] = ISTD_list[0]
                ISTD_report_list.append((ISTD_list[0],Transition_Name))
                return [ISTD_report_list,Transition_Name_dict] 
        else:
            if logger:
                logger.error(Transition_Name + ' has an invalid Transition_Name_ISTD of ' + 
                             str(ISTD_list[0]) + '. Please check the Transition_Name_Annot sheet')
            if ingui:
                print(Transition_Name + ' has an invalid Transition_Name_ISTD of ' + 
                      str(ISTD_list[0]) + '. Please check the Transition_Name_Annot sheet',
                      flush=True)
            sys.exit(-1)


    def _update_expanded_Transition_Name_df(expanded_Transition_Name_df_column_data,Transition_Name_df,logger=None):
        """Update the new Transition_Name df for each Transition_Name so that it can be used for normalisation of multiple ISTD

        Args:
            expanded_Transition_Name_df_column_data (pandas Series): A column from the new Transition_Name df to be updated with its corresponding Tranition_Name df values
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            logger (object): logger object created by start_logger in MSOrganiser

        Notes:
            It is actually one of the internal function of expand_Transition_Name_df. 
            It is meant to be interated over each column of expanded_Transition_Name_df_column_data.
            expanded_Transition_Name_df_column_data.name should be a Transition_Name that can be found in the columns of Transition_Name_df  

        Returns:
            expanded_Transition_Name_df_column_data.values (pandas Series): Values remain unchanged if no Transition_Name can be found. 
            Otherwise the values will be replaced with the Transition_Name values provided by Transition_Name_df
        
        """

        if expanded_Transition_Name_df_column_data.name[0] is None:
            return(expanded_Transition_Name_df_column_data.values)

        if list(Transition_Name_df.columns.values).count(expanded_Transition_Name_df_column_data.name[0]) == 1:
            return(Transition_Name_df.loc[:, expanded_Transition_Name_df_column_data.name[0] ])
        elif list(Transition_Name_df.columns.values).count(expanded_Transition_Name_df_column_data.name[0]) > 1 :
            # This check may be redundant because the
            # duplicate Transition_Name in input data has been taken care
            # by DuplicateCheck.py
            if logger:
                logger.warning(expanded_Transition_Name_df_column_data.name[0] + ' appears more than once in the input data frame. ' + 
                               'Ignore updating Transition_Name_df.')
            if ingui:
                print(expanded_Transition_Name_df_column_data.name[0] + ' appears more than once in the input data frame. ' + 
                      'Ignore updating Transition_Name_df.',
                      flush = True)
        else:
            # This check may be redundant because the
            # x is iterated from the columns of Transition_Name_df
            if logger:
                logger.warning(expanded_Transition_Name_df_column_data.name[0] + ' cannot be found in the input data frame. ' +
                               'Ignore updating Transition_Name_df.')
            if ingui:
                print(expanded_Transition_Name_df_column_data.name[0] + ' cannot be found in the input data frame. ' +
                     'Ignore updating Transition_Name_df.',
                     flush = True)
        return(expanded_Transition_Name_df_column_data.values)

    def _update_ISTD_data_from_Transition_Name_df(ISTD_data_column_data,
                                                  Transition_Name_dict,Transition_Name_df,
                                                  logger=None,ingui=False,
                                                  allow_multiple_istd = False):
        """Update the ISTD data for each Transition_Name. Value remains as NAN when there is an issue

        Args:
            ISTD_data_column_data (pandas Series): A column from the ISTD_data to be updated with its corresponding ISTD values
            Transition_Name_dict (dict): A dictionary to map each transition name to its ISTD
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen
            allow_multiple_istd (bool): if True, Transition_Name_dict can have mulitple internal standards for one transition
        
        Returns:
            ISTD_data_column_data.values (pandas Series): Values remain unchanged if no Transition_Name_ISTD can be found. 
            Otherwise the values will be replaced with the Transition_Name_ISTD values provided by Transition_Name_df

        """

        # When a Transition_Name name has no/duplicate Transition_Name_ISTD or not found in the map file, just leave the funtion
        # A warning is already given in update_Transition_Name_dict so we do not need to write this again

        #If we do not allow multiple istd, Transition_Name_dict[x.name] will be a string or None
        if not allow_multiple_istd:
            # ISTD_data_column_data.name is the Transition_Name
            # Transition_Name_dict[ISTD_data_column_data.name] is Transition_Name_ISTD
            if Transition_Name_dict[ISTD_data_column_data.name] is None:
                return(ISTD_data_column_data.values)
            if list(Transition_Name_df.columns.values).count(Transition_Name_dict[ISTD_data_column_data.name]) == 1:
                return(Transition_Name_df.loc[:, Transition_Name_dict[ISTD_data_column_data.name] ])
            elif list(Transition_Name_df.columns.values).count(Transition_Name_dict[ISTD_data_column_data.name]) > 1 :
                # This check may be redundant because the
                # duplicate Transition_Name_ISTD in input data has been taken care
                # by DuplicateCheck.py
                if logger:
                    logger.warning(Transition_Name_dict[ISTD_data_column_data.name] + ' appears more than once in the input data frame. ' +
                                   'Ignore normalisation in this column ' + ISTD_data_column_data.name)
                if ingui:
                    print(Transition_Name_dict[ISTD_data_column_data.name] + ' appears more than once in the input data frame. ' +
                          'Ignore normalisation in this column ' + ISTD_data_column_data.name, 
                          flush = True)
            else:
                if logger:
                    logger.warning(Transition_Name_dict[ISTD_data_column_data.name] + ' cannot be found in the input data frame. ' +
                                   'Ignore normalisation in this column ' + ISTD_data_column_data.name)
                if ingui:
                    print(Transition_Name_dict[ISTD_data_column_data.name] + ' cannot be found in the input data frame. ' +
                          'Ignore normalisation in this column ' + ISTD_data_column_data.name, 
                          flush = True)
            return(ISTD_data_column_data.values)
        else:
            # ISTD_data_column_data.name is of the tuple form (Transition_Name, Transition_Name_ISTD)
            # Transition_Name_dict is not used in this case
            # ISTD_data_column_data.name[1] will be a string or None
            if not ISTD_data_column_data.name[1]:
                return(ISTD_data_column_data.values)

            if list(Transition_Name_df.columns.values).count((ISTD_data_column_data.name[1],ISTD_data_column_data.name[1])) == 1:
                return(Transition_Name_df.loc[:, (ISTD_data_column_data.name[1],ISTD_data_column_data.name[1]) ])
            elif list(Transition_Name_df.columns.values).count((ISTD_data_column_data.name[1],ISTD_data_column_data.name[1])) > 1 :
                # This check may be redundant because the
                # duplicate Transition_Name_ISTD in input data has been taken care
                # by DuplicateCheck.py
                if logger:
                    logger.warning(ISTD_data_column_data.name[1] + ' appears more than once in the input data frame. ' +
                                   'Ignore normalisation in this column ' + str(ISTD_data_column_data.name))
                if ingui:
                    print(ISTD_data_column_data.name[1] + ' appears more than once in the input data frame. ' +
                          'Ignore normalisation in this column ' + str(ISTD_data_column_data.name), flush = True)
            else:
                if logger:
                    logger.warning(ISTD_data_column_data.name[1] + ' cannot be found in the input data frame. ' + 
                                   'Ignore normalisation in this column ' + str(ISTD_data_column_data.name))
                if ingui:
                    print(ISTD_data_column_data.name[1] + ' cannot be found in the input data frame. ' + 
                          'Ignore normalisation in this column ' + str(ISTD_data_column_data.name), 
                          flush = True)
            return(ISTD_data_column_data.values)

    def expand_Transition_Name_df(Transition_Name_df,Transition_Name_dict,
                                  logger=None,ingui=False):
        """Expand Transition_Name_df so that it can be normalised by multiple ISTD

        Args:
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            Transition_Name_dict (dict): A python dictionary to map the Transition_Name to the Transition_Name_ISTD and an ISTD report to map Transition_Name_ISTD to Transition_Name
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen

        Returns:
            (list): list containing:
                * expanded_Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns suited for normalisation by multiple ISTD
        """

        #Create empty dataframe with a preset column name and the expanded Transition_Name_df
        # Initialize empty list
        tuples=[("Sample_Name","")]      
        for Transition_Name in Transition_Name_dict:
            if len(Transition_Name_dict[Transition_Name]) == 0:
                #print((Transition_Name, ""))
                tuples.append((Transition_Name, ""))
            else:
                for Transition_Name_ISTD in Transition_Name_dict[Transition_Name]:
                    #print((Transition_Name, Transition_Name_ISTD))
                    tuples.append((Transition_Name, Transition_Name_ISTD))
        column_index = pd.MultiIndex.from_tuples(tuples, names=["Transition_Name", "Transition_Name_ISTD"])

        expanded_Transition_Name_df = pd.DataFrame(columns=column_index, index=Transition_Name_df.index)
        expanded_Transition_Name_df["Sample_Name"] = Transition_Name_df["Sample_Name"]

        expanded_Transition_Name_df = expanded_Transition_Name_df.apply(
            lambda x: ISTD_Operations._update_expanded_Transition_Name_df(
                expanded_Transition_Name_df_column_data=x,
                Transition_Name_df=Transition_Name_df,
                logger=logger)
                if x.name != 'Sample_Name' else x,
                axis=0)

        return expanded_Transition_Name_df

    def normalise_by_ISTD(Transition_Name_df,Transition_Name_dict,
                          logger=None,ingui=False,
                          allow_multiple_istd = False):
        """Perform normalisation using the values from the Transition_Name_ISTD

        Args:
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            Transition_Name_dict (dict): A python dictionary to map the Transition_Name to the Transition_Name_ISTD and an ISTD report to map Transition_Name_ISTD to Transition_Name
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen
            allow_multiple_istd (bool): if True, allow normalisation of Transition_Name_df mulitple internal standards (in development)

        Returns:
            (list): list containing:
                * norm_Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns with the normalised values
                * ISTD_data (pandas DataFrame): A data frame of sample as rows and transition names as columns with the ISTD area as values. Output as excel only at testing mode

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
        [ISTD_data] = ISTD_Operations._create_ISTD_data_from_Transition_Name_df(Transition_Name_df,Transition_Name_dict,
                                                                                logger=logger,ingui=ingui,
                                                                                allow_multiple_istd = allow_multiple_istd)

        #Perform an elementwise normalisation so that it is easy to debug.
        #To prevent Division by zero error, use astype
        norm_Transition_Name_df.iloc[:,1:] = Transition_Name_df.iloc[:,1:].astype('float64') / ISTD_data.iloc[:,1:].astype('float64')

        #Convert relevant columns to numeric
        ISTD_data = ISTD_data.apply(pd.to_numeric,errors='ignore')
        norm_Transition_Name_df = norm_Transition_Name_df.apply(pd.to_numeric,errors='ignore')

        #Convert positive and negative infinity to NaN
        ISTD_data = ISTD_data.replace([np.inf, -np.inf], np.nan)
        norm_Transition_Name_df = norm_Transition_Name_df.replace([np.inf, -np.inf], np.nan)

        return [norm_Transition_Name_df,ISTD_data]

    def _create_ISTD_Conc_from_Transition_Name_Annot(Transition_Name_df,ISTD_Annot_df,ISTD_column,
                                                     logger=None,ingui=False,
                                                     allow_multiple_istd = False):
        """Create a dataframe of ISTD Concentrations

        Args:
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            ISTD_Annot_df (pandas DataFrame): A panda data frame containing the ISTD Annotation
            ISTD_column (str): The column from ISTD Annotation that needs to be map to ISTD_data
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen

        Returns:
            ISTD_Conc (pandas DataFrame): A data frame of sample as rows and transition names as columns with the corresponding ISTD Concentration.

        """

        #Create an empty data frame
        ISTD_Conc = pd.DataFrame(columns=Transition_Name_df.columns, index=Transition_Name_df.index)

        #Sample_Name must be present
        ISTD_Operations._validate_Transition_Name_df(Transition_Name_df,logger,ingui)
        ISTD_Conc["Sample_Name"] = Transition_Name_df["Sample_Name"]

        #Compulsory columns Transition_Name and Transition_Name_ISTD and verified when reading the Transition_Name_Annot file
        #We do not need to check for these columns again

        #Check if ISTD_column is a column in the ISTD_Annot_df
        if ISTD_column not in ISTD_Annot_df.columns:
            if logger:
                logger.warning("\"%s\" is not a column in the ISTD_Annot sheet. Returning an empty data frame",ISTD_column)
            if ingui:
                print("\"" + ISTD_column + "\" is not a column in the ISTD_Annot file. Returning an empty data frame",flush=True)
            return [ISTD_Conc]

        #Each row of ISTD_Annot_df is a column of transition name, 
        #a transition name ISTD and its concentration (denoted as ISTD_column)
        for index, row in ISTD_Annot_df.iterrows():
            if allow_multiple_istd:
                #For each row, we map the concentration to ISTD_Conc 
                #which share the same transition name and transition name ISTD
                if (row['Transition_Name'],row['Transition_Name_ISTD']) in ISTD_Conc.columns:
                    ISTD_Conc[(row['Transition_Name'],row['Transition_Name_ISTD'])] = row[ISTD_column]
            else:
                #For each row, we map the concentration to ISTD_Conc 
                #which share the same transition name
                if row['Transition_Name'] in ISTD_Conc.columns:
                    ISTD_Conc[row['Transition_Name']] = row[ISTD_column]
                    
        return(ISTD_Conc)

    def getConc_by_ISTD(Transition_Name_df,ISTD_Annot_df,Sample_Annot_df,
                        logger=None,ingui=False,
                        allow_multiple_istd = False,
                        allow_multiple_data_file_path = False):
        """Perform calculation of analyte concentration using values from Transition_Name_Annot_ISTD
        
        Args:
            Transition_Name_df (pandas DataFrame): A data frame of sample as rows and transition names as columns
            ISTD_Annot_df (pandas DataFrame): A data frame showing the ISTD annotation
            Sample_Annot_df (pandas DataFrame): A data frame showing the sample name annotation
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen
            allow_multiple_istd (bool): if True, allow normalisation of Transition_Name_df mulitple internal standards
            allow_multiple_data_file_path (bool): if True, allow calculation of concentration using Sample_Annot_df that has more than one data file name

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
            ISTD_Conc_df = ISTD_Operations._create_ISTD_Conc_from_Transition_Name_Annot(Transition_Name_df,ISTD_Annot_df,ISTD_Conc_Column,
                                                                                        logger=logger,ingui=ingui,
                                                                                        allow_multiple_istd = allow_multiple_istd)
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

        #We cannot accept > 1 Data_File_path if we are not doing concatenation to save memory
        if(len(Sample_Annot_df.Data_File_Name.unique()) > 1 and not allow_multiple_data_file_path):
            #Return empty data set
            if logger:
                logger.error('Skipping step to get normConc. At no concatenation mode, Sample Annotation data frame has more than one Data_File_Name.')
            if ingui:
                print('Skipping step to get normConc. At no concatenation mode, Sample Annotation data frame has more than one Data_File_Name.' ,flush=True)
            for things in Sample_Annot_df.Data_File_Name.unique():
                if logger:
                    logger.warning('/"%s/"',things)
                if ingui:
                    print('\"' + things + '\"',flush=True)
            return [Conc_df,Conc_df,Conc_df]

        # We cannot accept duplicated Data_File_Name and Sample Name in Sample_Annot_df input
        if(len(Sample_Annot_df[["Data_File_Name","Sample_Name"]][Sample_Annot_df[["Data_File_Name","Sample_Name"]].duplicated(keep=False)]) > 0):
            #Return empty data set
            if logger:
                logger.warning('Skipping step to get normConc. Sample Annotation data frame has non-unique Sample_Name.')
                logger.warning('\n{}'.format( Sample_Annot_df[["Data_File_Name","Sample_Name"]][Sample_Annot_df[["Data_File_Name","Sample_Name"]].duplicated(keep=False)].to_string(index=False) ) )
            if ingui:
                print('Skipping step to get normConc. Sample Annotation data frame has non-unique Sample_Name.' ,flush=True)
                print(Sample_Annot_df[["Data_File_Name","Sample_Name"]][Sample_Annot_df[["Data_File_Name","Sample_Name"]].duplicated(keep=False)].to_string(index=False), flush =True)
            return [Conc_df,Conc_df,Conc_df]

        #Calculate the dilution factor or "ISTD_to_Sample_Amount_Ratio"
        Sample_Annot_df["ISTD_to_Sample_Amount_Ratio"] = Sample_Annot_df["ISTD_Mixture_Volume_[uL]"].astype('float64') / Sample_Annot_df["Sample_Amount"].astype('float64')
        #Convert positive and negative infinity to NaN
        Sample_Annot_df["ISTD_to_Sample_Amount_Ratio"] = Sample_Annot_df["ISTD_to_Sample_Amount_Ratio"].replace([np.inf, -np.inf], np.nan)

        #Filter the Transition_Name_df to get the Sample_Name column
        if allow_multiple_istd :
            merged_df = Transition_Name_df.loc[:, Transition_Name_df.columns == ("Sample_Name","")]
            #Assuming the Sample_Name is on the first level and blank on the second level
            merged_df.columns = merged_df.columns.droplevel(1)
        else:
            merged_df = Transition_Name_df.loc[:, Transition_Name_df.columns == "Sample_Name"]

        # We cannot accept duplicated Sample_Name in Transition_Name_df input (Input normalised area data frame)
        if(len(merged_df[["Sample_Name"]][merged_df[["Sample_Name"]].duplicated(keep=False)]) > 0):
            #Return empty data set
            if logger:
                logger.warning('Skipping step to get normConc. Input normalised area data frame has non-unique Sample_Name.')
                logger.warning('\n{}'.format(merged_df[["Sample_Name"]][merged_df[["Sample_Name"]].duplicated(keep=False)].to_string(index=False) ) )
            if ingui:
                print('Skipping step to get normConc. Input normalised area has non-unique Sample_Name.' ,flush=True)
                print(merged_df[["Sample_Name"]][merged_df[["Sample_Name"]].duplicated(keep=False)].to_string(index=False), flush =True)
            return [Conc_df,Conc_df,Conc_df]

        # Now that we have Sample_Name in Transition_Name_df and Sample_Annot_df, we need to check if they can be merged.

        # Give a warning if there are samples in the raw data that the sample annotation file do not have.
        # In the row concatenation case, the Sample_Name should all be unique
        # In the column concatenation case, the Sample_Name should be repeated for every
        # Data_File_Name group
        unique_Sample_Name_list =  Sample_Annot_df["Sample_Name"].tolist()
        merged_Sample_Name_list = merged_df["Sample_Name"].tolist()
        unused_Sample_Name_list = sorted(list(set(merged_Sample_Name_list).difference(unique_Sample_Name_list)))
        if(len(unused_Sample_Name_list) > 0):
            if logger:
                logger.warning('There are Sample Names in the input raw data set that is ' +
                               'not in the Sample_Name column of the Sample Annotation sheet.\n' +
                               "\n".join(unused_Sample_Name_list) + '\n' +
                               'Check that these sample names are in the Sample_Annot sheet. ' +
                               'Make sure the corresponding Data_File_Name is correct.')
            if ingui:
                print('There are Sample Names in the input raw data set that is ' +
                      'not in the Sample_Name column of the Sample Annotation sheet.\n' +
                      "\n".join(unused_Sample_Name_list) + '\n' +
                      'Check that these sample names are in the Sample_Annot sheet. ' +
                      'Make sure the corresponding Data_File_Name is correct.',
                      flush=True)

        # Merge it with the Sample_Annot_df so that the order of the Sample_name follows Transition_Name_df
        # We do a left join merge so samples not present in Transition_Name_df will not be used.
        merged_df = pd.merge(merged_df, Sample_Annot_df.loc[:, ["Sample_Name","ISTD_to_Sample_Amount_Ratio"]], 
                             how="left", on="Sample_Name")

        ISTD_Samp_Ratio_df = pd.DataFrame(index=Transition_Name_df.index, columns=Transition_Name_df.columns, dtype='float64')
        #ISTD_Samp_Ratio_df.apply(lambda x: x.update(merged_df["ISTD_to_Sample_Amount_Ratio"]) , axis=0)
        ISTD_Samp_Ratio_df = ISTD_Samp_Ratio_df.apply(lambda x: merged_df["ISTD_to_Sample_Amount_Ratio"] , axis=0)

        #Assignment of string must come after df apply
        ISTD_Samp_Ratio_df['Sample_Name'] = Transition_Name_df['Sample_Name']
        #print(ISTD_Samp_Ratio_df,flush=True)
        #print(ISTD_Samp_Ratio_df.info())

        #Perform an elementwise multiplication so that it is easy to debug.
        Conc_df.iloc[:,1:] = Transition_Name_df.iloc[:,1:].astype('float64') * ISTD_Conc_df.iloc[:,1:].astype('float64') * ISTD_Samp_Ratio_df.iloc[:,1:].astype('float64')

        #Convert positive and negative infinity to NaN
        Conc_df = Conc_df.replace([np.inf, -np.inf], np.nan)
        ISTD_Conc_df = ISTD_Conc_df.replace([np.inf, -np.inf], np.nan)
        ISTD_Samp_Ratio_df = ISTD_Samp_Ratio_df.replace([np.inf, -np.inf], np.nan)

        return [Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df]