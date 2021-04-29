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

def get_Parameters_df(stored_args, MS_FilePath = None,
                      MS_FilePaths = [], using_multiple_input_files = False):
    """To set up a pandas dataframe storing the input parameters, This data frame will be converted to a PDF page

    Args:
        stored_args (dict): A dictionary storing the input parameters. The dictionary is created in MSParser
        MS_FilePath (str): The file path to the MRM transition name file.
        MS_FilePaths (list): A list of file path to the MRM transition name file.
        using_multiple_input_files (bool): if True, the Input_File parameter will be constructed from multiple input files, denoted in MS_FilePaths (in development)
        
    Returns:
        Parameters_df (pandas DataFrame): A dataframe storing the input parameters

    """

    Parameter_list = []

    #Get specific keys into the parameters list
    if using_multiple_input_files:
        i = 1
        for input_file in [os.path.basename(file) for file in MS_FilePaths]:
            Parameter_list.append(("Input_File " + str(i),input_file))
            i +=1
    else:
        if MS_FilePath is not None:
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

def output_concatenated_wide_data(stored_args, 
                                  concatenate_df_list, concatenate_df_sheet_name,
                                  logger=None):

    #Output concatenated wide data after going through all the files
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
                DfConcatenateOutput.df_to_file(concatenate_df_sheet_name[i],concatenate_df_list[i],
                                               transpose = False,
                                               allow_multiple_istd = False)
            elif concatenate_df_sheet_name[i] in ["Area", "RT", "FWHM", "S/N", "Symmetry",
                                                  "Precursor Ion", "Product Ion"]:
                DfConcatenateOutput.df_to_file(concatenate_df_sheet_name[i],concatenate_df_list[i],
                                               transpose=stored_args['Transpose_Results'],
                                               allow_multiple_istd = False)
            else:
                DfConcatenateOutput.df_to_file(concatenate_df_sheet_name[i],concatenate_df_list[i],
                                               transpose=stored_args['Transpose_Results'],
                                               allow_multiple_istd=stored_args['Allow_Multiple_ISTD'])
    if stored_args['Output_Format'] == "Excel" :
        DfConcatenateOutput.end_writer()

def output_concatenated_long_table(stored_args, 
                                   concatenate_df_list, concatenate_df_sheet_name,
                                   logger=None):

    #Output concatenated long table
    if stored_args['Long_Table']:
        #Set up the file writing configuration for Excel, or csv ...
        if stored_args['Output_Format'] == "Excel" :
            if stored_args['Long_Table_Annot']:
                result_name = "Long_Table_with_Annot"
            else:
                result_name = "Long_Table"
            DfConcatenateLongOutput = MSDataOutput_Excel(stored_args['Output_Directory'], "Concatenated", 
                                                         result_name = result_name ,logger=logger, ingui=True)
        elif stored_args['Output_Format'] == "csv" :
            DfConcatenateLongOutput = MSDataOutput_csv(stored_args['Output_Directory'], "Concatenated", 
                                                       result_name = "" ,logger=logger, ingui=True)
        DfConcatenateLongOutput.start_writer()
        Long_Table_index = concatenate_df_sheet_name.index("Long_Table")
        if stored_args['Output_Format'] == "csv" and stored_args['Long_Table_Annot']:
            concatenate_df_sheet_name[Long_Table_index] = "Long_Table_with_Annot"
        DfConcatenateLongOutput.df_to_file(concatenate_df_sheet_name[Long_Table_index],concatenate_df_list[Long_Table_index])
        if stored_args['Output_Format'] == "Excel" :
            DfConcatenateLongOutput.end_writer()

def no_concatenate_workflow(stored_args, logger=None, testing = False):

    #Use during unit testing
    file_data_list = []
    file_name = []

    #We do this for every mass hunter file output
    #MS_Files is no longer a long string of paths separated by ;, we split them into a list
    for MS_FilePath in stored_args['MS_Files']:

        if not testing:
            print("Working on " + MS_FilePath,flush=True)
        if logger:
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
                                     ingui = True,
                                     testing = testing)

        #Generate the parameters report
        Parameters_df = get_Parameters_df(stored_args = stored_args,
                                          MS_FilePath = MS_FilePath)
        PDFReport.create_parameters_report(Parameters_df)

        if stored_args['Transpose_Results']:
            result_name = "TransposeResults"
        else:
            result_name = "Results"

        if not testing:
            #Set up the file writing configuration for Excel, or csv ...
            if stored_args['Output_Format'] == "Excel":
                DfOutput = MSDataOutput_Excel(stored_args['Output_Directory'], MS_FilePath, 
                                              result_name = result_name ,
                                              logger = logger, ingui = True)
            elif stored_args['Output_Format'] == "csv":
                DfOutput = MSDataOutput_csv(stored_args['Output_Directory'], MS_FilePath, 
                                            result_name = result_name ,
                                            logger = logger, ingui = True)
        if not testing:
            DfOutput.start_writer()

        #Use during unit testing
        file_data = []
        sheet_name = []

        for column_name in stored_args['Output_Options']:
            #Start the data extraction or analysis and output them straight away
            if column_name == 'normArea by ISTD':
                #Perform normalisation using ISTD
                [norm_Area_df,ISTD_Area,ISTD_map_df,ISTD_Report] = MyData.get_Normalised_Area(column_name,stored_args['Annot_File'],
                                                                                              allow_multiple_istd = stored_args['Allow_Multiple_ISTD'])

                #Output the normalised area results

                #If testing check box is checked and not doing unit testing, 
                #output the ISTD_Area results
                if stored_args['Testing'] and not testing:
                    DfOutput.df_to_file("ISTD_Area",ISTD_Area,
                                        transpose=stored_args['Transpose_Results'],
                                        allow_multiple_istd=stored_args['Allow_Multiple_ISTD']
                                       )

                #If testing check box is checked and doing unit testing, 
                #output the ISTD_Area in the file_data list
                if stored_args['Testing'] and testing:
                    file_data.append(ISTD_Area)
                    sheet_name.append("ISTD_Area")

                #If not doing unit testing,
                #Output the normalised area and transition annotation results
                if not testing:
                    DfOutput.df_to_file("Transition_Name_Annot",ISTD_map_df)
                    DfOutput.df_to_file("normArea_by_ISTD",norm_Area_df,
                                        transpose=stored_args['Transpose_Results'],
                                        allow_multiple_istd=stored_args['Allow_Multiple_ISTD'])

                #If doing unit testing, output the normalised area and 
                #transition annotation results in the file_data list
                if testing:
                    file_data.extend([ISTD_map_df,norm_Area_df])
                    sheet_name.extend(["Transition_Name_Annot", "normArea_by_ISTD"])
               
                #Generate the ISTD normalisation report
                PDFReport.create_ISTD_report(ISTD_Report)

            elif column_name == 'normConc by ISTD':
                #Perform concentration need_full_data
                [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df] = MyData.get_Analyte_Concentration(column_name,stored_args['Annot_File'],
                                                                                                                  allow_multiple_istd=stored_args['Allow_Multiple_ISTD'])

                #Remove the column "Merge_Status" as it is not relevant
                #Reorder the column such that "Concentration_Unit" is at the last column
                Sample_Annot_df = Sample_Annot_df[["Data_File_Name", "Sample_Name",
                                                   "Sample_Amount", "Sample_Amount_Unit",
                                                   "ISTD_Mixture_Volume_[uL]", "ISTD_to_Sample_Amount_Ratio",
                                                   "Concentration_Unit"]]

                #Output the concentration results

                #If testing check box is checked and not doing unit testing, 
                #output the ISTD_Conc and ISTD_to_Samp_Amt_Ratio results
                if stored_args['Testing'] and not testing:
                    DfOutput.df_to_file("ISTD_Conc",ISTD_Conc_df,
                                        transpose=stored_args['Transpose_Results'],
                                        allow_multiple_istd=stored_args['Allow_Multiple_ISTD'])
                    DfOutput.df_to_file("ISTD_to_Samp_Amt_Ratio",ISTD_Samp_Ratio_df,
                                        transpose=stored_args['Transpose_Results'],
                                        allow_multiple_istd=stored_args['Allow_Multiple_ISTD'])

                #If testing check box is checked and doing unit testing, 
                #output the ISTD_Conc and ISTD_to_Samp_Amt_Ratio in the file_data list
                if stored_args['Testing'] and testing:
                    file_data.extend([ISTD_Conc_df,ISTD_Samp_Ratio_df])
                    sheet_name.extend(["ISTD_Conc", "ISTD_to_Samp_Amt_Ratio"])

                #If not doing unit testing,
                #Output the concentration data and sample annotation results
                if not testing:
                    DfOutput.df_to_file("Sample_Annot",Sample_Annot_df)
                    DfOutput.df_to_file("normConc_by_ISTD",norm_Conc_df,
                                        transpose=stored_args['Transpose_Results'],
                                        allow_multiple_istd=stored_args['Allow_Multiple_ISTD'])

                #If doing unit testing, output the Sample_Annot_df and
                #norm_Conc_df results in the file_data list
                if testing:
                    file_data.extend([Sample_Annot_df, norm_Conc_df])
                    sheet_name.extend(["Sample_Annot", "normConc_by_ISTD"])


            else:
                #We extract the data directly from the file and output accordingly
                Output_df = MyData.get_from_Input_Data(column_name,
                                                       allow_multiple_istd=False)

                #If not doing unit testing,
                #Output the Output_df results
                if not testing:
                    DfOutput.df_to_file(column_name,Output_df,
                                        transpose=stored_args['Transpose_Results'],
                                        allow_multiple_istd=False)

                #If doing unit testing, output the Output_df
                #in the file_data list
                if testing:
                    file_data.append(Output_df)
                    sheet_name.append(column_name)

        #End the writing configuration for Excel, ...
        if stored_args['Output_Format'] == "Excel" and not testing:
            DfOutput.end_writer()

        #Output the report to a pdf file
        if not testing:
            PDFReport.output_to_PDF()

        #Output the LongTable Data Table in another csv or excel sheet
        if stored_args['Long_Table']:
            Long_Table_df = MyData.get_Long_Table(allow_multiple_istd=stored_args['Allow_Multiple_ISTD'],
                                                  concatenation_type = None)

            result_name = "Long_Table" 
            if stored_args['Long_Table_Annot']:
                result_name = "Long_Table_with_Annot"

            #If doing unit testing, output the Long_Table_df
            #in the file_data list
            if testing:
                file_data.append(Long_Table_df)
                sheet_name.append("Long_Table")

            if not testing:
                #Set up the file writing configuration for Excel, or csv ...
                if stored_args['Output_Format'] == "Excel":
                    DfLongOutput = MSDataOutput_Excel(stored_args['Output_Directory'], MS_FilePath, 
                                                      result_name = result_name ,logger=logger, ingui=True)
                elif stored_args['Output_Format'] == "csv":
                    DfLongOutput = MSDataOutput_csv(stored_args['Output_Directory'], MS_FilePath, 
                                                    result_name = "" ,logger=logger, ingui=True)
                DfLongOutput.start_writer()
                DfLongOutput.df_to_file("Long_Table",Long_Table_df)

                if stored_args['Output_Format'] == "Excel" :
                    DfLongOutput.end_writer()

        #Use during unit testing
        if testing:
            file_name.append(MS_FilePath)
            file_data_list.append([file_data,sheet_name])

    #Use during unit testing
    if testing:
        return([file_data_list, file_name])

def concatenate_along_rows_workflow(stored_args, logger=None, testing = False):

    #Initiate the pdf report file
    PDFReport = MSDataReport_PDF(output_directory = stored_args['Output_Directory'], 
                                 input_file_path = "ConcatenatedRow", 
                                 logger = logger, 
                                 ingui = True,
                                 testing = testing)

    #Generate the parameters report
    Parameters_df = get_Parameters_df(stored_args = stored_args,
                                      MS_FilePaths = stored_args['MS_Files'],
                                      using_multiple_input_files = True
                                      )

    PDFReport.create_parameters_report(Parameters_df)

    no_need_full_data_columns = []
    need_full_data_columns = []

    for column_name in stored_args['Output_Options']:
        if column_name in ["Area","RT","FWHM","S/N","Symmetry",
                           "Precursor Ion","Product Ion"]:
            no_need_full_data_columns.append(column_name)
        else:
            if column_name == 'normConc by ISTD' and 'normArea by ISTD' not in need_full_data_columns:
                need_full_data_columns.append("normArea by ISTD")
            need_full_data_columns.append(column_name)
            if any(['normArea by ISTD' in stored_args['Output_Options'],
                    'normConc by ISTD' in stored_args['Output_Options']
                   ]) and 'Area' not in no_need_full_data_columns:
                no_need_full_data_columns.append("Area")

    concatenate_df_list = []
    concatenate_df_sheet_name = []

    #We first need to concatenate Output Options that do not require full data like
    #Area, RT, etc
    if(len(no_need_full_data_columns) > 0):

        #We do this for every mass hunter file output
        #MS_Files is no longer a long string of paths separated by ;, we split them into a list
        for MS_FilePath in stored_args['MS_Files']:

            MyNoCalcData = MS_Analysis(MS_FilePath = MS_FilePath, 
                                       MS_FileType = stored_args['MS_FileType'], 
                                       Annotation_FilePath = stored_args['Annot_File'],
                                       logger = logger, 
                                       ingui = True, 
                                       longtable = stored_args['Long_Table'], 
                                       longtable_annot = stored_args['Long_Table_Annot'])

            #Initialise a list of df and sheet name
            one_file_df_list = []
            one_file_df_sheet_name = []

            for column_name in no_need_full_data_columns:
                #We extract the data directly from the file and put them in the list accordingly
                Output_df = MyNoCalcData.get_from_Input_Data(column_name,
                                                             allow_multiple_istd= False)
                one_file_df_list.extend([Output_df])
                one_file_df_sheet_name.extend([column_name])

            #Output the LongTable Data Table in another csv or excel sheet
            if stored_args['Long_Table']:
                Long_Table_df = MyNoCalcData.get_Long_Table(allow_multiple_istd=stored_args['Allow_Multiple_ISTD'],
                                                            concatenation_type = None)
                one_file_df_list.extend([Long_Table_df])
                one_file_df_sheet_name.extend(["Long_Table"])

            #After creating the one_file_df_list and one_file_df_sheet_name
            #Start to concatenate when we reach the second file
            if len(concatenate_df_list) == 0:
                concatenate_df_list = one_file_df_list
                concatenate_df_sheet_name = one_file_df_sheet_name
            else:
                #When we have the second file onwards
                for i in range(len(one_file_df_list)):
                    #Concatenate Row Wise all df except those indicated
                    if not one_file_df_sheet_name[i] in ["Transition_Name_Annot"]:
                        concatenate_df_list[i] = pd.concat([concatenate_df_list[i], one_file_df_list[i]], 
                                                           ignore_index=True, 
                                                           sort=False, 
                                                           axis = 0)

    #We now create data frame of output options that require the full data like
    #normArea by ISTD, normConc by ISTD, etc

    if(len(need_full_data_columns) > 0):

        MyCalcData = MS_Analysis(MS_FilePaths = stored_args['MS_Files'], 
                                 MS_FileType = stored_args['MS_FileType'], 
                                 Annotation_FilePath = stored_args['Annot_File'],
                                 logger = logger, 
                                 ingui = True, 
                                 longtable = stored_args['Long_Table'], 
                                 longtable_annot = stored_args['Long_Table_Annot'])


        #print("Working on Output options that needs to be calculated",flush=True)
        for column_name in need_full_data_columns:
            if column_name == 'normArea by ISTD':

                #Perform normalisation using ISTD
                [norm_Area_df,ISTD_Area,ISTD_map_df,ISTD_Report] = MyCalcData.get_Normalised_Area(column_name,stored_args['Annot_File'],
                                                                                                  allow_multiple_istd = stored_args['Allow_Multiple_ISTD'],
                                                                                                  using_multiple_input_files = True,
                                                                                                  concatenation_type = "rows")

                #If testing, output the ISTD_Area results in the concatenate_df list
                if stored_args['Testing']:
                    concatenate_df_list.extend([ISTD_Area])
                    concatenate_df_sheet_name.extend(["ISTD_Area"])

                #Put the normalised area and transition annotation results in the concatenate_df list
                concatenate_df_list.extend([ISTD_map_df,norm_Area_df])
                concatenate_df_sheet_name.extend(["Transition_Name_Annot","normArea_by_ISTD"])

                #Generate the ISTD normalisation report
                PDFReport.create_ISTD_report(ISTD_Report)

            elif column_name == 'normConc by ISTD':
                #Perform concentration calculation using ISTD
                [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df] = MyCalcData.get_Analyte_Concentration(column_name,stored_args['Annot_File'],
                                                                                                                      allow_multiple_istd=stored_args['Allow_Multiple_ISTD'],
                                                                                                                      using_multiple_input_files = True,
                                                                                                                      concatenation_type = "rows")

                #Remove the column "Merge_Status" as it is not relevant
                #Reorder the column such that "Concentration_Unit" is at the last column
                Sample_Annot_df = Sample_Annot_df[["Data_File_Name", "Sample_Name",
                                                   "Sample_Amount", "Sample_Amount_Unit",
                                                   "ISTD_Mixture_Volume_[uL]", "ISTD_to_Sample_Amount_Ratio",
                                                   "Concentration_Unit"]]
                
                #If testing, output the ISTD_Conc and ISTD_to_Samp_Amt_Ratio results in the list
                if stored_args['Testing']:
                    concatenate_df_list.extend([ISTD_Conc_df,ISTD_Samp_Ratio_df])
                    concatenate_df_sheet_name.extend(["ISTD_Conc","ISTD_to_Samp_Amt_Ratio"])

                #Output the concentration data and sample annotation results in the list
                concatenate_df_list.extend([Sample_Annot_df,norm_Conc_df])
                concatenate_df_sheet_name.extend(["Sample_Annot","normConc_by_ISTD"])

        #Merge the Long_Table created from calculation_columns to the Long_Table created from no_need_full_data_columns
        if stored_args['Long_Table']:
            for index, column_name in enumerate(need_full_data_columns):
                if column_name == 'normArea by ISTD':
                    need_full_data_columns[index] = 'normArea'
                if column_name == 'normConc by ISTD':
                    need_full_data_columns[index] = 'normConc'
            Long_Table_df = MyCalcData.get_Long_Table(allow_multiple_istd=stored_args['Allow_Multiple_ISTD'],
                                                      concatenation_type = "rows")
            if "Long_Table" in concatenate_df_sheet_name:
                Long_Table_index = concatenate_df_sheet_name.index("Long_Table")
                common_columns = list(set(concatenate_df_list[Long_Table_index].columns).intersection(Long_Table_df.columns))
                front_columns = [x for x in Long_Table_df.columns if x not in need_full_data_columns]
                concatenate_df_list[Long_Table_index] = pd.merge(concatenate_df_list[Long_Table_index], 
                                                                 Long_Table_df,
                                                                 how='inner',
                                                                 on = common_columns)
                col_order = front_columns + no_need_full_data_columns + need_full_data_columns
                concatenate_df_list[Long_Table_index] = concatenate_df_list[Long_Table_index][col_order]
            else:
                concatenate_df_list.extend([Long_Table_df])
                concatenate_df_sheet_name.extend(["Long_Table"])

    return([PDFReport, concatenate_df_list, concatenate_df_sheet_name])

def concatenate_along_columns_workflow(stored_args, logger=None, testing = False):

    #Initiate the pdf report file
    PDFReport = MSDataReport_PDF(output_directory = stored_args['Output_Directory'], 
                                 input_file_path = "ConcatenatedColumn", 
                                 logger = logger, 
                                 ingui = True,
                                 testing = testing)

    #Generate the parameters report
    Parameters_df = get_Parameters_df(stored_args = stored_args,
                                      MS_FilePaths = stored_args['MS_Files'],
                                      using_multiple_input_files = True
                                      )
    PDFReport.create_parameters_report(Parameters_df)

    no_need_full_data_columns = []
    need_full_data_columns = []

    for column_name in stored_args['Output_Options']:
        if column_name in ["Area","RT","FWHM","S/N","Symmetry",
                           "Precursor Ion","Product Ion"]:
            no_need_full_data_columns.append(column_name)
        else:
            if column_name == 'normConc by ISTD' and 'normArea by ISTD' not in need_full_data_columns:
                need_full_data_columns.append("normArea by ISTD")
            need_full_data_columns.append(column_name)
            if any(['normArea by ISTD' in stored_args['Output_Options'],
                    'normConc by ISTD' in stored_args['Output_Options']
                   ]) and 'Area' not in no_need_full_data_columns:
                no_need_full_data_columns.append("Area")
    
    concatenate_df_list = []
    concatenate_df_sheet_name = []

    #We first need to concatenate Output Options that do not require full data like
    #Area, RT, etc
    if(len(no_need_full_data_columns) > 0):
        #print("Working on Output options that do not need to be calculated",flush=True)

        #We do this for every mass hunter file output
        #MS_Files is no longer a long string of paths separated by ;, we split them into a list
        for MS_FilePath in stored_args['MS_Files']:

            MyNoCalcData = MS_Analysis(MS_FilePath = MS_FilePath, 
                                       MS_FileType = stored_args['MS_FileType'], 
                                       Annotation_FilePath = stored_args['Annot_File'],
                                       logger = logger, 
                                       ingui = True, 
                                       longtable = stored_args['Long_Table'], 
                                       longtable_annot = stored_args['Long_Table_Annot'])

            #Initialise a list of df and sheet name
            one_file_df_list = []
            one_file_df_sheet_name = []

            for column_name in no_need_full_data_columns:
                #We extract the data directly from the file and put them in the list accordingly
                Output_df = MyNoCalcData.get_from_Input_Data(column_name,
                                                             allow_multiple_istd = False)
                one_file_df_list.extend([Output_df])
                one_file_df_sheet_name.extend([column_name])

            #Output the LongTable Data Table in another csv or excel sheet
            if stored_args['Long_Table']:
                Long_Table_df = MyNoCalcData.get_Long_Table(allow_multiple_istd=stored_args['Allow_Multiple_ISTD'],
                                                            concatenation_type = None)
                one_file_df_list.extend([Long_Table_df])
                one_file_df_sheet_name.extend(["Long_Table"])

            #After creating the one_file_df_list and one_file_df_sheet_name
            #Start to concatenate when we reach the second file
            if len(concatenate_df_list) == 0:
                concatenate_df_list = one_file_df_list
                concatenate_df_sheet_name = one_file_df_sheet_name
            else:
                #When we have the second file onwards
                for i in range(len(one_file_df_list)):
                    #Concantenate Row Wise
                    if one_file_df_sheet_name[i] in ["Long_Table"]:
                        concatenate_df_list[i] = pd.concat([concatenate_df_list[i], one_file_df_list[i]], 
                                                           ignore_index=True,
                                                           sort=False, 
                                                           axis = 0)
                    else:
                        #Concantenate Column Wise
                        #Remove the Sample_Name column
                            appending_df = one_file_df_list[i].loc[:, one_file_df_list[i].columns != 'Sample_Name']
                            concatenate_df_list[i] = pd.concat([concatenate_df_list[i], appending_df], 
                                                               ignore_index=False, 
                                                               sort=False, 
                                                               axis = 1)

    #We now create data frame of output options that require the full data like
    #normArea by ISTD, normConc by ISTD, etc

    if(len(need_full_data_columns) > 0):

        MyCalcData = MS_Analysis(MS_FilePaths = stored_args['MS_Files'], 
                                 MS_FileType = stored_args['MS_FileType'], 
                                 Annotation_FilePath = stored_args['Annot_File'],
                                 logger = logger, 
                                 ingui = True, 
                                 longtable = stored_args['Long_Table'], 
                                 longtable_annot = stored_args['Long_Table_Annot'])


        #print("Working on Output options that needs to be calculated",flush=True)
        for column_name in need_full_data_columns:
            if column_name == 'normArea by ISTD':

                #Perform normalisation using ISTD
                [norm_Area_df,ISTD_Area,ISTD_map_df,ISTD_Report] = MyCalcData.get_Normalised_Area(column_name,stored_args['Annot_File'],
                                                                                                  allow_multiple_istd = stored_args['Allow_Multiple_ISTD'],
                                                                                                  using_multiple_input_files = True,
                                                                                                  concatenation_type = "columns")

                #If testing, output the ISTD_Area results in the concatenate_df list
                if stored_args['Testing']:
                    concatenate_df_list.extend([ISTD_Area])
                    concatenate_df_sheet_name.extend(["ISTD_Area"])

                #Put the normalised area and transition annotation results in the concatenate_df list
                concatenate_df_list.extend([ISTD_map_df,norm_Area_df])
                concatenate_df_sheet_name.extend(["Transition_Name_Annot","normArea_by_ISTD"])

                #Generate the ISTD normalisation report
                PDFReport.create_ISTD_report(ISTD_Report)

            elif column_name == 'normConc by ISTD':
                #Perform concentration calculation using ISTD
                [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df] = MyCalcData.get_Analyte_Concentration(column_name,stored_args['Annot_File'],
                                                                                                                      allow_multiple_istd=stored_args['Allow_Multiple_ISTD'],
                                                                                                                      using_multiple_input_files = True,
                                                                                                                      concatenation_type = "columns")

                #Remove the column "Merge_Status" as it is not relevant
                #Reorder the column such that "Concentration_Unit" is at the last column
                Sample_Annot_df = Sample_Annot_df[["Data_File_Name", "Sample_Name",
                                                   "Sample_Amount", "Sample_Amount_Unit",
                                                   "ISTD_Mixture_Volume_[uL]", "ISTD_to_Sample_Amount_Ratio",
                                                   "Concentration_Unit"]]
                
                #If testing, output the ISTD_Conc and ISTD_to_Samp_Amt_Ratio results in the list
                if stored_args['Testing']:
                    concatenate_df_list.extend([ISTD_Conc_df,ISTD_Samp_Ratio_df])
                    concatenate_df_sheet_name.extend(["ISTD_Conc","ISTD_to_Samp_Amt_Ratio"])

                #Output the concentration data and sample annotation results in the list
                concatenate_df_list.extend([Sample_Annot_df,norm_Conc_df])
                concatenate_df_sheet_name.extend(["Sample_Annot","normConc_by_ISTD"])

        #Merge the Long_Table created from calculation_columns to the Long_Table created from no_need_full_data_columns
        if stored_args['Long_Table']:
            for index, column_name in enumerate(need_full_data_columns):
                if column_name == 'normArea by ISTD':
                    need_full_data_columns[index] = 'normArea'
                if column_name == 'normConc by ISTD':
                    need_full_data_columns[index] = 'normConc'
            Long_Table_df = MyCalcData.get_Long_Table(allow_multiple_istd=stored_args['Allow_Multiple_ISTD'],
                                                      concatenation_type = "columns")
            if "Long_Table" in concatenate_df_sheet_name:
                Long_Table_index = concatenate_df_sheet_name.index("Long_Table")
                common_columns = list(set(concatenate_df_list[Long_Table_index].columns).intersection(Long_Table_df.columns))
                front_columns = [x for x in Long_Table_df.columns if x not in need_full_data_columns]
                concatenate_df_list[Long_Table_index] = pd.merge(Long_Table_df,
                                                                 concatenate_df_list[Long_Table_index], 
                                                                 how = 'inner',
                                                                 on = common_columns )
                col_order = front_columns + no_need_full_data_columns + need_full_data_columns
                concatenate_df_list[Long_Table_index] = concatenate_df_list[Long_Table_index][col_order]
            else:
                concatenate_df_list.extend([Long_Table_df])
                concatenate_df_sheet_name.extend(["Long_Table"])

    return([PDFReport, concatenate_df_list, concatenate_df_sheet_name])

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

    if stored_args['Concatenate']=="No Concatenate":
        no_concatenate_workflow(stored_args,logger)
    elif stored_args['Concatenate']=="Concatenate along Sample Name (rows)":
        [PDFReport, concatenate_df_list, concatenate_df_sheet_name] = concatenate_along_rows_workflow(stored_args,logger)
    elif stored_args['Concatenate']=="Concatenate along Transition Name (columns)":
        [PDFReport, concatenate_df_list, concatenate_df_sheet_name] = concatenate_along_columns_workflow(stored_args, logger)

    if stored_args['Concatenate']!="No Concatenate":
        #Output the report to a pdf file
        PDFReport.output_to_PDF()
        #Output concatenated wide data after going through all the files
        output_concatenated_wide_data(stored_args, 
                                       concatenate_df_list = concatenate_df_list, 
                                       concatenate_df_sheet_name = concatenate_df_sheet_name,
                                       logger = logger)

        #Output concatenated long table
        output_concatenated_long_table(stored_args, 
                                       concatenate_df_list = concatenate_df_list, 
                                       concatenate_df_sheet_name = concatenate_df_sheet_name,
                                       logger = logger)

    #End log on a job
    logger.info("Job is finished.")
    print("Job is finished",flush=True)