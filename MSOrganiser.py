# coding: utf-8

#TODO
#Do it for other machines
#Plotting of graph
#CoV calculation

import MSParser
from MSCalculate import ISTD_Operations
from MSAnalysis import MS_Analysis
import MSDataOutput
from MSDataReport import MSDataReport_PDF

from logging.handlers import TimedRotatingFileHandler

import os
import sys
import logging
import pandas as pd

from datetime import datetime
import time

def start_logger(log_directory_path):

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
    Parameter_list = []

    #Get specific keys into the parameters list
    Parameter_list.append(("Input_File",os.path.basename(MS_FilePath)))

    if stored_args['Output_Format']:
        Parameter_list.append(("Output_Format",stored_args['Output_Format']))

    if stored_args['ISTD_Map']:
        Parameter_list.append(("ISTD_Map_File",os.path.basename(stored_args['ISTD_Map'])))

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

        MyData = MS_Analysis(MS_FilePath, logger, ingui=True, testing = stored_args['Testing'])

        output_filename = os.path.splitext(os.path.basename(MS_FilePath))[0]
        #Initiate the pdf report file
        PDFReport = MSDataReport_PDF(output_file_path = os.path.join(stored_args['Output_Directory'] , output_filename), logger=logger)

        #Set up the file writing configuration for Excel, ...
        writer = MSDataOutput.start_writer(stored_args['Output_Format'],stored_args['Output_Directory'],output_filename)

        #Generate the parameters report
        Parameters_df = get_Parameters_df(stored_args,MS_FilePath)
        PDFReport.create_parameters_report(Parameters_df)
        
        for column_name in stored_args['Output_Options']:
            if column_name == 'normArea by ISTD':
                #Perform normalisation using ISTD
                [norm_Area_df,ISTD_Area,ISTD_map_df,ISTD_Report] = MyData.get_Normalised_Area(column_name,stored_args['ISTD_Map'])

                #Output the normalised area results
                if stored_args['Testing']:
                    MSDataOutput.df_to_file(writer,stored_args['Output_Format'],"ISTD Area",ISTD_Area,logger,ingui=True,transpose=stored_args['Transpose_Results'])
                MSDataOutput.df_to_file(writer,stored_args['Output_Format'],"ISTD map",ISTD_map_df,logger,ingui=True)
                MSDataOutput.df_to_file(writer,stored_args['Output_Format'],"normArea by ISTD",norm_Area_df,logger,ingui=True,transpose=stored_args['Transpose_Results'])
                    
                #Generate the ISTD normalisation report
                PDFReport.create_ISTD_report(ISTD_Report)

            elif column_name == 'normConc by ISTD':
                #Perform concentration calculation
                [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df] = MyData.get_Analyte_Concentration(column_name,stored_args['ISTD_Map'])

                if stored_args['Testing']:
                    MSDataOutput.df_to_file(writer,stored_args['Output_Format'],"ISTD Conc",ISTD_Conc_df,logger,ingui=True,transpose=stored_args['Transpose_Results'])
                    MSDataOutput.df_to_file(writer,stored_args['Output_Format'],"ISTD to Samp Vol Ratio",ISTD_Samp_Ratio_df,logger,ingui=True,transpose=stored_args['Transpose_Results'])
                MSDataOutput.df_to_file(writer,stored_args['Output_Format'],"Sample Annot",Sample_Annot_df,logger,ingui=True)
                MSDataOutput.df_to_file(writer,stored_args['Output_Format'],"normConc by ISTD",norm_Conc_df,logger,ingui=True,transpose=stored_args['Transpose_Results'])

            else:
                #We extract the data directly from the file and output accordingly
                Output_df = MyData.get_from_Input_Data(column_name)
                MSDataOutput.df_to_file(writer,stored_args['Output_Format'],column_name,Output_df,logger,ingui=True,transpose=stored_args['Transpose_Results'])
                    
        #End the writing configuration for Excel, ...
        MSDataOutput.end_writer(writer,stored_args['Output_Format'],logger,ingui=True)

        #Output the report to a pdf file
        PDFReport.output_to_PDF()

    #End log on a job
    logger.info("Job is finished.")
    print("Job is finished",flush=True)