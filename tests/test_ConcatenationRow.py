import unittest
import os
import pandas as pd
import openpyxl
from MSOrganiser import concatenate_along_rows_workflow
from MSDataOutput import MSDataOutput

WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                          "test_concatenate_row_multipleISTD", "WideTableFormRow1.csv")
WIDETABLEFORMROW2_MULTIPLEISTD_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                          "test_concatenate_row_multipleISTD", "WideTableFormRow2.csv")
WIDETABLEFORMROW_MULTIPLEISTD_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 
                                           "test_concatenate_row_multipleISTD", "WideTableFormRow_Annotation.xlsm")
WIDETABLEFORMROW_MULTIPLEISTD_CONCATENATERESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                            "test_concatenate_row_multipleISTD", "WideTableFormRow_ConcatenateResults.xlsx")
WIDETABLEFORMROW_MULTIPLEISTD_CONCATENATERESULTS_TRANSPOSE_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                                      "test_concatenate_row_multipleISTD", "WideTableFormRow_Concatenate_TransposeResults.xlsx")
WIDETABLEFORMROW_MULTIPLEISTD_CONCATENATERESULTS_LONGTABLE_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                                      "test_concatenate_row_multipleISTD", "WideTableFormRow_Concatenate_LongTable.xlsx")
WIDETABLEFORMROW_MULTIPLEISTD_CONCATENATERESULTS_LONGTABLE_WITH_ANNOT_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                                                 "test_concatenate_row_multipleISTD", "WideTableFormRow_Concatenate_LongTable_with_Annot.xlsx")

WIDETABLEFORMROW1_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                          "test_concatenate_row", "WideTableFormRow1.csv")
WIDETABLEFORMROW2_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                          "test_concatenate_row", "WideTableFormRow2.csv")
WIDETABLEFORMROW_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 
                                           "test_concatenate_row", "WideTableFormRow_Annotation.xlsm")
WIDETABLEFORMROW_CONCATENATERESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                            "test_concatenate_row", "WideTableFormRow_ConcatenateResults.xlsx")
WIDETABLEFORMROW_CONCATENATERESULTS_TRANSPOSE_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                                      "test_concatenate_row", "WideTableFormRow_Concatenate_TransposeResults.xlsx")
WIDETABLEFORMROW_CONCATENATERESULTS_LONGTABLE_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                                      "test_concatenate_row", "WideTableFormRow_Concatenate_LongTable.xlsx")
WIDETABLEFORMROW_CONCATENATERESULTS_LONGTABLE_WITH_ANNOT_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                                                 "test_concatenate_row", "WideTableFormRow_Concatenate_LongTable_with_Annot.xlsx")


class Concatenation_By_Row_Test(unittest.TestCase):
    def test_concatenate_by_rows(self):
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_FILENAME, WIDETABLEFORMROW2_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'Concatenate along Sample Name (rows)', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
            }
        [PDFReport, concatenate_df_list, concatenate_df_sheet_name] = concatenate_along_rows_workflow(stored_args,testing = True)
        #print(concatenate_df_sheet_name)
        for sheet_name in concatenate_df_sheet_name:
            if sheet_name != "Long_Table":
                data_index = concatenate_df_sheet_name.index(sheet_name)
                ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW_CONCATENATERESULTS_FILENAME,
                                                  sheet_name = sheet_name,
                                                  allow_multiple_istd = False)
                self.__compare_df(concatenate_df_list[data_index],ExcelData_df)

    def test_concatenate_by_rows_LongTable(self):
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_FILENAME, WIDETABLEFORMROW2_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'Concatenate along Sample Name (rows)', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': True, 
            'Long_Table_Annot': False, 
            'Testing': False
            }
        [PDFReport, concatenate_df_list, concatenate_df_sheet_name] = concatenate_along_rows_workflow(stored_args,testing = True)
        data_index = concatenate_df_sheet_name.index("Long_Table")
        ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW_CONCATENATERESULTS_LONGTABLE_FILENAME,
                                          sheet_name = "Long_Table",
                                          allow_multiple_istd = False)
        ExcelData_df = ExcelData_df.fillna('')
        self.__compare_df(concatenate_df_list[data_index],ExcelData_df)

    def test_concatenate_by_rows_LongTable_with_Annot(self):
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_FILENAME, WIDETABLEFORMROW2_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'Concatenate along Sample Name (rows)', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': True, 
            'Long_Table_Annot': True, 
            'Testing': False
            }
        [PDFReport, concatenate_df_list, concatenate_df_sheet_name] = concatenate_along_rows_workflow(stored_args,testing = True)
        data_index = concatenate_df_sheet_name.index("Long_Table")
        ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW_CONCATENATERESULTS_LONGTABLE_WITH_ANNOT_FILENAME,
                                          sheet_name = "Long_Table",
                                          allow_multiple_istd = False)
        ExcelData_df = ExcelData_df.fillna('')
        self.__compare_df(concatenate_df_list[data_index],ExcelData_df)

    def test_concatenate_by_rows_transpose(self):
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_FILENAME, WIDETABLEFORMROW2_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'Concatenate along Sample Name (rows)', 
            'Transpose_Results': True, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
            }
        [PDFReport, concatenate_df_list, concatenate_df_sheet_name] = concatenate_along_rows_workflow(stored_args,testing = True)
        for sheet_name in concatenate_df_sheet_name:
            if sheet_name != "Long_Table":
                data_index = concatenate_df_sheet_name.index(sheet_name)

                # Not every sheet_name needs to be transposed.
                if sheet_name in ["Area", "normArea_by_ISTD", "normConc_by_ISTD"]:
                    concatenate_df_list[data_index] = MSDataOutput.transpose_MSdata(concatenate_df_list[data_index],
                                                                                    allow_multiple_istd = False)
                concatenate_df_list[data_index] = concatenate_df_list[data_index].fillna('')

                ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW_CONCATENATERESULTS_TRANSPOSE_FILENAME,
                                                  sheet_name = sheet_name,
                                                  allow_multiple_istd = False,
                                                  transpose = True)
                ExcelData_df = ExcelData_df.fillna('')

                self.__compare_df(concatenate_df_list[data_index],ExcelData_df)

    def test_concatenate_by_rows_multiple_ISTD(self):
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME, WIDETABLEFORMROW2_MULTIPLEISTD_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_MULTIPLEISTD_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'Concatenate along Sample Name (rows)', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': True, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
            }
        [PDFReport, concatenate_df_list, concatenate_df_sheet_name] = concatenate_along_rows_workflow(stored_args,testing = True)
        #print(concatenate_df_sheet_name)
        for sheet_name in concatenate_df_sheet_name:
            if sheet_name != "Long_Table":
                data_index = concatenate_df_sheet_name.index(sheet_name)
                ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW_MULTIPLEISTD_CONCATENATERESULTS_FILENAME,
                                                  sheet_name = sheet_name,
                                                  allow_multiple_istd = True)
                self.__compare_df(concatenate_df_list[data_index],ExcelData_df)

    def test_concatenate_by_rows_multiple_ISTD_LongTable(self):
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME, WIDETABLEFORMROW2_MULTIPLEISTD_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_MULTIPLEISTD_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'Concatenate along Sample Name (rows)', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': True, 
            'Long_Table': True, 
            'Long_Table_Annot': False, 
            'Testing': False
            }
        [PDFReport, concatenate_df_list, concatenate_df_sheet_name] = concatenate_along_rows_workflow(stored_args,testing = True)
        data_index = concatenate_df_sheet_name.index("Long_Table")
        ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW_MULTIPLEISTD_CONCATENATERESULTS_LONGTABLE_FILENAME,
                                          sheet_name = "Long_Table",
                                          allow_multiple_istd = True)
        ExcelData_df = ExcelData_df.fillna('')
        self.__compare_df(concatenate_df_list[data_index],ExcelData_df)

    def test_concatenate_by_rows_multiple_ISTD_LongTable_with_Annot(self):
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME, WIDETABLEFORMROW2_MULTIPLEISTD_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_MULTIPLEISTD_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'Concatenate along Sample Name (rows)', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': True, 
            'Long_Table': True, 
            'Long_Table_Annot': True, 
            'Testing': False
            }
        [PDFReport, concatenate_df_list, concatenate_df_sheet_name] = concatenate_along_rows_workflow(stored_args,testing = True)
        data_index = concatenate_df_sheet_name.index("Long_Table")
        ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW_MULTIPLEISTD_CONCATENATERESULTS_LONGTABLE_WITH_ANNOT_FILENAME,
                                          sheet_name = "Long_Table",
                                          allow_multiple_istd = True)
        ExcelData_df = ExcelData_df.fillna('')
        self.__compare_df(concatenate_df_list[data_index],ExcelData_df)

    def test_concatenate_by_rows_multiple_ISTD_transpose(self):
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME, WIDETABLEFORMROW2_MULTIPLEISTD_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_MULTIPLEISTD_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'Concatenate along Sample Name (rows)', 
            'Transpose_Results': True, 
            'Allow_Multiple_ISTD': True, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
            }
        [PDFReport, concatenate_df_list, concatenate_df_sheet_name] = concatenate_along_rows_workflow(stored_args,testing = True)
        for sheet_name in concatenate_df_sheet_name:
            if sheet_name != "Long_Table":
                data_index = concatenate_df_sheet_name.index(sheet_name)

                # Not every sheet_name needs to be transposed.
                if sheet_name in ["Area", "normArea_by_ISTD", "normConc_by_ISTD"]:
                    concatenate_df_list[data_index] = MSDataOutput.transpose_MSdata(concatenate_df_list[data_index],
                                                                                    allow_multiple_istd = True)
                concatenate_df_list[data_index] = concatenate_df_list[data_index].fillna('')

                ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW_MULTIPLEISTD_CONCATENATERESULTS_TRANSPOSE_FILENAME,
                                                  sheet_name = sheet_name,
                                                  allow_multiple_istd = True,
                                                  transpose = True)
                ExcelData_df = ExcelData_df.fillna('')

                self.__compare_df(concatenate_df_list[data_index],ExcelData_df)

    def __compare_df(self,MSData_df,ExcelData_df):
        MSData_df = MSData_df.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        ExcelData_df = ExcelData_df.apply(pd.to_numeric, errors='ignore', downcast = 'float')
        pd.testing.assert_frame_equal(MSData_df,ExcelData_df)

    def __sheet_to_df(self,workbook,sheet_name, 
                      allow_multiple_istd = False, transpose = False):

        # Assume that the header is at the first row of the sheet.
        header_col = [0]
        # Assume that there is no index column
        index_col = None

        if allow_multiple_istd and not transpose and sheet_name in ["Area", "normArea_by_ISTD", "normConc_by_ISTD"]:
            # Assume that the header is at the first two row of the sheet.
            header_col = [0,1]
            # Assume that the first column is the index column 
            index_col = [0]

        ExcelData_df = pd.read_excel(
            io = workbook,
            header = header_col,
            index_col = index_col,
            engine = "openpyxl",
            sheet_name= sheet_name
            )

        # We need to update the column names as the second level column name can be blank
        # But pandas will fill it in as "Unnamed: {Level position}"
        if allow_multiple_istd and not transpose and sheet_name in ["Area", "normArea_by_ISTD", "normConc_by_ISTD"]:
            tuples=[]
            for index, column_tuple in enumerate(ExcelData_df.columns.values):
                if("Unnamed:" in column_tuple[1]):
                    tuples.append((column_tuple[0],""))
                else:
                    tuples.append(column_tuple)
            column_index = pd.MultiIndex.from_tuples(tuples, names=["Transition_Name", "Transition_Name_ISTD"])
            ExcelData_df.columns = column_index
            #print(ExcelData_df.columns)
            #print(ExcelData_df.columns.levels)
            #for level in range(ExcelData_df.columns.nlevels):
                #unique = ExcelData_df.columns.levels[level]
                #print(unique)

        return ExcelData_df

#class Concatenation_By_Row_Test(unittest.TestCase):
#    print("Here")

if __name__ == '__main__':
    unittest.main()
