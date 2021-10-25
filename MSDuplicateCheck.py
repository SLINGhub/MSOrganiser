import sys
from collections import Counter

def check_duplicated_columns_in_wide_data(input_wide_data, output_option,
                                          logger = None, ingui = True,
                                          allow_multiple_istd = False):
    """Function to check for duplicate column names (usually Transition Name) in a given wide data.

    Args:
        input_wide_data (pandas DataFrame): A data frame of sample as rows and transition names as columns
        output_option (str): The name of the contents that the data frame contains. Example: Area, RT etc...
        logger (object): logger object created by start_logger in MSOrganiser
        ingui (bool): if True, print analysis status to screen
        allow_multiple_istd (bool): if True, allow input_wide_data to have mulitple internal standards

    """

    # Convert the dataframe column name to a list
    column_name_list = input_wide_data.columns.values.tolist()
    # Get a list of duplicated column names
    duplicated_column_name_list = [key for key in Counter(column_name_list).keys() if Counter(column_name_list)[key] > 1]

    # When there are duplicated
    if len(duplicated_column_name_list) > 0:

        # Convert the list into a string
        duplicated_column_name_string = ""
        if allow_multiple_istd:
            duplicated_column_name_string = ", ".join(map(str, duplicated_column_name_list))
        else:
            duplicated_column_name_string = ", ".join(duplicated_column_name_list)

        # Inform the user and stop the program 
        if logger:
            logger.warning('In the %s data frame, ' + 
                           'there are column names (Transition_Name) in the output files that are duplicated. ' +
                           'The data in these duplicated column names may be different. ' +
                           'Please check the input files especially if you are concatenating by columns. ' +
                           'Duplicated columns are %s',
                           output_option, duplicated_column_name_string)
        if ingui:
            print('In the ' + output_option + ' data frame, ' + 
                  'there are column names (Transition_Name) in the output files that are duplicated. ' +
                  'The data in these duplicated column names may be different. ' +
                  'Please check the input files especially if you are concatenating by columns. ' + 
                  'Duplicated columns are ' + duplicated_column_name_string, flush=True)
        sys.exit(-1)

def check_duplicated_sample_names_in_wide_data(input_wide_data, output_option,
                                               logger = None, ingui = True,
                                               allow_multiple_istd = False):
    """Function to check for duplicate sample names in a given wide data.

    Args:
        input_wide_data (pandas DataFrame): A data frame of sample as rows and transition names as columns
        output_option (str): The name of the contents that the data frame contains. Example: Area, RT etc...
        logger (object): logger object created by start_logger in MSOrganiser
        ingui (bool): if True, print analysis status to screen
        allow_multiple_istd (bool): if True, allow input_wide_data to have mulitple internal standards

    """

    # Convert the sample name column to a list
    unique_Sample_Name_list = []
    if allow_multiple_istd:
        unique_Sample_Name_list = input_wide_data[("Sample_Name","")].tolist()
    else:
        unique_Sample_Name_list = input_wide_data["Sample_Name"].tolist()

    # Get a list of duplicated column names
    duplicated_Sample_Name_list = [key for key in Counter(unique_Sample_Name_list).keys() if Counter(unique_Sample_Name_list)[key] > 1]

    # When there are duplicated
    if len(duplicated_Sample_Name_list) > 0:

        # Convert the list into a string
        duplicated_Sample_Name_string = ", ".join(duplicated_Sample_Name_list)

        # Inform the user and stop the program 
        if logger:
            logger.warning('In the %s data frame, ' + 
                           'there are sample names in the output files that are duplicated. ' +
                           'The data in these duplicated row names may be different. ' +
                           'Please check the input files especially if you are concatenating by rows. ' +
                           'Duplicated sample names are %s',
                           output_option, duplicated_Sample_Name_string)
        if ingui:
            print('In the ' + output_option + ' data frame, ' + 
                  'there are sample names in the output files that are duplicated. ' +
                  'The data in these duplicated row names may be different. ' +
                  'Please check the input files especially if you are concatenating by rows. ' , 
                  'Duplicated sample names are ' + duplicated_Sample_Name_string, flush = True)

        sys.exit(-1)


