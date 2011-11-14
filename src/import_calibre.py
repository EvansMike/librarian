#!/bin/env python
'''
Import e-books from calibre database avoiding duplicates
Run with calibre-debug -e import_calibre.py
'''
import sys, os
import sqlite3
import load_config
import logging
import locale
import gettext

plat = sys.platform

#Platform dependent stuff
if plat == "darwin":
  pass # plat = "mac"
elif plat== "win32":
  pass #plat = "windows"
elif plat == "linux2":
  HOME_DIR = os.getenv('HOME')
  pass #linuxStuff()

locale.setlocale(locale.LC_ALL, '')
APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

logger = logging.getLogger("librarian")
logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s:%(message)s', level=logging.DEBUG)


class calibre_import:
  ''' Do the import and insert the data into the list.
  Called from librarian.py

  '''
  def __init__(self):
    # Read the config file
    config = load_config.load_config()
    self.calibre_base = HOME_DIR + "/" + config.calibre_db
    logging.info(self.calibre_base)
    pass

  def read_db(self):

    pass

  def insert_data(self, booklist):
    '''Insert the data into a booklist and return the list.

    Parameters:
    booklist -- a GTKListStore object.

    '''

    conn = sqlite3.connect(self.calibre_base)
    c = conn.cursor()
    ''' Example safe query
    t = (symbol,)
    c.execute('select * from books where symbol=?', t)
    '''
    '''
    c.execute('select name, title from authors, books, books_authors_link \
    where books_authors_link.book=books_authors_link.author;')
    '''
    for row in c:
      print row


if __name__ == "__main__":
  app = calibre_import()
  app.insert_data(None)
