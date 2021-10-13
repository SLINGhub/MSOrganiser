import pandas as pd
import numpy as np
import sys
import logging
import os
from pathlib import Path

class MSRawData:
    """
    A class to describe raw data obtained from the MS machine

    Args:
        filePath (str): file path of the input MRM transition name file
        logger (object): logger object created by start_logger in MSOrganiser
        ingui (bool): if True, print analysis status to screen
    """

    def __init__(self, filepath, logger=None, ingui=True):
        self.__logger = logger
        self.__ingui = ingui
        self.__filecheck(Path(filepath))

    def __filecheck(self,filepath):
        """Check if filepath exists and is a file"""
        if not filepath.exists():
            if self.__logger:
                self.__logger.error('Input file path ' + '\'' + str(filepath) + '\'' +
                                    ' could not be found. ' +
                                    'Please check if the input file path.')
            if self.__ingui:
                print('Input file path ' + '\'' + str(filepath) +  '\'' +
                      ' could not be found. ' +
                      'Please check if the input file path.',
                      flush = True)
            sys.exit(-1)
        elif not filepath.is_file():
            if self.__logger:
                self.__logger.error('Input file path ' + '\'' + str(filepath) + '\'' + 
                                    ' does not lead to a system file. ' + 
                                    'Please check if the input file path is a system file and not a folder.')
            if self.__ingui:
                print('Input file path ' + '\'' + str(filepath) + '\'' +
                      ' does not lead to a system file. ' + 
                      'Please check if the input file path is a system file and not a folder.',
                      flush = True)
            sys.exit(-1)

    def remove_whiteSpaces(self,df):
        """Strip the whitespaces for each string columns of a df

        Args:
            df (pandas DataFrame): A panda data frame

        Returns:
            df (pandas DataFrame): A panda data frame with white space removed

        """
        df[df.select_dtypes(['object']).columns] = df.select_dtypes(['object']).apply(lambda x: x.str.strip())
        return df


class AgilentMSRawData(MSRawData):
    """
    To describe raw data obtained from the Agilent MS machine

    Args:
        filePath (str): file path of the input MRM transition name file
        logger (object): logger object created by start_logger in MSOrganiser
        ingui (bool): if True, print analysis status to screen
    """

    def __init__(self, filepath, logger=None, ingui=True):
        MSRawData.__init__(self,filepath, ingui = ingui,logger=logger)
        self.__logger = logger
        self.__ingui = ingui
        self.__readfile(filepath)
        self.__getdataform(filepath)
        self.__filename = os.path.basename(filepath)
        self.VALID_COMPOUND_RESULTS = ('Area','RT','FWHM','S/N','Symmetry')
        self.VALID_COMPOUND_METHODS = ('Precursor Ion','Product Ion')

    def get_table(self,column_name,is_numeric=True):
        """Function to get the table from MassHunter Raw Data

        Args:
            column_name (str): The name of the column given in the Output_Options.

        Returns:
            A data frame of sample as rows and transition names as columns with values from the chosen column name

        """
        if self.DataForm == "WideTableForm":
            return self.__get_table_wide(column_name,is_numeric)
        elif self.DataForm == "CompoundTableForm":
            return self.__get_table_compound(column_name,is_numeric)

    #def get_data_file_name(self):
    #    """Function to get the list of sample names in a form of a dataframe
    #
    #    Returns:
    #        A data frame of sample as rows and transition names as columns with values from the chosen column name
    #
    #    """
    #    if self.DataForm == "WideTableForm":
    #        return self.__get_data_file_name_wide()
    #    elif self.DataForm == "CompoundTableForm":
    #        return self.__get_data_file_name_compound()

    def __get_table_wide(self,column_name,is_numeric=True):
        """Function to get the table from MassHunter Raw Data in Wide Table form"""

        #Get the data file name and give error when it cannot be found
        DataFileName_df = self.__get_data_file_name_wide()

        #Check if Column name comes from Results or Methods group
        if column_name in self.VALID_COMPOUND_RESULTS:
            column_group = "Results"
        elif column_name in self.VALID_COMPOUND_METHODS:
            column_group = "Method"
        else:
            if self.__logger:
                self.__logger.error('%s is not a valid column in MassHunter or not available as a valid output for this program.',column_name)
            if self.__ingui:
                print(column_name + ' is not a valid column in MassHunter or not available as a valid output for this program.',flush=True)
            sys.exit(-1)

        #Extract the data  with the given column name and group
        table_index = self.RawData.iloc[0,:].str.contains(column_group) & self.RawData.iloc[1,:].str.contains(column_name)
        table_df = self.RawData.loc[:,table_index].copy()

        if table_df.empty:
            return table_df

        #Remove the column group text and whitespaces
        table_df.iloc[0,:] = table_df.iloc[0,:].str.replace(column_group, "").str.strip()

        #Assign column name
        colnames = table_df.iloc[0,:].astype('str').str.strip()
        table_df.columns = colnames

        #We remove the first and second row because the column names are given
        table_df = table_df.iloc[2:]
        
        #Reset the row index
        table_df = table_df.reset_index(drop=True)

        #Convert text numbers into numeric
        if is_numeric:
            table_df = table_df.apply(pd.to_numeric, errors='coerce')

        table_df = pd.concat([DataFileName_df, table_df], axis=1)
        
        #Strip the whitespaces for each string columns
        table_df = self.remove_whiteSpaces(table_df)

        return table_df

    def __get_table_compound(self,column_name,is_numeric=True):
        """Function to get the table from MassHunter Raw Data in Compound Table form"""

        #Get the data file name and give error when it cannot be found
        DataFileName_df = self.__get_data_file_name_compound()

        #Get the compound table df and give error when it cannot be found
        #CompoundName_df = self.__get_compound_name_compound(column_name)
        table_df = self.__get_compound_name_compound(column_name)

        if table_df.empty:
            return table_df

        table_df = table_df.transpose()

        #Assign column name
        colnames = table_df.iloc[0,:].astype('str').str.strip()
        table_df.columns = colnames
        
        #We remove the first row because the column names are given
        table_df = table_df.iloc[1:]

        #If column name is a compound method, only the first row has data, we need to replicate data for all the rows
        if column_name in self.VALID_COMPOUND_METHODS:
            table_df = pd.concat([table_df]*DataFileName_df.shape[0], ignore_index=True)
        
        #Reset the row index
        table_df = table_df.reset_index(drop=True)

        #Convert text numbers into numeric
        if is_numeric:
            table_df = table_df.apply(pd.to_numeric, errors='coerce')

        table_df = pd.concat([DataFileName_df, table_df], axis=1)

        #Strip the whitespaces for each string columns
        table_df = self.remove_whiteSpaces(table_df)

        return table_df

    def __get_compound_name_compound(self,column_name):
        """Function to get the df Transition Name as Rows, Sample Name as Columns with values from the chosen column_name. E.g Area """

        # Get the column index of where the Transition Names are. We know for sure that it is on the third row
        Compound_Col = self.RawData.iloc[0,:].str.contains("Compound Method") & self.RawData.iloc[1,:].str.contains("Name")
        Compound_Col_Index = Compound_Col.index[Compound_Col == True].tolist()
        #Give an error if we can't get any transition name
        if len(Compound_Col_Index) == 0 :
            if self.__logger:
                self.__logger.error('\'' + self.__filename + '\' ' +
                                    'has no column contaning \"Name\" in Compound Method Table. ' +
                                    'Please check the input file.')
            if self.__ingui:
                print('\'' + self.__filename + '\' ' +
                      'has no column contaning \"Name\" in Compound Method Table. ' +
                      'Please check the input file.',
                      flush=True)
            sys.exit(-1)

        # Find cols with Transition in second row and Qualifier Method in the first row
        Qualifier_Method_Col = self.RawData.iloc[0,:].str.contains("Qualifier \d Method", regex=True) & self.RawData.iloc[1,:].str.contains("Transition")
        # Get the column index where the group of Qualifier Method first appeared.
        Qualifier_Method_Col_Index = Qualifier_Method_Col.index[Qualifier_Method_Col == True].tolist()

        # Find cols with Data File in the second row
        DataFileName_Col = self.RawData.iloc[1,:].str.contains("Data File")
        # Find the number of Qualifiers each Transition is entitled to have
        No_of_Qual_per_Transition = int((Qualifier_Method_Col.values == True).sum() / (DataFileName_Col.values == True).sum() )

        #We start a new Compound_list
        Compound_list = []

        #We start on row three
        self.RawData.iloc[2:,sorted(Compound_Col_Index + Qualifier_Method_Col_Index[0:No_of_Qual_per_Transition] )].apply(lambda x: AgilentMSRawData._get_Compound_List(x=x,
                                                                                                                                                                        Compound_list=Compound_list),
                                                                                                                          axis=1)

        CompoundName_df = pd.DataFrame(Compound_list)
        CompoundName_df = self.remove_whiteSpaces(CompoundName_df)

        #All Column Name (e.g Area) and Transition index
        ColName_Col = self.RawData.iloc[1,:].str.contains(column_name) | self.RawData.iloc[1,:].str.contains("Transition")
        ColName_Col_Index = ColName_Col.index[ColName_Col == True].tolist()

        #Transition from Compound Method
        CpdMethod_Transition_Col = self.RawData.iloc[0,:].str.contains("Compound Method") & self.RawData.iloc[1,:].str.contains("Transition")
        CpdMethod_Transition_Col_Index = CpdMethod_Transition_Col.index[CpdMethod_Transition_Col == True].tolist()

        #Column Name (e.g Area) found only at the Qualifier
        ColName_Qualifier_Col = self.RawData.iloc[0,:].str.contains("Qualifier \d Results", regex=True) & self.RawData.iloc[1,:].str.contains(column_name)
        ColName_Qualifier_Col_Index = ColName_Qualifier_Col.index[ColName_Qualifier_Col == True].tolist()

        #The Column Name (e.g Area), no transitons and not from Qualifier
        ColName_Compound_Col_Index = [x for x in ColName_Col_Index if x not in sorted(CpdMethod_Transition_Col_Index + Qualifier_Method_Col_Index + ColName_Qualifier_Col_Index, key = int)]

        table_list = []

        #We start on row three, update the table list with the column_name
        self.RawData.iloc[2:,sorted(ColName_Col_Index, key=int)].apply(lambda x: AgilentMSRawData._get_Compound_Data(x=x,
                                                                                                                     table_list=table_list, 
                                                                                                                     ColName_Compound_Col_Index = ColName_Compound_Col_Index,
                                                                                                                     Qualifier_Method_Col_Index = Qualifier_Method_Col_Index,
                                                                                                                     ColName_Qualifier_Col_Index = ColName_Qualifier_Col_Index,
                                                                                                                     No_of_Qual_per_Transition = No_of_Qual_per_Transition)
                                                                       ,axis=1)

        if pd.DataFrame(table_list).empty:
            return(pd.DataFrame(table_list))
        else:
            return(pd.concat([CompoundName_df, pd.DataFrame(table_list) ], axis=1))
        return(pd.DataFrame()) 

    def _get_Compound_Data(x,table_list,ColName_Compound_Col_Index,Qualifier_Method_Col_Index,ColName_Qualifier_Col_Index,No_of_Qual_per_Transition):
        """Function to get the values from the chosen column_name. E.g(Area) from a given row from the raw MRM data from Agilent in Compound Table form. table_list will be updated"""

        #Get Compound row
        Compound_df = pd.DataFrame(x[x.index.isin(ColName_Compound_Col_Index)])
        Compound_df = Compound_df.T.values.tolist()
        #Append to table_list
        table_list.extend(Compound_df)

        #Get Qualifier row
        for i in range(0,No_of_Qual_per_Transition):
            #Check if there is a transition 
            #print([Qualifier_Method_Col_Index[i]])
            #print(x[ x.index.isin([Qualifier_Method_Col_Index[i]])].values.tolist()[0])
            #sys.exit(0)
            Transition = x[ x.index.isin([Qualifier_Method_Col_Index[i]])].values.tolist()[0]
            if(pd.isna(Transition)):
                break
            else:
                #When there is a transition, we need to collect a subset of ColName_Qualifier_Col_Index that correspond to this transition
                #ColName_Qualifier_Col_Index_subset = [ColName_Qualifier_Col_Index[index] for index in range(0+i,int(len(ColName_Qualifier_Col_Index)/No_of_Qual_per_Transition),No_of_Qual_per_Transition)]
                ColName_Qualifier_Col_Index_subset = [ColName_Qualifier_Col_Index[index] for index in range(0+i,int(len(ColName_Qualifier_Col_Index)),No_of_Qual_per_Transition)]
                Qualifier_df = pd.DataFrame(x[x.index.isin(ColName_Qualifier_Col_Index_subset)])
                Qualifier_df = Qualifier_df.T.values.tolist()

                #Append to table_list
                table_list.extend(Qualifier_df)

                #if i == 0:
                #    print(Transition)
                #    print(Qualifier_df)
                #    sys.exit(0)

    def _get_Compound_List(x,Compound_list):
        """Function to get the Transition Names and Qualifiers from a given row from the raw MRM data from Agilent in Compound Table form. Compound_list will be updated"""
        #x is a series
        #Remove NA if any
        s = x.dropna().copy()
        #Update the Qualifer name if there is any
        s[s.str.contains("->")] = "Qualifier (" + s[s.str.contains("->")].values + ")"
        Compound_list.extend(s.values.tolist())


    def __get_data_file_name_wide(self):
        """Function to get the list of sample names from MassHunter Raw Data in Wide Table form"""

        DataFileName_Col = self.RawData.iloc[0,:].str.contains("Sample") & self.RawData.iloc[1,:].str.contains("Data File")
        DataFileName_df = self.RawData.loc[:,DataFileName_Col].copy()

        if DataFileName_df.empty:
            if self.__logger:
                self.__logger.error('\'' + self.__filename + '\' ' +
                                    'has no column containing \"Data File\". ' + 
                                    'Please check the input file.')
            if self.__ingui:
                print('\'' + self.__filename + '\' ' +
                      'has no column containing \"Data File\". ' + 
                      'Please check the input file.',
                      flush=True)
            sys.exit(-1)

        #We standardise the name to Sample_Name
        colnames = ["Sample_Name"]
        DataFileName_df.columns = colnames

        #We remove the first and second row because the column names are given
        DataFileName_df = DataFileName_df.iloc[2:]

        #Reset the row index
        DataFileName_df = DataFileName_df.reset_index(drop=True)

        #Strip the whitespaces for each string columns
        DataFileName_df = self.remove_whiteSpaces(DataFileName_df)

        #Remove the .d extention for Agilent Files
        DataFileName_df["Sample_Name"] = DataFileName_df["Sample_Name"].replace('.d$','',regex=True)

        return DataFileName_df

    def __get_data_file_name_compound(self):
        """Function to get the list of sample names from MassHunter Raw Data in Compound Table form"""

        DataFileName_Col = self.RawData.iloc[1,:].str.contains("Data File")
        #We take the copy of the original dataframe, convert the Series output into a Dataframe
        DataFileName_df = self.RawData.loc[2,DataFileName_Col].copy().to_frame()
        
        if DataFileName_df.empty:
            if self.__logger:
                self.__logger.error('\'' + self.__filename + '\' ' +
                                    'has no column containing \"Data File\". ' + 
                                    'Please check the input file.')
            if self.__ingui:
                print('\'' + self.__filename + '\' ' +
                      'has no column containing \"Data File\". ' + 
                      'Please check the input file.',
                      flush=True)
            sys.exit(-1)

        #We standardise the name to Sample Name
        colnames = ["Sample_Name"]
        DataFileName_df.columns = colnames
        
        #Reset the row index
        DataFileName_df = DataFileName_df.reset_index(drop=True)

        #Strip the whitespaces for each string columns
        DataFileName_df = self.remove_whiteSpaces(DataFileName_df)

        #Remove the .d extention for Agilent Files

        DataFileName_df["Sample_Name"] = DataFileName_df["Sample_Name"].replace('.d$','',regex=True)

        return DataFileName_df

    def __readfile(self,filepath):
        """Function to read the input file"""

        # Check if input is blank/None
        if not filepath:
            if self.__logger:
                self.__logger.error('%s is empty. Please give an input file', str(filepath))
            if self.__ingui:
                print(str(filepath) + ' is empty. Please give an input file',flush=True)
            sys.exit(-1)

        # Check if the file exists for reading
        if not os.path.isfile(filepath):
            if self.__logger:
                self.__logger.error('%s does not exists. Please check the input file',str(filepath))
            if self.__ingui:
                print(str(filepath) + ' does not exists. Please check the input file',flush=True)
            sys.exit(-1)

        #self.RawData = pd.read_csv(filepath, header=None,low_memory=False,encoding = "ISO-8859-1")
        all_encoders_fail = True
        for encoder in ["ANSI","ISO-8859-1","utf-8"]:
            try:
                self.RawData = pd.read_csv(filepath, header=None,low_memory=False, encoding = encoder)
                all_encoders_fail = False
            except UnicodeDecodeError:
                if self.__logger:
                    self.__logger.warning('Warning: Unable to read csv file using the %s encoder',encoder)
                continue
        if all_encoders_fail:
            if self.__logger:
                self.__logger.error('Unable to read csv file with the available encoders')
            if self.__ingui:
                print('Unable to read csv file with the available encoders',flush=True)
            sys.exit(-1)

        # Check if the file has content
        if self.RawData.empty:
            if self.__logger:
                self.__logger.error('%s is an empty file. Please check the input file',str(filepath))
            if self.__ingui:
                print(str(filepath) + ' is an empty file. Please check the input file',flush=True)
            sys.exit(-1)
        
        # On the first row, fill empty cells forward 
        self.RawData.iloc[0,:] = self.RawData.iloc[0,:].fillna(method='ffill')

    def __getdataform(self,filepath):
        """Function to get the Masshunter data form"""

        if "Sample" in self.RawData.iloc[0,0]:
            self.DataForm = "WideTableForm"
        elif "Compound Method" in self.RawData.iloc[0,0]:
            self.DataForm = "CompoundTableForm"
        else:
            if self.__logger:
                self.__logger.error('%s is not in Wide Table or Compound Table form. Please check the input file',str(filepath))
            if self.__ingui:
                print(str(filepath) + ' is not in Wide Table or Compound Table form. Please check the input file',flush=True)
            sys.exit(-1)

class SciexMSRawData(MSRawData):
    """
    To describe raw data obtained from the Sciex MS machine

    Args:
        filePath (str): file path of the input MRM transition name file
        logger (object): logger object created by start_logger in MSOrganiser
        ingui (bool): if True, print analysis status to screen
    """

    def __init__(self, filepath, logger=None, ingui=True):
        MSRawData.__init__(self,filepath, ingui = ingui,logger=logger)
        self.__logger = logger
        self.__ingui = ingui
        self.__readfile(filepath)
        self.__filename = os.path.basename(filepath)
        self.VALID_COMPOUND_RESULTS = ('Area','RT','FWHM','S/N')

    def get_table(self,column_name,is_numeric=True):
        """Function to get the table from Sciex MultiQuant Raw Data

        Args:
            column_name (str): The name of the column given in the Output_Options.

        Returns:
            A data frame of sample as rows and transition names as columns with values from the chosen column name

        """
        column_name = self.AgilentColumnName_to_SciexColumnName(column_name)

        #Catch any duplicated data that prevent us from pivoting.
        self.RawData.index = np.arange(2,len(self.RawData)+2)
        duplicate_df = [g for _, g in self.RawData.groupby(['Sample Name','Component Name']) if len(g) > 1]
        if(len(duplicate_df)>0):
            duplicate_df = pd.concat(duplicate_df)
            duplicate_df_filename = os.path.splitext(os.path.basename(self.__filename))[0] + "_" + column_name + "_Duplicate.csv"
            self.__logger.error('There are duplicate %s for a given sample name and component name. See %s for more info',column_name,duplicate_df_filename)
            if self.__ingui:
                print('There are duplicate ' + column_name + ' for a given sample name and component name. See ' + duplicate_df_filename + ' for more info.' ,flush=True)
            print(duplicate_df.loc[:,['Sample Name','Component Name',column_name]].head())
            duplicate_df.to_csv(duplicate_df_filename,sep=',',index=True)
            sys.exit(-1)

        Table_df = self.RawData.pivot(index='Sample Name' ,columns='Component Name',values=column_name).reset_index()
        Table_df.columns.name = None
        Table_df.rename(columns={'Sample Name':'Sample_Name'}, inplace=True)

        return(Table_df)

    def AgilentColumnName_to_SciexColumnName(self,column_name):
        """Function to convert the column_name (Output Option) from Agilent to Sciex form

        Note:
            By default the Output Option name follows Agilent.

        Args:
            column_name (str): The name of the column given in the Output_Options.

        Returns:
            column_name (str): Name converted to Sciex form

        """

        if column_name not in self.VALID_COMPOUND_RESULTS:
            if self.__logger:
                self.__logger.error('%s is not a valid column in Sciex or not available as a valid output for this program.',column_name)
            if self.__ingui:
                print(column_name + ' is not a valid column in Sciex or not available as a valid output for this program.',flush=True)
            sys.exit(-1)

        if column_name == 'RT':
            return('Retention Time')
        elif column_name == 'FWHM':
            return('Width at 50%')
        elif column_name == 'S/N':
            return('Signal / Noise')
        else:
            return(column_name)

    def __readfile(self,filepath):
        """Function to read the input file"""

        #Check if input is blank/None
        if not filepath:
            if self.__logger:
                self.__logger.error('%s is empty. Please give an input file', str(filepath))
            if self.__ingui:
                print(str(filepath) + ' is empty. Please give an input file',flush=True)
            sys.exit(-1)

        #Check if the file exists for reading
        if not os.path.isfile(filepath):
            if self.__logger:
                self.__logger.error('%s does not exists. Please check the input file',str(filepath))
            if self.__ingui:
                print(str(filepath) + ' does not exists. Please check the input file',flush=True)
                sys.exit(-1)

        self.RawData = pd.read_csv(filepath,sep='\t',header=0,low_memory=False)

        #Check if the file has content
        if self.RawData.empty:
            if self.__logger:
                self.__logger.error('%s is an empty file. Please check the input file',str(filepath))
            if self.__ingui:
                print(str(filepath) + ' is an empty file. Please check the input file',flush=True)
            sys.exit(-1)

        #Check if 'Sample Name' and 'Component Name' is inside RawData
        if 'Sample Name' not in list(self.RawData.columns.values) or "Component Name" not in list(self.RawData.columns.values):
            if self.__logger:
                self.__logger.error('%s must have Sample Name and Component Name present in the Sciex file.',str(filepath))
            if self.__ingui:
                print(str(filepath) + ' must have Sample Name and Component Name present in the Sciex file.',flush=True)
            sys.exit(-1)

