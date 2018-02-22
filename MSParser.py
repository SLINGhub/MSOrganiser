import json
from gooey import Gooey
from gooey import GooeyParser
import os
import sys

#This needs to be be right at the top
@Gooey(program_name='MS Data Organiser',
       program_description='Create summary tables from MassHunter csv files',
       advanced=True,
       default_size=(610,710))

def parse_MSOrganiser_args(args_json_file_path=""):
    """ Use ArgParser to build up the arguments we will use in our script"""

    """ Save the arguments in a default json file so that we can retrieve them every time we run the script."""
    #Create default json file is located in the same directory as the executable file
    if not args_json_file_path:
        args_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),"MSOrganiser-args.json")
    else:
        args_file =  args_json_file_path

    #Load the parameters from json file or create an empty dictionary
    stored_args = __load_args_from_json(args_file)

    #Create a Gooey Parser from the stored args
    parser = create_Gooey_Parser(stored_args)

    #Update the args with the most recent parameter settings
    args = parser.parse_args()
    stored_args = vars(args)

    #Verify that the arguments are valid before saving/using them
    #Check if Output_Options is selected
    if not stored_args['Output_Options']:
        print("Please key in at least one result to output",flush=True)
        sys.exit(-1)

    #Store the values of the arguments so we have them next time we run
    __save_args_to_json(args_file,stored_args)

    #Convert the string in Transpose Results to boolean
    if stored_args['Transpose_Results'] == 'True':
        stored_args['Transpose_Results'] = True
    else:
        stored_args['Transpose_Results'] = False

    return stored_args

def __load_args_from_json(args_file):

    #Declare an empty dictionary
    stored_args = {}

    # Read in the prior arguments as a dictionary
    if os.path.isfile(args_file):
        with open(args_file) as data_file:
            stored_args = json.load(data_file)

    return stored_args

def __save_args_to_json(args_file,stored_args):
    #Store the values of the arguments so we have them next time we run

    #By default json file will be the same directory as the exe file
    try:
        with open(args_file, 'w') as data_file:
            json.dump(stored_args, data_file)
    except Exception as e:
        print("Warning: Unable to save input settings in " + args_file + " due to this error message",flush=True)
        print(e,flush=True)


def create_Gooey_Parser(stored_args):
    parser = GooeyParser()

    if not stored_args.get('Output_Format'):
        Output_Format = 'Excel'
    else:
        Output_Format = stored_args.get('Output_Format')

    if not stored_args.get('Transpose_Results'):
        Transpose_Results = 'False'
    else:
        Transpose_Results = stored_args.get('Transpose_Results')

    required_args = parser.add_argument_group("Required Input", gooey_options={'columns': 1 } )
    analysis_args = parser.add_argument_group("For Normalisation", gooey_options={'columns': 1 } )
    output_args = parser.add_argument_group("Output Settings", gooey_options={ 'columns': 2 } )
    optional_args = parser.add_argument_group(gooey_options={'show_border': True, 'columns': 2 } )

    #Required Arguments 
    #required_args.add_argument('--MS_Files',action='store',nargs="+",help="Input the MS raw files.\nData File is a required column for MassHunter\nSample Name and Component Name are required columns for Sciex", 
    #                           widget="MultiFileChooser", 
    #                           default=stored_args.get('MS_Files'))
    required_args.add_argument('--MS_Files',help="Input the MS raw files.\nData File is a required column for MassHunter\nSample Name and Component Name are required columns for Sciex", 
                               widget='MultiFileChooser', 
                               default=stored_args.get('MS_Files'))
    #required_args.add_argument('MS_Files_Type',action='store',nargs="+",help="Input the MS raw files.\nData File is a required column for MassHunter", widget="MultiFileChooser",default=stored_args.get('MS_Files'))
    required_args.add_argument('--Output_Directory',action='store', help="Output directory to save summary report.", 
                               widget="DirChooser", default=stored_args.get('Output_Directory'))
    required_args.add_argument('--Output_Options', choices=['Area','normArea by ISTD','normConc by ISTD','RT','FWHM','S/N','Precursor Ion','Product Ion'], nargs="+", help='Select specific information to output', widget="Listbox", default=stored_args.get('Output_Options'))

    #Analysis Arguments
    analysis_args.add_argument('--ISTD_Map', action='store', help='Input the ISTD map file. Required for normalisation', widget="FileChooser",default=stored_args.get('ISTD_Map'))

    #Output Arguments 
    output_args.add_argument('--Output_Format', choices=['Excel'], help='Select specific file type to output', default=Output_Format)
    output_args.add_argument('--Transpose_Results', choices=['True','False'], help='Set this option to True to let the samples be the columns instead of the Transition_Names',default=Transpose_Results)
    #output_args.add_argument('--Transpose_Results', action='store_false', help='Select this option to let the samples be the columns',default=defaults.get('Transpose_Results'))
    
    #Optional Arguments 
    optional_args.add_argument('--Testing', action='store_true', help='Testing mode will generate more output tables.')

    return parser
