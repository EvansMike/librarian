#!/bin/env python3
### setup.py ###

from setuptools import setup
import os
from subprocess import call

# Update the version number using git data
last_commit = str(os.popen("/usr/bin/git show --format='%ci %cr' | head -n 1 | awk '{print $1}'").read())
#last_commit = last_commit.replace('_','.').replace('\n','')
commits = os.popen("git rev-list HEAD --count --after='" + last_commit + " 00:00'").read()
commits = commits.replace('\n','')
date = last_commit.replace('-','.').replace('\n','')
vf = open('src/version.py','w')
vf.write('__version__ = "' + str(date) + '.' + str(commits) + '"\n')
vf.close()

# We create the package with
# python setup.py sdist
# For an rpm
# python setup.py bdist_rpm
# To install
# python setup.py install


from distutils.core import setup
from distutils import cmd
from distutils.command.install_data import install_data as _install_data
from distutils.command.build import build as _build
#import msgfmt
import os

'''
class build_trans(cmd.Command):
    description = 'Compile .po files into .mo files'
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        po_dir = os.path.join(os.path.dirname(os.curdir), 'src/po')
        for path, names, filenames in os.walk(po_dir):
            for f in filenames:
                if f.endswith('.po'):
                    lang = f[:-3]
                    src = os.path.join(path, f)
                    dest_path = os.path.join('build', 'locale', lang, 'LC_MESSAGES')
                    dest = os.path.join(dest_path, 'librarian.mo')
                    if not os.path.exists(dest_path):
                        os.makedirs(dest_path)
                    if not os.path.exists(dest):
                        print ('Compiling %s' % src)
                        msgfmt.make(src, dest)
                    else:
                        src_mtime = os.stat(src)[8]
                        dest_mtime = os.stat(dest)[8]
                        if src_mtime > dest_mtime:
                            print ('Compiling %s' % src)
                            msgfmt.make(src, dest)
'''

class build(_build):
    #sub_commands = _build.sub_commands + [('build_trans', None)]
    def run(self):
        _build.run(self)

class install_data(_install_data):
    def run(self):
        for lang in os.listdir('build/locale/'):
            lang_dir = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
            lang_file = os.path.join('build', 'locale', lang, 'LC_MESSAGES', 'librarian.mo')
            self.data_files.append( (lang_dir, [lang_file]) )
        _install_data.run(self)

cmdclass = {
    'build': build,
    #'build_trans': build_trans,
    'install_data': install_data,
}
from src import version
print(version.__version__)
setup (
    name='librarian',
    version=version.__version__,
    description='Helps you catalogue your books using a webcam or barcode scanner to scan the ISBN barcodes',
    python_requires='>=3',
    long_description = '',
    author='Mike Evans',
    author_email='mikee@saxicola.co.uk',
    url='https://github.com/EvansMike/librarian.git',
    license='GNU General Public License',
    packages=['librarian'],
    package_dir={'librarian': 'src'},
    entry_points={
        'console_scripts': [
        'librarian = librarian.librarian:main'
        ]},
    #data_files=[("share/applications",["desktop/librarian.desktop"])],
    package_data={'librarian': ['po/*', 'ui/*','librarian.png']},
    #scripts=['bin/librarian'],
    cmdclass=cmdclass
)
