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
        self.compare_tables("Area",self.WideData,self.WideDataResults)
        self.compare_tables("Area",self.WideData,self.WideDataTransposeResults,transpose=True)
        self.compare_tables("Area",self.LargeWideData,self.LargeWideDataResults)
        self.compare_tables("Area",self.CompoundData,self.CompoundDataResults)
        self.compare_tables("Area",self.SciexData,self.SciexDataResults)

    def test_getRTTable(self):
        self.compare_tables("RT",self.WideData,self.WideDataResults)
        self.compare_tables("RT",self.WideData,self.WideDataTransposeResults,transpose=True)
        self.compare_tables("RT",self.LargeWideData,self.LargeWideDataResults)
        self.compare_tables("RT",self.CompoundData,self.CompoundDataResults)
        self.compare_tables("RT",self.SciexData,self.SciexDataResults)

    def test_getFWHMTable(self):
        self.compare_tables("FWHM",self.WideData,self.WideDataResults)
        self.compare_tables("FWHM",self.WideData,self.WideDataTransposeResults,transpose=True)
        self.compare_tables("FWHM",self.LargeWideData,self.LargeWideDataResults)
        self.compare_tables("FWHM",self.SciexData,self.SciexDataResults)

    def tearDown(self):
        self.WideDataResults.close()
        self.WideDataTransposeResults.close()
        self.LargeWideDataResults.close()
        self.CompoundDataResults.close()
        self.SciexDataResults.close()

    def compare_tables(self,table_name,MSDataObject,ExcelWorkbook,transpose=False):
        ExcelWorkbook = self.sheet_to_table(ExcelWorkbook,table_name).apply(pd.to_numeric, errors='ignore', downcast = 'float')
        if transpose:
            MSDataObject = MSDataOutput.transpose_MSdata(MSDataObject.get_table(table_name)).apply(pd.to_numeric, errors='ignore', downcast = 'float')
        else:
            MSDataObject = MSDataObject.get_table(table_name).apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(MSDataObject,ExcelWorkbook)

    def sheet_to_table(self,workbook,sheet_name):
        ws = workbook[sheet_name]
        data = ws.values
        cols = next(data)
        data = list(data)
        return pd.DataFrame(data, columns=cols)

if __name__ == '__main__':
    unittest.main()
