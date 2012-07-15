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
dialog. (NB Write setup dialog.)  Perhaps XML too?
See here for convertion script
First do:
mysqldump -p --compatible=ansi  books > books
http://www.jbip.net/content/how-convert-mysql-sqlite
Correct syntax to create authors table in sqlit3
CREATE TABLE "authors" ( "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,"name" text NOT NULL);

The query differences between MySQL and sqlite3 are often minor but enough
to warrant the two classes.  There may be better ways to this beside 
having two classes, maybe a string write function that builds the query 
string for each type.  Something to think about.
'''


import sys,os
import load_config as config
#import gconf_config as config
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

config = config.load_config() # For file based config

try:
  db_user = config.db_user
  db_pass = config.db_pass
  db_base = config.db_base
  db_host = config.db_host
  db_lite = config.lite_db
  config.lite_base = "books-out.sqlite.db"
except: quit()


########################################################################
class sqlite:
  ''' 
  Database queries for sqlite.

  '''  
  import sqlite3
  
  def __init__(self):
    self.con = self.sqlite3.connect(db_lite)
    self.con.row_factory = self.sqlite3.Row
    self.cur = self.con.cursor()
    logging.info("This connection is using sqlite3")
    
    
  def get_all_books(self):
    ''' 
    An example of how to call the code from mysql from here.  This is
    to avoid duplication code where the query code is identical.  For 
    trivial selects this will the case, in other cases the sqlite3 code 
    will differ slightly.
    return mysql().get_all_books()
  
    '''
    self.cur.execute("SELECT * FROM books WHERE copies > 0 order by author;")
    return self.cur.fetchall()
  
  def get_borrowed_books(self):
    return mysql().get_borrowed_books()
    
  def get_borrows(self, bid, copies):
    ''' Differing syntax for sqlite'''
    self.cur.execute("SELECT * FROM borrows where book = ? AND i_date IS NULL \
        AND o_date IS NOT NULL LIMIT ?;", (bid,copies))
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
    self.cur.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", \
               ('%%%s%%' % search_string, '%%%s%%' % search_string))
    return  self.cur.fetchall()  
  
  def insert_book_complete(self,title,authors, isbn, abstract,year,publisher,
              city,mtype, add_date):
    ''' 
    Insert a books' complete details in to the DB.
    
    ''' 
    return self.cur.execute("INSERT INTO books(title, author, isbn,abstract, \
      year, publisher, city, copies, mtype, add_date) \
      VALUES(?, ?, ?,?,?,?,?,?,?,?);", \
        (title, authors, isbn, abstract,year,publisher,city, 1, mtype, add_date))
         
  def insert_unique_author(self, authors):
    '''
    Insert author(s) ensuring uniqueness.
    
    '''
    self.cur.execute("INSERT OR IGNORE INTO authors(name) values(?);", authors)
     
  def get_by_id(self, book_id):
    ''' 
    Search for book on its ID.  NB. This is NOT its ISBN
    NB The normal parameter substitution doesn't seem to work here  getting:
    Incorrect number of bindings supplied. The current statement uses 1, and there are N supplied.
    errors if the number has more than one digit.  N = number of digits. 
    '''
    self.cur.execute("SELECT * FROM  books where id = '%s';" % book_id)
    return self.cur.fetchall()
    
    
    
#######################################################################    
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
    
    def get_by_id(self, book_id):
      ''' Search for book on its ID.  NB. This is NOT its ISBN
      
      '''
      return self.cur.execute ("SELECT * FROM  books where id = %s;",book_id)
  
  def insert_unique_author(self, authors):
    '''
    Insert author(s) ensuring uniqueness.
    
    '''
    return self.cur.execute("INSERT IGNORE INTO authors(name) values(%s);", authors) 
    
     
    def insert_book_complete(self,title,authors, isbn, abstract,year,publisher,
                city,mtype, add_date):
      ''' Insert a books' complete details in to the DB.
      
      ''' 
      return self.cur.execute("INSERT INTO books(title, author, isbn,abstract, \
        year, publisher, city, copies, mtype, add_date) \
        VALUES(%s, %s, %s,%s,%s,%s,%s,%s,%s,%s);", \
          (title, authors, isbn, abstract,year,publisher,city, 1, mtype, add_date))
         
    def insert_unique_author(self, authors):
      self.cur.execute("INSERT IGNORE INTO authors(name) values(%s);", [authors])
      
########################################################################      
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
  mybooks = lite.get_all_books()
  #mybooks = my.search_books("cat")
  for book in mybooks:
    print book
  #my.get_borrowed_books()
  
