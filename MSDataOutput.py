from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from pandas import ExcelWriter
import os
import sys

def start_writer(output_format,output_directory,output_filename):
    """Function to start a writer object"""
    if output_format=="Excel":
        writer = os.path.join(output_directory, output_filename + '_Results.xlsx' )
        writer = ExcelWriter(writer,engine='openpyxl')
    elif output_format=="csv":
        writer = os.path.join(output_directory, output_filename)
    return writer

def transpose_MSdata(MS_df):
    #Transpose the data
    MS_df = MS_df.T
    #Now the first column is the index, we need to convert back to a first column
    MS_df.reset_index(level=0, inplace=True)
    #Assign the column names from first row
    colnames = MS_df.iloc[0,:].astype('str').str.strip()
    MS_df.columns = colnames
    #We remove the first row because the column names are given
    MS_df = MS_df.iloc[1:]
    #Rename the first column to Compound Name
    MS_df.rename(columns={'Sample_Name':'Transition_Name'}, inplace=True)
    return MS_df

def df_to_file(writer,output_format,output_option,df,logger=None,ingui=False,transpose=False):
    """Funtion to write a df to a file"""

    #Replace '/' as excel cannot have this as sheet title
    if output_option == 'S/N':
        output_option = output_option.replace('/','_to_')

    #If df is empty we send a warning and skip the df
    if df.empty:
        if logger:
            logger.warning('%s has no data. Please check the input file',output_option)
        if ingui:
            print(output_option + ' has no data. Please check the input file',flush=True)
        return

    if transpose:
        df = transpose_MSdata(df)
   
    #Output file into Excel
    if output_format=="Excel":
        try:
            df.to_excel(excel_writer=writer,sheet_name=output_option, index=False)
            worksheet = writer.sheets[output_option]
            for i, width in enumerate(get_col_widths(df)):
                #print(get_column_letter(i+1))
                #print(width)
                #worksheet.set_column(i-1, i-1, width)
                #worksheet.column_dimensions[get_column_letter(i+1)].width = width
                if i==0:
                    continue
                worksheet.column_dimensions[get_column_letter(i)].width = width + 1
        except Exception as e:
            print("Unable to write df to excel file",flush=True)
            print(e,flush=True)
    elif output_format=="csv":
         df.to_csv(writer + output_option + '_Results.csv',sep=',',index=False)

def get_col_widths(dataframe):
    """Function to get the correct width to output the excel file nicely"""
    # First we find the maximum length of the index column   
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) + 1 for col in dataframe.columns]

def end_writer(writer,output_format,logger=None,ingui=False):
    """Function to close a writer object"""
    if output_format=="Excel":
        try:
            writer.save()
        except Exception as e:
            if ingui:
                print('Unable to save Excel file due to:',flush=True)
                print(e,flush=True)
            if logger:
                logger.error('Unable to save Excel file due to:')
                logger.error(e)
            sys.exit(-1)
