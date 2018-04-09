from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from pandas import ExcelWriter
import os
import sys
import pandas as pd


class MSDataOutput:
    """To describe the general setup for Data Output. Default to excel file"""
    def __init__(self, output_directory, input_file_path, logger=None, ingui=True):
        self.output_directory = output_directory
        self.output_filename = os.path.splitext(os.path.basename(input_file_path))[0]
        self.logger = logger
        self.ingui = ingui
        self.writer = None

    def transpose_MSdata(MS_df):
        """Function to transpose data"""
        #Transpose the data
        MS_df = MS_df.T
        #Now the first column is the index, we need to convert back to a first column
        MS_df.reset_index(level=0, inplace=True)
        #Assign the column names from first row
        colnames = MS_df.iloc[0,:].astype('str').str.strip()
        MS_df.columns = colnames
        MS_df.columns.name = None
        #We remove the first row because the column names are given
        MS_df = MS_df.iloc[1:]
        #Rename the first column to Compound Name
        MS_df.rename(columns={'Sample_Name':'Transition_Name'}, inplace=True)
        #Reset the index since we remove first row and convert numeric columns from object to numeric
        MS_df = MS_df.reset_index(drop=True)
        MS_df = MS_df.apply(pd.to_numeric, errors='ignore')
        return MS_df

    def start_writer(self):
        self.writer = os.path.join(self.output_directory, self.__output_filename)

    def df_to_file_preparation(output_option,df,transpose=False,logger=None,ingui=False):
        """Function to check and set up the settings needed for printing to file"""

        #If df is empty we send a warning and skip the df
        if df.empty:
            if logger:
                logger.warning('%s has no data. Please check the input file',output_option)
            if ingui:
                print(output_option + ' has no data. Please check the input file',flush=True)
            return([df,output_option])

        #Replace '/' as excel cannot have this as sheet title or file name
        if output_option == 'S/N':
            output_option = output_option.replace('/','_to_')

        if transpose:
            df = MSDataOutput.transpose_MSdata(df)

        return([df,output_option])


    def df_to_file(self,output_option,df,transpose=False):
        """Funtion to write a df to a csv file"""
        if self.writer is None:
            self.start_writer()

        [df,output_option] = MSDataOutput.df_to_file_preparation(output_option,df,transpose,self.logger,self.ingui)

        #If df is empty, just leave the function, warning has been sent to df_to_file_preparation
        if df.empty:
            return

        df.to_csv(self.writer + output_option + '_Results.csv',sep=',',index=False)
   

class MSDataOutput_Excel(MSDataOutput):
    """To describe the general setup for Data Output to Excel"""
    def start_writer(self):
        self.writer = os.path.join(self.output_directory, self.output_filename + '_Results.xlsx' )
        self.writer = ExcelWriter(self.writer,engine='openpyxl')

    def end_writer(self):
        """Function to close a writer object"""
        try:
            self.writer.save()
        except Exception as e:
            if self.ingui:
                print('Unable to save Excel file due to:',flush=True)
                print(e,flush=True)
            if self.logger:
                self.logger.error('Unable to save Excel file due to:')
                self.logger.error(e)
            sys.exit(-1)

    def get_col_widths(dataframe):
        """Function to get the correct width to output the excel file nicely"""
        # First we find the maximum length of the index column   
        idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
        # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
        return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) + 1 for col in dataframe.columns]

    def df_to_file(self,output_option,df,transpose=False):
        """Funtion to write a df to a excel file"""
        if self.writer is None:
            self.start_writer()

        [df,output_option] = MSDataOutput.df_to_file_preparation(output_option,df,transpose,self.logger,self.ingui)

        #If df is empty, just leave the function, warning has been sent to df_to_file_preparation
        if df.empty:
            return

        try:
            df.to_excel(excel_writer=self.writer,sheet_name=output_option, index=False)
            worksheet = self.writer.sheets[output_option]
            for i, width in enumerate(MSDataOutput_Excel.get_col_widths(df)):
                if i==0:
                    continue
                worksheet.column_dimensions[get_column_letter(i)].width = width + 1
        except Exception as e:
            print("Unable to write df to excel file",flush=True)
            print(e,flush=True)