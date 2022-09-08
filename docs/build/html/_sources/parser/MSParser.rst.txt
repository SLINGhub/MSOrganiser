MSParser
=========

.. automodule:: MSParser
    :members:
    :undoc-members:
    :noindex:

.. function:: parse_MSOrganiser_args(args_json_file_path="")

   Function to start the Gooey Interface, record the stored arguments and write them to a json file

   :param args_json_file_path: The file path to where the json file be created. Default is where the MSOrganiser.exe file is
   :type args_json_file_path: str
   :rtype: *stored_args (dict)* - A dictionary storing the input parameters.
