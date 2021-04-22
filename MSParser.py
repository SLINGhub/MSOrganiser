import json
from gooey import Gooey
from gooey import GooeyParser
import os
import sys

#This needs to be be right at the top with parse_MSOrganiser_args
@Gooey(program_name='MS Data Organiser',
       program_description='Create summary tables from MassHunter csv files',
       advanced=True,
       #tabbed_groups=True,
       default_size=(710,680),
       #menu=[{
       # 'name': 'File',
       # 'items': [{
       #         'type': 'AboutDialog',
       #         'menuTitle': 'About',
       #         'name': 'Gooey Layout Demo',
       #         'description': 'An example of Gooey\'s layout flexibility',
       #         'version': '1.2.1',
       #         'copyright': '2018',
       #         'website': 'https://github.com/chriskiehl/Gooey',
       #         'developer': 'http://chriskiehl.com/',
       #         'license': 'MIT'
       #     }]
       # }]
       )
def parse_MSOrganiser_args(args_json_file_path=""):
    """Function to start the Gooey Interface, record the stored arguments and write them to a json file
    
    Args:
        args_json_file_path (str): The file path to where the json file be created. Default is where the MSOrganiser.exe file is

    Returns:
        stored_args (dict): A dictionary storing the input parameters.

    """
    #Create default json file is located in the same directory as the executable file
    if not args_json_file_path:
        args_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),"MSOrganiser-args.json")
    else:
        args_file =  args_json_file_path

    #Load the parameters from json file or create an empty dictionary
    stored_args = _load_args_from_json(args_file=args_file)

    #Create a Gooey Parser from the stored args
    parser = _create_Gooey_Parser(stored_args)

    #Update the args with the most recent parameter settings
    args = parser.parse_args()
    stored_args = vars(args)

    #Verify that the arguments are valid before saving/using them

    #Check if MS_Files option is not empty
    if not stored_args['MS_Files']:
        print("Please key in at least one input MS file",flush=True)
        sys.exit(-1)

    #Check if Output_Directory option is not empty
    if not stored_args['Output_Directory']:
        print("Please key in at least one output directory",flush=True)
        sys.exit(-1)

    #Check if Output_Options is selected
    if not stored_args['Output_Options']:
        print("Please key in at least one result to output",flush=True)
        sys.exit(-1)

    #Check if Concatenate is selected
    if not stored_args['Concatenate']:
        print("Please key in at least one option",flush=True)
        sys.exit(-1)

    #Store the values of the arguments so we have them next time we run
    _save_args_to_json(args_file,stored_args)

    #Convert the string in Transpose Results to boolean
    if stored_args['Transpose_Results'] == 'True':
        stored_args['Transpose_Results'] = True
    else:
        stored_args['Transpose_Results'] = False

    #Convert the string in Allow Mulitple ISTD to boolean
    if stored_args['Allow_Multiple_ISTD'] == 'True':
        stored_args['Allow_Multiple_ISTD'] = True
    else:
        stored_args['Allow_Multiple_ISTD'] = False

    #Convert the string in Long Table to boolean
    if stored_args['Long_Table'] == 'True':
        stored_args['Long_Table'] = True
    else:
        stored_args['Long_Table'] = False

    #Convert the string in Long Table to boolean
    if stored_args['Long_Table_Annot'] == 'True':
        stored_args['Long_Table_Annot'] = True
    else:
        stored_args['Long_Table_Annot'] = False

    return stored_args

def _load_args_from_json(args_file):
    #Declare an empty dictionary
    stored_args = {}

    # Read in the prior arguments as a dictionary
    if os.path.isfile(args_file):
        with open(args_file) as data_file:
            stored_args = json.load(data_file)

    return stored_args

def _save_args_to_json(args_file,stored_args):
    #Store the values of the arguments so we have them next time we run

    #When outputing the json file, the list needs to combine into one string
    #separated by ";", to output as {File1};{File2}, not [{File1},{File2}]
    stored_args['MS_Files'] = ';'.join(stored_args['MS_Files'])

    #By default json file will be the same directory as the exe file
    try:
        with open(args_file, 'w') as data_file:
            json.dump(stored_args, data_file)
    except Exception as e:
        print("Warning: Unable to save input settings in " + args_file + " due to this error message",flush=True)
        print(e,flush=True)

    #We now convert it back into a list
    stored_args['MS_Files'] = list(stored_args['MS_Files'].split(";"))

def _create_Gooey_Parser(stored_args):
    """Function to create the Gooey Interface, record the stored arguments into the gui interface
    
    Args:
        stored_args (dict): A dictionary storing the input parameters.

    Returns:
        parser (object): A dictionary storing the input parameters.

    """
    parser = GooeyParser()

    if not stored_args.get('MS_FileType'):
        MS_FileType = 'Agilent Wide Table in csv'
    else:
        MS_FileType = stored_args.get('MS_FileType')

    if not stored_args.get('Output_Format'):
        Output_Format = 'Excel'
    else:
        Output_Format = stored_args.get('Output_Format')

    if not stored_args.get('Concatenate'):
        Concatenate = 'No Concatenate'
    else:
        Concatenate = stored_args.get('Concatenate')

    if not stored_args.get('Transpose_Results'):
        Transpose_Results = 'False'
    else:
        Transpose_Results = stored_args.get('Transpose_Results')

    if not stored_args.get('Allow_Multiple_ISTD'):
        Allow_Multiple_ISTD = 'False'
    else:
        Allow_Multiple_ISTD = stored_args.get('Allow_Multiple_ISTD')

    if not stored_args.get('Long_Table'):
        Long_Table = 'False'
    else:
        Long_Table = stored_args.get('Long_Table')

    if not stored_args.get('Long_Table_Annot'):
        Long_Table_Annot = 'False'
    else:
        Long_Table_Annot = stored_args.get('Long_Table_Annot')

    required_args = parser.add_argument_group("Required Input", gooey_options={'columns': 1 } )
    analysis_args = parser.add_argument_group("Data Extraction", gooey_options={'columns': 1 } )
    output_args = parser.add_argument_group("Output Settings", gooey_options={ 'columns': 2 } )
    optional_args = parser.add_argument_group("Optional Settings", gooey_options={'columns': 1 } )

    #Required Arguments 
    #nargs="+" is needed to turn multiple input into a list.
    required_args.add_argument('--MS_Files',
                               required=True,
                               nargs='+',
                               #help="Input the MS raw files.\nData File is a required column for MassHunter\nSample Name and Component Name are required columns for Sciex", 
                               help="Input the MS raw files.\nData File is a required column for MassHunter", 
                               widget='MultiFileChooser', 
                               default=stored_args.get('MS_Files'))
    required_args.add_argument('--MS_FileType',
                               required=True,
                               choices=['Agilent Wide Table in csv',
                                        'Agilent Compound Table in csv',
                                        'Multiquant Long Table in txt'], 
                               help='Input the MS raw file type', default=MS_FileType)
    required_args.add_argument('--Output_Directory',
                               required=True,
                               action='store', 
                               help="Output directory to save summary report.", 
                               widget="DirChooser", default=stored_args.get('Output_Directory'))
    #required_args.add_argument('--Output_Options', choices=['Area','normArea by ISTD','normConc by ISTD','RT','FWHM','S/N','Symmetry','Precursor Ion','Product Ion'], nargs="+", help='Select specific information to output', widget="Listbox", default=stored_args.get('Output_Options'))

    #Analysis Arguments
    analysis_args.add_argument('--Output_Options', choices=['Area','normArea by ISTD','normConc by ISTD','RT','FWHM','S/N','Symmetry','Precursor Ion','Product Ion'], nargs="+", help='Select specific information to output', widget="Listbox", default=stored_args.get('Output_Options'))
    #analysis_args.add_argument('--Output_Options', choices=['Area','RT','FWHM','S/N','Symmetry','Precursor Ion','Product Ion'], nargs="+", help='Select specific information to output', widget="Listbox", default=stored_args.get('Output_Options'))
    analysis_args.add_argument('--Annot_File', action='store', help='Input the annotation excel macro file required for normalisation and concentration calculation', widget="FileChooser",default=stored_args.get('Annot_File'))

    #Output Arguments 
    output_args.add_argument('--Output_Format', choices=['Excel','csv'], 
                             help='Select specific file type to output csv form will give multiple sheets', 
                             default=Output_Format)
    output_args.add_argument('--Concatenate', choices=['No Concatenate','Concatenate along Sample Name (rows)','Concatenate along Transition Name (columns)'], 
                             help='Concatenate multiple input files into one output file. Note that this is done after data cleaning and calculation for each input file', 
                             default=Concatenate)
    output_args.add_argument('--Transpose_Results', choices=['True','False'], 
                             help='Set this option to True to let the samples to be the columns instead of the Transition_Name',
                             default=Transpose_Results)
    output_args.add_argument('--Allow_Multiple_ISTD', choices=['True','False'], 
                             help='Set this option to True to normalised using multiple ISTD',
                             default=Allow_Multiple_ISTD)
    output_args.add_argument('--Long_Table', choices=['True','False'], 
                             help='Set this option to True to output the data in Long Table',
                             default=Long_Table)
    output_args.add_argument('--Long_Table_Annot', choices=['True','False'], 
                             help='Set this option to True to add ISTD, Sample Type and Concentration Unit ' + 
                                  'from Annot_File to the Long Table output',
                             default=Long_Table_Annot)
    
    #Optional Arguments 
    optional_args.add_argument('--Testing', action='store_true', help='Testing mode will generate more output tables.')

    return parser