import unittest
import os
import pandas as pd
import openpyxl
from MSRawData import AgilentMSRawData
from MSRawData import SciexMSRawData
from MSDataOutput import MSDataOutput

WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm.csv')
WIDETABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_Results.xlsx')
WIDETABLEFORM_TRANSPOSE_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_TransposeResults.xlsx')

LARGE_WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'sPerfect_Index_AllLipids_raw.csv')
LARGE_WIDETABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'sPerfect_Index_AllLipids_raw_Results.xlsx')

COMPOUNDTABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'CompoundTableForm.csv')
COMPOUNDTABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'CompoundTableForm_Results.xlsx')

SCIEX_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'Mohammed_SciEx_data.txt')
SCIEX_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'Mohammed_SciEx_data_Results.xlsx')

class Agilent_Test(unittest.TestCase):

    def setUp(self):
        self.WideData = AgilentMSRawData(WIDETABLEFORM_FILENAME,ingui=True)
        self.LargeWideData = AgilentMSRawData(LARGE_WIDETABLEFORM_FILENAME,ingui=True)
        self.CompoundData = AgilentMSRawData(COMPOUNDTABLEFORM_FILENAME,ingui=True)
        self.SciexData = SciexMSRawData(SCIEX_FILENAME,ingui=True)

        self.WideDataResults = openpyxl.load_workbook(WIDETABLEFORM_RESULTS_FILENAME)
        self.WideDataTransposeResults = openpyxl.load_workbook(WIDETABLEFORM_TRANSPOSE_RESULTS_FILENAME)
        self.LargeWideDataResults = openpyxl.load_workbook(LARGE_WIDETABLEFORM_RESULTS_FILENAME)
        self.CompoundDataResults = openpyxl.load_workbook(COMPOUNDTABLEFORM_RESULTS_FILENAME)
        self.SciexDataResults = openpyxl.load_workbook(SCIEX_RESULTS_FILENAME)

    def test_DataForm(self):
        self.assertEqual("WideTableForm",self.WideData.DataForm)
        self.assertEqual("WideTableForm",self.LargeWideData.DataForm)
        self.assertEqual("CompoundTableForm",self.CompoundData.DataForm)

    def test_getAreaTable(self):
        pd.util.testing.assert_frame_equal(self.WideData.get_table("Area"),self.sheet_to_table(self.WideDataResults,"Area"))
        pd.util.testing.assert_frame_equal(MSDataOutput.transpose_MSdata(self.WideData.get_table("Area")),self.sheet_to_table(self.WideDataTransposeResults,"Area"))
        
        #Downcast both to the smallest numerical dtype possible
        right = self.sheet_to_table(self.LargeWideDataResults,"Area").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        Area_df = self.LargeWideData.get_table("Area").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(Area_df,right)

        #Downcast both to the smallest numerical dtype possible
        right = self.sheet_to_table(self.CompoundDataResults,"Area").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        Area_df = self.CompoundData.get_table("Area").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(Area_df,right)

        #Downcast both to the smallest numerical dtype possible
        right = self.sheet_to_table(self.SciexDataResults,"Area").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        Area_df = self.SciexData.get_table("Area").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(Area_df,right)

    def test_getRTTable(self):
        pd.util.testing.assert_frame_equal(self.WideData.get_table("RT"),self.sheet_to_table(self.WideDataResults,"RT"))
        pd.util.testing.assert_frame_equal(MSDataOutput.transpose_MSdata(self.WideData.get_table("RT")),self.sheet_to_table(self.WideDataTransposeResults,"RT"))

        #Downcast both to the smallest numerical dtype possible
        right = self.sheet_to_table(self.LargeWideDataResults,"RT").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        RT_df = self.LargeWideData.get_table("RT").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(RT_df,right)

        #Downcast both to the smallest numerical dtype possible
        right = self.sheet_to_table(self.CompoundDataResults,"RT").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        RT_df = self.CompoundData.get_table("RT").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(RT_df,right)

        #Downcast both to the smallest numerical dtype possible
        right = self.sheet_to_table(self.SciexDataResults,"RT").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        RT_df = self.SciexData.get_table("RT").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(RT_df,right)

    def test_getFWHMTable(self):
        pd.util.testing.assert_frame_equal(self.WideData.get_table("FWHM"),self.sheet_to_table(self.WideDataResults,"FWHM"))
        pd.util.testing.assert_frame_equal(MSDataOutput.transpose_MSdata(self.WideData.get_table("FWHM")),self.sheet_to_table(self.WideDataTransposeResults,"FWHM"))

        #Downcast both to the smallest numerical dtype possible
        right = self.sheet_to_table(self.LargeWideDataResults,"FWHM").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        FWHM_df = self.LargeWideData.get_table("FWHM").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(FWHM_df,right)

        #Downcast both to the smallest numerical dtype possible
        right = self.sheet_to_table(self.SciexDataResults,"FWHM").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        FWHM_df = self.SciexData.get_table("FWHM").apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(FWHM_df,right)

    def tearDown(self):
        self.WideDataResults.close()
        self.WideDataTransposeResults.close()
        self.LargeWideDataResults.close()
        self.CompoundDataResults.close()
        self.SciexDataResults.close()

    def sheet_to_table(self,workbook,sheet_name):
        ws = workbook[sheet_name]
        data = ws.values
        cols = next(data)
        data = list(data)
        return pd.DataFrame(data, columns=cols)

if __name__ == '__main__':
    unittest.main()
