### setup.py ###
#from distutils.core import setup
import os
from setuptools import setup
import version

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()
  
setup (name='Librarian',
      version=version.__version__,
      description='Helps you catalogue your books using a webcam to scan \
      the ISBN barcodes',
      author='Mike Evans',
      author_email='mikee@saxicola.co.uk',
      url='https://github.com/EvansMike/librarian.git',
      license='GNU General Public License',
      py_modules=['librarian'],
      long_description=read('../README'),
      #packages=['librarian'],
      package_data={'librarian': ['po/*']}
)

