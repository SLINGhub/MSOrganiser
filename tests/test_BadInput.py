import unittest
import os
from unittest.mock import patch
import MSParser
from MSOrganiser import no_concatenate_workflow
from MSDataOutput import MSDataOutput_Excel
from MSDataOutput import MSDataOutput_csv

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

VALID_WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                            "test_bad_input", 'Valid_WideTableForm.csv')

VALID_COMPOUNDTABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                "test_bad_input", 'Valid_CompoundTableForm.csv')

NO_DATAFILENAME_WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                      "test_bad_input", 'NoDataFileColumn_WideTableForm.csv')

NO_DATAFILENAME_COMPOUNDTABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                          "test_bad_input", 'NoDataFileColumn_CompoundTableForm.csv')

NO_NAME_COMPOUNDTABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                  "test_bad_input", 'NoName_CompoundTableForm_Qualifier.csv')

INVALID_AGILENT_DATAFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                 "test_bad_input", 'Invalid_WideTableForm.csv')

INVALID_AGILENT_DATAFORM_FILENAME2 = os.path.join(os.path.dirname(__file__),"testdata", 
                                                  "test_bad_input", 'Invalid_WideTableForm2.csv')

EMPTY_WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                            "test_bad_input", 'Empty_WideTableForm.csv')

WRONG_EXTENTION_ANNOTATION_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                   "test_bad_input", 'Valid_WideTableForm_Annot.csv')

INPUT_ANNOTATION_FOLDERNAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                           "test_bad_input", 'input_annotation_folder')

class Bad_Input_Json_Test(unittest.TestCase):
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
        mock_print.assert_called_with('Please key in at least one input MS file.',
                                      flush = True)

        #Read the parser
        with self.assertRaises(SystemExit) as cm:
            stored_args = MSParser.parse_MSOrganiser_args(args_json_file_path = NO_OUTPUT_DIRECTORY_JSONFILENAME,
                                                          testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to no output directory input
        mock_print.assert_called_with('Please key in at least one output directory.',
                                      flush = True)


        #Read the parser
        with self.assertRaises(SystemExit) as cm:
            stored_args = MSParser.parse_MSOrganiser_args(args_json_file_path = NO_OUTPUT_OPTIONS_JSONFILENAME,
                                                          testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to no output option input
        mock_print.assert_called_with('Please key in at least one result to output.',
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
                                      "or \'normConc by ISTD\' are selected in Output_Options.",
                                      flush = True)

        self.patcher.stop()

class Bad_Input_File_Test(unittest.TestCase):
    # See https://realpython.com/lessons/mocking-print-unit-tests/
    # for more details on mock
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

        # Ensure that the error was due to input of a folder instead of a file
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

        # Ensure that the error was due to input of a csv file that does not exists
        mock_print.assert_called_with('Input file path ' + '\'non_existing_file.csv\'' +
                                      ' could not be found. ' +
                                      'Please check if the input file path.',
                                      flush = True)

        self.patcher.stop()

    def test_input_file_empty(self):
        """Check if the software is able to detect if the Agilent input file in
           Wide Table Form is empty and gives an error
        """

        # Replace the print function in MSRawData.py file to a mock
        self.patcher = patch('MSRawData.print')
        mock_print = self.patcher.start()

        stored_args = {
            'MS_Files': [EMPTY_WIDETABLEFORM_FILENAME], 
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

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to empty input data
        mock_print.assert_called_with(EMPTY_WIDETABLEFORM_FILENAME +
                                      ' is an empty file. Please check the input file.',
                                      flush = True)

        self.patcher.stop()

    def test_input_invalid_output_option(self):
        """Check if the software is able to detect if the input output options are valid.
           If not, gives an error and inform the user about this issue.
        """

        # Replace the print function in MSRawData.py file to a mock
        self.patcher = patch('MSRawData.print')
        mock_print = self.patcher.start()

        stored_args = {
            'MS_Files': [VALID_WIDETABLEFORM_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Invalid Output Option', 'Area'], 
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

        # Ensure that the error was due to an invalid output option
        mock_print.assert_called_with('Output option Invalid Output Option ' + 
                                      'is not a valid column in MassHunter or not ' + 
                                      'available as a valid output for this program.',
                                      flush=True)


        stored_args = {
            'MS_Files': [VALID_COMPOUNDTABLEFORM_FILENAME], 
            'MS_FileType': 'Agilent Compound Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Invalid Output Option', 'Area'], 
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

        # Ensure that the error was due to an invalid output option
        mock_print.assert_called_with('Output option Invalid Output Option ' + 
                                      'is not a valid column in MassHunter or not ' + 
                                      'available as a valid output for this program.',
                                      flush=True)

        self.patcher.stop()

    def test_invalid_agilent_dataform(self):
        """Check if the software is able to detect if the Agilent input file is
           neither in Wide Table or Compound Table Form.
        """

        # Replace the print function in MSRawData.py file to a mock
        self.patcher = patch('MSRawData.print')
        mock_print = self.patcher.start()

        stored_args = {
            'MS_Files': [INVALID_AGILENT_DATAFORM_FILENAME], 
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

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to invalid Agilent input file 
        # which is neither in Wide Table or Compound Table Form.
        mock_print.assert_called_with(INVALID_AGILENT_DATAFORM_FILENAME + ' ' +
                                      'is missing \"Sample\" at first row and column in Wide Table form ' + 
                                      'or missing \"Compound Method\" at first row and column in Compound Table form. ' +
                                      'Please check the input file.',
                                      flush=True)

        #self.patcher.stop()

        stored_args = {
            'MS_Files': [INVALID_AGILENT_DATAFORM_FILENAME2], 
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

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to invalid Agilent input file 
        # which is neither in Wide Table or Compound Table Form.
        mock_print.assert_called_with(INVALID_AGILENT_DATAFORM_FILENAME2 + ' ' +
                                      'is missing \"Sample\" at first row and column in Wide Table form ' + 
                                      'or missing \"Compound Method\" at first row and column in Compound Table form. ' +
                                      'Please check the input file.',
                                      flush=True)

        self.patcher.stop()
    
    def test_input_agilent_file_no_data_file(self):
        """Check if the software is able to detect if the Agilent input file in
           Wide Table Form or Compound Table Form have a Data File column 
        """

        # Replace the print function in MSRawData.py file to a mock
        self.patcher = patch('MSRawData.print')
        mock_print = self.patcher.start()

        stored_args = {
            'MS_Files': [NO_DATAFILENAME_WIDETABLEFORM_FILENAME], 
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

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to no Data File column in the Agilent Wide Table Form in csv
        mock_print.assert_called_with('\'' + os.path.basename(NO_DATAFILENAME_WIDETABLEFORM_FILENAME) + '\' ' +
                                      'has no column containing \"Data File\". ' + 
                                      'Please check the input file.',
                                      flush = True)


        stored_args = {
            'MS_Files': [NO_DATAFILENAME_COMPOUNDTABLEFORM_FILENAME], 
            'MS_FileType': 'Agilent Compound Table in csv', 
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

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to no Data File column in the Agilent Compound Table Form in csv
        mock_print.assert_called_with('\'' + os.path.basename(NO_DATAFILENAME_COMPOUNDTABLEFORM_FILENAME) + '\' ' +
                                      'has no column containing \"Data File\". ' + 
                                      'Please check the input file.',
                                      flush = True)

        self.patcher.stop()

    def test_input_agilent_compound_table_file_no_name(self):
        """Check if the software is able to detect if the Agilent input file in
           Compound Table Form have a Name column 
        """
        stored_args = {
            'MS_Files': [NO_NAME_COMPOUNDTABLEFORM_FILENAME], 
            'MS_FileType': 'Agilent Compound Table in csv', 
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

        # Replace the print function in MSRawData.py file to a mock
        self.patcher = patch('MSRawData.print')
        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to no Name column
        # in Compound Method Table for
        # Agilent Compound Table Form in csv
        mock_print.assert_called_with('\'' + os.path.basename(NO_NAME_COMPOUNDTABLEFORM_FILENAME) + '\' ' +
                                      'has no column contaning \"Name\" in Compound Method Table. ' + 
                                      'Please check the input file.',
                                      flush = True)

        self.patcher.stop()

    def test_input_valid_output_option_agilent_no_data_excel(self):
        """Check if the software is able to detect if the input output option is valid
           but the output option is not found in the input file when creating an excel file
        """

        # Replace the print function in MSDataOutput.py file to a mock
        self.patcher = patch('MSDataOutput.print')
        mock_print = self.patcher.start()

        output_directory = os.path.join(os.path.dirname(__file__),"testdata", "test_bad_input")

        stored_args = {
            'MS_Files': [VALID_WIDETABLEFORM_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': output_directory, 
            'Output_Options': ['Area', 'S/N'], 
            'Annot_File': "", 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        #print(file_name)
        #print(file_data_list[0][0][1])
        #print(file_data_list[0][0][0])

        DfOutput = MSDataOutput_Excel(stored_args['Output_Directory'], VALID_WIDETABLEFORM_FILENAME, 
                                      result_name = "Results" ,
                                      logger = None, ingui = True)
        DfOutput.start_writer()
        DfOutput.df_to_file("Area",file_data_list[0][0][0],
                            transpose=stored_args['Transpose_Results'],
                            allow_multiple_istd = False)
        DfOutput.df_to_file("S/N",file_data_list[0][0][1],
                            transpose=stored_args['Transpose_Results'],
                            allow_multiple_istd = False)
        DfOutput.end_writer(testing = True)

        # Ensure that the warning was due to no data available for that output option
        mock_print.assert_called_with('S/N has no data. Please check the input file.',
                                      flush=True)

        self.patcher.stop()

    def test_input_valid_output_option_agilent_no_data_csv(self):
        """Check if the software is able to detect if the input output option is valid
           but the output option is not found in the input file when creating a csv file
        """

        # Replace the print function in MSDataOutput.py file to a mock
        self.patcher = patch('MSDataOutput.print')
        mock_print = self.patcher.start()

        output_directory = os.path.join(os.path.dirname(__file__),"testdata", "test_bad_input")

        stored_args = {
            'MS_Files': [VALID_WIDETABLEFORM_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': output_directory, 
            'Output_Options': ['S/N'], 
            'Annot_File': "", 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': True, 
            'Long_Table_Annot': False, 
            'Testing': False
            }
        [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)

        DfOutput = MSDataOutput_csv(stored_args['Output_Directory'], VALID_WIDETABLEFORM_FILENAME, 
                                    result_name = "" , logger = None, ingui = True)
        DfOutput.start_writer()
        DfOutput.df_to_file("S/N",file_data_list[0][0][0],
                            transpose=stored_args['Transpose_Results'],
                            allow_multiple_istd = False)
            
        # Ensure that the warning was due to no data available for that output option
        mock_print.assert_called_with('S/N has no data. Please check the input file.',
                                      flush=True)

        #self.patcher.stop()

        DfLongOutput = MSDataOutput_csv(stored_args['Output_Directory'], VALID_WIDETABLEFORM_FILENAME, 
                                        result_name = "" , logger = None, ingui=True)
        DfLongOutput.start_writer()
        DfLongOutput.df_to_file("Long_Table",file_data_list[0][0][1])

        # Ensure that the warning was due to no data available for that output option
        mock_print.assert_called_with('Long_Table has no data. Please check the input file.',
                                      flush=True)

        self.patcher.stop()

class Bad_Annotation_Test(unittest.TestCase):
    # See https://realpython.com/lessons/mocking-print-unit-tests/
    # for more details on mock

    def test_input_annotation_cannot_be_found(self):
        """Check if the software is able to detect if the input annotation file exists.
           If not, gives an error and inform the user about this issue.

        """

        # Replace the print function in Annotation.py file to a mock
        self.patcher = patch('Annotation.print')
        mock_print = self.patcher.start()

        output_directory = os.path.join(os.path.dirname(__file__),"testdata", "test_bad_input")

        stored_args = {
            'MS_Files': [VALID_WIDETABLEFORM_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': output_directory, 
            'Output_Options': ['Area', 'normArea by ISTD'], 
            'Annot_File': "non_existing_annot_file.xlsm", 
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

        # Ensure that the error was due to no Data File column in the Agilent Wide Table Form in csv
        mock_print.assert_called_with('Input annotation ' + '\'non_existing_annot_file.xlsm\'' +
                                      ' could not be found. ' +
                                      'Please check the input file path.',
                                      flush = True)

        self.patcher.stop()

    def test_input_annotation_wrong_file_extention(self):
        """Check if the software is able to detect if the input annotation file
           has the wrong file extension
        """

        # Replace the print function in Annotation.py file to a mock
        self.patcher = patch('Annotation.print')
        mock_print = self.patcher.start()

        output_directory = os.path.join(os.path.dirname(__file__),"testdata", "test_bad_input")

        stored_args = {
            'MS_Files': [VALID_WIDETABLEFORM_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': output_directory, 
            'Output_Options': ['Area', 'normArea by ISTD'], 
            'Annot_File': WRONG_EXTENTION_ANNOTATION_FILENAME, 
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

        # Ensure that the error was due to no Data File column in the Agilent Wide Table Form in csv
        mock_print.assert_called_with('This program no longer accepts csv file as input for the annotation file. Please use the excel template file given.',
                                      flush = True)

        self.patcher.stop()

    def test_input_annotation_is_a_folder(self):
        """Check if the software is able to detect a folder input when a system
           file input is expected

        """

        # Replace the print function in Annotation.py file to a mock
        self.patcher = patch('Annotation.print')
        mock_print = self.patcher.start()

        stored_args = {
            'MS_Files': [VALID_WIDETABLEFORM_FILENAME],
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': INPUT_ANNOTATION_FOLDERNAME, 
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

        # Ensure that the error was due to input of a folder instead of a file
        mock_print.assert_called_with('Input file path ' + '\'' + INPUT_ANNOTATION_FOLDERNAME + '\'' +
                                      ' does not lead to a system file. ' + 
                                      'Please check if the input file path is a system file and not a folder.',
                                      flush = True)

        self.patcher.stop()

if __name__ == '__main__':
    unittest.main()
