#!/bin/env python
'''
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
  MA 02110-1301, USA.
'''
'''
This just queries the calibre sqlite db file directly.
It may be better to use the "calibredb list" command, this would avoid
needing the set up paths to file etc.
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

logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s:%(message)s', level=logging.INFO)
#logging.disable(logging.INFO)

class calibre_import:
  ''' Do the import and insert the data into the list.
  Called from librarian.py

  '''
  def __init__(self):

    pass


  def insert_data(self, booklist = []):
    ''' Directly use the database to get book list.

    Parameters:
    booklist -- The gtk.liststore into which the books will be added

    '''
    # Read the config file
    try:
      config = load_config.load_config()
      self.calibre_base = HOME_DIR + "/" + config.calibre_db
      logging.info(self.calibre_base)
    except:
      return
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
        '', '', '', '0', 0, 0, 'e-book'])

    return self.booklist

  def insert_data2(self, booklist = []):
    ''' Use "calibredb list" command to get book list.  May make it more
    portable and avoids user having to set dabase paths.  It does seem to
    be slower however.

    Parameters:
    booklist -- The gtk.liststore into which the books will be added

    '''
    import commands
    self.booklist = booklist
    try:  book_string = commands.getoutput("calibredb list --separator=\"\t\"")
    except: # Calibre not installed perhaps.
      print (_("You don't appear to have Calibre installed, or it's not in your PATH."))
      return
    book_list = book_string.split("\n")
    #print book_list
    for  line in book_list:
      if str((line.split("\t")[0])).isdigit():
        #print line.split("\t")[2],  line.split("\t")[1]
        self.booklist.append(['', str(line.split("\t")[1]).strip(),str(line.split("\t")[2]).strip() ,
        '', '', '', '0', 0, 0, 'e-book'])
    return self.booklist

if __name__ == "__main__":
  app = calibre_import()
  booklist = []
  booklist = app.insert_data2(booklist)
  #quit()
  for row in booklist:
    print row

