import unittest
import os
import pandas as pd
import openpyxl
from MSAnalysis import MS_Analysis
from MSOrganiser import concatenate_along_rows_workflow

WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm.csv')
WIDETABLEFORM_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_Annotation.xlsm')
WIDETABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_Results.xlsx')
WIDETABLEFORM_LONGTABLE_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_LongTable.xlsx')
WIDETABLEFORM_LONGTABLE_WITH_ANNOT_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_LongTable_with_Annot.xlsx')

LARGE_WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'LargeTestData.csv')
LARGE_WIDETABLEFORM_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 'LargeTestData_Annotation.xlsm')
LARGE_WIDETABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'LargeTestData_Results.xlsx')

COMPOUNDTABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'CompoundTableForm.csv')
COMPOUNDTABLEFORM_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 'CompoundTableForm_Annotation.xlsm')
COMPOUNDTABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'CompoundTableForm_Results.xlsx')

SCIEX_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'SciExTestData.txt')
SCIEX_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 'SciExTestData_Annotation.xlsm')
SCIEX_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'SciExTestData_Results.xlsx')

class Agilent_Test(unittest.TestCase):

    def setUp(self):
        MyWideData = MS_Analysis(MS_FilePath = WIDETABLEFORM_FILENAME,
                                 MS_FileType = 'Agilent Wide Table in csv',
                                 Annotation_FilePath = WIDETABLEFORM_ANNOTATION,
                                 ingui = True)
        WideDataResults = openpyxl.load_workbook(WIDETABLEFORM_RESULTS_FILENAME)

        MyLargeWideData = MS_Analysis(MS_FilePath = LARGE_WIDETABLEFORM_FILENAME,
                                      MS_FileType = 'Agilent Wide Table in csv',
                                      Annotation_FilePath = LARGE_WIDETABLEFORM_ANNOTATION,
                                      ingui = True)
        LargeWideDataResults = openpyxl.load_workbook(LARGE_WIDETABLEFORM_RESULTS_FILENAME)

        MyCompoundData = MS_Analysis(MS_FilePath = COMPOUNDTABLEFORM_FILENAME,
                                     MS_FileType = 'Agilent Compound Table in csv',
                                     Annotation_FilePath = COMPOUNDTABLEFORM_ANNOTATION,
                                     ingui = True)
        CompoundDataResults = openpyxl.load_workbook(COMPOUNDTABLEFORM_RESULTS_FILENAME)

        MySciexData = MS_Analysis(MS_FilePath = SCIEX_FILENAME,
                                  MS_FileType = 'Multiquant Long Table in txt',
                                  Annotation_FilePath = SCIEX_ANNOTATION,
                                  ingui = True)
        SciexResults = openpyxl.load_workbook(SCIEX_RESULTS_FILENAME)

        self.DataList = [MyWideData,MyLargeWideData,MyCompoundData,MySciexData]
        self.DataResultList = [WideDataResults,LargeWideDataResults,CompoundDataResults,SciexResults]

        self.MyLongTableData = MS_Analysis(MS_FilePath = WIDETABLEFORM_FILENAME,
                                           MS_FileType = 'Agilent Wide Table in csv',
                                           Annotation_FilePath = WIDETABLEFORM_ANNOTATION,
                                           ingui = True,
                                           longtable = True, 
                                           longtable_annot = False)
        self.LongTableDataResults = openpyxl.load_workbook(WIDETABLEFORM_LONGTABLE_FILENAME)

        self.MyLongTableDataWithAnnot = MS_Analysis(MS_FilePath = WIDETABLEFORM_FILENAME,
                                                    MS_FileType = 'Agilent Wide Table in csv',
                                                    Annotation_FilePath = WIDETABLEFORM_ANNOTATION,
                                                    ingui = True,
                                                    longtable = True, 
                                                    longtable_annot = True)
        self.LongTableDataWithAnnotResults = openpyxl.load_workbook(WIDETABLEFORM_LONGTABLE_WITH_ANNOT_FILENAME)

    def test_getnormAreaTable(self):
        """Check if the software is able to calculate the normalise area using MS_Analysis.get_Normalised_Area from these datasets 

        * WideTableForm.csv
        * LargeTestData.csv
        * CompoundTableForm.csv
        * SciExTestData.txt
        """

        #Perform normalisation using ISTD
        for i in range(len(self.DataList)):
            [norm_Area_df,ISTD_Area,Transition_Name_Annot,ISTD_Report] = self.DataList[i].get_Normalised_Area('normArea by ISTD')
            self.__compare_df('normArea_by_ISTD',norm_Area_df,self.DataResultList[i])
            self.__compare_df('Transition_Name_Annot',Transition_Name_Annot,self.DataResultList[i])


    def test_getAnalyteConcTable(self):
        """Check if the software is able to calculate the transition names concentration using MS_Analysis.get_Analyte_Concentration from these datasets

        * WideTableForm.csv
        * LargeTestData.csv
        * CompoundTableForm.csv
        * SciExTestData.txt
        """

        #Perform analyte concentration using ISTD
        for i in range(len(self.DataList)):
            [norm_Conc_df,ISTD_Conc_df,ISTD_Samp_Ratio_df,Sample_Annot_df] = self.DataList[i].get_Analyte_Concentration('normConc by ISTD')
            self.__compare_df('normConc_by_ISTD',norm_Conc_df,self.DataResultList[i])
            #Remove the column "Merge_Status" as it is not relevant
            #Reorder the column such that "Concentration_Unit" is at the last column
            Sample_Annot_df = Sample_Annot_df[["Data_File_Name", "Sample_Name",
                                               "Sample_Amount", "Sample_Amount_Unit",
                                               "ISTD_Mixture_Volume_[uL]", "ISTD_to_Sample_Amount_Ratio",
                                               "Concentration_Unit"]]
            self.__compare_df('Sample_Annot',Sample_Annot_df,self.DataResultList[i])

    def test_getLongTable(self):
        """Check if the software is able to get the LongTable from these datasets

        * WideTableForm.csv
        """
        self.MyLongTableData.get_from_Input_Data('Area', outputdata = False)
        Long_Table_df = self.MyLongTableData.get_Long_Table()
        self.__compare_df('Long_Table',Long_Table_df,self.LongTableDataResults)

        self.MyLongTableDataWithAnnot.get_from_Input_Data('Area', outputdata = False)
        self.MyLongTableDataWithAnnot.get_Normalised_Area('normArea by ISTD', outputdata = False)
        self.MyLongTableDataWithAnnot.get_Analyte_Concentration('normConc by ISTD', outputdata = False)
        Long_Table_df = self.MyLongTableDataWithAnnot.get_Long_Table()
        self.__compare_df('Long_Table',Long_Table_df,self.LongTableDataWithAnnotResults)
           
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
