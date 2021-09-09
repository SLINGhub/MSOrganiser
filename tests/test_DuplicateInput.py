import unittest
import os
import sys
from unittest.mock import patch
from MSOrganiser import check_duplicated_columns_in_wide_data
from MSRawData import AgilentMSRawData

WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__), 
                                      "testdata",
                                      "test_duplicate_input", 
                                      'WideTableFormDuplicateColumns.csv')

class Duplicate_Input_Test(unittest.TestCase):
    # See https://realpython.com/lessons/mocking-print-unit-tests/
    # for more details on mock
    def setUp(self):
        # Replace the print function in MSOrganiser.py file to a mock
        self.patcher = patch('MSOrganiser.print')
    def test_WideData_Duplicate_Column(self):
        """Check if the software is able to find duplicate columns (transition name) in one Agilent raw data
           in Wide Table Form.

        * Extract Area using AgilentMSRawData.get_table
        * Able to detect that the duplicated columns are LPC 18:0 and MHC d18:1/16:0d3 (IS)
        """
        output_option = "Area"
        AreaWideData = AgilentMSRawData(WIDETABLEFORM_FILENAME,ingui=True).get_table(output_option)
        duplicated_column_name_list = ["LPC 18:0", "MHC d18:1/16:0d3 (IS)"]
        duplicated_column_name_string = ", ".join(duplicated_column_name_list)

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            check_duplicated_columns_in_wide_data(input_wide_data = AreaWideData, 
                                                  output_option = output_option,
                                                  logger = None, ingui = True,
                                                  allow_multiple_istd = False,
                                                  testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to the duplicated columns
        # and not something else
        mock_print.assert_called_with('In the ' + output_option + ' data frame, ' + 
                                      'There are column names (Transition_Name) in the output files that are duplicated. ' +
                                      'The data in these duplicated column names may be different. ' +
                                      'Please check the input files especially if you are concatenating by columns.' + 
                                      'Duplicated columns are ' + duplicated_column_name_string,
                                      flush = True)

        # Showing what is in mock
        #sys.stdout.write(str( mock_print.call_args ) + '\n')
        #sys.stdout.write(str( mock_print.call_args_list ) + '\n')

        mock_print = self.patcher.stop()

    def tearDown(self):
        self.patcher.stop()

if __name__ == '__main__':
    unittest.main()