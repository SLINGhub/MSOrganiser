import unittest
import os
import pandas as pd
import openpyxl
from MSOrganiser import no_concatenate_workflow
from MSDataOutput import MSDataOutput

WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                          "test_no_concatenate_multipleISTD", "WideTableFormRow1.csv")
WIDETABLEFORMROW2_MULTIPLEISTD_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                          "test_no_concatenate_multipleISTD", "WideTableFormRow2.csv")
WIDETABLEFORMROW_MULTIPLEISTD_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 
                                           "test_no_concatenate_multipleISTD", "WideTableFormRow_Annotation.xlsx")
WIDETABLEFORMROW1_MULTIPLEISTD_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                               "test_no_concatenate_multipleISTD", "WideTableFormRow1_Results.xlsx")
WIDETABLEFORMROW1_MULTIPLEISTD_RESULTS_TRANSPOSE_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                                         "test_no_concatenate_multipleISTD", "WideTableFormRow1_TransposeResults.xlsx")
WIDETABLEFORMROW1_MULTIPLEISTD_RESULTS_LONGTABLE_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                                         "test_no_concatenate_multipleISTD", "WideTableFormRow1_LongTable.xlsx")
WIDETABLEFORMROW1_MULTIPLEISTD_RESULTS_LONGTABLE_WITH_ANNOT_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                                                    "test_no_concatenate_multipleISTD", 
                                                                                    "WideTableFormRow1_LongTable_with_Annot.xlsx")

WIDETABLEFORMROW1_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                          "test_no_concatenate", "WideTableFormRow1.csv")
WIDETABLEFORMROW2_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                          "test_no_concatenate", "WideTableFormRow2.csv")
WIDETABLEFORMROW_ANNOTATION = os.path.join(os.path.dirname(__file__),"testdata", 
                                           "test_no_concatenate", "WideTableFormRow_Annotation.xlsx")
WIDETABLEFORMROW1_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                  "test_no_concatenate", "WideTableFormRow1_Results.xlsx")
WIDETABLEFORMROW1_RESULTS_TRANSPOSE_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                            "test_no_concatenate", "WideTableFormRow1_TransposeResults.xlsx")
WIDETABLEFORMROW1_RESULTS_LONGTABLE_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                            "test_no_concatenate", "WideTableFormRow1_LongTable.xlsx")
WIDETABLEFORMROW1_RESULTS_LONGTABLE_WITH_ANNOT_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 
                                                                       "test_no_concatenate", "WideTableFormRow1_LongTable_with_Annot.xlsx")
class NoConcatenation_Test(unittest.TestCase):
    def test_no_concatenate(self):
        """Check if the software is able to from the two input raw data

        * Extract the Area
        * Calculate the normalised Area and concentation

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_FILENAME, WIDETABLEFORMROW2_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        # We just check the results of the first file input 
        [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)
        file_name_index = file_name.index(WIDETABLEFORMROW1_FILENAME)
        [file_data,sheet_names] = file_data_list[file_name_index]

        for sheet_name in sheet_names:
            if sheet_name != "Long_Table":
                data_index = sheet_names.index(sheet_name)
                ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW1_RESULTS_FILENAME,
                                                  sheet_name = sheet_name,
                                                  allow_multiple_istd = False)
                self.__compare_df(file_data[data_index],ExcelData_df)

    def test_no_concatenate_LongTable(self):
        """Check if the software is able to from the two input raw data

        * Extract the Area
        * Calculate the normalised Area and concentation
        * Create a Long Table without Annotation

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_FILENAME, WIDETABLEFORMROW2_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': True, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        # We just check the results of the first file input 
        [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)
        file_name_index = file_name.index(WIDETABLEFORMROW1_FILENAME)
        [file_data,sheet_names] = file_data_list[file_name_index]

        data_index = sheet_names.index("Long_Table")
        ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW1_RESULTS_LONGTABLE_FILENAME,
                                          sheet_name = "Long_Table",
                                          allow_multiple_istd = True)
        ExcelData_df = ExcelData_df.fillna('')
        self.__compare_df(file_data[data_index],ExcelData_df)

    def test_no_concatenate_LongTable_with_Annot(self):
        """Check if the software is able to from the two input raw data

        * Extract the Area
        * Calculate the normalised Area and concentation
        * Create a Long Table with Annotation

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_FILENAME, WIDETABLEFORMROW2_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': True, 
            'Long_Table_Annot': True, 
            'Testing': False
        }

        # We just check the results of the first file input 
        [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)
        file_name_index = file_name.index(WIDETABLEFORMROW1_FILENAME)
        [file_data,sheet_names] = file_data_list[file_name_index]

        data_index = sheet_names.index("Long_Table")
        ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW1_RESULTS_LONGTABLE_WITH_ANNOT_FILENAME,
                                          sheet_name = "Long_Table",
                                          allow_multiple_istd = True)
        ExcelData_df = ExcelData_df.fillna('')
        self.__compare_df(file_data[data_index],ExcelData_df)

    def test_no_concatenate_transpose(self):
        """Check if the software is able to from the two input raw data

        * Extract the Area
        * Calculate the normalised Area and concentation
        * Transpose the results correctly

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_FILENAME, WIDETABLEFORMROW2_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': True, 
            'Allow_Multiple_ISTD': False, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        # We just check the results of the first file input 
        [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)
        file_name_index = file_name.index(WIDETABLEFORMROW1_FILENAME)
        [file_data,sheet_names] = file_data_list[file_name_index]

        for sheet_name in sheet_names:
            if sheet_name != "Long_Table":
                data_index = sheet_names.index(sheet_name)

                # Not every sheet_name needs to be transposed.
                if sheet_name in ["Area", "normArea_by_ISTD", "normConc_by_ISTD"]:
                    if sheet_name in ["normArea_by_ISTD", "normConc_by_ISTD"]:
                        file_data[data_index] = MSDataOutput.transpose_MSdata(file_data[data_index],
                                                                              allow_multiple_istd = False)
                    elif sheet_name in ["Area"]:
                        file_data[data_index] = MSDataOutput.transpose_MSdata(file_data[data_index],
                                                                              allow_multiple_istd = False)
                    else:
                        print("We have a non-existing sheet_name")
                        exit(-1)

                file_data[data_index] = file_data[data_index].fillna('')

                ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW1_RESULTS_TRANSPOSE_FILENAME,
                                                  sheet_name = sheet_name,
                                                  allow_multiple_istd = False,
                                                  transpose = True)
                ExcelData_df = ExcelData_df.fillna('')

                self.__compare_df(file_data[data_index],ExcelData_df)

    def test_no_concatenate_multiple_ISTD(self):
        """Check if the software is able to from the two input raw data

        * Extract the Area
        * Calculate the normalised Area and concentation using multiple ISTD

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME, WIDETABLEFORMROW2_MULTIPLEISTD_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_MULTIPLEISTD_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': True, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        # We just check the results of the first file input 
        [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)
        file_name_index = file_name.index(WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME)
        [file_data,sheet_names] = file_data_list[file_name_index]

        for sheet_name in sheet_names:
            if sheet_name != "Long_Table":
                data_index = sheet_names.index(sheet_name)
                ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW1_MULTIPLEISTD_RESULTS_FILENAME,
                                                  sheet_name = sheet_name,
                                                  allow_multiple_istd = True)
                #print(ExcelData_df)
                #print(file_data[data_index])
                self.__compare_df(file_data[data_index],ExcelData_df)

    def test_no_concatenate_multiple_ISTD_LongTable(self):
        """Check if the software is able to from the two input raw data

        * Extract the Area
        * Calculate the normalised Area and concentation using multiple ISTD
        * Create a Long Table without Annotation

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME, WIDETABLEFORMROW2_MULTIPLEISTD_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_MULTIPLEISTD_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': True, 
            'Long_Table': True, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        # We just check the results of the first file input 
        [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)
        file_name_index = file_name.index(WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME)
        [file_data,sheet_names] = file_data_list[file_name_index]

        data_index = sheet_names.index("Long_Table")
        ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW1_MULTIPLEISTD_RESULTS_LONGTABLE_FILENAME,
                                          sheet_name = "Long_Table",
                                          allow_multiple_istd = True)
        ExcelData_df = ExcelData_df.fillna('')
        self.__compare_df(file_data[data_index],ExcelData_df)

    def test_no_concatenate_multiple_ISTD_LongTable_with_Annot(self):
        """Check if the software is able to from the two input raw data

        * Extract the Area
        * Calculate the normalised Area and concentation using multiple ISTD
        * Create a Long Table with Annotation

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME, WIDETABLEFORMROW2_MULTIPLEISTD_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_MULTIPLEISTD_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': False, 
            'Allow_Multiple_ISTD': True, 
            'Long_Table': True, 
            'Long_Table_Annot': True, 
            'Testing': False
        }

        # We just check the results of the first file input 
        [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)
        file_name_index = file_name.index(WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME)
        [file_data,sheet_names] = file_data_list[file_name_index]

        data_index = sheet_names.index("Long_Table")
        ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW1_MULTIPLEISTD_RESULTS_LONGTABLE_WITH_ANNOT_FILENAME,
                                          sheet_name = "Long_Table",
                                          allow_multiple_istd = True)
        ExcelData_df = ExcelData_df.fillna('')
        self.__compare_df(file_data[data_index],ExcelData_df)

    def test_no_concatenate_multiple_ISTD_transpose(self):
        """Check if the software is able to from the two input raw data

        * Extract the Area
        * Calculate the normalised Area and concentation using multiple ISTD
        * Transpose the results correctly

        """
        stored_args = {
            'MS_Files': [WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME, WIDETABLEFORMROW2_MULTIPLEISTD_FILENAME], 
            'MS_FileType': 'Agilent Wide Table in csv', 
            'Output_Directory': 'D:\\MSOrganiser', 
            'Output_Options': ['Area', 'normArea by ISTD', 'normConc by ISTD'], 
            'Annot_File': WIDETABLEFORMROW_MULTIPLEISTD_ANNOTATION, 
            'Output_Format': 'Excel', 
            'Concatenate': 'No Concatenate', 
            'Transpose_Results': True, 
            'Allow_Multiple_ISTD': True, 
            'Long_Table': False, 
            'Long_Table_Annot': False, 
            'Testing': False
        }

        # We just check the results of the first file input 
        [file_data_list, file_name] = no_concatenate_workflow(stored_args,testing = True)
        file_name_index = file_name.index(WIDETABLEFORMROW1_MULTIPLEISTD_FILENAME)
        [file_data,sheet_names] = file_data_list[file_name_index]

        for sheet_name in sheet_names:
            if sheet_name != "Long_Table":
                data_index = sheet_names.index(sheet_name)

                # Not every sheet_name needs to be transposed.
                if sheet_name in ["Area", "normArea_by_ISTD", "normConc_by_ISTD"]:
                    if sheet_name in ["normArea_by_ISTD", "normConc_by_ISTD"]:
                        file_data[data_index] = MSDataOutput.transpose_MSdata(file_data[data_index],
                                                                              allow_multiple_istd = True)
                    elif sheet_name in ["Area"]:
                        file_data[data_index] = MSDataOutput.transpose_MSdata(file_data[data_index],
                                                                              allow_multiple_istd = False)
                    else:
                        print("We have a non-existing sheet_name")
                        exit(-1)

                file_data[data_index] = file_data[data_index].fillna('')

                ExcelData_df = self.__sheet_to_df(workbook = WIDETABLEFORMROW1_MULTIPLEISTD_RESULTS_TRANSPOSE_FILENAME,
                                                  sheet_name = sheet_name,
                                                  allow_multiple_istd = True,
                                                  transpose = True)
                ExcelData_df = ExcelData_df.fillna('')

                self.__compare_df(file_data[data_index],ExcelData_df)

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

        if allow_multiple_istd and not transpose and sheet_name in ["normArea_by_ISTD", "normConc_by_ISTD"]:
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
        if allow_multiple_istd and not transpose and sheet_name in ["normArea_by_ISTD", "normConc_by_ISTD"]:
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
