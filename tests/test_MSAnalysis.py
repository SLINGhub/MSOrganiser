import unittest
import os
import pandas as pd
import openpyxl
from MSRawData import AgilentMSRawData
from MSAnalysis import MS_Analysis

WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm.csv')
WIDETABLEFORM_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_Annotation.xlsm')
WIDETABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_Results.xlsx')

class Agilent_Test(unittest.TestCase):

    def setUp(self):
        self.MyData = MS_Analysis(WIDETABLEFORM_FILENAME)
        self.WideDataResults = openpyxl.load_workbook(WIDETABLEFORM_RESULTS_FILENAME)

    def test_getnormAreaTable(self):
        #Perform normalisation using ISTD
        [norm_Area_df,ISTD_Area,ISTD_map_df,ISTD_Report] = self.MyData.get_Normalised_Area('normArea by ISTD',WIDETABLEFORM_ANNOTATION)
        right = self.sheet_to_table(self.WideDataResults,'normArea by ISTD')
        #Downcast both to the smallest numerical dtype possible
        right = right.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        norm_Area_df = norm_Area_df.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(norm_Area_df,right)

        right = self.sheet_to_table(self.WideDataResults,'ISTD map')
        #Downcast both to the smallest numerical dtype possible
        right = right.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        ISTD_map_df = ISTD_map_df.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(ISTD_map_df,right)

    def test_getAnalyteConcTable(self):
        #Perform analyte concentration using ISTD
        [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df] = self.MyData.get_Analyte_Concentration('normConc by ISTD',WIDETABLEFORM_ANNOTATION)
        right = self.sheet_to_table(self.WideDataResults,'normConc by ISTD')
        #Downcast both to the smallest numerical dtype possible
        right = right.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        norm_Conc_df = norm_Conc_df.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(norm_Conc_df,right)

        right = self.sheet_to_table(self.WideDataResults,'Sample Annot')
        #Downcast both to the smallest numerical dtype possible
        right = right.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        Sample_Annot_df = Sample_Annot_df.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(Sample_Annot_df,right)


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
