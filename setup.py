### setup.py ###
from distutils.core import setup
import os
#from setuptools import setup
from src import version
# We create the package with
# python setup.py sdist 
# For an rpm
# python setup.py bdist_rpm 
# To install
# python setup.py install

  
freedesktop_files = [
  # application icon                                                                                                          
  ("share/icons/hicolor/48x48/apps",                                                                                          
  ["desktop/keepnote.png"]),                                                                                                 
  # desktop menu entry                                                                                                        
  ("share/applications",                                                                                                      
  ["desktop/librarian.desktop"])
  ]

setup (
      name='librarian',
      version=version.__version__,
      description='Helps you catalogue your books using a webcam to scan the ISBN barcodes',
      long_description = '',
      author='Mike Evans',
      author_email='mikee@saxicola.co.uk',
      url='https://github.com/EvansMike/librarian.git',
      license='GNU General Public License',
      packages=['librarian'],
      package_dir={'librarian': 'src'},
      data_files=[("share/applications",["desktop/librarian.desktop"])],
      package_data={'librarian': ['po/*', 'ui/*','librarian.jpg']},
      scripts=['bin/librarian']
)

