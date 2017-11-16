import pandas as pd
import numpy as np
import sys
import os
import logging

from openpyxl import load_workbook

class ISTD_Operations():
    """A collection of functions to perform calculation"""

    #def __init__( logger=None,ingui=True):
        #logger = logger
        #ingui = ingui
        #Compound_dict = {}
        #ISTD_report = []

    def remove_whiteSpaces(df):
        #Strip the whitespaces for each string columns of a df
        df[df.select_dtypes(['object']).columns] = df.select_dtypes(['object']).apply(lambda x: x.str.strip())
        return df

    def read_ISTD_map(filepath,column_name,logger=None,ingui=False):

        #Check if input is blank/None
        if not filepath:
            if logger:
                logger.error('A ISTD map file is required to perform this calculation: %s', column_name)
            if ingui:
                print('A ISTD map file is required to perform this calculation: ' + column_name)
            sys.exit(-1)

        #Check if file exists
        if not os.path.isfile(filepath):
            if logger:
                logger.error('%s does not exists. Please check the input file',filepath)
            if ingui:
                print(filepath + ' does not exists. Please check the input file')
            sys.exit(-1)

        #Read the excel file
        #ISTD_map_df = pd.read_csv(filepath)
        try:
            wb = load_workbook(filename=filepath,data_only=True)
        except Exception as e:
            if logger:
                logger.error("Unable to read excel file %s",filepath)
                logger.error(e)
            if ingui:
                print("Unable to read excel file " + filepath)
                print(e)
            sys.exit(-1)
        
        #Check if the excel file has the sheet "ISTDmap"
        if "ISTDmap" not in wb.get_sheet_names():
            if logger:
                logger.error('Sheet name ISTDmap does not exists. Please check the input ISTD map file')
            if ingui:
                print('Sheet name ISTDmap does not exists. Please check the input ISTD map file')
            sys.exit(-1)
        else:
            #Convert worksheet to a dataframe
            worksheet = wb.get_sheet_by_name("ISTDmap")
            ISTD_map_df = worksheet.values
            cols = next(ISTD_map_df)[0:]
            ISTD_map_df = pd.DataFrame(ISTD_map_df, columns=cols)

        #Remove whitespaces in column names
        ISTD_map_df.columns = ISTD_map_df.columns.str.strip()

        #Remove whitespace for each string column
        ISTD_map_df = ISTD_Operations.remove_whiteSpaces(ISTD_map_df)

        #Validate the ISTD sheet is valid (Has the Compound and ISTD columns)
        ISTD_Operations.validate_ISTD_map(ISTD_map_df,logger,ingui)

        #Check if the excel file has the sheet "ISTDmap"
        if "ISTDannot" not in wb.get_sheet_names():
            if logger:
                logger.error('Sheet name ISTDannot does not exists. Please check the input ISTD map file')
            if ingui:
                print('Sheet name ISTDannot does not exists. Please check the input ISTD map file')
            sys.exit(-1)
        else:
            #Convert worksheet to a dataframe
            worksheet = wb.get_sheet_by_name("ISTDannot")
            ISTD_annot_df = worksheet.values
            cols = next(ISTD_annot_df)[0:]
            ISTD_annot_df = pd.DataFrame(ISTD_annot_df, columns=cols)

        #Close the workbook
        wb.close()

        #When there are inputs in this sheet
        if not ISTD_annot_df.empty:
            #Remove whitespaces in column names
            ISTD_annot_df.columns = ISTD_annot_df.columns.str.strip()
            
            #Remove whitespace for each string column
            ISTD_annot_df = ISTD_Operations.remove_whiteSpaces(ISTD_annot_df)
            
            #Validate the ISTDannot sheet is valid (Has the ISTD column)
            ISTD_Operations.validate_ISTD_annot(ISTD_annot_df,logger,ingui)

            #Additional check on ISTD_map_file to ensure each compound with ISTD has ISTD concentration and IS to Sample ratio values
            ISTD_list_in_map_sheet = list(filter(None,ISTD_map_df['ISTD'].unique()))
            ISTD_list_in_annot_sheet = list(filter(None,ISTD_annot_df['ISTD'].unique()))
            missing_ISTD = set(ISTD_list_in_map_sheet) - set(ISTD_list_in_annot_sheet)
            if missing_ISTD:
                if logger:
                    logger.warning('There are ISTD in ISTD_map not mentioned in ISTD_annot.')
                if ingui:
                    print('There are ISTD in ISTD_map not mentioned in ISTD_annot.')
                for compound in missing_ISTD:
                    if logger:
                        logger.warning('/"%s/"',compound)
                    if ingui:
                        print('\"' + compound + '\"')
            #Merge the two data frame by common ISTD
            ISTD_map_df = pd.merge(ISTD_map_df, ISTD_annot_df, on='ISTD', how='outer')
        
        #We leave this alone as users may put access ISTD 
        #Remove Rows with ISTD with no compounds
        #ISTD_map_df = ISTD_map_df.dropna(subset=['Compound'])

        return ISTD_map_df

    def validate_ISTD_map(ISTD_map_df,logger=None,ingui=False):
        #Validate the ISTD map file is valid with some compulsory columns
        if ISTD_map_df.empty:
            if logger:
                logger.warning("The input ISTD map data frame has no data.")
            if ingui:
                print("The input ISTD map data frame has no data.")
            sys.exit(-1)

        if 'Compound' not in ISTD_map_df:
            if logger:
                logger.error('The ISTD map file is missing the column Compound.')
            if ingui:
                print('The ISTD map file is missing the column Compound.')
            sys.exit(-1)

        #Check if Compound column has duplicate compounds
        duplicateValues = ISTD_map_df['Compound'].duplicated()
        if duplicateValues.any():
            duplicatelist = [ str(int(i) + 2)  for i in duplicateValues[duplicateValues==True].index.tolist()]
            if logger:
                logger.error("The Compound column in the ISTD map data has duplicate compounds at row %s", ', '.join(duplicatelist))
            if ingui:
                print("The Compound column in the ISTD map data has duplicate compounds at row " + ', '.join(duplicatelist))
            sys.exit(-1)

        if 'ISTD' not in ISTD_map_df:
            if logger:
                logger.error('The ISTD map file is missing the column ISTD.')
            if ingui:
                print('The ISTD map file is missing the column ISTD.')
            sys.exit(-1)

    def validate_ISTD_annot(ISTD_annot_df,logger=None,ingui=False):
        #Validate the ISTD annot file is valid with some compulsory columns
        #This data frame can be empty
        '''
        if ISTD_annot_df.empty:
            if logger:
                logger.error("The input ISTD annot data frame has no data.")
            if ingui:
                print("The input ISTD annot data frame has no data.")
            sys.exit(-1)
        '''

        if 'ISTD' not in ISTD_annot_df:
            if logger:
                logger.error('The ISTD annot file is missing the column ISTD.')
            if ingui:
                print('The ISTD annot file is missing the column ISTD.')
            sys.exit(-1)

        #Check if ISTD column has duplicate ISTD
        duplicateValues = ISTD_annot_df['ISTD'].duplicated()
        if duplicateValues.any():
            duplicatelist = [ str(int(i) + 2)  for i in duplicateValues[duplicateValues==True].index.tolist()]
            if logger:
                logger.error("The ISTD column in the ISTD annot data has duplicate ISTD at row %s", ', '.join(duplicatelist))
            if ingui:
                print("The ISTD column in the ISTD annot data has duplicate ISTD at row " + ', '.join(duplicatelist))
            sys.exit(-1)

    def validate_Compound_df(Compound_df,logger=None,ingui=False):
        if "Data File" not in Compound_df:
            if logger:
                logger.error("The input data frame does not contain the column Data File")
            if ingui:
                print("The input data frame does not contain the column Data File")
            sys.exit(-1)


    def create_ISTD_data_from_Compound_df(Compound_df,ISTD_map_df,logger=None,ingui=False):

        #Create a dictionary to map the Compound name to the ISTD and an ISTD report to map ISTD to Compound name
        #We start a new Compound_dict and ISTD_report
        Compound_dict = {}
        ISTD_report = []

        #Create the Compound_dict and ISTD_report
        Compound_df.iloc[:,1:].apply(lambda x: ISTD_Operations.update_Compound_dict(x=x,ISTD_map_df=ISTD_map_df,Compound_dict=Compound_dict,ISTD_report_list = ISTD_report,logger=logger,ingui=ingui),axis=0)

        #Create empty dataframe with a preset column name and index
        ISTD_data = pd.DataFrame(columns=Compound_df.columns, index=Compound_df.index)

        #Data File must be present
        ISTD_Operations.validate_Compound_df(Compound_df,logger,ingui)
        ISTD_data["Data File"] = Compound_df["Data File"]

        #Create a ISTD table from the Compound df
        ISTD_data.iloc[:,1:].apply(lambda x: ISTD_Operations.update_ISTD_data_from_Compound_df(x=x,Compound_dict=Compound_dict,Compound_df=Compound_df,ISTD_report_list = ISTD_report,logger=logger,ingui=ingui),axis=0)

        #Convert ISTD report from list to dataframe and report any warnings if any
        ISTD_report = pd.DataFrame(ISTD_report)
        ISTD_report.columns=(['ISTD','Compound'])
        ISTD_report = ISTD_report.sort_values(by=['ISTD','Compound'])

        #Check ISTD_report for any problems
        if "!Missing Compounds in map file" in ISTD_report['ISTD'].unique():
            if ingui:
                print("There are compounds in data set not mentioned in the map file.")
                for things in ISTD_report.loc[ ISTD_report['ISTD'] == "!Missing Compounds in map file" , 'Compound' ]:
                    print('\"' + things + '\"')

        if "!Duplicate ISTD in map file" in ISTD_report['ISTD'].unique():
            if ingui:
                print("There are compounds in data set with more than one internal standards mentioned in the map file.")
                for things in ISTD_report.loc[ ISTD_report['ISTD'] == "!Duplicate ISTD in map file" , 'Compound' ]:
                    print('\"' + things + '\"')

        if "!Blank ISTD in map file" in ISTD_report['ISTD'].unique():
            if ingui:
                print("There are compounds in data set mentioned in the map file but has a blank internal standard.")
                for things in ISTD_report.loc[ ISTD_report['ISTD'] == "!Blank ISTD in map file" , 'Compound' ]:
                    print('\"' + things + '\"')

        if "!Missing ISTD in data" in ISTD_report['ISTD'].unique():
            if ingui:
                print("There are internal standards in the map file that cannot be found in data set.")
                for things in ISTD_report.loc[ ISTD_report['ISTD'] == "!Missing ISTD in data" , 'Compound' ]:
                    print('\"' + things + '\"')

        if "!Duplicate ISTD in data" in ISTD_report['ISTD'].unique():
            if ingui:
                print("There are internal standards in the map file that are duplicated in data set. Please check compound file")
                for things in ISTD_report.loc[ ISTD_report['ISTD'] == "!Duplicate ISTD in data" , 'Compound' ]:
                    print('\"' + things + '\"')

        #Make ISTD column to be the index
        ISTD_report = ISTD_report.set_index(['ISTD'])

        return [ISTD_report,ISTD_data]

    def update_Compound_dict(x,ISTD_map_df,Compound_dict,ISTD_report_list,logger=None,ingui=False):
        '''Updating the Compound dict to map Compound to their ISTD'''

        #Get the mapping of one compound to exactly one ISTD
        ISTD_list = ISTD_map_df.loc[ISTD_map_df['Compound']==x.name,"ISTD"].tolist()

        if not ISTD_list:
            if logger:
                logger.warning("%s is not found in the ISTD map file. Please check ISTD map file",x.name)
            #if ingui:
                #print(x.name + " has no internal standard. Please check ISTD map file")
            Compound_dict[x.name] = None
            ISTD_report_list.append(("!Missing Compounds in map file",x.name))
        elif len(ISTD_list) > 1:
            if logger:
                logger.warning("%s has duplicates or multiple internal standards. %s Please check ISTD map file",x.name," ".join(ISTD_list))
            #if ingui:
                #print(x.name + " has duplicates or multiple internal standards. " + " ".join(ISTD_list) + " Please check ISTD map file")
            ISTD_report_list.append(("!Duplicate ISTD in map file",x.name))
        elif not ISTD_list[0]:
            #Value may be none
            if logger:
                logger.warning("%s has a blank internal standard. Please check ISTD map file",x.name)
                Compound_dict[x.name] = None
                ISTD_report_list.append(("!Blank ISTD in map file",x.name))
        elif not isinstance(ISTD_list[0],float):
            Compound_dict[x.name] = ISTD_list[0]
            ISTD_report_list.append((ISTD_list[0],x.name))
        elif np.isnan(ISTD_list[0]):
            #Value may be nan
            if logger:
                logger.warning("%s has a blank internal standard. Please check ISTD map file",x.name)
                Compound_dict[x.name] = None
                ISTD_report_list.append(("!Blank ISTD in map file",x.name))
        else:
            if logger:
                logger.warning("%s has an invalid ISTD of %s. Please check ISTD map file",x.name,str(ISTD_list[0]))
            if ingui:
                print(x.name + " has an invalid ISTD of " + str(ISTD_list[0]) + ". Please check ISTD map file")
            sys.exit(-1)

    def update_ISTD_data_from_Compound_df(x,Compound_dict,Compound_df,ISTD_report_list,logger=None,ingui=False):
        '''Update the ISTD data for each compound'''
        '''Value remains as NAN when there is an issue'''

        #When a compound name has no/duplicate ISTD or not found in the map file, just leave the funtion
        #A warning is already given in update_Compound_dict so we do not need to write this again
        if not Compound_dict[x.name]:
            return

        #When a compound name has nan ISTD, just leave the funtion

        #If the Compound_df has presence of duplicate ISTD compounds or do not have the ISTD indicated in the map file 
        #we will give a warning and will not update ISTD data
        if list(Compound_df.columns.values).count(Compound_dict[x.name]) == 1:
            x.update(Compound_df.loc[:, Compound_dict[x.name] ])
        elif list(Compound_df.columns.values).count(Compound_dict[x.name]) > 1 :
            if logger:
                logger.warning("%s appears more than once in the input data frame. Ignore normalisation in column %s", Compound_dict[x.name],x.name)
            #if ingui:
                #print(Compound_dict[x.name] + " appears more than once in the input data frame. Ignore normalisation in this column " + x.name)
            ISTD_report_list.append(("!Duplicate ISTD in data",x.name + " -> " + Compound_dict[x.name] ))
        else:
            if logger:
                logger.warning("%s cannot be found in the input data frame. Ignore normalisation in this column %s",Compound_dict[x.name],x.name)
            #if ingui:
                #print(Compound_dict[x.name] + " cannot be found in the input data frame. Ignore normalisation in this column " + x.name)
            ISTD_report_list.append(("!Missing ISTD in data", x.name + " -> " + Compound_dict[x.name] ))

    def normalise_by_ISTD(Compound_df,ISTD_map_df,logger=None,ingui=False):
        '''Perform normalisation using the values from the ISTD'''
        #If the Compound table or ISTD map df is empty, return an empty data frame
        if Compound_df.empty:
            if logger:
                logger.warning("The input Compound data frame has no data. Skipping normalisation by ISTD")
            if ingui:
                print("The input Compound data frame has no data. Skipping normalisation by ISTD")
            return [pd.DataFrame(),pd.DataFrame(),pd.DataFrame()]

        #Create empty dataframe with a preset column name and index
        ISTD_data = pd.DataFrame(columns=Compound_df.columns, index=Compound_df.index)
        norm_Compound_df = pd.DataFrame(columns=Compound_df.columns, index=Compound_df.index)

        #Data File must be present
        ISTD_Operations.validate_Compound_df(Compound_df,logger,ingui)
        norm_Compound_df["Data File"] = Compound_df["Data File"]

        #Create the ISTD data from Compound df and ISTD map file
        [ISTD_report,ISTD_data] = ISTD_Operations.create_ISTD_data_from_Compound_df(Compound_df,ISTD_map_df,logger,ingui)

        #Perform an elementwise normalisation so that it is easy to debug.
        #To prevent Division by zero error, use astype
        norm_Compound_df.iloc[:,1:] = Compound_df.iloc[:,1:].astype('float64') / ISTD_data.iloc[:,1:].astype('float64')

        #Convert relevant columns to numeric
        ISTD_data = ISTD_data.apply(pd.to_numeric,errors='ignore')
        norm_Compound_df = norm_Compound_df.apply(pd.to_numeric,errors='ignore')

        return [norm_Compound_df,ISTD_data,ISTD_report]

    def create_ISTD_data_from_map_file(Compound_df,ISTD_map_df,ISTD_column,logger,ingui):

        #Create an empty data frame
        ISTD_data = pd.DataFrame(columns=Compound_df.columns, index=Compound_df.index)

        #Data File must be present
        ISTD_Operations.validate_Compound_df(Compound_df,logger,ingui)
        ISTD_data["Data File"] = Compound_df["Data File"]

        #Compulsory columns Compound and ISTD and verified when reading the ISTD map file
        #We do not need to check for these columns again

        #Check if ISTD_column is a column in the ISTD_map_df
        if ISTD_column not in ISTD_map_df.columns:
            if logger:
                logger.warning("\"%s\" is not a column in the ISTD map file. Returning an empty data frame",ISTD_column)
            if ingui:
                print("\"" + ISTD_column + "\" is not a column in the ISTD map file. Returning an empty data frame")
            return [ISTD_data]

        for index, row in ISTD_map_df.iterrows():
            if row['Compound'] in ISTD_data.columns:
                ISTD_data[row['Compound']] = row[ISTD_column]
        
        return(ISTD_data)

    def getConc_by_ISTD(Compound_df,ISTD_map_df,logger=None,ingui=False):
        '''Perform calculation of conc using values from ISTD'''
        #If the Compound table or ISTD map df is empty, return an empty data frame
        if Compound_df.empty:
            if logger:
                logger.warning("The input Compound data frame has no data. Skipping step to get normConc")
            if ingui:
                print("The input Compound data frame has no data. Skipping step to get normConc")
            return [pd.DataFrame(),pd.DataFrame(),pd.DataFrame()]

        Conc_df = pd.DataFrame(columns=Compound_df.columns, index=Compound_df.index)

        #Data File must be present
        ISTD_Operations.validate_Compound_df(Compound_df,logger,ingui)
        Conc_df["Data File"] = Compound_df["Data File"]

        #Create the ISTD data from Compound df and ISTD map file
        if "ISTD_Conc" in list(ISTD_map_df.columns.values) and "ISTD_to_Samp_Vol_Ratio" in list(ISTD_map_df.columns.values):
            ISTD_Conc_df = ISTD_Operations.create_ISTD_data_from_map_file(Compound_df,ISTD_map_df,"ISTD_Conc",logger,ingui)
            ISTD_Samp_Ratio_df = ISTD_Operations.create_ISTD_data_from_map_file(Compound_df,ISTD_map_df,"ISTD_to_Samp_Vol_Ratio",logger,ingui)
            #Perform an elementwise multiplication so that it is easy to debug.
            Conc_df.iloc[:,1:] = Compound_df.iloc[:,1:].astype('float64') * ISTD_Conc_df.iloc[:,1:].astype('float64') * ISTD_Samp_Ratio_df.iloc[:,1:].astype('float64')
        else:
            #Return empty data set
            if logger:
                logger.warning("Empty ISTDannot sheet is given or merging of ISTDmap and ISTDannot sheets is unsuccessful. Skipping step to get normConc")
            if ingui:
                print("Empty ISTDannot sheet is given or merging of ISTDmap and ISTDannot sheets is unsuccessful. Skipping step to get normConc")
            return [Conc_df,Conc_df,Conc_df]

        return [Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df]