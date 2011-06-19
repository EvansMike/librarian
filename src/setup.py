#!/bin/env python
### setup.py ###
# SEE: http://www.linux.com/archive/feed/118439
#FIX ME OR NOT

from distutils.core import setup

setup (name='Librarian',
version='0.0.1',
description='Tracks your book collection',
author='Mike Evans',
author_email='mikee@saxicola.co.uk',
url='http://millstreamcomputing.co.uk',
license='GPL',
packages=['librarian'],
package_dir={'librarian': '.'},
package_data={'librarian': ['po/*']},
data_files=[('share/eventcal', ['test.html'])]
)
