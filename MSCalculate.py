import pandas as pd
import numpy as np
import sys
import os
import logging

from openpyxl import load_workbook
from Annotation import MS_Template

class ISTD_Operations():
    """A collection of functions to perform calculation"""

    #def __init__( logger=None,ingui=True):
        #logger = logger
        #ingui = ingui
        #Transition_Name_dict = {}
        #ISTD_report = []

    def remove_whiteSpaces(df):
        #Strip the whitespaces for each string columns of a df
        df[df.select_dtypes(['object']).columns] = df.select_dtypes(['object']).apply(lambda x: x.str.strip())
        return df

    def read_ISTD_map(filepath,column_name,logger=None,ingui=False):

        AnnotationList = MS_Template(filepath=filepath,column_name=column_name, logger=logger,ingui=ingui)
        Transition_Name_Annot_df = AnnotationList.Read_Transition_Name_Annot_Sheet()
        ISTD_Annot_df = AnnotationList.Read_ISTD_Annot_Sheet()

        #print(ISTD_Annot_df)
        #print(Transition_Name_Annot_df)
        #ISTD_map_df = pd.read_csv(filepath)
        #sys.exit(0)
        
        if not ISTD_Annot_df.empty:
            #Additional check to ensure each Transition_Name_ISTD in Transition_Name_Annot sheet has 
            #Also appears in  the ISTD_Annot sheet
            ISTD_list_in_Transition_Name_Annot_sheet = list(filter(None,Transition_Name_Annot_df['Transition_Name_ISTD'].unique()))
            ISTD_list_in_Annot_sheet = list(filter(None,ISTD_Annot_df['Transition_Name_ISTD'].unique()))
            missing_ISTD = set(ISTD_list_in_Transition_Name_Annot_sheet) - set(ISTD_list_in_Annot_sheet)
            if missing_ISTD:
                if self.__logger:
                    self.__logger.warning('There are Transition_Name_ISTD in Transition_Name_Annot not mentioned in ISTD_Annot.')
                if self.__ingui:
                    self.__print('There are Transition_Name_ISTD in Transition_Name_Annot not mentioned in ISTD_Annot.',flush=True)
                for Transition_Name in missing_ISTD:
                    if self.__logger:
                        self.__logger.warning('/"%s/"',Transition_Name)
                    if self.__ingui:
                        print('\"' + Transition_Name + '\"',flush=True)
            #Merge the two data frame by common ISTD
            Transition_Name_Annot_df = pd.merge(Transition_Name_Annot_df, ISTD_Annot_df, on='Transition_Name_ISTD', how='outer')

        #We leave this alone as users may put excess ISTD 
        #Remove Rows with ISTD with no Transition_Names
        Transition_Name_Annot_df = Transition_Name_Annot_df.dropna(subset=['Transition_Name'])

        return Transition_Name_Annot_df

    def validate_Transition_Name_df(Transition_Name_df,logger=None,ingui=False):
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

    def create_ISTD_data_from_Transition_Name_df(Transition_Name_df,Transition_Name_Annot_df,logger=None,ingui=False):

        #Create a dictionary to map the Transition_Name to the Transition_Name_ISTD and an ISTD report to map Transition_Name_ISTD to Transition_Name
        #We start a new Transition_Name_dict and ISTD_report
        Transition_Name_dict = {}
        ISTD_report = []

        #Create the Transition_Name_dict and ISTD_report
        Transition_Name_df.iloc[:,1:].apply(lambda x: ISTD_Operations.update_Transition_Name_dict(x=x,Transition_Name_Annot_df=Transition_Name_Annot_df,Transition_Name_dict=Transition_Name_dict,ISTD_report_list = ISTD_report,logger=logger,ingui=ingui),axis=0)

        #Create empty dataframe with a preset column name and index
        ISTD_data = pd.DataFrame(columns=Transition_Name_df.columns, index=Transition_Name_df.index)

        #Sample_Name must be present
        ISTD_Operations.validate_Transition_Name_df(Transition_Name_df,logger,ingui)
        ISTD_data["Sample_Name"] = Transition_Name_df["Sample_Name"]

        #Create a ISTD table from the Transition_Name df
        ISTD_data.iloc[:,1:].apply(lambda x: ISTD_Operations.update_ISTD_data_from_Transition_Name_df(x=x,Transition_Name_dict=Transition_Name_dict,Transition_Name_df=Transition_Name_df,ISTD_report_list = ISTD_report,logger=logger,ingui=ingui),axis=0)

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

    def update_Transition_Name_dict(x,Transition_Name_Annot_df,Transition_Name_dict,ISTD_report_list,logger=None,ingui=False):
        '''Updating the Transition_Name dict to map Transition_Name to their Transition_Name_ISTD'''

        #Get the mapping of one Transition_Name to exactly one ISTD
        ISTD_list = Transition_Name_Annot_df.loc[Transition_Name_Annot_df['Transition_Name']==x.name,"Transition_Name_ISTD"].tolist()

        if not ISTD_list:
            if logger:
                logger.warning("%s is not found in the Transition_Name_Annot sheet. Please check ISTD map file",x.name)
            Transition_Name_dict[x.name] = None
            ISTD_report_list.append(("!Missing Transition_Name in map file",x.name))
        elif len(ISTD_list) > 1:
            if logger:
                logger.warning("%s has duplicates or multiple internal standards. %s Please check ISTD map file",x.name," ".join(ISTD_list))
            #if ingui:
                #print(x.name + " has duplicates or multiple internal standards. " + " ".join(ISTD_list) + " Please check ISTD map file")
            ISTD_report_list.append(("!Duplicate Transition_Name_ISTD in map file",x.name))
        elif not ISTD_list[0]:
            #Value may be none
            if logger:
                logger.warning("%s has a blank internal standard. Please check ISTD map file",x.name)
                Transition_Name_dict[x.name] = None
                ISTD_report_list.append(("!Blank Transition_Name_ISTD in map file",x.name))
        elif not isinstance(ISTD_list[0],float):
            Transition_Name_dict[x.name] = ISTD_list[0]
            ISTD_report_list.append((ISTD_list[0],x.name))
        elif np.isnan(ISTD_list[0]):
            #Value may be nan
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

    def update_ISTD_data_from_Transition_Name_df(x,Transition_Name_dict,Transition_Name_df,ISTD_report_list,logger=None,ingui=False):
        '''Update the ISTD data for each Transition_Name'''
        '''Value remains as NAN when there is an issue'''

        #When a Transition_Name name has no/duplicate Transition_Name_ISTD or not found in the map file, just leave the funtion
        #A warning is already given in update_Transition_Name_dict so we do not need to write this again
        if not Transition_Name_dict[x.name]:
            return

        #When a Transition_Name name has nan Transition_Name_ISTD, just leave the funtion

        #If the Transition_Name_df has presence of duplicate Transition_Name_ISTD for the given Transition_Names or do not have the Transition_Name_ISTD indicated in the map file 
        #we will give a warning and will not update ISTD data
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

    def normalise_by_ISTD(Transition_Name_df,Transition_Name_Annot_df,logger=None,ingui=False):
        '''Perform normalisation using the values from the Transition_Name_ISTD'''
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
        ISTD_Operations.validate_Transition_Name_df(Transition_Name_df,logger,ingui)
        norm_Transition_Name_df["Sample_Name"] = Transition_Name_df["Sample_Name"]

        #Create the ISTD data from Transition_Name df and ISTD map file
        [ISTD_report,ISTD_data] = ISTD_Operations.create_ISTD_data_from_Transition_Name_df(Transition_Name_df,Transition_Name_Annot_df,logger,ingui)

        #Perform an elementwise normalisation so that it is easy to debug.
        #To prevent Division by zero error, use astype
        norm_Transition_Name_df.iloc[:,1:] = Transition_Name_df.iloc[:,1:].astype('float64') / ISTD_data.iloc[:,1:].astype('float64')

        #Convert relevant columns to numeric
        ISTD_data = ISTD_data.apply(pd.to_numeric,errors='ignore')
        norm_Transition_Name_df = norm_Transition_Name_df.apply(pd.to_numeric,errors='ignore')

        return [norm_Transition_Name_df,ISTD_data,ISTD_report]

    def create_ISTD_data_from_Transition_Name_Annot(Transition_Name_df,Transition_Name_Annot_df,ISTD_column,logger,ingui):

        #Create an empty data frame
        ISTD_data = pd.DataFrame(columns=Transition_Name_df.columns, index=Transition_Name_df.index)

        #Sample_Name must be present
        ISTD_Operations.validate_Transition_Name_df(Transition_Name_df,logger,ingui)
        ISTD_data["Sample_Name"] = Transition_Name_df["Sample_Name"]

        #Compulsory columns Transition_Name and Transition_Name_ISTD and verified when reading the Transition_Name_Annot file
        #We do not need to check for these columns again

        #Check if ISTD_column is a column in the Transition_Name_Annot_df when merged with ISTD_Annot
        if ISTD_column not in Transition_Name_Annot_df.columns:
            if logger:
                logger.warning("\"%s\" is not a column in the ISTD_Annot sheet. Returning an empty data frame",ISTD_column)
            if ingui:
                print("\"" + ISTD_column + "\" is not a column in the ISTD_Annot file. Returning an empty data frame",flush=True)
            return [ISTD_data]

        for index, row in Transition_Name_Annot_df.iterrows():
            if row['Transition_Name'] in ISTD_data.columns:
                ISTD_data[row['Transition_Name']] = row[ISTD_column]
        
        return(ISTD_data)

    def getConc_by_ISTD(Transition_Name_df,Transition_Name_Annot_df,Exp_Medium,logger=None,ingui=False):
        '''Perform calculation of conc using values from Transition_Name_Annot_ISTD'''
        #If the Transition_Name table or ISTD map df is empty, return an empty data frame
        if Transition_Name_df.empty:
            if logger:
                logger.warning("The input Transition_Name data frame has no data. Skipping step to get normConc")
            if ingui:
                print("The input Transition_Name data frame has no data. Skipping step to get normConc",flush=True)
            return [pd.DataFrame(),pd.DataFrame(),pd.DataFrame()]

        Conc_df = pd.DataFrame(columns=Transition_Name_df.columns, index=Transition_Name_df.index)

        #Sample_Name must be present
        ISTD_Operations.validate_Transition_Name_df(Transition_Name_df,logger,ingui)
        Conc_df["Sample_Name"] = Transition_Name_df["Sample_Name"]

        #If we have a plasma experiment
        if Exp_Medium == "Plasma":
            Annot_Columns = list(Transition_Name_Annot_df.columns.values)
            if all(things in Annot_Columns for things in ["ISTD_Conc_nM","ISTD_Mixture_Volume","Plasma_Volume"]):
                ISTD_Conc_df = ISTD_Operations.create_ISTD_data_from_Transition_Name_Annot(Transition_Name_df,Transition_Name_Annot_df,"ISTD_Conc_nM",logger,ingui)

                if Transition_Name_Annot_df["ISTD_Conc_nM"].isnull().any():
                    if logger:
                        logger.warning("Some ISTD_Conc_nM input values are missing. Please check the ISTD_Annot sheet. Remember to save your file")
                    if ingui:
                        print("Some ISTD_Conc_nM input values are missing. Please check the ISTD_Annot sheet. Remember to save your file",flush=True)
                if Transition_Name_Annot_df["ISTD_Mixture_Volume"].isnull().all():
                    if logger:
                        logger.warning("ISTD_Mixture input value is missing. Skipping step to get normConc")
                    if ingui:
                        print("ISTD_Mixture input value is missing. Skipping step to get normConc",flush=True)
                if Transition_Name_Annot_df["Plasma_Volume"].isnull().all():
                    if logger:
                        logger.warning("Plasma_Volume input value is missing. Skipping step to get normConc")
                    if ingui:
                        print("Plasma_Volume value is missing. Skipping step to get normConc",flush=True)

                ISTD_Conc_df = ISTD_Operations.create_ISTD_data_from_Transition_Name_Annot(Transition_Name_df,Transition_Name_Annot_df,"ISTD_Conc_nM",logger,ingui)
                Transition_Name_Annot_df["ISTD_to_Plasma_Vol_Ratio"] = Transition_Name_Annot_df["ISTD_Mixture_Volume"].astype('float64') / Transition_Name_Annot_df["Plasma_Volume"].astype('float64')
                ISTD_Samp_Ratio_df = ISTD_Operations.create_ISTD_data_from_Transition_Name_Annot(Transition_Name_df,Transition_Name_Annot_df,"ISTD_to_Plasma_Vol_Ratio",logger,ingui)
                #Perform an elementwise multiplication so that it is easy to debug.
                Conc_df.iloc[:,1:] = Transition_Name_df.iloc[:,1:].astype('float64') * ISTD_Conc_df.iloc[:,1:].astype('float64') * ISTD_Samp_Ratio_df.iloc[:,1:].astype('float64')
            else:
                #Return empty data set
                if logger:
                    logger.warning("Empty ISTD_Annot sheet is given or merging of Transition_Name_Annot and ISTD_Annot sheets is unsuccessful. Skipping step to get normConc")
                if ingui:
                    print("Empty ISTD_Annot sheet is given or merging of Transition_Name_Annot and ISTD_Annot sheets is unsuccessful. Skipping step to get normConc",flush=True)
                return [Conc_df,Conc_df,Conc_df]
 
        return [Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df]