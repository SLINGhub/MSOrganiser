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
        MyWideData = MS_Analysis(WIDETABLEFORM_FILENAME,'Agilent Wide Table in csv',WIDETABLEFORM_ANNOTATION,ingui=True)
        WideDataResults = openpyxl.load_workbook(WIDETABLEFORM_RESULTS_FILENAME)

        MyLargeWideData = MS_Analysis(LARGE_WIDETABLEFORM_FILENAME,'Agilent Wide Table in csv',LARGE_WIDETABLEFORM_ANNOTATION,ingui=True)
        LargeWideDataResults = openpyxl.load_workbook(LARGE_WIDETABLEFORM_RESULTS_FILENAME)

        MyCompoundData = MS_Analysis(COMPOUNDTABLEFORM_FILENAME,'Agilent Compound Table in csv',COMPOUNDTABLEFORM_ANNOTATION,ingui=True)
        CompoundDataResults = openpyxl.load_workbook(COMPOUNDTABLEFORM_RESULTS_FILENAME)

        MySciexData = MS_Analysis(SCIEX_FILENAME,'Multiquant Long Table in txt',SCIEX_ANNOTATION,ingui=True)
        SciexResults = openpyxl.load_workbook(SCIEX_RESULTS_FILENAME)

        self.DataList = [MyWideData,MyLargeWideData,MyCompoundData,MySciexData]
        #self.DataAnnotationList = [WIDETABLEFORM_ANNOTATION,LARGE_WIDETABLEFORM_ANNOTATION,COMPOUNDTABLEFORM_ANNOTATION,SCIEX_ANNOTATION]
        self.DataResultList = [WideDataResults,LargeWideDataResults,CompoundDataResults,SciexResults]

    def test_getnormAreaTable(self):
        """Check if the software is able to calculate the normalise area using MS_Analysis.get_Normalised_Area from these datasets 

        * WideTableForm.csv
        * sPerfect_Index_AllLipids_raw.csv
        * CompoundTableForm.csv
        * Mohammed_SciEx_data.txt
        """

        #Perform normalisation using ISTD
        for i in range(len(self.DataList)):
            [norm_Area_df,ISTD_Area,Transition_Name_Annot,ISTD_Report] = self.DataList[i].get_Normalised_Area('normArea by ISTD')
            self.__compare_df('normArea_by_ISTD',norm_Area_df,self.DataResultList[i])
            self.__compare_df('Transition_Name_Annot',Transition_Name_Annot,self.DataResultList[i])


    def test_getAnalyteConcTable(self):
        """Check if the software is able to calculate the transition names concentration using MS_Analysis.get_Analyte_Concentration from these datasets

        * WideTableForm.csv
        * sPerfect_Index_AllLipids_raw.csv
        * CompoundTableForm.csv
        * Mohammed_SciEx_data.txt
        """

        #Perform analyte concentration using ISTD
        for i in range(len(self.DataList)):
            [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df] = self.DataList[i].get_Analyte_Concentration('normConc by ISTD')
            self.__compare_df('normConc_by_ISTD',norm_Conc_df,self.DataResultList[i])
            self.__compare_df('Sample_Annot',Sample_Annot_df,self.DataResultList[i])
      
    def tearDown(self):
        for i in range(len(self.DataResultList)):
            self.DataResultList[i].close()

    def __compare_df(self,table_name,MSData_df,ExcelWorkbook):
        MSData_df = MSData_df.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        ExcelWorkbook = self.__sheet_to_table(ExcelWorkbook,table_name).apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.testing.assert_frame_equal(MSData_df,ExcelWorkbook)

    def __sheet_to_table(self,workbook,sheet_name):
        ws = workbook[sheet_name]
        data = ws.values
        cols = next(data)
        data = list(data)
        return pd.DataFrame(data, columns=cols)

if __name__ == '__main__':
    unittest.main()
