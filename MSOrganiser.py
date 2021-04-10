# coding: utf-8
import sys
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

def get_Parameters_df(stored_args, MS_FilePath):
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

    if stored_args['Annot_File']:
        Parameter_list.append(("Annot_File",os.path.basename(stored_args['Annot_File'])))

    if stored_args['Output_Options']:
        for things in stored_args['Output_Options']:
            Parameter_list.append(("Output_Options",things))

    if stored_args['Output_Format']:
        Parameter_list.append(("Output_Format",stored_args['Output_Format']))

    if stored_args['Concatenate']:
        Parameter_list.append(("Concatenate",stored_args['Concatenate']))

    if stored_args['Allow_Multiple_ISTD'] is not None:
        Parameter_list.append(("Allow_Multiple_ISTD",stored_args['Allow_Multiple_ISTD']))

    if stored_args['Transpose_Results'] is not None:
        Parameter_list.append(("Transpose_Results",stored_args['Transpose_Results']))

    if stored_args['Long_Table'] is not None:
        Parameter_list.append(("Long_Table",stored_args['Long_Table']))

    if stored_args['Long_Table_Annot'] is not None:
        Parameter_list.append(("Long_Table_Annot",stored_args['Long_Table_Annot']))

    Parameters_df = pd.DataFrame(Parameter_list,columns=['Parameters', 'Value'])
    return Parameters_df

def set_DfOutput_configuration(stored_args, MS_FilePath, result_name, logger, ingui = True):

    if stored_args['Output_Format'] == "Excel" :
        DfOutput = MSDataOutput_Excel(stored_args['Output_Directory'], MS_FilePath, result_name = result_name ,
                                      logger = logger, ingui = ingui)
    elif stored_args['Output_Format'] == "csv" :
        DfOutput = MSDataOutput_csv(stored_args['Output_Directory'], MS_FilePath, result_name = result_name ,
                                    logger = logger, ingui = ingui)

    return DfOutput


if __name__ == '__main__':

    #Read the parser
    stored_args = MSParser.parse_MSOrganiser_args()

    #Start log on a job
    #Logfile will be the same directory as the exe file
    logger = start_logger(os.path.abspath(os.path.dirname(sys.argv[0])))
    logger.info("Starting the job.")
    print("Starting the job.",flush=True)

    #In Gooey 1.0.8, there is no need to split stored_args['MS_Files'] by ";"
    #As stored_args['MS_Files'] is a list
    #Find the number of input files
    input_files_amount = len(stored_args['MS_Files'])
    concatenate_df_list = []
    concatenate_df_sheet_name = []

    #We do this for every mass hunter file output
    #MS_Files is no longer a long string of paths separated by ;, we split them into a list
    for MS_FilePath in stored_args['MS_Files']:

        print("Working on " + MS_FilePath,flush=True)
        logger.info("Working on " + MS_FilePath)

        MyData = MS_Analysis(MS_FilePath = MS_FilePath, 
                             MS_FileType = stored_args['MS_FileType'], 
                             Annotation_FilePath = stored_args['Annot_File'],
                             logger = logger, 
                             ingui = True, 
                             longtable = stored_args['Long_Table'], 
                             longtable_annot = stored_args['Long_Table_Annot'])

        #Initiate the pdf report file
        PDFReport = MSDataReport_PDF(output_directory = stored_args['Output_Directory'], 
                                     input_file_path = MS_FilePath, 
                                     logger = logger, 
                                     ingui = True)

        #Generate the parameters report
        Parameters_df = get_Parameters_df(stored_args = stored_args,
                                          MS_FilePath = MS_FilePath)
        PDFReport.create_parameters_report(Parameters_df)

        if stored_args['Transpose_Results']:
            result_name = "TransposeResults"
        else:
            result_name = "Results"

        #Set up the file writing configuration for Excel, or csv ...
        if stored_args['Concatenate']=="No Concatenate":

            DfOutput = set_DfOutput_configuration(stored_args = stored_args, 
                                                  MS_FilePath = MS_FilePath, 
                                                  result_name = result_name, 
                                                  logger = logger, ingui = True)
            DfOutput.start_writer()


        #Initialise a list of df and sheet name
        one_file_df_list = []
        one_file_df_sheet_name = []
        for column_name in stored_args['Output_Options']:
            if column_name == 'normArea by ISTD':
                #Perform normalisation using ISTD
                [norm_Area_df,ISTD_Area,ISTD_map_df,ISTD_Report] = MyData.get_Normalised_Area(column_name,stored_args['Annot_File'],
                                                                                              allow_multiple_istd = stored_args['Allow_Multiple_ISTD'])

                #Output the normalised area results

                #If testing, output the ISTD_Area results
                if stored_args['Testing']:
                    if stored_args['Concatenate']!="No Concatenate":
                        one_file_df_list.extend([ISTD_Area])
                        one_file_df_sheet_name.extend(["ISTD_Area"])
                    else:
                        DfOutput.df_to_file("ISTD_Area",ISTD_Area,transpose=stored_args['Transpose_Results'])

                #Output the normalised area and transition annotation results
                if stored_args['Concatenate']!="No Concatenate":
                    one_file_df_list.extend([ISTD_map_df,norm_Area_df])
                    one_file_df_sheet_name.extend(["Transition_Name_Annot","normArea_by_ISTD"])
                else:
                    DfOutput.df_to_file("Transition_Name_Annot",ISTD_map_df)
                    DfOutput.df_to_file("normArea_by_ISTD",norm_Area_df,transpose=stored_args['Transpose_Results'])
                    
                #Generate the ISTD normalisation report
                PDFReport.create_ISTD_report(ISTD_Report)

            elif column_name == 'normConc by ISTD':
                #Perform concentration calculation
                [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df] = MyData.get_Analyte_Concentration(column_name,stored_args['Annot_File'])

                #Remove the column "Merge_Status" as it is not relevant
                #Reorder the column such that "Concentration_Unit" is at the last column
                Sample_Annot_df = Sample_Annot_df[["Data_File_Name", "Sample_Name",
                                                   "Sample_Amount", "Sample_Amount_Unit",
                                                   "ISTD_Mixture_Volume_[uL]", "ISTD_to_Sample_Amount_Ratio",
                                                   "Concentration_Unit"]]

                if stored_args['Testing']:
                    if stored_args['Concatenate']!="No Concatenate":
                        one_file_df_list.extend([ISTD_Conc_df,ISTD_Samp_Ratio_df])
                        one_file_df_sheet_name.extend(["ISTD_Conc","ISTD_to_Samp_Amt_Ratio"])
                    else:
                        DfOutput.df_to_file("ISTD_Conc",ISTD_Conc_df,transpose=stored_args['Transpose_Results'])
                        DfOutput.df_to_file("ISTD_to_Samp_Amt_Ratio",ISTD_Samp_Ratio_df,transpose=stored_args['Transpose_Results'])

                if stored_args['Concatenate']!="No Concatenate":
                    one_file_df_list.extend([Sample_Annot_df,norm_Conc_df])
                    one_file_df_sheet_name.extend(["Sample_Annot","normConc_by_ISTD"])
                else:
                    DfOutput.df_to_file("Sample_Annot",Sample_Annot_df)
                    DfOutput.df_to_file("normConc_by_ISTD",norm_Conc_df,transpose=stored_args['Transpose_Results'])

            else:
                #We extract the data directly from the file and output accordingly
                Output_df = MyData.get_from_Input_Data(column_name)
                if stored_args['Concatenate']!="No Concatenate":
                    one_file_df_list.extend([Output_df])
                    one_file_df_sheet_name.extend([column_name])
                else:
                    DfOutput.df_to_file(column_name,Output_df,transpose=stored_args['Transpose_Results'])

        #End the writing configuration for Excel, ...
        if stored_args['Output_Format'] == "Excel":
            if stored_args['Concatenate']=="No Concatenate":
                DfOutput.end_writer()

        #Output the report to a pdf file
        PDFReport.output_to_PDF()

        #Output the LongTable Data Table in another csv or excel sheet
        if stored_args['Long_Table']:
            Long_Table_df = MyData.get_Long_Table(allow_multiple_istd = False)
            if stored_args['Concatenate']!="No Concatenate":
                one_file_df_list.extend([Long_Table_df])
                one_file_df_sheet_name.extend(["Long_Table"])
            else:
                #Set up the file writing configuration for Excel, or csv ...
                if stored_args['Output_Format'] == "Excel" :
                    DfLongOutput = MSDataOutput_Excel(stored_args['Output_Directory'], MS_FilePath, 
                                                      result_name = "Long_Table" ,logger=logger, ingui=True)
                elif stored_args['Output_Format'] == "csv" :
                    DfLongOutput = MSDataOutput_csv(stored_args['Output_Directory'], MS_FilePath, 
                                                    result_name = "" ,logger=logger, ingui=True)
                DfLongOutput.start_writer()
                DfLongOutput.df_to_file("Long_Table",Long_Table_df)
                if stored_args['Output_Format'] == "Excel" :
                    DfLongOutput.end_writer()

        #Concatenate data when this option is chosen for a given file
        if stored_args['Concatenate']!="No Concatenate":
            #When we have the first file
            if len(concatenate_df_list) == 0:
                concatenate_df_list = one_file_df_list
                concatenate_df_sheet_name = one_file_df_sheet_name
            else:
                #When we have the second file onwards
                for i in range(len(one_file_df_list)):
                    if stored_args['Concatenate']=="Concatenate along Sample Name (rows)":
                        #Concatenate all df except those indicated
                        if not one_file_df_sheet_name[i] in ["Transition_Name_Annot"]:
                            concatenate_df_list[i] = pd.concat([concatenate_df_list[i], one_file_df_list[i]], 
                                                               ignore_index=True, 
                                                               sort=False, 
                                                               axis = 0)
                    elif stored_args['Concatenate']=="Concatenate along Transition Name (columns)":
                        #Concantenate Row Wise
                        if one_file_df_sheet_name[i] in ["Transition_Name_Annot","Sample_Annot","Long_Table"]:
                            #Concatenate all df except those indicated
                            if not one_file_df_sheet_name[i] in ["Transition_Name_Annot"]:
                                concatenate_df_list[i] = pd.concat([concatenate_df_list[i], one_file_df_list[i]], 
                                                                   ignore_index=True,
                                                                   sort=False, 
                                                                   axis = 0)
                        else:
                            #Concantenate Column Wise
                            concatenate_df_list[i] = pd.concat([concatenate_df_list[i], one_file_df_list[i]], 
                                                               ignore_index=False, 
                                                               sort=False, 
                                                               axis = 1)



    #Output concatenated data after going through all the files
    if stored_args['Concatenate']!="No Concatenate":

        if stored_args['Transpose_Results']:
            result_name = "TransposeResults"
        else:
            result_name = "Results"

        logger.info("Outputting concatenated file.")
        print("Creating concatenated file.",flush=True)

        #Set up the file writing configuration for Excel, or csv ...
        if stored_args['Output_Format'] == "Excel" :
            DfConcatenateOutput = MSDataOutput_Excel(stored_args['Output_Directory'], "Concatenated", 
                                                     result_name ,logger=logger, ingui=True)
        elif stored_args['Output_Format'] == "csv" :
            DfConcatenateOutput = MSDataOutput_csv(stored_args['Output_Directory'], "Concatenated",
                                                  result_name ,logger=logger, ingui=True)
        DfConcatenateOutput.start_writer()
        for i in range(len(concatenate_df_list)):
            if concatenate_df_sheet_name[i] != "Long_Table":
                #Decide the appropriate table to perfrom the transpose if set to True.
                if concatenate_df_sheet_name[i] in ["Transition_Name_Annot","Sample_Annot"]:
                    #For these two data frame, no transpose is required.
                    DfConcatenateOutput.df_to_file(concatenate_df_sheet_name[i],concatenate_df_list[i])
                else:
                    DfConcatenateOutput.df_to_file(concatenate_df_sheet_name[i],concatenate_df_list[i],
                                                   transpose=stored_args['Transpose_Results'])
        if stored_args['Output_Format'] == "Excel" :
            DfConcatenateOutput.end_writer()

        if stored_args['Long_Table']:
            #Set up the file writing configuration for Excel, or csv ...
            if stored_args['Output_Format'] == "Excel" :
                DfConcatenateLongOutput = MSDataOutput_Excel(stored_args['Output_Directory'], "Concatenated", 
                                                             result_name = "Long_Table" ,logger=logger, ingui=True)
            elif stored_args['Output_Format'] == "csv" :
                DfConcatenateLongOutput = MSDataOutput_csv(stored_args['Output_Directory'], "Concatenated", 
                                                           result_name = "" ,logger=logger, ingui=True)
            DfConcatenateLongOutput.start_writer()
            Long_Table_index = concatenate_df_sheet_name.index("Long_Table")
            DfConcatenateLongOutput.df_to_file(concatenate_df_sheet_name[Long_Table_index],concatenate_df_list[Long_Table_index])
            if stored_args['Output_Format'] == "Excel" :
                DfConcatenateLongOutput.end_writer()



    #End log on a job
    logger.info("Job is finished.")
    print("Job is finished",flush=True)