import sys
import os
import warnings
from jinja2 import Environment, FileSystemLoader

def is_frozen():
    return getattr(sys, 'frozen', False)

#This is to fixed the error of not able to find cairo dll files
#C:\Users\bchjjs\AppData\Local\Temp
def get_report_dir(dir_name):
    if is_frozen():
        # MEIPASS explanation:
        # https://pythonhosted.org/PyInstaller/#run-time-operation
        basedir = getattr(sys, '_MEIPASS', None)
        if not basedir:
            basedir = os.path.dirname(sys.executable)
        resource_dir = os.path.join(basedir, dir_name)
        if not os.path.isdir(resource_dir):
            raise IOError(
                ("Cannot locate MSreport resources. It seems that the program was frozen, "
                 "but resource files were not copied into directory of the executable "
                 "file. Please copy `msreport` folders into `{}{}` directory.".format(resource_dir, os.sep)))
        return resource_dir
    else:
        resource_dir = os.path.dirname(__file__)
    return os.path.join(resource_dir, dir_name)

#dllspath = get_report_dir('cairo_dll')
os.environ['PATH'] = get_report_dir('cairo_dll') + os.pathsep + os.environ['PATH']

#To remove the @font-face not available in Windows warning
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
    from weasyprint import HTML

class MSDataReport:
    """To describe the general setup for Data Reporting"""
    def __init__(self, output_directory, input_file_path, logger=None, ingui=True):
        output_filename = os.path.splitext(os.path.basename(input_file_path))[0]
        self.output_file_path = os.path.join(output_directory , output_filename)
        self.logger = logger
        self.ingui = ingui


class MSDataReport_PDF(MSDataReport):
    """To describe the general setup for Data Reporting in pdf"""
    def __init__(self, output_directory, input_file_path, logger=None, ingui=True):
        #Initialise the same way as MSDataReport
        super().__init__(output_directory, input_file_path, logger, ingui)
        #But change the output file path
        self.output_file_path = self.output_file_path +  "_Report.pdf"

        #These variables are unique to MSDataReport_PDF
        self.__pdf_pages = []
        report_dir = get_report_dir('msreport')
        env = Environment(loader=FileSystemLoader(report_dir))
        self.__ISTD_report_template = env.get_template("ISTD_Report.html")
        self.__Parameters_report_template = env.get_template("Parameters_Report.html")
        self.__stylesheet_file = os.path.join(report_dir,"typography.css")

    def is_frozen():
        return getattr(sys, 'frozen', False)

    def create_parameters_report(self,Parameters_df):
        #Generate the parameters report
        if not Parameters_df.empty:
            template_vars = {"title": "Parameters", "Parameter_Report": Parameters_df.to_html(index=False)}
            html_string = self.__Parameters_report_template.render(template_vars)
            html = HTML(string=html_string)
            self.__pdf_pages.append(html.render(stylesheets=[self.__stylesheet_file]))
        else:
            if self.logger:
                self.logger.warning('Parameters_df is empty.')
            if self.ingui:
                print('Parameters_df is empty.',flush=True)

    def create_ISTD_report(self,ISTD_Report):
        #Generate the ISTD normalisation report
        if not ISTD_Report.empty:
            template_vars = {"title": "ISTD_Normalisation_Report", "ISTD_Report": ISTD_Report.to_html()}
            html_string = self.__ISTD_report_template.render(template_vars)
            html = HTML(string=html_string)
            self.__pdf_pages.append(html.render(stylesheets=[self.__stylesheet_file]))

    def output_to_PDF(self):
        #Output the ISTD report for each file
        val = []
        for doc in self.__pdf_pages:
            for p in doc.pages:
                val.append(p)
        #print(self.__pdf_pages[0].copy(val))
        pdf_file = self.__pdf_pages[0].copy(val).write_pdf(self.output_file_path) # use metadata of first pdf







