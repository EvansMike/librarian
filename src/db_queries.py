#!/bin/env python
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
'''
Move all the db queries here.  There will be equivalent queries for both
MySQL and SQLite so the user can choose either storage type from the setup
dialog. (NB Write setup dialog.)
'''


import sys,os
import load_config
import gconf_config
import locale
import gettext
import logging

locale.setlocale(locale.LC_ALL, '')
APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

#logger = logging.getLogger("librarian")
logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s:%(message)s', level=logging.DEBUG)
#logging.disable(logging.INFO)

# Get system platform
plat = sys.platform

# Read the config file

#config = load_config.load_config() # For file based config
config = gconf_config.gconf_config() # For gconf config.
try:
  db_user = config.db_user
  db_pass = config.db_pass
  db_base = config.db_base
  db_host = config.db_host
except: quit()



class sqlite:
  ''' 
  Database queries for sqlite.

  '''  
  def __init__(self):
    pass
  
  pass
  

class mysql:
  '''
  Database queries for MySQL
  
  '''
  import MySQLdb
  import MySQLdb.cursors
  def __init__(self):
    db = self.MySQLdb.connect(host=db_host, db=db_base,  passwd = db_pass)
    self.cur = db.cursor(self.MySQLdb.cursors.DictCursor)
    
    
  def get_all_books(self):
    ''' 
    Get all of the books and return a list.
    
    '''
    command = "SELECT * FROM books WHERE copies > 0 order by author;"
    self.cur.execute(command)
    return  self.cur.fetchall()
    
  def get_borrowed_books(self):
    ''' 
    Get a list of books that have been borrowed.
    
    '''
    command = "select * from books, borrows where books.id = borrows.book \
                      and i_date is null;"
    self.cur.execute(command)
    return self.cur.fetchall()
    
  def get_borrows(self, bid, copies):
    '''
    Get the borrows for a specific book.
    
    '''
    self.cur.execute("SELECT * FROM borrows where book = %s AND i_date IS NULL \
        AND o_date IS NOT NULL LIMIT %s;", [bid,copies])
    return self.cur.fetchall()
    
  def get_all_borrowers(self):
    '''
    Get all the borrowers in the database.
    
    '''
    self.cur.execute ("SELECT * FROM  borrowers;")
    return self.cur.fetchall()
    
  def search_books(self, search_string):
    ''' 
    Get books based on author and title search.
    
    '''
    self.cur.execute("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s", \
        [('%%%s%%' % search_string), ('%%%s%%' % search_string)])
    return  self.cur.fetchall()
    
    
class calibre:
  import calibre
  def __init__(self):
    self.e_books = self.calibre.calibre()
    
  def get_all_calibre(self):
    return self.e_books
  

# Test harness starts here
if __name__ == "__main__":
  lite = sqlite()
  my = mysql()
  cali = calibre()
  # Check connection and booklist getting.
  mybooks = my.get_all_books()
  #mybooks = my.search_books("cat")
  for book in mybooks:
    print book
  my.get_borrowed_books()
  
