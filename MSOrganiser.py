# coding: utf-8

import MSParser
from MSAnalysis import MS_Analysis
from MSDataOutput import MSDataOutput_Excel
from MSDataOutput import MSDataOutput_csv
from MSDataReport import MSDataReport_PDF

from logging.handlers import TimedRotatingFileHandler

import os
import sys
import logging
import pandas as pd

from datetime import datetime
import time

def start_logger(log_directory_path):
    """To set up the log file folder and default configuration give a log directory path

    Args:
        log_directory_path (str): The directory path to create a folder containing the log files.
        
    Returns:
        logger (object): A logger object used for the MSOrganiser software.

    """

    logdirectory = os.path.join(log_directory_path,"logfiles")

    try:
        os.makedirs(logdirectory, exist_ok=True)
    except Exception as e:
        print("Unable to create log directory in " + logdirectory + " due to this error message",flush=True)
        print(e,flush=True)
        sys.exit(-1)

    logger = logging.getLogger("MSOrganiser")
    logger.setLevel(logging.INFO)

    # create file handler (fh)
    logfilename = os.path.join(logdirectory , 'Test_Log')
    fh = TimedRotatingFileHandler(logfilename,
                                       when='midnight',
                                       interval=1,
                                       backupCount=2)
    
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    # add the handlers to the logger
    logger.addHandler(fh)
    return logger

def get_Parameters_df(stored_args,MS_FilePath):
    """To set up a pandas dataframe storing the input parameters, This data frame will be converted to a PDF page

    Args:
        stored_args (dict): A dictionary storing the input parameters. The dictionary is created in MSParser
        MS_FilePath (str): The file path to the MRM transition name file.
        
    Returns:
        Parameters_df (pandas DataFrame): A dataframe storing the input parameters

    """

    Parameter_list = []

    #Get specific keys into the parameters list
    Parameter_list.append(("Input_File",os.path.basename(MS_FilePath)))

    Parameter_list.append(("Input_File_Type",stored_args['MS_FileType']))

    if stored_args['Output_Format']:
        Parameter_list.append(("Output_Format",stored_args['Output_Format']))

    if stored_args['Annot_File']:
        Parameter_list.append(("Annot_File",os.path.basename(stored_args['Annot_File'])))

    if stored_args['Output_Options']:
        for things in stored_args['Output_Options']:
            Parameter_list.append(("Output_Options",things))

    Parameters_df = pd.DataFrame(Parameter_list,columns=['Parameters', 'Value'])
    return Parameters_df

if __name__ == '__main__':

    #Read the parser
    stored_args = MSParser.parse_MSOrganiser_args()

    #Start log on a job
    #Logfile will be the same directory as the exe file
    logger = start_logger(os.path.abspath(os.path.dirname(sys.argv[0])))
    logger.info("Starting the job.")
    print("Starting the job.",flush=True)

    #We do this for every mass hunter file output
    #MS_Files is not a long string of paths separated by ;, we split them into a list
    for MS_FilePath in stored_args['MS_Files'].split(';'):

        print("Working on " + MS_FilePath,flush=True)
        logger.info("Working on " + MS_FilePath)

        MyData = MS_Analysis(MS_FilePath, stored_args['MS_FileType'], stored_args['Annot_File'],logger, ingui=True, longtable = stored_args['Long_Table'], longtable_annot = stored_args['Long_Table_Annot'])

        #Initiate the pdf report file
        PDFReport = MSDataReport_PDF(stored_args['Output_Directory'], MS_FilePath, logger, ingui=True)

        if stored_args['Transpose_Results']:
            result_name = "TransposeResults"
        else:
            result_name = "Results"

        #Set up the file writing configuration for Excel, or csv ...
        if stored_args['Output_Format'] == "Excel" :
            DfOutput = MSDataOutput_Excel(stored_args['Output_Directory'], MS_FilePath, result_name = result_name ,logger=logger, ingui=True)
        elif stored_args['Output_Format'] == "csv" :
            DfOutput = MSDataOutput_csv(stored_args['Output_Directory'], MS_FilePath, result_name = result_name ,logger=logger, ingui=True)
        DfOutput.start_writer()

        #Generate the parameters report
        Parameters_df = get_Parameters_df(stored_args,MS_FilePath)
        PDFReport.create_parameters_report(Parameters_df)

        for column_name in stored_args['Output_Options']:
            if column_name == 'normArea by ISTD':
                #Perform normalisation using ISTD
                [norm_Area_df,ISTD_Area,ISTD_map_df,ISTD_Report] = MyData.get_Normalised_Area(column_name,stored_args['Annot_File'])

                #Output the normalised area results
                if stored_args['Testing']:
                    DfOutput.df_to_file("ISTD_Area",ISTD_Area,transpose=stored_args['Transpose_Results'])
                DfOutput.df_to_file("Transition_Name_Annot",ISTD_map_df)
                DfOutput.df_to_file("normArea_by_ISTD",norm_Area_df,transpose=stored_args['Transpose_Results'])
                    
                #Generate the ISTD normalisation report
                PDFReport.create_ISTD_report(ISTD_Report)

            elif column_name == 'normConc by ISTD':
                #Perform concentration calculation
                [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df] = MyData.get_Analyte_Concentration(column_name,stored_args['Annot_File'])

                if stored_args['Testing']:
                    DfOutput.df_to_file("ISTD_Conc",ISTD_Conc_df,transpose=stored_args['Transpose_Results'])
                    DfOutput.df_to_file("ISTD_to_Samp_Vol_Ratio",ISTD_Samp_Ratio_df,transpose=stored_args['Transpose_Results'])
                DfOutput.df_to_file("Sample_Annot",Sample_Annot_df)
                DfOutput.df_to_file("normConc_by_ISTD",norm_Conc_df,transpose=stored_args['Transpose_Results'])

            else:
                #We extract the data directly from the file and output accordingly
                Output_df = MyData.get_from_Input_Data(column_name)
                DfOutput.df_to_file(column_name,Output_df,transpose=stored_args['Transpose_Results'])

        #End the writing configuration for Excel, ...
        if stored_args['Output_Format'] == "Excel" :
            DfOutput.end_writer()

        #Output the report to a pdf file
        PDFReport.output_to_PDF()
                 
        #Output the LongTable Data Table in another csv or excel sheet
        if stored_args['Long_Table']:
            #Set up the file writing configuration for Excel, or csv ...
            if stored_args['Output_Format'] == "Excel" :
                DfLongOutput = MSDataOutput_Excel(stored_args['Output_Directory'], MS_FilePath, result_name = "LongTable" ,logger=logger, ingui=True)
            elif stored_args['Output_Format'] == "csv" :
                DfLongOutput = MSDataOutput_csv(stored_args['Output_Directory'], MS_FilePath, result_name = "LongTable" ,logger=logger, ingui=True)
            DfLongOutput.start_writer()
            DfLongOutput.df_to_file("Long_Table",MyData.get_Long_Table())
            if stored_args['Output_Format'] == "Excel" :
                DfLongOutput.end_writer()

        #Output the report to a pdf file
        PDFReport.output_to_PDF()

    #End log on a job
    logger.info("Job is finished.")
    print("Job is finished",flush=True)