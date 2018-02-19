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

    def checkExcelWorksheet_in_Workbook(self,sheetname,wb):
        #Check if the excel file has the sheet "Transition_Name_Annot"
        if sheetname not in wb.sheetnames:
            if self.__logger:
                self.__logger.error('Sheet name ' + sheetname + ' does not exists. Please check the input excel file')
            if self.__ingui:
                print('Sheet name ' + sheetname + ' does not exists. Please check the input excel file',flush=True)
            sys.exit(-1)

    def check_if_df_is_empty(self,sheetname,df):
        #Validate the Transition_Name_Annot sheet has data
        if df.empty:
            if self.__logger:
                self.__logger.warning('The input ' + sheetname + ' data frame has no data.')
            if self.__ingui:
                print('The input ' + sheetname + ' data frame has no data.',flush=True)
            sys.exit(-1)

    def checkColumns_in_df(self,colname,sheetname,df):
        #Check if the column name exists as a header in the df
        if colname not in df:
            if self.__logger:
                self.__logger.error('The ' + sheetname  + ' sheet is missing the column ' + colname + '.')
            if self.__ingui:
                print('The ' + sheetname  + ' sheet is missing the column ' + colname + '.',flush=True)
            sys.exit(-1)

    def checkDuplicates_in_cols(self,colname,sheetname,df):
        #Check if Transition_Name column has duplicate Transition_Names
        duplicateValues = df[colname].duplicated()
        if duplicateValues.any():
            duplicatelist = [ str(int(i) + 2)  for i in duplicateValues[duplicateValues==True].index.tolist()]
            if self.__logger:
                self.__logger.error('The ' + colname + ' in the ' + sheetname + ' sheet has duplicate transition names at row %s', ', '.join(duplicatelist))
            if self.__ingui:
                print('The ' + colname + ' in the ' + sheetname + ' sheet has duplicate transition names at row ' + ', '.join(duplicatelist),flush=True)
            sys.exit(-1)

    def Read_Transition_Name_Annot_Sheet(self):
        #Open the excel file
        wb = self.readExcelWorkbook()

        #Check if the excel file has the sheet "Transition_Name_Annot"
        self.checkExcelWorksheet_in_Workbook("Transition_Name_Annot",wb)
        
        #Convert worksheet to a dataframe
        worksheet = wb["Transition_Name_Annot"]
        #Get the column names in the first row of the excel sheet
        cols = next(worksheet.values)[0:]
        Transition_Name_Annot_df = pd.DataFrame(worksheet.values, columns=cols)

        #We remove the first row as the headers as been set up
        Transition_Name_Annot_df = Transition_Name_Annot_df.iloc[1:]
        #Reset the row index
        Transition_Name_Annot_df = Transition_Name_Annot_df.reset_index(drop=True)

        #Remove rows and columns with all None, NA,NaN
        Transition_Name_Annot_df = Transition_Name_Annot_df.dropna(axis=0, how='all')
        Transition_Name_Annot_df = Transition_Name_Annot_df.dropna(axis=1, how='all')

        #Validate the Transition_Name_Annot sheet is valid (Has the Transition_Name and Transition_Name_ISTD columns are not empty)
        self.validate_Transition_Name_Annot_sheet("Transition_Name_Annot",Transition_Name_Annot_df)

        #Remove whitespaces in column names
        Transition_Name_Annot_df.columns = Transition_Name_Annot_df.columns.str.strip()
            
        #Remove whitespace for each string column
        Transition_Name_Annot_df = MS_Template.remove_whiteSpaces(Transition_Name_Annot_df)

        #Close the workbook
        wb.close()

        return Transition_Name_Annot_df

    def validate_Transition_Name_Annot_sheet(self,sheetname,Transition_Name_Annot_df):
        #Validate the Transition_Name_Annot sheet has data
        self.check_if_df_is_empty(sheetname,Transition_Name_Annot_df)

        #Check if the column Transition_Name exists as a header in Transition_Name_Annot_df
        self.checkColumns_in_df('Transition_Name',sheetname,Transition_Name_Annot_df)

        #Check if Transition_Name column has duplicate Transition_Names
        self.checkDuplicates_in_cols('Transition_Name',sheetname,Transition_Name_Annot_df)

        #Check if the column Transition_Name exists as a header in Transition_Name_Annot_df
        self.checkColumns_in_df('Transition_Name_ISTD',sheetname,Transition_Name_Annot_df)

    def Read_ISTD_Annot_Sheet(self):
        #Open the excel file
        wb = self.readExcelWorkbook()

        #Check if the excel file has the sheet "Transition_Name_Annot"
        self.checkExcelWorksheet_in_Workbook("ISTD_Annot",wb)
        
        #Convert worksheet to a dataframe
        worksheet = wb["ISTD_Annot"]

        #Check that sheet is valid
        self.validate_ISTD_Annot_Sheet(worksheet)

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
        self.checkDuplicates_in_cols('Transition_Name_ISTD','ISTD_Annot',ISTD_Annot_df)

        #Remove whitespaces in column names
        ISTD_Annot_df.columns = ISTD_Annot_df.columns.str.strip()

        #Convert all but first column to numeric
        #ISTD_Annot_df = ISTD_Annot_df.apply(pd.to_numeric, errors='ignore')
        ISTD_Annot_df['ISTD_Conc_[nM]'] = pd.to_numeric(ISTD_Annot_df['ISTD_Conc_[nM]'], errors='coerce')
        #print(ISTD_Annot_df.info())

        #Remove whitespace for each string column
        ISTD_Annot_df = MS_Template.remove_whiteSpaces(ISTD_Annot_df)

        #Close the workbook
        wb.close()
        
        return(ISTD_Annot_df)

    def validate_ISTD_Annot_Sheet(self,worksheet):
        #Check if the sheet has been tampled
        if worksheet["A2"].value != "Transition_Name_ISTD":
            if self.__logger:
                self.__logger.error('Sheet ISTD_Annot is missing the column Transition_Name_ISTD at position A2')
            if self.__ingui:
                print('Sheet ISTD_Annot is missing the column Transition_Name_ISTD at position A2',flush=True)
            sys.exit(-1)

        if worksheet["E3"].value != "ISTD_Conc_[nM]":
            if self.__logger:
                self.__logger.error('Sheet ISTD_Annot is missing the column ISTD_Conc_nM at position E3')
            if self.__ingui:
                print('Sheet ISTD_Annot is missing the column ISTD_Conc_nM at position E3',flush=True)
            sys.exit(-1)

    def Read_Sample_Annot_Sheet(self,MS_FilePathList=[]):
        #Open the excel file
        wb = self.readExcelWorkbook()

        #Check if the excel file has the sheet "Transition_Name_Annot"
        self.checkExcelWorksheet_in_Workbook("Sample_Annot",wb)
        
        #Convert worksheet to a dataframe
        worksheet = wb["Sample_Annot"]
        #Get the column names in the first row of the excel sheet
        cols = next(worksheet.values)[0:]
        Sample_Annot_df = pd.DataFrame(worksheet.values, columns=cols)

        #We remove the first row as the headers as been set up
        Sample_Annot_df = Sample_Annot_df.iloc[1:]
        #Reset the row index
        Sample_Annot_df = Sample_Annot_df.reset_index(drop=True)

        #Remove rows and columns with all None, NA,NaN
        Sample_Annot_df = Sample_Annot_df.dropna(axis=0, how='all')
        Sample_Annot_df = Sample_Annot_df.dropna(axis=1, how='all')

        #Validate the Transition_Name_Annot sheet is valid (Has the Transition_Name and Transition_Name_ISTD columns are not empty)
        self.validate_Sample_Annot_sheet("Sample_Annot",Sample_Annot_df)

        #We take the Sample Annotation data that can be found in the MS_FilePathList
        #Else we just take all of them
        if not MS_FilePathList:
            Sample_Annot_df = Sample_Annot_df[Sample_Annot_df.Raw_Data_File_Name.isin(MS_FilePathList)]

        #Remove whitespaces in column names
        Sample_Annot_df.columns = Sample_Annot_df.columns.str.strip()

        #Convert all but number columns to numeric
        Sample_Annot_df['Sample_Amount'] = pd.to_numeric(Sample_Annot_df['Sample_Amount'], errors='coerce')
        Sample_Annot_df['ISTD_Mixture_Volume_[uL]'] = pd.to_numeric(Sample_Annot_df['ISTD_Mixture_Volume_[uL]'], errors='coerce')
        #print(Sample_Annot_df.info())

        #Remove whitespace for each string column
        Sample_Annot_df = MS_Template.remove_whiteSpaces(Sample_Annot_df)

        #Close the workbook
        wb.close()

        return Sample_Annot_df

    def validate_Sample_Annot_sheet(self,sheetname,Sample_Annot_df):
        #Validate the Sample_Annot sheet has data
        self.check_if_df_is_empty(sheetname,Sample_Annot_df)

        #Check if the column Raw_Data_File_Name exists as a header in Sample_Annot_df
        self.checkColumns_in_df('Raw_Data_File_Name',sheetname,Sample_Annot_df)

        #Check if the column Merge_Status exists as a header in Sample_Annot_df
        #self.checkColumns_in_df('Merge_Status',sheetname,Sample_Annot_df)

        #Check if the column Sample_Name exists as a header in Sample_Annot_df
        self.checkColumns_in_df('Sample_Name',sheetname,Sample_Annot_df)

        #Check if the column Sample_Type exists as a header in Sample_Annot_df
        self.checkColumns_in_df('Sample_Type',sheetname,Sample_Annot_df)

        #Check if the column Sample_Amount exists as a header in Sample_Annot_df
        self.checkColumns_in_df('Sample_Amount',sheetname,Sample_Annot_df)

        #Check if the column Sample_Amount_Unit exists as a header in Sample_Annot_df
        self.checkColumns_in_df('Sample_Amount_Unit',sheetname,Sample_Annot_df)

        #Check if the column ISTD_Mixture_Volume_[uL] exists as a header in Sample_Annot_df
        self.checkColumns_in_df('ISTD_Mixture_Volume_[uL]',sheetname,Sample_Annot_df)

