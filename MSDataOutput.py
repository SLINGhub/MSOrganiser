from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from pandas import ExcelWriter
import os
import sys
import pandas as pd


class MSDataOutput:
    """
    A class to describe the general setup for Data Output.

    Args:
        output_directory (str): directory path to output the data
        input_file_path (str): file path of the input MRM transition name file. To be used for the output filename
        logger (object): logger object created by start_logger in MSOrganiser
        ingui (bool): if True, print analysis status to screen

    """
    def __init__(self, output_directory, input_file_path, result_name = "Results" ,logger=None, ingui=True):
        self.output_directory = output_directory
        self.output_filename = os.path.splitext(os.path.basename(input_file_path))[0]
        self.result_name = result_name
        self.logger = logger
        self.ingui = ingui
        self.writer = None

    def transpose_MSdata(MS_df):
        """Function to transpose data

        Args:
            MS_df (pandas DataFrame): A panda data frame

        Returns:
            MS_df (pandas DataFrame): A panda data frame with data transposed

        """
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
        """Function to open a writer object"""
        self.writer = os.path.join(self.output_directory, self.output_filename)

    def df_to_file_preparation(output_option,df,transpose=False,logger=None,ingui=False):
        """Function to check and set up the settings needed before writing to a file.

        Args:
            output_option (str): the Output_Options value given to MSOrganiser.
            df (pandas DataFrame): A panda data frame to output
            transpose (bool): if True, transpose the dataframe first before writing to the Excel sheet
            logger (object): logger object created by start_logger in MSOrganiser
            ingui (bool): if True, print analysis status to screen

        Returns:
            (list): list containing:

                * df (pandas DataFrame): A panda data frame to output. Transposed if transpose is set to True
                * output_option (str): Updated output options if changes are required E.g S/N to S_to_N
        
        """

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
        """Funtion to write a df to a csv file named {input file name}_{output_option}_{result filename}.csv .

        Args:
            output_option (str): the name of the result csv file. MSOrganiser puts it as the Output_Options value
            df (pandas DataFrame): A panda data frame to output to csv
            transpose (bool): if True, transpose the dataframe first before writing to the Excel sheet

        Note:
            For the output option S/N, it will be changed to S_to_N as filenames does not accept slashes. This is done in the function df_to_file_preparation
        
        """
        if self.writer is None:
            self.start_writer()

        [df,output_option] = MSDataOutput.df_to_file_preparation(output_option,df,transpose,self.logger,self.ingui)

        #If df is empty, just leave the function, warning has been sent to df_to_file_preparation
        if df.empty:
            return

        df.to_csv(self.writer + '_' + self.result_name + '_' + output_option + '.csv',sep=',',index=False)

class MSDataOutput_csv(MSDataOutput):
    """
    A class to describe the general setup for Data Output to csv.

    Args:
        output_directory (str): directory path to output the data
        input_file_path (str): file path of the input MRM transition name file. To be used for the output filename
        logger (object): logger object created by start_logger in MSOrganiser
        ingui (bool): if True, print analysis status to screen

    """
    def df_to_file(self,output_option,df,transpose=False):
        """Funtion to write a df to an excel file.

        Args:
            output_option (str): the name of the sheet
            df (pandas DataFrame): A panda data frame to output to Excel
            transpose (bool): if True, transpose the dataframe first before writing to the Excel sheet
        
        Note:
            For the output option S/N, it will be changed to S_to_N as excel does not accept slashes. This is done in the function df_to_file_preparation
        
        """
        if self.writer is None:
            self.start_writer()

        [df,output_option] = MSDataOutput.df_to_file_preparation(output_option,df,transpose,self.logger,self.ingui)

        #If df is empty, just leave the function, warning has been sent to df_to_file_preparation
        if df.empty:
            return

        if(output_option in ['Sample_Annot', 'Transition_Name_Annot']) :
            csv_filename = output_option + '.csv'
        else:
            csv_filename = self.writer + '_' + self.result_name + '_' + output_option + '.csv'

        try:
            df.to_csv(csv_filename,sep=',',index=False)
        except Exception as e:
            print("Unable to write df to csv file name" + csv_filename,flush=True)
            print(e,flush=True)

class MSDataOutput_Excel(MSDataOutput):
    """
    A class to describe the general setup for Data Output to Excel.

    Args:
        output_directory (str): directory path to output the data
        input_file_path (str): file path of the input MRM transition name file. To be used for the output filename
        logger (object): logger object created by start_logger in MSOrganiser
        ingui (bool): if True, print analysis status to screen

    """
    def start_writer(self):
        """Function to open an Excel writer object using openpyxl"""
        self.writer = os.path.join(self.output_directory, self.output_filename + '_' +  self.result_name + '.xlsx' )
        self.writer = ExcelWriter(self.writer,engine='openpyxl')

    def end_writer(self):
        """Function to close an Excel writer object"""
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

    def __get_col_widths(dataframe):
        """Function to get the correct width to output the excel file nicely"""
        # First we find the maximum length of the index column   
        idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
        # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
        return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) + 1 for col in dataframe.columns]

    def df_to_file(self,output_option,df,transpose=False):
        """Funtion to write a df to an excel file.

        Args:
            output_option (str): the name of the sheet
            df (pandas DataFrame): A panda data frame to output to Excel
            transpose (bool): if True, transpose the dataframe first before writing to the Excel sheet
        
        Note:
            For the output option S/N, it will be changed to S_to_N as excel does not accept slashes. This is done in the function df_to_file_preparation
        
        """
        if self.writer is None:
            self.start_writer()

        [df,output_option] = MSDataOutput.df_to_file_preparation(output_option,df,transpose,self.logger,self.ingui)

        #If df is empty, just leave the function, warning has been sent to df_to_file_preparation
        if df.empty:
            return

        try:
            df.to_excel(excel_writer=self.writer,sheet_name=output_option, index=False)
            worksheet = self.writer.sheets[output_option]
            for i, width in enumerate(MSDataOutput_Excel.__get_col_widths(df)):
                if i==0:
                    continue
                worksheet.column_dimensions[get_column_letter(i)].width = width + 1
        except Exception as e:
            print("Unable to write df to excel file",flush=True)
            print(e,flush=True)