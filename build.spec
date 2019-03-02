import gooey
import pyphen

gooey_root = os.path.dirname(gooey.__file__)
gooey_languages = Tree(os.path.join(gooey_root, 'languages'), prefix = 'gooey/languages')
gooey_images = Tree(os.path.join(gooey_root, 'images'), prefix = 'gooey/images')

pyphen_root = os.path.dirname(pyphen.__file__)
pyphen_dictionaries = Tree(os.path.join(pyphen_root, 'dictionaries'), prefix = 'pyphen/dictionaries')

cairo_toc = Tree(os.path.join(os.getcwd(),'cairo_dll'), prefix = 'cairo_dll' )
extras_toc = Tree(os.path.join(os.getcwd(),'msreport'), prefix = 'msreport' )
#print(extras_toc)

a = Analysis(['MSOrganiser.py'],
             pathex=['.\\testenv\\Scripts'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
			 binaries=[]
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
          upx=True,
          console=False,
          windowed=True,
          icon=os.path.join(gooey_root, 'images', 'program_icon.ico'),
		  version='version.txt'
		  )
