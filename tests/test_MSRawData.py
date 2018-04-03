import unittest
import os
import pandas as pd
import openpyxl
from MSRawData import AgilentMSRawData
from MSDataOutput import MSDataOutput

WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm.csv')
WIDETABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_Results.xlsx')
WIDETABLEFORM_TRANSPOSE_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_TransposeResults.xlsx')
COMPOUNDTABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'CompoundTableForm.csv')

class Agilent_Test(unittest.TestCase):

    def setUp(self):
        self.WideData = AgilentMSRawData(WIDETABLEFORM_FILENAME,ingui=True)
        self.CompoundData = AgilentMSRawData(COMPOUNDTABLEFORM_FILENAME,ingui=True)

        self.WideDataResults = openpyxl.load_workbook(WIDETABLEFORM_RESULTS_FILENAME)
        self.WideDataTransposeResults = openpyxl.load_workbook(WIDETABLEFORM_TRANSPOSE_RESULTS_FILENAME)

    def test_DataForm(self):
        self.assertEqual("WideTableForm",self.WideData.DataForm)
        self.assertEqual("CompoundTableForm",self.CompoundData.DataForm)

    def test_getAreaTable(self):
        pd.util.testing.assert_frame_equal(self.WideData.get_table("Area"),self.sheet_to_table(self.WideDataResults,"Area"))
        pd.util.testing.assert_frame_equal(MSDataOutput.transpose_MSdata(self.WideData.get_table("Area")),self.sheet_to_table(self.WideDataTransposeResults,"Area"))
        #pd.util.testing.assert_frame_equal(self.CompoundData.get_table("Area"),AreaTable)

    def test_getRTTable(self):
        pd.util.testing.assert_frame_equal(self.WideData.get_table("RT"),self.sheet_to_table(self.WideDataResults,"RT"))
        pd.util.testing.assert_frame_equal(MSDataOutput.transpose_MSdata(self.WideData.get_table("RT")),self.sheet_to_table(self.WideDataTransposeResults,"RT"))

    def test_getFWHMTable(self):
        pd.util.testing.assert_frame_equal(self.WideData.get_table("FWHM"),self.sheet_to_table(self.WideDataResults,"FWHM"))
        pd.util.testing.assert_frame_equal(MSDataOutput.transpose_MSdata(self.WideData.get_table("FWHM")),self.sheet_to_table(self.WideDataTransposeResults,"FWHM"))

    def tearDown(self):
        self.WideDataResults.close()

    def sheet_to_table(self,workbook,sheet_name):
        ws = workbook[sheet_name]
        data = ws.values
        cols = next(data)
        data = list(data)
        return pd.DataFrame(data, columns=cols)

if __name__ == '__main__':
    unittest.main()
