### setup.py ###
from distutils.core import setup
import os
#from setuptools import setup
import version
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
      py_modules=['add_edit'\
      'admin','amazonlookup','book','borrowers','calibre','create_qr',\
      'db_queries','extract_books','freebase_lookup','freebase-lookup-sample',\
      'gconf_config','get_orders','guiscan','lib_print','librarian',\
      'load_config','lookup_books','media_admin','messages','setup',\
      'user_admin','version',
      ],
      #packages=['librarian'],
      package_data={'librarian': ['po/*']
      }
)

