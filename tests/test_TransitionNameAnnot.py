import unittest
import os
from unittest.mock import patch
from Annotation import MS_Template
from MSCalculate import ISTD_Operations

INVALIDSHEETNAME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                           "testdata", "test_transition_annot", 
                                           "WideTableForm_Annotation_InvalidSheetName.xlsx")

EMPTYDATA_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                    "testdata", "test_transition_annot", 
                                    "WideTableForm_Annotation_EmptyData.xlsx")

NOTRANSITIONNAME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                           "testdata", "test_transition_annot", 
                                           "WideTableForm_Annotation_NoTransitionName.xlsx")

NOTRANSITIONNAMEISTD_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                               "testdata", "test_transition_annot", 
                                               "WideTableForm_Annotation_NoTransitionNameISTD.xlsx")

DUPLICATEDATA_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                        "testdata", "test_transition_annot", 
                                        "WideTableForm_Annotation_DuplicateData.xlsx")

DUPLICATEDATA_MULTIPLEISTD_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                                     "testdata", "test_transition_annot", 
                                                     "WideTableForm_Annotation_DuplicateData_MultipleISTD.xlsx")

WIDETABLEFORM_ANNOTATION_WITH_MISSING_ISTD = os.path.join(os.path.dirname(__file__),
                                                          "testdata", "test_transition_annot", 
                                                          "WideTableForm_Annotation_WithMissingISTD.xlsx")

class TransitionNameAnnot_Test(unittest.TestCase):
    # See https://realpython.com/lessons/mocking-print-unit-tests/
    # for more details on mock
    def setUp(self):
        # Replace the print function in Annotation.py file to a mock
        self.patcher = patch('Annotation.print')
        self.valid_sheet_name = "Transition_Name_Annot"

    def test_validation_InvalidSheetName(self):
        """Check if the software is able to check if the Annotation file has
           the correct Transition_Name_Annot sheet name. 

        * Read the file
        * Highlight the sheet name should be "Transition_Name_Annot", not something else.

        """

        MS_FilePathList = ["WideTableForm.csv"]

        mock_print = self.patcher.start()

        AnnotationList = MS_Template(filepath = INVALIDSHEETNAME_ANNOTATION,
                                     column_name = "Area",
                                     logger = None,
                                     ingui = True,
                                     doing_normalization = False, 
                                     allow_multiple_istd = False)

        with self.assertRaises(SystemExit) as cm:
            Transition_Name_Annot_df = AnnotationList.Read_Transition_Name_Annot_Sheet()

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to an invalid Sheet Name
        mock_print.assert_called_with('Sheet name ' + self.valid_sheet_name + ' does not exists.' + 
                                      ' Please check the input excel file.', 
                                      flush = True)

    def test_validation_EmptyData(self):
        """Check if the software is able to check if the Transition Name Annotation file is empty
           and only stop the process if normalisation is required. 

        * Read the file
        * Highlight if the there are no data in the sheet and only stop if normalisation is required

        """
        MS_FilePathList = ["WideTableForm.csv"]

        mock_print = self.patcher.start()

        # Ensure that Transition_Name_Annot_df is empty but code runs 
        # as doing_normalization is false
        AnnotationList = MS_Template(filepath = EMPTYDATA_ANNOTATION,
                                     column_name = "Area",
                                     logger = None,
                                     ingui = True,
                                     doing_normalization = False, 
                                     allow_multiple_istd = False)

        Transition_Name_Annot_df = AnnotationList.Read_Transition_Name_Annot_Sheet()
        self.assertTrue(Transition_Name_Annot_df.empty)


        AnnotationList = MS_Template(filepath = EMPTYDATA_ANNOTATION,
                                     column_name = "Area",
                                     logger = None,
                                     ingui = True,
                                     doing_normalization = True, 
                                     allow_multiple_istd = False)
        with self.assertRaises(SystemExit) as cm:
            Transition_Name_Annot_df = AnnotationList.Read_Transition_Name_Annot_Sheet()

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to Empty dataset when normalisation is required
        mock_print.assert_called_with('The input ' + self.valid_sheet_name + ' sheet has no data.',
                                      flush=True)

    def test_validation_MissingColumnNames(self):
        """Check if the software is able to check if the Transition Name Annotation file has
           missing column which are actually required. 

        * Read the file
        * Highlight the presence of missing columns and the need to to have them

        """
        MS_FilePathList = ["WideTableForm.csv"]

        mock_print = self.patcher.start()

        missing_column_test_files = [NOTRANSITIONNAME_ANNOTATION,
                                     NOTRANSITIONNAMEISTD_ANNOTATION]
        missing_columns_list = ["Transition_Name", "Transition_Name_ISTD"]

        for i in range(len(missing_column_test_files)):
            AnnotationList = MS_Template(filepath = missing_column_test_files[i],
                                         column_name = "Area",
                                         logger = None,
                                         ingui = True,
                                         doing_normalization = False, 
                                         allow_multiple_istd = False)

            with self.assertRaises(SystemExit) as cm:
                Transition_Name_Annot_df = AnnotationList.Read_Transition_Name_Annot_Sheet()

            # Ensure that the system ends with a -1 to indicate an error
            self.assertEqual(cm.exception.code, -1)

            # Ensure that the error was due to missing columns
            mock_print.assert_called_with('The ' + self.valid_sheet_name  + 
                                          ' sheet is missing the column ' + missing_columns_list[i] + '.',
                                          flush=True)

    def test_validation_DuplicateData(self):
        """Check if the software is able to check if the Transition Name Annotation file has
           duplicate data. 

        * Read the file
        * Highlight the presence of duplicate Transition Name if multiple ISTD is not allowed
        * Highlight the presence of duplicate Transition Name and 
        * Transition Name ISTD if multiple ISTD is allowed

        """
        MS_FilePathList = ["WideTableForm.csv"]

        mock_print = self.patcher.start()

        AnnotationList = MS_Template(filepath = DUPLICATEDATA_ANNOTATION,
                                     column_name = "Area",
                                     logger = None,
                                     ingui = True,
                                     doing_normalization = False, 
                                     allow_multiple_istd = False)
        with self.assertRaises(SystemExit) as cm:
            Transition_Name_Annot_df = AnnotationList.Read_Transition_Name_Annot_Sheet()

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to duplicate Transition Name
        mock_print.assert_called_with('Data at Transition_Name column(s) in the ' +
                                      self.valid_sheet_name + ' ' +
                                      'sheet has duplicates at row 6, 10.', 
                                      flush = True)

        AnnotationList = MS_Template(filepath = DUPLICATEDATA_MULTIPLEISTD_ANNOTATION,
                                     column_name = "Area",
                                     logger = None,
                                     ingui = True,
                                     doing_normalization = False, 
                                     allow_multiple_istd = True)
        with self.assertRaises(SystemExit) as cm:
            Transition_Name_Annot_df = AnnotationList.Read_Transition_Name_Annot_Sheet()

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to duplicate Transition Name
        mock_print.assert_called_with('Data at Transition_Name, Transition_Name_ISTD column(s) in the ' +
                                      self.valid_sheet_name + ' ' +
                                      'sheet has duplicates at row 8, 13, 15.', 
                                      flush = True)

    def test_warn_ISTD_in_Transition_Name_Annot_but_not_in_ISTD_Annot(self):
        """Check if the software is able to check if the Transition Name Annotation file has
           duplicate data. 

        * Read the file
        * Highlight the presence of duplicate Transition Name if multiple ISTD is not allowed

        """

        MS_FilePathList = ["WideTableForm.csv"]
        missing_ISTD = ["LPC 17:0 (IS)", "MHC d18:1/16:0d3 (IS)"]

        self.patcher = patch('MSCalculate.print')
        mock_print = self.patcher.start()

        Transition_Name_Annot_df = ISTD_Operations.read_ISTD_map(filepath = WIDETABLEFORM_ANNOTATION_WITH_MISSING_ISTD,
                                                                 column_name = "Area",
                                                                 logger = None, ingui = True,
                                                                 doing_normalization = False, 
                                                                 allow_multiple_istd = False)

        # Ensure that the error was due to missing columns
        mock_print.assert_called_with('There are Transition_Name_ISTD in Transition_Name_Annot not mentioned in ISTD_Annot.\n' + 
                                      "\n".join(missing_ISTD) + '\n' +
                                      'Check that these ISTD are in the ISTD_Annot sheet.',
                                      flush=True)

if __name__ == '__main__':
    unittest.main()
