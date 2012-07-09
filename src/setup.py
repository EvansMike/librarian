### setup.py ###
#from distutils.core import setup
from setuptools import setup

setup (name='Librarian',
      version='2012070901',
      description='EventCal generates HTML calendars in day-, week- and month-views',
      author='Mike Evans',
      author_email='omouse@gmail.com',
      url='http://code.google.com/p/eventcal/',
      license='MIT',
      py_modules=['librarian'],
      #packages=['librarian'],
      package_data={'librarian': ['po/*']}
)

