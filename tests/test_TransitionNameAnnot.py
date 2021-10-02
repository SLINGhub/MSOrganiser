import unittest
import os
from unittest.mock import patch
from Annotation import MS_Template
from MSCalculate import ISTD_Operations
from MSAnalysis import MS_Analysis

INVALIDSHEETNAME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                           "testdata", "test_transition_annot", 
                                           "WideTableForm_Annotation_InvalidSheetName.xlsx")

EMPTYDATA_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                    "testdata", "test_transition_annot", 
                                    "WideTableForm_Annotation_EmptyData.xlsx")

EMPTYTRANSITIONNAME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                              "testdata", "test_transition_annot", 
                                              "WideTableForm_Annotation_EmptyTransitionName.xlsx")

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

WIDETABLEFORM_ANNOTATION_WITH_ISTD_NOT_IN_ISTD_ANNOT = os.path.join(os.path.dirname(__file__),
                                                                    "testdata", "test_transition_annot", 
                                                                    "WideTableForm_Annotation_ISTD_not_in_ISTDAnnot.xlsx")

WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),
                                      "testdata", "test_transition_annot",
                                      "WideTableForm.csv")

BLANKTRANSITIONNAMEISTD_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                                  "testdata", "test_transition_annot", 
                                                  "WideTableForm_Annotation_BlankTransitionNameISTD.xlsx")

BLANKTRANSITIONNAMEISTD_MULTIPLEISTD_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                                               "testdata", "test_transition_annot", 
                                                               "WideTableForm_Annotation_BlankTransitionNameISTD_MultipleISTD.xlsx")

WIDETABLEFORM_ANNOTATION_WITH_TRANSITIONNAME_ONLY_IN_RAWDATA = os.path.join(os.path.dirname(__file__),
                                                                            "testdata", "test_transition_annot", 
                                                                            "WideTableForm_Annotation_TransitionName_only_in_InputData.xlsx")

WIDETABLEFORM_ANNOTATION_ISTD_NOT_IN_INPUTDATA = os.path.join(os.path.dirname(__file__),
                                                              "testdata", "test_transition_annot", 
                                                              "WideTableForm_Annotation_ISTD_not_in_InputData.xlsx")

WIDETABLEFORM_ANNOTATION_ISTD_NOT_IN_INPUTDATA_MULTIPLEISTD = os.path.join(os.path.dirname(__file__),
                                                                           "testdata", "test_transition_annot", 
                                                                           "WideTableForm_Annotation_ISTD_not_in_InputData_MultipleISTD.xlsx")

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
        * Highlight if there are no data in the sheet and only stop if normalisation is required

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

        # Ensure that error is given as doing_normalization is true
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

    def test_validation_EmptyTransitionName(self):
        """Check if the software is able to detect annotations with no transition names 

        * Read the file
        * Highlight if there are annotations with no transition names

        """
        MS_FilePathList = ["WideTableForm.csv"]

        mock_print = self.patcher.start()

        AnnotationList = MS_Template(filepath = EMPTYTRANSITIONNAME_ANNOTATION,
                                     column_name = "Area",
                                     logger = None,
                                     ingui = True,
                                     doing_normalization = False, 
                                     allow_multiple_istd = False)
        with self.assertRaises(SystemExit) as cm:
            Transition_Name_Annot_df = AnnotationList.Read_Transition_Name_Annot_Sheet()

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to Empty dataset when normalisation is required
        mock_print.assert_called_with('There are transition name annotations that are not ' +
                                      'associated with a transition name at row(s) 5, 7. ' +
                                      'Ensure that every annotation is associated with a Transition_Name.', 
                                      flush = True)

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
                                      'sheet has duplicates at row(s) 6, 10.', 
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
                                      'sheet has duplicates at row(s) 8, 13, 15.', 
                                      flush = True)

    def test_warn_ISTD_in_Transition_Name_Annot_but_not_in_ISTD_Annot(self):
        """Check if the software is able to warn if the ISTD in the 
           Transition_Name_Annot sheet is absent in the ISTD_Annot sheet 

        * Read the file
        * Warn if the ISTD in the Transition_Name_Annot sheet is absent in the ISTD_Annot sheet

        """

        MS_FilePathList = ["WideTableForm.csv"]
        missing_ISTD = ["LPC 17:0 (IS)", "MHC d18:1/16:0d3 (IS)"]

        self.patcher = patch('MSCalculate.print')
        mock_print = self.patcher.start()

        Transition_Name_Annot_df = ISTD_Operations.read_ISTD_map(filepath = WIDETABLEFORM_ANNOTATION_WITH_ISTD_NOT_IN_ISTD_ANNOT,
                                                                 column_name = "Area",
                                                                 logger = None, ingui = True,
                                                                 doing_normalization = False, 
                                                                 allow_multiple_istd = False)

        # Ensure that the warning was due to some Transition_Name_ISTD in Transition_Name_Annot not mentioned in ISTD_Annot
        mock_print.assert_called_with('There are Transition_Name_ISTD in Transition_Name_Annot not mentioned in ISTD_Annot.\n' + 
                                      "\n".join(missing_ISTD) + '\n' +
                                      'Check that these ISTD are in the ISTD_Annot sheet.',
                                      flush=True)

    def test_warn_BlankISTD(self):
        """Check if the software is able to warn if there are transition names with blank ISTD

        * Read the file
        * Warn if there are transition names with blank ISTD
        """
        MS_FilePathList = ["WideTableForm.csv"]

        self.patcher = patch('MSCalculate.print')
        mock_print = self.patcher.start()

        # No Multiple ISTD Annotation Case

        MyWideData = MS_Analysis(MS_FilePath = WIDETABLEFORM_FILENAME,
                                 MS_FileType = 'Agilent Wide Table in csv',
                                 Annotation_FilePath = BLANKTRANSITIONNAMEISTD_ANNOTATION,
                                 ingui = True)

        Area_df = MyWideData._get_Area_df_for_normalisation(using_multiple_input_files = False)

        
        Transition_Name_Annot_df = ISTD_Operations.read_ISTD_map(filepath = BLANKTRANSITIONNAMEISTD_ANNOTATION, 
                                                                 column_name = "Area",
                                                                 logger = None, ingui = True,
                                                                 doing_normalization = False, 
                                                                 allow_multiple_istd = False)

        [ISTD_report,Transition_Name_dict] = ISTD_Operations.create_Transition_Name_dict(Transition_Name_df = Area_df,
                                                                                         Transition_Name_Annot_df = Transition_Name_Annot_df,
                                                                                         logger = False, 
                                                                                         ingui = True,
                                                                                         allow_multiple_istd = False)

        # Ensure that the warning was due to some transition names not having a blank ISTD
        mock_print.assert_called_with('There are Transition_Names mentioned in the ' +
                                      'Transition_Name_Annot sheet but have a blank Transition_Name_ISTD.\n' +
                                      '\"LPC 18:0\"\n' + 
                                      '\"MHC d18:1/24:1\"', 
                                      flush = True)
        # Multiple ISTD Annotation Case

        MyWideData = MS_Analysis(MS_FilePath = WIDETABLEFORM_FILENAME,
                                 MS_FileType = 'Agilent Wide Table in csv',
                                 Annotation_FilePath = BLANKTRANSITIONNAMEISTD_MULTIPLEISTD_ANNOTATION ,
                                 ingui = True)

        Area_df = MyWideData._get_Area_df_for_normalisation(using_multiple_input_files = False)

        
        Transition_Name_Annot_df = ISTD_Operations.read_ISTD_map(filepath = BLANKTRANSITIONNAMEISTD_MULTIPLEISTD_ANNOTATION, 
                                                                 column_name = "Area",
                                                                 logger = None, ingui = True,
                                                                 doing_normalization = False, 
                                                                 allow_multiple_istd = True)

        [ISTD_report,Transition_Name_dict] = ISTD_Operations.create_Transition_Name_dict(Transition_Name_df = Area_df,
                                                                                         Transition_Name_Annot_df = Transition_Name_Annot_df,
                                                                                         logger = False, 
                                                                                         ingui = True,
                                                                                         allow_multiple_istd = True)

        # Ensure that the warning was due to some transition names not having a blank ISTD
        mock_print.assert_called_with('There are Transition_Names mentioned in the ' +
                                      'Transition_Name_Annot sheet but have a blank Transition_Name_ISTD.\n' +
                                      '\"LPC 18:0\"\n' + 
                                      '\"LPC 18:1\"\n' + 
                                      '\"MHC d18:1/24:1\"', 
                                      flush = True)

    def test_warn_TransitionName_in_Input_Data_but_not_in_Transition_Name_Annot(self):
        """Check if the software is able to warn if there are transition names in the 
           input data but not in the Transition_Name_Annot sheet

        * Read the file
        * Warn if there are transition names in the input data but not in the Transition_Name_Annot sheet
        """

        MS_FilePathList = ["WideTableForm.csv"]

        self.patcher = patch('MSCalculate.print')
        mock_print = self.patcher.start()

        # No Multiple ISTD Annotation Case

        MyWideData = MS_Analysis(MS_FilePath = WIDETABLEFORM_FILENAME,
                                 MS_FileType = 'Agilent Wide Table in csv',
                                 Annotation_FilePath = WIDETABLEFORM_ANNOTATION_WITH_TRANSITIONNAME_ONLY_IN_RAWDATA ,
                                 ingui = True)

        Area_df = MyWideData._get_Area_df_for_normalisation(using_multiple_input_files = False)

        
        Transition_Name_Annot_df = ISTD_Operations.read_ISTD_map(filepath = WIDETABLEFORM_ANNOTATION_WITH_TRANSITIONNAME_ONLY_IN_RAWDATA , 
                                                                 column_name = "Area",
                                                                 logger = None, ingui = True,
                                                                 doing_normalization = False, 
                                                                 allow_multiple_istd = False)

        [ISTD_report,Transition_Name_dict] = ISTD_Operations.create_Transition_Name_dict(Transition_Name_df = Area_df,
                                                                                         Transition_Name_Annot_df = Transition_Name_Annot_df,
                                                                                         logger = False, 
                                                                                         ingui = True,
                                                                                         allow_multiple_istd = False)

        # Ensure that the warning was due to some transition names not having a blank ISTD
        mock_print.assert_called_with('There are transitions in the input data set not mentioned ' + 
                                      'in the Transition_Name column of the Transition_Name_Annot sheet.\n' +
                                      '\"LPC 20:0 (IS)\"\n' + 
                                      '\"MHC d18:1/24:0\"', 
                                      flush = True)

    def test_warn_ISTD_in_Transition_Name_Annot_but_not_in_Input_Data(self):
        """Check if the software is able to warn if there are ISTD
           that is indicated in the Transition_Name_ISTD column
           but are not present in the input data

        * Read the file
        * Warn if there are ISTD that is indicated in the 
          Transition_Name_ISTD column but are not present in the input data
        """

        MS_FilePathList = ["WideTableForm.csv"]

        self.patcher = patch('MSCalculate.print')
        mock_print = self.patcher.start()

        MyWideData = MS_Analysis(MS_FilePath = WIDETABLEFORM_FILENAME,
                                 MS_FileType = 'Agilent Wide Table in csv',
                                 Annotation_FilePath = WIDETABLEFORM_ANNOTATION_ISTD_NOT_IN_INPUTDATA ,
                                 ingui = True)

        Area_df = MyWideData._get_Area_df_for_normalisation(using_multiple_input_files = False)

        
        Transition_Name_Annot_df = ISTD_Operations.read_ISTD_map(filepath = WIDETABLEFORM_ANNOTATION_ISTD_NOT_IN_INPUTDATA , 
                                                                 column_name = "Area",
                                                                 logger = None, ingui = True,
                                                                 doing_normalization = True, 
                                                                 allow_multiple_istd = False)

        [ISTD_report,Transition_Name_dict] = ISTD_Operations.create_Transition_Name_dict(Transition_Name_df = Area_df,
                                                                                         Transition_Name_Annot_df = Transition_Name_Annot_df,
                                                                                         logger = False, 
                                                                                         ingui = True,
                                                                                         allow_multiple_istd = False)

        # Ensure that the warning was due to ISTD mentioned in the Transition_Name_Annot sheet
        # but cannot be found in the input data set
        mock_print.assert_called_with('There are Transition_Names mentioned ' + 
                                      'in the Transition_Name_Annot sheet ' +
                                      'whose Transition_Names_ISTD does not exists ' +
                                      'in the input dataset.\n' +
                                      '\"LPC 18:0\"\n' + 
                                      '\"LPC 20:0 (IS)\"', 
                                      flush = True)

        #Perform normalisation using ISTD
        [norm_Area_df,ISTD_Area] = ISTD_Operations.normalise_by_ISTD(Area_df,Transition_Name_dict,
                                                                     logger = False,
                                                                     ingui = True,
                                                                     allow_multiple_istd = False)

        # Ensure that the warning was due to normalisation not done because 
        # the ISTD mentioned in the Transition_Name_Annot sheet
        # but cannot be found in the input data set
        mock_print.assert_called_with('LPC 17:1 (IS) cannot be found in the input data frame. ' + 
                                      'Ignore normalisation in this column LPC 20:0 (IS)',
                                      flush = True)

    def test_warn_ISTD_in_Transition_Name_Annot_but_not_in_Input_Data(self):
        """Check if the software is able to warn if there are ISTD
           that is indicated in the Transition_Name_ISTD column
           but are not present in the input data (Multiple ISTD case)

        * Read the file
        * Warn if there are ISTD that is indicated in the 
          Transition_Name_ISTD column but are not present in the input data
        """

        # Multiple ISTD case
        MS_FilePathList = ["WideTableForm.csv"]

        self.patcher = patch('MSCalculate.print')
        mock_print = self.patcher.start()

        MyWideData = MS_Analysis(MS_FilePath = WIDETABLEFORM_FILENAME,
                                 MS_FileType = 'Agilent Wide Table in csv',
                                 Annotation_FilePath = WIDETABLEFORM_ANNOTATION_ISTD_NOT_IN_INPUTDATA_MULTIPLEISTD ,
                                 ingui = True)

        Area_df = MyWideData._get_Area_df_for_normalisation(using_multiple_input_files = False)

        
        Transition_Name_Annot_df = ISTD_Operations.read_ISTD_map(filepath = WIDETABLEFORM_ANNOTATION_ISTD_NOT_IN_INPUTDATA_MULTIPLEISTD , 
                                                                 column_name = "Area",
                                                                 logger = None, ingui = True,
                                                                 doing_normalization = True, 
                                                                 allow_multiple_istd = True)

        [ISTD_report,Transition_Name_dict] = ISTD_Operations.create_Transition_Name_dict(Transition_Name_df = Area_df,
                                                                                         Transition_Name_Annot_df = Transition_Name_Annot_df,
                                                                                         logger = False, 
                                                                                         ingui = True,
                                                                                         allow_multiple_istd = True)
        # Ensure that the warning was due to 
        mock_print.assert_called_with('There are Transition_Names mentioned ' + 
                                      'in the Transition_Name_Annot sheet ' +
                                      'whose Transition_Names_ISTD does not exists ' +
                                      'in the input dataset.\n' +
                                      '\"LPC 18:0\"\n' + 
                                      '\"LPC 18:1\"', 
                                      flush = True)

        ##Update the Area_df so that it can be normalised by multiple ISTD
        Area_df = ISTD_Operations.expand_Transition_Name_df(Area_df,Transition_Name_dict,
                                                            logger = False, 
                                                            ingui = True)

        #Perform normalisation using ISTD
        [norm_Area_df,ISTD_Area] = ISTD_Operations.normalise_by_ISTD(Area_df,Transition_Name_dict,
                                                                     logger = False,
                                                                     ingui = True,
                                                                     allow_multiple_istd = True)

        mock_print.assert_called_with('LPC 17:1 (IS) cannot be found in the input data frame. ' + 
                                      'Ignore normalisation in this column (\'LPC 18:0\', \'LPC 17:1 (IS)\')',
                                      flush = True)



    def tearDown(self):
        self.patcher.stop()
if __name__ == '__main__':
    unittest.main()
