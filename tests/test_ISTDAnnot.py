import unittest
import os
from unittest.mock import patch
from Annotation import MS_Template
from MSCalculate import ISTD_Operations

INVALIDSHEETNAME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                           "testdata", "test_istd_annot", 
                                           "WideTableForm_Annotation_InvalidSheetName.xlsx")

NOTRANSITIONNAMEISTD_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                               "testdata", "test_istd_annot", 
                                               "WideTableForm_Annotation_NoTransitionNameISTD.xlsx")

NOISTDCONC_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                     "testdata", "test_istd_annot", 
                                     "WideTableForm_Annotation_NoISTDConc.xlsx")

NOCUSTOMUNIT_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                       "testdata", "test_istd_annot", 
                                       "WideTableForm_Annotation_NoCustomUnit.xlsx")

OLDCUSTOMUNITFORM1_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                             "testdata", "test_istd_annot", 
                                             "WideTableForm_Annotation_OldCustomUnitForm1.xlsx")

OLDCUSTOMUNITFORM2_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                             "testdata", "test_istd_annot", 
                                             "WideTableForm_Annotation_OldCustomUnitForm2.xlsx")

INVALIDCUSTOMUNIT_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                            "testdata", "test_istd_annot", 
                                            "WideTableForm_Annotation_InvalidCustomUnit.xlsx")

class ISTDAnnot_Test(unittest.TestCase):
    # See https://realpython.com/lessons/mocking-print-unit-tests/
    # for more details on mock
    def setUp(self):
        # Replace the print function in Annotation.py file to a mock
        self.patcher = patch('Annotation.print')
        self.valid_sheet_name = "ISTD_Annot"

    def test_validation_InvalidSheetName(self):
        """Check if the software is able to check if the Annotation file has
           the correct ISTD_Annot sheet name. 

        * Read the file
        * Highlight the sheet name should be "ISTD_Annot", not something else.

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
            ISTD_Annot_df = AnnotationList.Read_ISTD_Annot_Sheet()

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to an invalid Sheet Name
        mock_print.assert_called_with('Sheet name ' + self.valid_sheet_name + ' does not exists.' + 
                                      ' Please check the input excel file.', 
                                      flush = True)

    def test_validation_MissingColumnNames(self):
        """Check if the software is able to check if the ISTD Annotation file has
           missing column which are actually required. 

        * Read the file
        * Highlight the presence of missing columns and the need to to have them

        """

        MS_FilePathList = ["WideTableForm.csv"]

        mock_print = self.patcher.start()

        missing_column_test_files = [NOTRANSITIONNAMEISTD_ANNOTATION, NOISTDCONC_ANNOTATION,
                                     NOCUSTOMUNIT_ANNOTATION]
        missing_columns_list = ["Transition_Name_ISTD", "ISTD_Conc_[nM]", "Custom_Unit"]
        missing_columns_position = ["A2", "E3", "F2"]

        for i in range(len(missing_column_test_files)):
            AnnotationList = MS_Template(filepath = missing_column_test_files[i],
                                         column_name = "Area",
                                         logger = None,
                                         ingui = True,
                                         doing_normalization = False, 
                                         allow_multiple_istd = False)

            with self.assertRaises(SystemExit) as cm:
                ISTD_Annot_df = AnnotationList.Read_ISTD_Annot_Sheet()

            # Ensure that the system ends with a -1 to indicate an error
            self.assertEqual(cm.exception.code, -1)

            # Ensure that the error was due to missing columns
            mock_print.assert_called_with('Sheet ' + self.valid_sheet_name  + 
                                          ' is missing the column ' + missing_columns_list[i] + 
                                          ' at position ' + missing_columns_position[i] + '.',
                                          flush=True)

    def test_validation_CustomUnit(self):
        """Check if the software is able to check if ISTD Annotation file's
           Custom_Unit column details is correct. "[?M] or [?mol/uL]" is valid
           If the value is in the form "[?M]" or "[?M] or [?mol/mL]", 
           highlight to use a later version of the software.
           If the value is in other forms, highlight that it is invalid.

        * Read the file
        * If the value is in the form "[?M]" or "[?M] or [?mol/mL]", 
          highlight to use a later version of the software.
        * If the value is in other forms, highlight that it is invalid.

        """
        MS_FilePathList = ["WideTableForm.csv"]

        mock_print = self.patcher.start()

        old_column_units_files = [OLDCUSTOMUNITFORM1_ANNOTATION, OLDCUSTOMUNITFORM2_ANNOTATION]
        old_column_units_list = ["[uM]", "[uM] or [nmol/mL]"]

        for i in range(len(old_column_units_files)):
            AnnotationList = MS_Template(filepath = old_column_units_files[i],
                                         column_name = "Area",
                                         logger = None,
                                         ingui = True,
                                         doing_normalization = False, 
                                         allow_multiple_istd = False)

            with self.assertRaises(SystemExit) as cm:
                ISTD_Annot_df = AnnotationList.Read_ISTD_Annot_Sheet()

            # Ensure that the system ends with a -1 to indicate an error
            self.assertEqual(cm.exception.code, -1)

            # Ensure that the error was due to missing columns
            mock_print.assert_called_with('Sheet ISTD_Annot\'s column Custom_Unit option ' +
                                          old_column_units_list[i] + ' ' +
                                          'is no longer accepted in MSOrganiser. ' +
                                          'Please use a later version of MSTemplate_Creator (above 1.0.3).',
                                          flush=True)

        AnnotationList = MS_Template(filepath = INVALIDCUSTOMUNIT_ANNOTATION,
                                     column_name = "Area",
                                     logger = None,
                                     ingui = True,
                                     doing_normalization = False, 
                                     allow_multiple_istd = False)

        with self.assertRaises(SystemExit) as cm:
            ISTD_Annot_df = AnnotationList.Read_ISTD_Annot_Sheet()

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to missing columns
        mock_print.assert_called_with('Sheet ISTD_Annot\'s column Custom_Unit option ' +
                                      '[uM] or [umol/L] is invalid.', 
                                      flush=True)

if __name__ == '__main__':
    unittest.main()
