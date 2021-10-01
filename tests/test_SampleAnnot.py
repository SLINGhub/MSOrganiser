import unittest
import os
from unittest.mock import patch
from MSCalculate import ISTD_Operations
from MSAnalysis import MS_Analysis

INVALIDSHEETNAME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                           "testdata", "test_sample_annot", 
                                           "WideTableForm_Annotation_InvalidSheetName.xlsx")

RAWDATAFILENAME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                          "testdata", "test_sample_annot", 
                                          "WideTableForm_Annotation_RawDataFileName.xlsx")

NODATAFILENAME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                         "testdata", "test_sample_annot", 
                                         "WideTableForm_Annotation_NoDataFileName.xlsx")

NOSAMPLENAME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                       "testdata", "test_sample_annot", 
                                       "WideTableForm_Annotation_NoSampleName.xlsx")

NOSAMPLETYPE_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                       "testdata", "test_sample_annot", 
                                       "WideTableForm_Annotation_NoSampleType.xlsx")

NOSAMPLEAMOUNT_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                         "testdata", "test_sample_annot", 
                                         "WideTableForm_Annotation_NoSampleAmount.xlsx")

NOSAMPLEAMOUNTUNIT_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                             "testdata", "test_sample_annot", 
                                             "WideTableForm_Annotation_NoSampleAmountUnit.xlsx")

NOISTDVOLUME_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                       "testdata", "test_sample_annot", 
                                       "WideTableForm_Annotation_NoISTDVolume.xlsx")

NOCONCENTRATIONUNIT_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                              "testdata", "test_sample_annot", 
                                              "WideTableForm_Annotation_NoConcentrationUnit.xlsx")

MISSINGDATAFILENAMEENTRIES_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                                     "testdata", "test_sample_annot", 
                                                     "WideTableForm_MissingDataFileNameEntries.xlsx")

MISSINGSAMPLENAMEENTRIES_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                                   "testdata", "test_sample_annot", 
                                                   "WideTableForm_MissingSampleNameEntries.xlsx")

NOSAMPLEANNOTDATA_ANNOTATION = os.path.join(os.path.dirname(__file__),
                                            "testdata", "test_sample_annot", 
                                            "WideTableForm_NoSampleAnnotData.xlsx")

WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),
                                      "testdata", "test_sample_annot",
                                      'WideTableForm.csv')

WIDETABLEFORM_ANNOTATION_WITH_MISSING_SAMPLES = os.path.join(os.path.dirname(__file__),
                                                             "testdata", "test_sample_annot", 
                                                             "WideTableForm_Annotation_WithMissingSamples.xlsx")

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

        # Ensure that the error was due to an invalid Sheet Name
        mock_print.assert_called_with('Sheet name ' + self.valid_sheet_name + ' does not exists.' + 
                                      ' Please check the input excel file.', 
                                      flush = True)

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

        # Ensure that the error was due to the presence of Raw_Data_File_Name column
        mock_print.assert_called_with('The ' + self.valid_sheet_name + 
                                      ' sheet contains the column "Raw_Data_File_Name". ' +
                                      'This column name is no longer accepted in MSOrganiser. ' + 
                                      'Please use a later version of MSTemplate_Creator (above 0.0.1) that ' +
                                      'uses "Data_File_Name" instead.',
                                      flush = True)

    def test_validation_MissingColumnNames(self):
        """Check if the software is able to check if the Sample Annotation file has
           missing column which are actually required. 

        * Read the file
        * Highlight the presence of missing columns and the need to to have them

        """

        MS_FilePathList = ["WideTableForm.csv"]

        mock_print = self.patcher.start()

        missing_column_test_files = [NODATAFILENAME_ANNOTATION, NOSAMPLENAME_ANNOTATION,
                                     NOSAMPLETYPE_ANNOTATION, NOSAMPLEAMOUNT_ANNOTATION,
                                     NOSAMPLEAMOUNTUNIT_ANNOTATION, NOISTDVOLUME_ANNOTATION,
                                     NOCONCENTRATIONUNIT_ANNOTATION]
        missing_columns_list = ["Data_File_Name", "Sample_Name",
                                "Sample_Type", "Sample_Amount",
                                "Sample_Amount_Unit", "ISTD_Mixture_Volume_[uL]",
                                "Concentration_Unit"]

        for i in range(len(missing_column_test_files)):
            with self.assertRaises(SystemExit) as cm:
                Sample_Annot_df = ISTD_Operations.read_Sample_Annot(filepath = missing_column_test_files[i],
                                                                    MS_FilePathList = MS_FilePathList,
                                                                    column_name = "Area",
                                                                    logger = None,
                                                                    ingui = True)

            # Ensure that the system ends with a -1 to indicate an error
            self.assertEqual(cm.exception.code, -1)

            # Ensure that the error was due to missing columns
            mock_print.assert_called_with('The ' + self.valid_sheet_name  + 
                                          ' sheet is missing the column ' + missing_columns_list[i] + '.',
                                          flush=True)

    def test_validation_Missing_DataFile_Or_SampleName(self):
        """Check if the software is able to check if the Sample Annotation file has
           missing entries in the Data File Name or Sample Name column 

        * Read the file
        * Warn users that there are missing entries in the Data File Name or Sample Name column 

        """

        MS_FilePathList = ["WideTableForm.csv"]

        mock_print = self.patcher.start()

        Sample_Annot_df = ISTD_Operations.read_Sample_Annot(filepath = MISSINGDATAFILENAMEENTRIES_ANNOTATION,
                                                            MS_FilePathList = MS_FilePathList,
                                                            column_name = "Area",
                                                            logger = None,
                                                            ingui = True)

        # Ensure that the warning was due to missing entries in Data File Name column 
        mock_print.assert_called_with('There are sample names that are not associated ' + 
                                      'with a data file name at row(s) 7, 15. ' +
                                      'They will not be used during analysis. '
                                      'Ensure that both columns Data_File_Name and Sample_Name are filled for each sample.',
                                      flush = True)

        Sample_Annot_df = ISTD_Operations.read_Sample_Annot(filepath = MISSINGSAMPLENAMEENTRIES_ANNOTATION,
                                                            MS_FilePathList = MS_FilePathList,
                                                            column_name = "Area",
                                                            logger = None,
                                                            ingui = True)

        # Ensure that the warning was due to missing entries in Sample Name column 
        mock_print.assert_called_with('There are data file names that are not associated ' +
                                      'with a sample name at row(s) 6, 16, 22. ' +
                                      'They will not be used during analysis. ' +
                                      'Ensure that both columns Data_File_Name and Sample_Name are filled for each sample.',
                                      flush = True)

    def test_validation_MSFilePath_with_NoSampleAnnot(self):
        """Check if the software is able to check if a given MSFilePath has Sample Annotation data
           If not, it will throw an error and ask users not to input this MS raw file.

        * Read the file
        * Warn user if it finds a MSFilePath with no correspnding Sample Annotation data

        """
        MS_FilePathList = ["WideTableForm.csv", "WideTableForm1.csv", "WideTableForm2.csv"]

        mock_print = self.patcher.start()

        with self.assertRaises(SystemExit) as cm:
            Sample_Annot_df = ISTD_Operations.read_Sample_Annot(filepath = NOSAMPLEANNOTDATA_ANNOTATION,
                                                                MS_FilePathList = MS_FilePathList,
                                                                column_name = "Area",
                                                                logger = None,
                                                                ingui = True)

        # Ensure that the system ends with a -1 to indicate an error
        self.assertEqual(cm.exception.code, -1)

        # Ensure that the error was due to a MSFilePath with no correspnding Sample Annotation data
        mock_print.assert_called_with('The "Data_File_Name" column in the Sample Annotation sheet does not contain the input file name(s).\n' +
                                      'WideTableForm.csv\n' +
                                      'WideTableForm2.csv\n' +
                                      'Please correct the Sample Annotation sheet or the input file name.',
                                      flush = True)

    def test_warn_sample_in_MSFilePath_but_not_in_SampleAnnot(self):
        """Check if the software is able to list samples in a given MSFilePath that is not in the Sample Annotation data

        * Read the file
        * Warn user if it finds a sample in a given MSFilePath that is not in the Sample Annotation data

        """

        MyWideData = MS_Analysis(MS_FilePath = WIDETABLEFORM_FILENAME,
                                 MS_FileType = 'Agilent Wide Table in csv',
                                 Annotation_FilePath = WIDETABLEFORM_ANNOTATION_WITH_MISSING_SAMPLES,
                                 ingui = True)

        self.patcher = patch('MSCalculate.print')
        mock_print = self.patcher.start()

        [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df] = MyWideData.get_Analyte_Concentration(analysis_name = 'normConc by ISTD')

        # Ensure that the warning was due to a MSFilePath with no correspnding Sample Annotation data
        mock_print.assert_called_with('There are Sample Names in the input raw data set that is ' +
                                      'not in the Sample_Name column of the Sample Annotation sheet.\n' +
                                      '10_TQC_06\n' +
                                      '4_untreated\n' +
                                      'Check that these sample names are in the Sample_Annot sheet. ' +
                                      'Make sure the corresponding Data_File_Name is correct.',
                                      flush=True)


    def tearDown(self):
        self.patcher.stop()

if __name__ == '__main__':
    unittest.main()
