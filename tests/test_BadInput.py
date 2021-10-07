import unittest
import os
from unittest.mock import patch
import MSParser
from MSOrganiser import no_concatenate_workflow

NO_MS_FILE_JSONFILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                       "test_bad_input", 'No_MS_File.json')

NO_OUTPUT_DIRECTORY_JSONFILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                "test_bad_input", 'No_Output_Directory.json')

NO_OUTPUT_OPTIONS_JSONFILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                              "test_bad_input", 'No_Output_Options.json')

NO_ANNOT_FILE_JSONFILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                          "test_bad_input", 'No_Annot_File.json')

INPUT_FOLDERNAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                          "test_bad_input", 'input_folder.csv')

TEST_JSONFILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                 "test_bad_input", 'No_Output_Options.json')


class Parsing_Issue_Test(unittest.TestCase):
    # See https://realpython.com/lessons/mocking-print-unit-tests/
    # for more details on mock
    def test_invalid_json_file(self):
        """Check if the software is able to detect invalid json file

        """

        # Replace the print function in MSParser.py file to a mock
        self.patcher = patch('MSParser.print')
        mock_print = self.patcher.start()

        #Read the parser
        with self.assertRaises(SystemExit) as cm:
            stored_args = MSParser.parse_MSOrganiser_args(args_json_file_path = NO_MS_FILE_JSONFILENAME,
                                                          testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to no MS file input
        mock_print.assert_called_with('Please key in at least one input MS file',
                                      flush = True)

        #Read the parser
        with self.assertRaises(SystemExit) as cm:
            stored_args = MSParser.parse_MSOrganiser_args(args_json_file_path = NO_OUTPUT_DIRECTORY_JSONFILENAME,
                                                          testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to no output directory input
        mock_print.assert_called_with('Please key in at least one output directory',
                                      flush = True)


        #Read the parser
        with self.assertRaises(SystemExit) as cm:
            stored_args = MSParser.parse_MSOrganiser_args(args_json_file_path = NO_OUTPUT_OPTIONS_JSONFILENAME,
                                                          testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to no output option input
        mock_print.assert_called_with('Please key in at least one result to output',
                                      flush = True)

        #Read the parser
        with self.assertRaises(SystemExit) as cm:
            stored_args = MSParser.parse_MSOrganiser_args(args_json_file_path = NO_ANNOT_FILE_JSONFILENAME,
                                                          testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to no annotation file input when
        # normArea by ISTD or normConc by ISTD or both are selected 
        # in Output_Options
        mock_print.assert_called_with("Please key in an annotation file when \'normArea by ISTD\' " + 
                                      "or \'normConc by ISTD\' are selected in Output_Options",
                                      flush = True)

        self.patcher.stop()

    def test_wrong_file_extention(self):
        """Check if the software is able to detect wrong input file extention

        """

        # Replace the print function in MSAnalysis.py file to a mock
        self.patcher = patch('MSAnalysis.print')
        mock_print = self.patcher.start()

        stored_args = {
            'MS_Files': ["wrong_extention"], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': "", 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        mock_print = self.patcher.start()
        MS_FileType_list = ['Agilent Wide Table in csv', 
                            'Agilent Compound Table in csv',
                            'Multiquant Long Table in txt']
        MS_Files_list = ['no_csv_extention', 
                         'no_csv_extention',
                         'no_txt_extention']

        for i in range(len(MS_FileType_list)):

            stored_args['MS_FileType'] = MS_FileType_list[i]
            stored_args['MS_Files'] = [MS_Files_list[i]]
            right_extention = ""

            if MS_FileType_list[i] in ['Agilent Wide Table in csv', 'Agilent Compound Table in csv']:
                right_extention = ".csv"
            elif MS_FileType_list[i] in ['Multiquant Long Table in txt']:
                right_extention = ".txt"

            with self.assertRaises(SystemExit) as cm:
                [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

            # Ensure that the system ends with a -1 to indicate an error
            self.assertEqual(cm.exception.code, -1)

            # Ensure that the error was due to wrong file extention
            mock_print.assert_called_with('Input file path ' + 
                                          '\'' + MS_Files_list[i] + '\' ' + 
                                          'must have a '+ right_extention + ' ' + 
                                          'extention.',
                                           flush = True)

        self.patcher.stop()

    def test_input_file_is_a_folder(self):
        """Check if the software is able to detect a folder input when a system
           file input is expected

        """

        # Replace the print function in MSRawData.py file to a mock
        self.patcher = patch('MSRawData.print')
        mock_print = self.patcher.start()

        stored_args = {
            'MS_Files': [INPUT_FOLDERNAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': "", 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to wrong file extention
        mock_print.assert_called_with('Input file path ' + '\'' + INPUT_FOLDERNAME + '\'' +
                                      ' does not lead to a system file. ' + 
                                      'Please check if the input file path is a system file and not a folder.',
                                      flush = True)

        self.patcher.stop()

    def test_input_file_cannot_be_found(self):
        """Check if the software is able to detect if the input file exists.
           If not, gives an error and inform the user about this issue.

        """

        # Replace the print function in MSRawData.py file to a mock
        self.patcher = patch('MSRawData.print')
        mock_print = self.patcher.start()

        stored_args = {
            'MS_Files': ["non_existing_file.csv"], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': "", 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to wrong file extention
        mock_print.assert_called_with('Input file path ' + '\'non_existing_file.csv\'' +
                                      ' could not be found. ' +
                                      'Please check if the input file path.',
                                      flush = True)

        self.patcher.stop()

if __name__ == '__main__':
    unittest.main()
