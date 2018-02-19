# coding: utf-8

#TODO
#Do it for other machines
#Plotting of graph
#CoV calculation

from MSRawData import AgilentMSRawData
from MSRawData import SciexMSRawData
from MSCalculate import ISTD_Operations
import MSDataOutput
from MSDataReport import MSDataReport_PDF

from logging.handlers import TimedRotatingFileHandler
import argparse
import os
import json
from gooey import Gooey
from gooey import GooeyParser
import sys
import logging
import pandas as pd

from datetime import datetime
import time


@Gooey(program_name='MS Data Organiser',advanced=True,default_size=(610,710),group_by_type=False)
def parse_args():
    """ Use ArgParser to build up the arguments we will use in our script"""

    """ Save the arguments in a default json file so that we can retrieve them every time we run the script."""

    stored_args = {}
    # get the script name without the extension & use it to build up
    # the json filename
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    args_file =  "{}-args.json".format(script_name)

    # Read in the prior arguments as a dictionary
    if os.path.isfile(args_file):
        with open(args_file) as data_file:
            stored_args = json.load(data_file)

    parser = GooeyParser(description='Create summary tables from MassHunter csv files')

    if not stored_args.get('Output_Format'):
        Output_Format = 'Excel'
    else:
        Output_Format = stored_args.get('Output_Format')

    if not stored_args.get('Transpose_Results'):
        Transpose_Results = 'False'
    else:
        Transpose_Results = stored_args.get('Transpose_Results')
        if Transpose_Results == True:
            Transpose_Results = 'True'
        else:
            Transpose_Results = 'False'

    #Required Arguments 
    parser.add_argument('--MS_Files',action='store',nargs="+",help="Input the MS raw files.\nData File is a required column for MassHunter\nSample Name and Component Name are required columns for Sciex", 
                        widget="MultiFileChooser",default=stored_args.get('MS_Files'))
    #parser.add_argument('MS_Files_Type',action='store',nargs="+",help="Input the MS raw files.\nData File is a required column for MassHunter", widget="MultiFileChooser",default=stored_args.get('MS_Files'))
    parser.add_argument('--Output_Directory',action='store', help="Output directory to save summary report.", widget="DirChooser",default=stored_args.get('Output_Directory'))
    parser.add_argument('--Output_Format', choices=['Excel'], help='Select specific file type to output', default=Output_Format)
    parser.add_argument('--Transpose_Results', choices=['True','False'], help='Set this option to True to let the samples be the columns instead of the Transition_Names',default=Transpose_Results)
    
    #Optional Arguments 
    parser.add_argument('--ISTD_Map', action='store', help='Input the ISTD map file. Required for normalisation', widget="FileChooser",default=stored_args.get('ISTD_Map'))
    parser.add_argument('--Output_Options', choices=['Area','normArea by ISTD','normConc by ISTD','RT','FWHM','S/N','Precursor Ion','Product Ion'], nargs="+", help='Select specific information to output', widget="Listbox", default=stored_args.get('Output_Options'))
    parser.add_argument('--Testing', action='store_true', help='Testing mode will generate more output tables.')

    #parser.add_argument('--Transpose_Results', action='store_false', help='Select this option to let the samples be the columns',default=defaults.get('Transpose_Results'))

    args = parser.parse_args()

    #Convert the string in Transpose Results to boolean
    if args.Transpose_Results == 'True':
        args.Transpose_Results = True
    else:
        args.Transpose_Results = False

    #Join the list of file paths into one string separated by semicolon
    args_dict = vars(args)
    args_dict['MS_Files'] = ";".join(args_dict['MS_Files'])

    #Check if Output_Options is selected
    if not args_dict['Output_Options']:
        print("Please key in at least one result to output",flush=True)
        sys.exit(-1)

    #Store the values of the arguments so we have them next time we run
    #Json file will be the same directory as the exe file
    args_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),args_file)
    try:
        with open(args_file, 'w') as data_file:
            # Using vars(args) returns the data as a dictionary
            json.dump(vars(args), data_file)
    except Exception as e:
        print("Warning: Unable to save input settings in " + args_file + " due to this error message",flush=True)
        print(e,flush=True)
        #sys.exit(-1)

    return args

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

def get_Parameters_df(conf,MS_FilePath):
    Parameter_list = []
    args_dict = vars(conf)

    #Get specific keys into the parameters list
    Parameter_list.append(("Input_File",os.path.basename(MS_FilePath)))

    if args_dict['Output_Format']:
        Parameter_list.append(("Output_Format",args_dict['Output_Format']))

    if args_dict['ISTD_Map']:
        Parameter_list.append(("ISTD_Map_File",os.path.basename(args_dict['ISTD_Map'])))

    if args_dict['Output_Options']:
        for things in args_dict['Output_Options']:
            Parameter_list.append(("Output_Options",things))

    Parameters_df = pd.DataFrame(Parameter_list,columns=['Parameters', 'Value'])
    return Parameters_df

if __name__ == '__main__':

    #Read the parser
    conf = parse_args()

    #Start log on a job
    #Logfile will be the same directory as the exe file
    logger = start_logger(os.path.abspath(os.path.dirname(sys.argv[0])))
    logger.info("Starting the job.")
    print("Starting the job.",flush=True)

    #We do this for every mass hunter file output
    for MS_FilePath in conf.MS_Files.split(';'):

        print("Working on " + MS_FilePath,flush=True)
        logger.info("Working on " + MS_FilePath)

        #Check if file is from Agilent or Sciex
        if MS_FilePath.endswith('.csv'):
            RawData = AgilentMSRawData(filepath=MS_FilePath,logger=logger)
        elif MS_FilePath.endswith('.txt'):
            RawData = SciexMSRawData(filepath=MS_FilePath,logger=logger)
        output_filename = os.path.splitext(os.path.basename(MS_FilePath))[0]

        #Initiate the pdf report file
        PDFReport = MSDataReport_PDF(output_file_path = os.path.join(conf.Output_Directory , output_filename), logger=logger)

        #Generate the parameters report
        Parameters_df = get_Parameters_df(conf,MS_FilePath)
        PDFReport.create_parameters_report(Parameters_df)

        #Set up the file writing configuration for Excel, ...
        writer = MSDataOutput.start_writer(conf.Output_Format,conf.Output_Directory,output_filename)
        
        if conf.Output_Options:
            for column_name in conf.Output_Options:
                if column_name == 'normArea by ISTD':
                    #Perform normalisation using ISTD
                    #Get Area Table
                    Area_df = RawData.get_table('Area',is_numeric=True)
                    #Get ISTD map df
                    ISTD_map_df = ISTD_Operations.read_ISTD_map(conf.ISTD_Map,column_name,logger,ingui=True)
                    #Perform normalisation using ISTD
                    [norm_Area_df,ISTD_Area,ISTD_Report] = ISTD_Operations.normalise_by_ISTD(Area_df,ISTD_map_df,logger,ingui=True)
                    #Output the normalised area results
                    if conf.Testing:
                        MSDataOutput.df_to_file(writer,conf.Output_Format,"ISTD Area",ISTD_Area,logger,ingui=True,transpose=conf.Transpose_Results)
                    MSDataOutput.df_to_file(writer,conf.Output_Format,"ISTD map",ISTD_map_df,logger,ingui=True)
                    MSDataOutput.df_to_file(writer,conf.Output_Format,column_name,norm_Area_df,logger,ingui=True,transpose=conf.Transpose_Results)

                    #Generate the ISTD normalisation report
                    PDFReport.create_ISTD_report(ISTD_Report)

                elif column_name == 'normConc by ISTD':
                    try:
                        norm_Area_df
                    except NameError:
                        #Perform normalisation using ISTD
                        #Get Area Table
                        Area_df = RawData.get_table('Area',is_numeric=True)
                        #Get ISTD map df
                        ISTD_map_df = ISTD_Operations.read_ISTD_map(conf.ISTD_Map,column_name,logger,ingui=True)
                        #Perform normalisation using ISTD
                        [norm_Area_df,ISTD_Area,ISTD_Report] = ISTD_Operations.normalise_by_ISTD(Area_df,ISTD_map_df,logger,ingui=True)

                        #Generate the ISTD normalisation report
                        PDFReport.create_ISTD_report(ISTD_Report)

                    #Perform concentration calculation
                    #Get Sample_Annot_df
                    Sample_Annot_df = ISTD_Operations.read_Sample_Annot(conf.ISTD_Map,[os.path.basename(MS_FilePath)],column_name,logger,ingui=True)
                    [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df] = ISTD_Operations.getConc_by_ISTD(norm_Area_df,ISTD_map_df,Sample_Annot_df,logger,ingui=True)
                    if conf.Testing:
                        MSDataOutput.df_to_file(writer,conf.Output_Format,"ISTD Conc",ISTD_Conc_df,logger,ingui=True,transpose=conf.Transpose_Results)
                        MSDataOutput.df_to_file(writer,conf.Output_Format,"ISTD to Samp Vol Ratio",ISTD_Samp_Ratio_df,logger,ingui=True,transpose=conf.Transpose_Results)
                    MSDataOutput.df_to_file(writer,conf.Output_Format,"ISTD map",ISTD_map_df,logger,ingui=True)
                    MSDataOutput.df_to_file(writer,conf.Output_Format,column_name,norm_Conc_df,logger,ingui=True,transpose=conf.Transpose_Results)

                else:
                    #We extract the data directly from the file and output accordingly
                    Output_df = RawData.get_table(column_name,is_numeric=True)
                    MSDataOutput.df_to_file(writer,conf.Output_Format,column_name,Output_df,logger,ingui=True,transpose=conf.Transpose_Results)

        #End the writing configuration for Excel, ...
        MSDataOutput.end_writer(writer,conf.Output_Format,logger,ingui=True)

        #Output the report to a pdf file
        PDFReport.output_to_PDF()

    #End log on a job
    logger.info("Job is finished.")
    print("Job is finished",flush=True)