import unittest
import os
import pandas as pd
import openpyxl
from MSRawData import AgilentMSRawData
from MSCalculate import ISTD_Operations

WIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm.csv')
WIDETABLEFORM_ISTDMAP = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_ISTDmap.csv')
WIDETABLEFORM_RESULTS_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'WideTableForm_Results.xlsx')

MESSYWIDETABLEFORM_FILENAME = os.path.join(os.path.dirname(__file__),"testdata", 'MessyWideTableForm.csv')
MESSYWIDETABLEFORM_ISTDMAP = os.path.join(os.path.dirname(__file__),"testdata", 'MessyWideTableForm_ISTDmap.csv')

class Agilent_Test(unittest.TestCase):

    def setUp(self):
        '''
        self.WideData = AgilentMSRawData(WIDETABLEFORM_FILENAME,ingui=True)
        self.DataProcessing = ISTD_Operations(ingui=True)
        self.WideDataResults = openpyxl.load_workbook(WIDETABLEFORM_RESULTS_FILENAME)
        '''
        self.MessyWideData = AgilentMSRawData(MESSYWIDETABLEFORM_FILENAME,ingui=True)

    '''
    def test_getnormAreaTable(self):
        #Get Area Table
        #Area_df = self.WideData.get_table('Area',is_numeric=True)
        Messy_Area_df = self.MessyWideData.get_table('Area',is_numeric=True)

        #Get ISTD map df
        #WideTable_ISTD_map_df = self.DataProcessing.read_ISTD_map(WIDETABLEFORM_ISTDMAP,'normArea by ISTD')
        MessyWideTable_ISTD_map_df = ISTD_Operations.read_ISTD_map(MESSYWIDETABLEFORM_ISTDMAP,'normArea by ISTD')

        #Perform normalisation using ISTD and output the result
        #[norm_Area_df,ISTD_Area] = self.DataProcessing.normalise_by_ISTD(Area_df,WideTable_ISTD_map_df)
        [messynorm_Area_df,messyISTD_Area,messyISTD_report] = ISTD_Operations.normalise_by_ISTD(Messy_Area_df,MessyWideTable_ISTD_map_df,'normArea by ISTD')

        #Check if the values are equal
        #We set dtype to false because some columns are mixed of int64 and float64 when reading excel,
        #this is different from the norm Area output where all number are in float64 
        #pd.util.testing.assert_frame_equal(ISTD_Area,self.sheet_to_table(self.WideDataResults,"ISTD Area"),check_dtype=False)
        #pd.util.testing.assert_frame_equal(norm_Area_df,self.sheet_to_table(self.WideDataResults,"normArea by ISTD"),check_dtype=False)
    '''

    #def tearDown(self):
        #self.WideDataResults.close()

    def sheet_to_table(self,workbook,sheet_name):
        ws = workbook[sheet_name]
        data = ws.values
        cols = next(data)
        data = list(data)
        return pd.DataFrame(data, columns=cols)

if __name__ == '__main__':
    unittest.main()
