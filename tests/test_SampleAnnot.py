import unittest
import os
from unittest.mock import patch
from MSCalculate import ISTD_Operations

INVALIDSHEETNAME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                        "testdata", "test_sample_annot", 
                                        "WideTableForm_Annotation_InvalidSheetName.xlsx")

RAWDATAFILENAME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                        "testdata", "test_sample_annot", 
                                        "WideTableForm_Annotation_RawDataFileName.xlsx")

class SampleAnnot_Test(unittest.TestCase):
    # See https://realpython.com/lessons/mocking-print-unit-tests/
    # for more details on mock
    def setUp(self):
        # Replace the print function in Annotation.py file to a mock
        self.patcher = patch('Annotation.print')
        self.valid_sheet_name = "Sample_Annot"

    def test_validation_InvalidSheetName(self):
        """Check if the software is able to check if the Sample Annotation file has
           the correct sheet name. 

        * Read the file
        * Highlight the sheet name should be "Sample_Annot", not something else.

        """

        MS_FilePathList = ["WideTableForm.csv"]

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            Sample_Annot_df = ISTD_Operations.read_Sample_Annot(filepath = INVALIDSHEETNAME_ANNOTATION,
                                                                MS_FilePathList = MS_FilePathList,
                                                                column_name = "Area",
                                                                logger = None,
                                                                ingui = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to an invalid Sample Name
        mock_print.assert_called_with('Sheet name ' + self.valid_sheet_name + ' does not exists.' + 
                                      ' Please check the input excel file', 
                                      flush = True)

        #print(Sample_Annot_df)
    def test_validation_RawDataFileName(self):
        """Check if the software is able to check if the Sample Annotation file has
           the Raw_Data_File_Name column and highlight to use a later version of the software. 

        * Read the file
        * Highlight the presence of Raw_Data_File_Name column and the need to use
          an updated version of the software

        """

        MS_FilePathList = ["WideTableForm.csv"]

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            Sample_Annot_df = ISTD_Operations.read_Sample_Annot(filepath = RAWDATAFILENAME_ANNOTATION,
                                                                MS_FilePathList = MS_FilePathList,
                                                                column_name = "Area",
                                                                logger = None,
                                                                ingui = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to an invalid Sample Name
        mock_print.assert_called_with('The ' + self.valid_sheet_name + 
                                      ' sheet contains the column "Raw_Data_File_Name". ' +
                                      'This column name is no longer accepted in MSOrganiser. ' + 
                                      'Please use a later version of MSTemplate_Creator (above 0.0.1) that ' +
                                      'uses "Data_File_Name" instead.',
                                      flush = True)

    def tearDown(self):
        self.patcher.stop()

if __name__ == '__main__':
    unittest.main()
