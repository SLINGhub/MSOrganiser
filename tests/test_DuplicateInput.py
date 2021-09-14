import unittest
import os
import sys
import pandas as pd
import numpy as np
from unittest.mock import patch
from DuplicateCheck import check_duplicated_columns_in_wide_data
from DuplicateCheck import check_duplicated_sample_names_in_wide_data
from MSAnalysis import MS_Analysis

class Duplicate_Input_Test(unittest.TestCase):
    # See https://realpython.com/lessons/mocking-print-unit-tests/
    # for more details on mock
    def setUp(self):
        # Replace the print function in MSOrganiser.py file to a mock
        self.patcher = patch('DuplicateCheck.print')
    def test_Duplicate_Column(self):
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
                                      'There are column names (Transition_Name) in the output files that are duplicated. ' +
                                      'The data in these duplicated column names may be different. ' +
                                      'Please check the input files especially if you are concatenating by columns. ' + 
                                      'Duplicated columns are ' + duplicated_column_name_string,
                                      flush = True)

        # Showing what is in mock
        #sys.stdout.write(str( mock_print.call_args ) + '\n')
        #sys.stdout.write(str( mock_print.call_args_list ) + '\n')

        mock_print = self.patcher.stop()

    def test_Duplicate_Row(self):
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

        # Ensure that the error was due to the duplicated columns
        # and not something else
        mock_print.assert_called_with('In the ' + output_option + ' data frame, ' + 
                                      'There are sample names in the output files that are duplicated. ' +
                                      'The data in these duplicated column names may be different. ' +
                                      'Please check the input files especially if you are concatenating by rows. ' , 
                                      'Duplicated sample names are ' + duplicated_sample_name_string, 
                                      flush = True)

        mock_print = self.patcher.stop()

    def test_Duplicate_Column_MultipleISTD(self):
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
                                      'There are column names (Transition_Name) in the output files that are duplicated. ' +
                                      'The data in these duplicated column names may be different. ' +
                                      'Please check the input files especially if you are concatenating by columns. ' + 
                                      'Duplicated columns are ' + duplicated_column_name_string,
                                      flush = True)

        mock_print = self.patcher.stop()

    def test_Duplicate_Row_MultipleISTD(self):
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

        # Ensure that the error was due to the duplicated columns
        # and not something else
        mock_print.assert_called_with('In the ' + output_option + ' data frame, ' + 
                                      'There are sample names in the output files that are duplicated. ' +
                                      'The data in these duplicated column names may be different. ' +
                                      'Please check the input files especially if you are concatenating by rows. ' , 
                                      'Duplicated sample names are ' + duplicated_sample_name_string, 
                                      flush = True)

        mock_print = self.patcher.stop()

    def tearDown(self):
        self.patcher.stop()

if __name__ == '__main__':
    unittest.main()