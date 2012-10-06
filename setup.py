### setup.py ###
from distutils.core import setup
import os
#from setuptools import setup
from src import version
# We create the package with
# python setup.py sdist 

  
setup (name='Librarian',
      version=version.__version__,
      description='Helps you catalogue your books using a webcam to scan \
      the ISBN barcodes',
      author='Mike Evans',
      author_email='mikee@saxicola.co.uk',
      url='https://github.com/EvansMike/librarian.git',
      license='GNU General Public License',
      packages=['src'],
      package_data={'src': ['po/*']
      }
)

