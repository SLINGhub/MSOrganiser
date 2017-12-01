import pandas as pd
import numpy as np
import sys
import os
import logging

from openpyxl import load_workbook

class MS_Template():
    """A class to define the excel macro sheet"""
    def __init__(self,filepath,column_name, logger=None,ingui=True):
        self.__logger = logger
        self.__ingui = ingui
        self.filepath = filepath
        self.filecheck(column_name)

    def remove_whiteSpaces(df):
        #Strip the whitespaces for each string columns of a df
        df[df.select_dtypes(['object']).columns] = df.select_dtypes(['object']).apply(lambda x: x.str.strip())
        return df

    def filecheck(self,column_name):
        #Check if input is blank/None
        if not self.filepath:
            if self.__logger:
                self.__logger.error('A ISTD map file is required to perform this calculation: %s', column_name)
            if self.__ingui:
                print('A ISTD map file is required to perform this calculation: ' + column_name,flush=True)
            sys.exit(-1)

        #Check if file exists
        if not os.path.isfile(self.filepath):
            if self.__logger:
                self.__logger.error('%s does not exists. Please check the input file',self.filepath)
            if self.__ingui:
                print(filepath + ' does not exists. Please check the input file',flush=True)
            sys.exit(-1)

        if self.filepath.endswith('.csv'):
            if self.__logger:
                self.__logger.error('This program no longer accept csv file as input for the ISTD map file. Please use the excel template file given')
            if self.__ingui:
                print('This program no longer accept csv file as input for the ISTD map file. Please use the excel template file given',flush=True)
            sys.exit(-1)

    def readExcelWorkbook(self):
        #Read the excel file
        try:
            wb = load_workbook(filename=self.filepath,data_only=True)
        except Exception as e:
            if self.__logger:
                self.__logger.error("Unable to read excel file %s",self.filepath)
                self.__logger.error(e)
            if self.__ingui:
                print("Unable to read excel file " + self.filepath,flush=True)
                print(e,flush=True)
            sys.exit(-1)
        return wb

    def Read_Transition_Name_Annot_Sheet(self):
        #Open the excel file
        wb = self.readExcelWorkbook()

        #Check if the excel file has the sheet "Transition_Name_Annot"
        if "Transition_Name_Annot" not in wb.get_sheet_names():
            if self.__logger:
                self.__logger.error('Sheet name Transition_Name_Annot does not exists. Please check the input ISTD map file')
            if self.__ingui:
                print('Sheet name Transition_Name_Annot does not exists. Please check the input ISTD map file',flush=True)
            sys.exit(-1)
        else:
            #Convert worksheet to a dataframe
            worksheet = wb.get_sheet_by_name("Transition_Name_Annot")
            Transition_Name_Annot_df = worksheet.values
            cols = next(Transition_Name_Annot_df)[0:]
            Transition_Name_Annot_df = pd.DataFrame(Transition_Name_Annot_df, columns=cols)
            #Remove rows and columns with all None, NA,NaN
            Transition_Name_Annot_df = Transition_Name_Annot_df.dropna(axis=0, how='all')
            Transition_Name_Annot_df = Transition_Name_Annot_df.dropna(axis=1, how='all')

        #Validate the Transition_Name_Annot sheet is valid (Has the Transition_Name and Transition_Name_ISTD columns abd not empty)
        self.validate_Transition_Name_Annot_sheet(Transition_Name_Annot_df)

        #Remove whitespaces in column names
        Transition_Name_Annot_df.columns = Transition_Name_Annot_df.columns.str.strip()
            
        #Remove whitespace for each string column
        Transition_Name_Annot_df = MS_Template.remove_whiteSpaces(Transition_Name_Annot_df)

        #Close the workbook
        wb.close()

        return Transition_Name_Annot_df

    def validate_Transition_Name_Annot_sheet(self,Transition_Name_Annot_df):
        #Validate the Transition_Name_Annot shet is valid with some compulsory columns
        if Transition_Name_Annot_df.empty:
            if self.__logger:
                self.__logger.warning("The input Transition_Name_Annot data frame has no data.")
            if self.__ingui:
                print("The input Transition_Name_Annot data frame has no data.",flush=True)
            sys.exit(-1)

        if 'Transition_Name' not in Transition_Name_Annot_df:
            if self.__logger:
                self.__logger.error('The Transition_Name_Annot sheet is missing the column Transition_Name.')
            if self.__ingui:
                print('The Transition_Name_Annot sheet is missing the column Transition_Name.',flush=True)
            sys.exit(-1)

        #Check if Transition_Name column has duplicate Transition_Names
        duplicateValues = Transition_Name_Annot_df['Transition_Name'].duplicated()
        if duplicateValues.any():
            duplicatelist = [ str(int(i) + 2)  for i in duplicateValues[duplicateValues==True].index.tolist()]
            if self.__logger:
                self.__logger.error("The Transition_Name column in the Transition_Name_Annot data has duplicate transition names at row %s", ', '.join(duplicatelist))
            if self.__ingui:
                print("The Transition_Name column in the Transition_Name_Annot data has duplicate transition names at row " + ', '.join(duplicatelist),flush=True)
            sys.exit(-1)

        if 'Transition_Name_ISTD' not in Transition_Name_Annot_df:
            if self.__logger:
                self.__logger.error('The Transition_Name_Annot sheet is missing the column Transition_Name_ISTD.')
            if self.__ingui:
                print('The Transition_Name_Annot file is missing the column Transition_Name_ISTD.',flush=True)
            sys.exit(-1)

    def Read_ISTD_Annot_Sheet(self):
        #Open the excel file
        wb = self.readExcelWorkbook()

        #Check if the excel file has the sheet "ISTD_Annot"
        if "ISTD_Annot" not in wb.get_sheet_names():
            if self.__logger:
                self.__logger.error('Sheet name ISTD_Annot does not exists. Please check the input ISTD map file')
            if self.__ingui:
                print('Sheet name ISTD_Annot does not exists. Please check the input ISTD map file',flush=True)
            sys.exit(-1)
        else:
            #Convert worksheet to a dataframe
            worksheet = wb.get_sheet_by_name("ISTD_Annot")

            #Check that sheet is valid
            self.validate_ISTD_Annot_Sheet(worksheet)

            #Get the Extraction Volumes
            Plasma_Volume = worksheet["H2"].value
            ISTD_Mixture_Volume = worksheet["H3"].value

            #Get the column names
            cols = [worksheet["A2"].value,worksheet["E3"].value]

            #Get the ISTD Table and clean it up
            ISTD_Annot_df = worksheet.values
            ISTD_Annot_df = pd.DataFrame(ISTD_Annot_df)

            #We remove the first three row as the headers as been set up
            ISTD_Annot_df = ISTD_Annot_df.iloc[3:]

            #Reset the row index
            ISTD_Annot_df = ISTD_Annot_df.reset_index(drop=True)

            #Take specific columns (A and E only)
            ISTD_Annot_df = ISTD_Annot_df.iloc[:,[0,4]]
            ISTD_Annot_df.columns = cols

            #Remove rows with no Transition_Name_ISTD
            ISTD_Annot_df = ISTD_Annot_df.dropna(subset=['Transition_Name_ISTD'])
            #ISTD_Annot_df = ISTD_Annot_df.dropna(axis=0, how='all')

            #Check if Transition_Name_ISTD column has duplicate Transition_Name_ISTD
            duplicateValues = ISTD_Annot_df['Transition_Name_ISTD'].duplicated()
            if duplicateValues.any():
                duplicatelist = [ str(int(i) + 4)  for i in duplicateValues[duplicateValues==True].index.tolist()]
                if self.__logger:
                    self.__logger.error("The Transition_Name_ISTD column in the ISTD_Annot sheet has duplicate Transition_Name_ISTD at row %s", ', '.join(duplicatelist))
                if self.__ingui:
                    print("The Transition_Name_ISTD column in the ISTD_Annot data has duplicate Transition_Name_ISTD at row " + ', '.join(duplicatelist),flush=True)
                sys.exit(-1)

            #We add the Plasma_Volume and the ISTD_Mixture 
            ISTD_Annot_df["ISTD_Mixture_Volume"] = ISTD_Mixture_Volume
            ISTD_Annot_df["Plasma_Volume"] = Plasma_Volume

            #Remove whitespaces in column names
            ISTD_Annot_df.columns = ISTD_Annot_df.columns.str.strip()

            #Convert all but first column to numeric
            ISTD_Annot_df = ISTD_Annot_df.apply(pd.to_numeric, errors='ignore')
            #print(ISTD_Annot_df.dtypes)

            #Remove whitespace for each string column
            ISTD_Annot_df = MS_Template.remove_whiteSpaces(ISTD_Annot_df)

            return(ISTD_Annot_df)

        #Close the workbook
        self.wb.close()

    def validate_ISTD_Annot_Sheet(self,worksheet):
        #Check if the sheet has been tampled
        if worksheet["A2"].value != "Transition_Name_ISTD":
            if self.__logger:
                self.__logger.error('Sheet ISTD_Annot is missing the column Transition_Name_ISTD at position A2')
            if self.__ingui:
                print('Sheet ISTD_Annot is missing the column Transition_Name_ISTD at position A2',flush=True)
            sys.exit(-1)

        if worksheet["E3"].value != "ISTD_Conc_nM":
            if self.__logger:
                self.__logger.error('Sheet ISTD_Annot is missing the column ISTD_Conc_nM at position E3')
            if self.__ingui:
                print('Sheet ISTD_Annot is missing the column ISTD_Conc_nM at position E3',flush=True)
            sys.exit(-1)

        if worksheet["G2"].value != "Plasma":
            if self.__logger:
                self.__logger.error('Sheet ISTD_Annot is missing the column Plasma at position G2')
            if self.__ingui:
                print('Sheet ISTD_Annot is missing the column ISTD_Conc_nM at position G2',flush=True)
            sys.exit(-1)

        if worksheet["G3"].value != "ISTD_Mixture":
            if self.__logger:
                self.__logger.error('Sheet ISTD_Annot is missing the column ISTD_Mixture at position G3')
            if self.__ingui:
                print('Sheet ISTD_Annot is missing the column ISTD_Mixture at position G3',flush=True)
            sys.exit(-1)
