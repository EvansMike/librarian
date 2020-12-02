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
DEBUG = logging.debug

class calibre:
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
    book_count = 0
    self.booklist = booklist
    conn = sqlite3.connect(self.calibre_base)
    c = conn.cursor()
    # Get author title pair.
    c.execute('select name, title from authors, books, books_authors_link \
    where  books.id=books_authors_link.book \
    AND authors.id=books_authors_link.author \
    ;')
    DEBUG(c)
    # Insert data into booklist
    for row in c:
      book_count += 1
      name = row[0]
      author = []
      author.append(name[-1]) # Last part
      author.append(", ") # Decoration
      author.append(' '.join(name[0:-1])) # All except last part adding a space between them
      author = ''.join(author) # Join all elements into a string
      self.booklist.append(['', row[0], row[1],
        '', '', '', '0', 0, 0, 'e-book'])
    return self.booklist, book_count

    
  def get_comments_by_id(self, book_id):
        '''
        Get the comments for a book.
        @param int book ID
        @return Single query result.
        '''
        self.cur.execute("SELECT * FROM comments where book = '%s';" % book_id)
        return self.cur.fetchone()

        
  def search_calibre(self, needle, booklist = []):
    ''' Search the calibre database on the parameters given.
    The DB is searched twice for title and name.  Adding an OR clause to 
    the search made te query v e r y   s l o w to execute.  Much 
    quicker to do two searches.
    '''
    import string
    mybooklist = booklist
    try:
      config = load_config.load_config()
      self.calibre_base = HOME_DIR + "/" + config.calibre_db
      #logging.info(self.calibre_base)
    except:
      return
    self.booklist = booklist
    conn = sqlite3.connect(self.calibre_base)
    c = conn.cursor()
    # Get author title pair.
    query = "select name, title from authors, books, books_authors_link \
    where  books.id=books_authors_link.book \
    AND authors.id=books_authors_link.author \
    AND title LIKE '%%%s%%';"  % (needle)
    c.execute(query)
    # Insert data into booklist
    for row in c:
        mybooklist.append(['', row[0], row[1], \
        '', '', '', '0', 0, 0, 'e-book'])
    query = "select name, title from authors, books, books_authors_link \
    where  books.id=books_authors_link.book \
    AND authors.id=books_authors_link.author \
    AND name LIKE '%%%s%%';"  % (needle)
    c.execute(query)
    # Insert data into booklist
    for row in c:
        mybooklist.append(['', row[0], row[1], \
        '', '', '', '0', 0, 0, 'e-book'])
    return mybooklist

  def insert_data2(self, booklist = []):
    ''' Use "calibredb list" command to get book list.  May make it more
    portable and avoids user having to set dabase paths.  It does seem to
    be slower however.

    Parameters:
    booklist -- The gtk.liststore into which the books will be added

    '''
    book_count = 0
    import commands
    self.booklist = booklist
    try:  book_string = commands.getoutput("calibredb list --separator=\"\t\"")
    except: # Calibre not installed perhaps.
      print (_("You don't appear to have Calibre installed, or it's not in your PATH."))
      return
    book_list = book_string.split("\n")
    for  line in book_list:
      book_count += 1
      if str((line.split("\t")[0])).isdigit():
        name = str(line.split("\t")[2])
        name = str(line.split("\t")[2]).strip().split()
        #logging.info(name)
        author = []
        author.append(name[-1]) # Last part
        author.append(", ") # Decoration
        author.append(' '.join(name[0:-1])) # All except last part adding a space between them
        author = ''.join(author) # Join all elements into a string
        self.booklist.append(['', author ,str(line.split("\t")[1]).strip() ,
        '', '', '', '0', 0, 0, 'e-book'])
    return self.booklist, book_count

if __name__ == "__main__":
  ''' Simple test harness'''
  app = calibre()
  booklist = []
  booklist = app.insert_data(booklist)
  for row in booklist:
    print (row)
