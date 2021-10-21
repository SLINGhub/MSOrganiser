import unittest
import os
import sys
import pandas as pd
import numpy as np
from unittest.mock import patch
from MSDuplicateCheck import check_duplicated_columns_in_wide_data
from MSDuplicateCheck import check_duplicated_sample_names_in_wide_data
from MSOrganiser import concatenate_along_columns_workflow
from MSOrganiser import concatenate_along_rows_workflow
from MSOrganiser import no_concatenate_workflow

WIDETABLEFORMDUPLICATECOLUMN_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                     "test_duplicate_input", "WideTableFormDuplicateColumns.csv")

WIDETABLEFORMDUPLICATECOLUMN1_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                      "test_duplicate_input", "WideTableFormDuplicateColumn1.csv")
WIDETABLEFORMDUPLICATECOLUMN2_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                      "test_duplicate_input", "WideTableFormDuplicateColumn2.csv")

WIDETABLEFORMDUPLICATEROW_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                     "test_duplicate_input", "WideTableFormDuplicateRows.csv")

WIDETABLEFORMDUPLICATEROW1_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                      "test_duplicate_input", "WideTableFormDuplicateRow1.csv")
WIDETABLEFORMDUPLICATEROW2_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                      "test_duplicate_input", "WideTableFormDuplicateRow2.csv")

class Duplicate_Input_Test(unittest.TestCase):
    # See https://realpython.com/lessons/mocking-print-unit-tests/
    # for more details on mock
    def setUp(self):
        # Replace the print function in MSOrganiser.py file to a mock
        self.patcher = patch('MSDuplicateCheck.print')
    def test_function_duplicate_column(self):
        """Check if the software is able to find duplicate columns (transition name) after reading a raw
           data file.

        * Construct the output data frame after reading the raw data
        * Able to detect that the duplicated columns are LPC 18:0 and MHC d18:1/16:0d3 (IS)
        """
        output_option = 'Area'
        duplicated_column_name_list = ['LPC 18:0', 'MHC d18:1/16:0d3 (IS)']
        duplicated_column_name_string = ", ".join(duplicated_column_name_list)

        # Creating the output data frame
        Sample_df = pd.DataFrame(['Sample1', 'Sample2', 'Sample3'], columns = ['Sample_Name'])

        index = ['LPC 18:0', 'LPC 17:0 (IS)', 'LPC 20:0 (IS)',
                 'LPC 18:0', 'MHC d18:1/16:0d3 (IS)', 'MHC d18:1/24:1',
                 'MHC d18:1/16:0d3 (IS)', 'MHC d18:1/24:0']

        Area_df = pd.DataFrame(np.random.randn(3, 8), columns=index)

        Area_df = pd.concat([Sample_df, Area_df], axis=1)

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            check_duplicated_columns_in_wide_data(input_wide_data = Area_df, 
                                                  output_option = output_option,
                                                  logger = None, ingui = True,
                                                  allow_multiple_istd = False)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to the duplicated columns
        # and not something else
        mock_print.assert_called_with('In the ' + output_option + ' data frame, ' + 
                                      'there are column names (Transition_Name) in the output files that are duplicated. ' +
                                      'The data in these duplicated column names may be different. ' +
                                      'Please check the input files especially if you are concatenating by columns. ' + 
                                      'Duplicated columns are ' + duplicated_column_name_string,
                                      flush = True)

        # Showing what is in mock
        #sys.stdout.write(str( mock_print.call_args ) + '\n')
        #sys.stdout.write(str( mock_print.call_args_list ) + '\n')

        mock_print = self.patcher.stop()

    def test_function_duplicate_row(self):
        """Check if the software is able to find duplicate rows (sample name) after reading a raw
           data file.

        * Construct the output data frame after reading the raw data
        * Able to detect that the duplicated rows are 10_TQC_06 and 47_PQC_16
        """
        output_option = 'Area'
        duplicated_sample_name_list = ['10_TQC_06', '47_PQC_16']
        duplicated_sample_name_string = ", ".join(duplicated_sample_name_list)

        # Creating the output data frame
        sample_names = ['10_TQC_06', '47_PQC_16', 'Sample1', 'Sample2', 
                        '10_TQC_06', 'Sample3', '47_PQC_16', 'Sample4']
        Sample_df = pd.DataFrame(sample_names, columns = ['Sample_Name'])

        index = ['LPC 18:0', 'LPC 17:0 (IS)', 'LPC 20:0 (IS)',
                 'LPC 18:0', 'MHC d18:1/16:0d3 (IS)', 'MHC d18:1/24:1',
                 'MHC d18:1/16:0d3 (IS)', 'MHC d18:1/24:0']

        Area_df = pd.DataFrame(np.random.randn(8, 8), columns=index)
        Area_df = pd.concat([Sample_df, Area_df], axis=1)

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            check_duplicated_sample_names_in_wide_data(input_wide_data = Area_df, 
                                                       output_option = output_option,
                                                       logger = None, ingui = True,
                                                       allow_multiple_istd = False)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to the duplicated rows
        # and not something else
        mock_print.assert_called_with('In the ' + output_option + ' data frame, ' + 
                                      'there are sample names in the output files that are duplicated. ' +
                                      'The data in these duplicated row names may be different. ' +
                                      'Please check the input files especially if you are concatenating by rows. ' , 
                                      'Duplicated sample names are ' + duplicated_sample_name_string, 
                                      flush = True)

        mock_print = self.patcher.stop()

    def test_function_duplicate_column_multipleISTD(self):
        """Check if the software is able to find duplicate columns (transition name) after reading a raw
           data file in multiple ISTD mode.

        * Construct the output data frame after reading the raw data in multiple ISTD mode
        * Able to detect that the duplicated columns are ('LPC 18:0', 'LPC 20:0 (IS)') 
          and ('LPC 20:0 (IS)', 'LPC 17:0 (IS)')
        """

        output_option = "Area"
        duplicated_column_name_list = [('LPC 18:0', 'LPC 20:0 (IS)'), ('LPC 20:0 (IS)', 'LPC 17:0 (IS)')]
        duplicated_column_name_string = ", ".join(map(str, duplicated_column_name_list))

        # Creating the output data frame
        tuples = [('Sample_Name', '')]
        index = pd.MultiIndex.from_tuples(tuples, names=['Transition_Name', 'Transition_Name_ISTD'])
        Sample_df = pd.DataFrame(['Sample1', 'Sample2', 'Sample3'], columns = index)

        tuples = [('LPC 18:0', 'LPC 17:0 (IS)'),
                  ('LPC 18:0', 'LPC 20:0 (IS)'),
                  ('LPC 18:1', 'LPC 17:0 (IS)'),
                  ('LPC 18:0', 'LPC 20:0 (IS)'),
                  ('LPC 17:0 (IS)', 'LPC 17:0 (IS)'),
                  ('LPC 17:0 (IS)', 'LPC 20:0 (IS)'),
                  ('LPC 20:0 (IS)', 'LPC 17:0 (IS)'),
                  ('LPC 20:0 (IS)', 'LPC 20:0 (IS)'),
                  ('LPC 20:0 (IS)', 'LPC 17:0 (IS)')
                  ]

        index = pd.MultiIndex.from_tuples(tuples, names=["Transition_Name", "Transition_Name_ISTD"])
        Area_df = pd.DataFrame(np.random.randn(3, 9), columns=index)

        Area_df = pd.concat([Sample_df, Area_df], axis=1)

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            check_duplicated_columns_in_wide_data(input_wide_data = Area_df, 
                                                  output_option = output_option,
                                                  logger = None, ingui = True,
                                                  allow_multiple_istd = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to the duplicated columns
        # and not something else
        mock_print.assert_called_with('In the ' + output_option + ' data frame, ' + 
                                      'there are column names (Transition_Name) in the output files that are duplicated. ' +
                                      'The data in these duplicated column names may be different. ' +
                                      'Please check the input files especially if you are concatenating by columns. ' + 
                                      'Duplicated columns are ' + duplicated_column_name_string,
                                      flush = True)

        mock_print = self.patcher.stop()

    def test_function_duplicate_row_multipleISTD(self):
        """Check if the software is able to find duplicate rows (sample name) after reading a raw
           data file in multiple ISTD mode.

        * Construct the output data frame after reading the raw data in multiple ISTD mode
        * Able to detect that the duplicated rows are 10_TQC_06 and 47_PQC_16
        """

        output_option = 'Area'
        duplicated_sample_name_list = ['10_TQC_06', '47_PQC_16']
        duplicated_sample_name_string = ", ".join(duplicated_sample_name_list)

        # Creating the output data frame
        tuples = [('Sample_Name', '')]
        index = pd.MultiIndex.from_tuples(tuples, names=['Transition_Name', 'Transition_Name_ISTD'])
        sample_names = ['10_TQC_06', '47_PQC_16', 'Sample1', 'Sample2', 
                        '10_TQC_06', 'Sample3', '47_PQC_16', 'Sample4']
        Sample_df = pd.DataFrame(sample_names, columns = index)

        tuples = [('LPC 18:0', 'LPC 17:0 (IS)'),
                  ('LPC 18:0', 'LPC 20:0 (IS)'),
                  ('LPC 18:1', 'LPC 17:0 (IS)'),
                  ('LPC 17:0 (IS)', 'LPC 17:0 (IS)'),
                  ('LPC 17:0 (IS)', 'LPC 20:0 (IS)'),
                  ('LPC 20:0 (IS)', 'LPC 17:0 (IS)'),
                  ('LPC 20:0 (IS)', 'LPC 20:0 (IS)')
                  ]

        index = pd.MultiIndex.from_tuples(tuples, names=["Transition_Name", "Transition_Name_ISTD"])
        Area_df = pd.DataFrame(np.random.randn(8, 7), columns=index)

        Area_df = pd.concat([Sample_df, Area_df], axis=1)

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            check_duplicated_sample_names_in_wide_data(input_wide_data = Area_df, 
                                                       output_option = output_option,
                                                       logger = None, ingui = True,
                                                       allow_multiple_istd = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to the duplicated rows
        # and not something else
        mock_print.assert_called_with('In the ' + output_option + ' data frame, ' + 
                                      'there are sample names in the output files that are duplicated. ' +
                                      'The data in these duplicated row names may be different. ' +
                                      'Please check the input files especially if you are concatenating by rows. ' , 
                                      'Duplicated sample names are ' + duplicated_sample_name_string, 
                                      flush = True)

        mock_print = self.patcher.stop()

    def test_workflow_no_concatenate_duplicate_column(self):
        """Check if the software is able to find duplicate columns (transition name) after reading 
           one raw data files. 

        * Extract the Area
        * Find duplicate columns

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMDUPLICATECOLUMN_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area'], 
            'Annot_File': "", 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False,
            'Long_Table_Annot': False, 
            'Testing': False
        }

        output_option = 'Area'
        duplicated_column_name_list = ['LPC 18:0', 'MHC d18:1/16:0d3 (IS)']
        duplicated_column_name_string = ", ".join(duplicated_column_name_list)

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to the duplicated columns
        # and not something else
        mock_print.assert_called_with('In the ' + output_option + ' data frame, ' + 
                                      'there are column names (Transition_Name) in the output files that are duplicated. ' +
                                      'The data in these duplicated column names may be different. ' +
                                      'Please check the input files especially if you are concatenating by columns. ' + 
                                      'Duplicated columns are ' + duplicated_column_name_string,
                                      flush = True)

        mock_print = self.patcher.stop()

    def test_workflow_no_concatenate_duplicate_row(self):
        """Check if the software is able to find duplicate rows (sample name) after reading 
           one raw data files. 

        * Extract the Area
        * Find duplicate rows

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMDUPLICATEROW_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area'], 
            'Annot_File': "", 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False,
            'Long_Table_Annot': False, 
            'Testing': False
        }

        output_option = 'Area'
        duplicated_sample_name_list = ['10_TQC_06', '47_PQC_16']
        duplicated_sample_name_string = ", ".join(duplicated_sample_name_list)

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to the duplicated rows
        # and not something else
        mock_print.assert_called_with('In the ' + output_option + ' data frame, ' + 
                                      'there are sample names in the output files that are duplicated. ' +
                                      'The data in these duplicated row names may be different. ' +
                                      'Please check the input files especially if you are concatenating by rows. ' , 
                                      'Duplicated sample names are ' + duplicated_sample_name_string, 
                                      flush = True)

        mock_print = self.patcher.stop()

    def test_workflow_column_concatenate_duplicate_column(self):
        """Check if the software is able to find duplicate columns (transition name) after reading 
           two raw data files and concatenating by columns. 
           
           Duplicate columns only occur after concatenation as it file actually have unique columns
           individually

        * Extract the Area
        * Concatenate the Area by column
        * Find duplicate columns

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMDUPLICATECOLUMN1_FILENAME, 
                         WIDETABLEFORMDUPLICATECOLUMN2_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area'], 
            'Annot_File': "", 
            'Output_Format': 'Excel', 
            'Concatenate': 'Concatenate along Transition Name (columns)', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        duplicated_column_name_list = ['LPC 18:0', 'MHC d18:1/24:1']
        duplicated_column_name_string = ", ".join(duplicated_column_name_list)
        output_option = 'column concatenated Area'

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = concatenate_along_columns_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to the duplicated columns
        # and not something else
        mock_print.assert_called_with('In the ' + output_option + ' data frame, ' + 
                                      'there are column names (Transition_Name) in the output files that are duplicated. ' +
                                      'The data in these duplicated column names may be different. ' +
                                      'Please check the input files especially if you are concatenating by columns. ' + 
                                      'Duplicated columns are ' + duplicated_column_name_string,
                                      flush = True)

        mock_print = self.patcher.stop()

    def test_workflow_row_concatenate_duplicate_row(self):
        """Check if the software is able to find duplicate rows (sample names) after reading 
           two raw data files and concatenating by rows. 
           
           Duplicate rows only occur after concatenation as it file actually have unique columns
           individually

        * Extract the Area
        * Concatenate the Area by row
        * Find duplicate rows

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMDUPLICATEROW1_FILENAME, 
                         WIDETABLEFORMDUPLICATEROW2_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area'], 
            'Annot_File': "", 
            'Output_Format': 'Excel', 
            'Concatenate': 'Concatenate along Sample Name (rows)', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        output_option = 'row concatenated Area'
        duplicated_sample_name_list = ['3_30m', '1_untreated']
        duplicated_sample_name_string = ", ".join(duplicated_sample_name_list)

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = concatenate_along_rows_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to the duplicated rows
        # and not something else
        mock_print.assert_called_with('In the ' + output_option + ' data frame, ' + 
                                      'there are sample names in the output files that are duplicated. ' +
                                      'The data in these duplicated row names may be different. ' +
                                      'Please check the input files especially if you are concatenating by rows. ' , 
                                      'Duplicated sample names are ' +  duplicated_sample_name_string, 
                                      flush = True)

        mock_print = self.patcher.stop()

    def tearDown(self):
        self.patcher.stop()

if __name__ == '__main__':
    unittest.main()