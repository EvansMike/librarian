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
  HOME_DIR = os.getenv('HOME')
elif plat == "linux2":
  HOME_DIR = os.getenv('HOME')
  pass

locale.setlocale(locale.LC_ALL, '')
APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

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

  def insert_data(self, booklist = []):
    self.booklist = booklist
    conn = sqlite3.connect(self.calibre_base)
    c = conn.cursor()
    # Get author title pair.
    c.execute('select name, title from authors, books, books_authors_link \
    where  books.id=books_authors_link.author \
    AND authors.id=books_authors_link.book \
    ;')
    # Insert data into booklist
    for row in c:
      self.booklist.append(['', row[0], row[1],
        '', '', '', '0',
        0, 0])

    return self.booklist

if __name__ == "__main__":
  app = calibre_import()
  booklist = []
  booklist = app.insert_data(booklist)
  for row in booklist:
    print row

