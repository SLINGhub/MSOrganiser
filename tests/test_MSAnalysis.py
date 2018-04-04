import unittest
import os
import pandas as pd
import openpyxl
from MSAnalysis import MS_Analysis

WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm.csv')
WIDETABLEFORM_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_Annotation.xlsm')
WIDETABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_Results.xlsx')

LARGE_WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'sPerfect_Index_AllLipids_raw.csv')
LARGE_WIDETABLEFORM_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 'sPerfect_Index_AllLipids_raw_Annotation.xlsm')
LARGE_WIDETABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'sPerfect_Index_AllLipids_raw_Results.xlsx')

COMPOUNDTABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'CompoundTableForm.csv')
COMPOUNDTABLEFORM_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 'CompoundTableForm_Annotation.xlsm')
COMPOUNDTABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'CompoundTableForm_Results.xlsx')

SCIEX_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'Mohammed_SciEx_data.txt')
SCIEX_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 'Mohammed_SciEx_data_Annotation.xlsm')
SCIEX_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'Mohammed_SciEx_data_Results.xlsx')

class Agilent_Test(unittest.TestCase):

    def setUp(self):
        MyWideData = MS_Analysis(WIDETABLEFORM_FILENAME,ingui=False)
        WideDataResults = openpyxl.load_workbook(WIDETABLEFORM_RESULTS_FILENAME)

        MyLargeWideData = MS_Analysis(LARGE_WIDETABLEFORM_FILENAME,ingui=False)
        LargeWideDataResults = openpyxl.load_workbook(LARGE_WIDETABLEFORM_RESULTS_FILENAME)

        MyCompoundData = MS_Analysis(COMPOUNDTABLEFORM_FILENAME,ingui=False)
        CompoundDataResults = openpyxl.load_workbook(COMPOUNDTABLEFORM_RESULTS_FILENAME)

        MySciexData = MS_Analysis(SCIEX_FILENAME,ingui=False)
        SciexResults = openpyxl.load_workbook(SCIEX_RESULTS_FILENAME)

        self.DataList = [MyWideData,MyLargeWideData,MyCompoundData,MySciexData]
        self.DataAnnotationList = [WIDETABLEFORM_ANNOTATION,LARGE_WIDETABLEFORM_ANNOTATION,COMPOUNDTABLEFORM_ANNOTATION,SCIEX_ANNOTATION]
        self.DataResultList = [WideDataResults,LargeWideDataResults,CompoundDataResults,SciexResults]

    def compare_df(self,table_name,MSData_df,ExcelWorkbook):
        MSData_df = MSData_df.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        ExcelWorkbook = self.sheet_to_table(ExcelWorkbook,table_name).apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.util.testing.assert_frame_equal(MSData_df,ExcelWorkbook)

    def test_getnormAreaTable(self):
        #Perform normalisation using ISTD
        for i in range(len(self.DataList)):
            [norm_Area_df,ISTD_Area,ISTD_map_df,ISTD_Report] = self.DataList[i].get_Normalised_Area('normArea by ISTD',self.DataAnnotationList[i])
            self.compare_df('normArea by ISTD',norm_Area_df,self.DataResultList[i])
            self.compare_df('ISTD map',ISTD_map_df,self.DataResultList[i])


    def test_getAnalyteConcTable(self):
        #Perform analyte concentration using ISTD
        for i in range(len(self.DataList)):
            [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df] = self.DataList[i].get_Analyte_Concentration('normConc by ISTD',self.DataAnnotationList[i])
            self.compare_df('normConc by ISTD',norm_Conc_df,self.DataResultList[i])
            self.compare_df('Sample Annot',Sample_Annot_df,self.DataResultList[i])
      
    def tearDown(self):
        for i in range(len(self.DataResultList)):
            self.DataResultList[i].close()

    def sheet_to_table(self,workbook,sheet_name):
        ws = workbook[sheet_name]
        data = ws.values
        cols = next(data)
        data = list(data)
        return pd.DataFrame(data, columns=cols)

if __name__ == '__main__':
    unittest.main()
