import sys
import os
import warnings
import gooey
import pyphen
import tinycss2

def __is_frozen():
    return getattr(sys, 'frozen', False)

#This is to fixed the error of not able to find cairo dll files
#C:\Users\bchjjs\AppData\Local\Temp
def _get_report_dir(dir_name):
    if __is_frozen():
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
        resource_dir = os.path.dirname('__file__')
    return os.path.join(resource_dir, dir_name)

os.environ['PATH'] = _get_report_dir('cairo_dll') + os.pathsep + os.environ['PATH']

#To remove the @font-face not available in Windows warning
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
    import cairocffi
    import cairosvg

gooey_root = os.path.dirname(gooey.__file__)
gooey_languages = Tree(os.path.join(gooey_root, 'languages'), prefix = 'gooey/languages')
gooey_images = Tree(os.path.join(gooey_root, 'images'), prefix = 'gooey/images')

pyphen_root = os.path.dirname(pyphen.__file__)
pyphen_dictionaries = Tree(os.path.join(pyphen_root, 'dictionaries'), prefix = 'pyphen/dictionaries')

cairocffi_root = os.path.dirname(cairocffi.__file__)

cairosvg_root = os.path.dirname(cairosvg.__file__)

tinycss2_root = os.path.dirname(tinycss2.__file__)

cairo_toc = Tree(os.path.join(os.getcwd(),'cairo_dll'), prefix = 'cairo_dll' )
extras_toc = Tree(os.path.join(os.getcwd(),'msreport'), prefix = 'msreport' )
#print(extras_toc)

a = Analysis(['MSOrganiser.py'],
             pathex=['.\\testenv\\Scripts'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             binaries=[],
             datas=[ (os.path.join(cairocffi_root, 'VERSION'), 'cairocffi'),
                     (os.path.join(cairosvg_root, 'VERSION'), 'cairosvg'),
                     (os.path.join(tinycss2_root, 'VERSION'), 'tinycss2')
			 ],
             )

pyz = PYZ(a.pure)

options = [('u', None, 'OPTION'), ('u', None, 'OPTION'), ('u', None, 'OPTION')]

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          options,
          gooey_languages, # Add them in to collected files
          gooey_images, # Same here.
		  pyphen_dictionaries,
		  cairo_toc,
		  extras_toc,
          name='MSOrganiser',
          debug=False,
          strip=None,
          console=False,
          windowed=True,
          icon=os.path.join(gooey_root, 'images', 'program_icon.ico'),
		  version='version.txt'
		  )

#Command line
#pyinstaller MSOrganiser.py --add-data "./testenv/Lib/site-packages/pyphen/dictionaries;pyphen/dictionaries" --add-data "./testenv/Lib/site-packages/gooey/images;gooey/images" --add-data "./testenv/Lib/site-packages/gooey/languages;gooey/languages" --add-data "./cairo_dll;cairo_dll" --add-data "./msreport;msreport" --add-data "./testenv/Lib/site-packages/cairocffi/VERSION;cairocffi" --add-data "./testenv/Lib/site-packages/cairosvg/VERSION;cairosvg" --add-data "./testenv/Lib/site-packages/tinycss2/VERSION;tinycss2"