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
NOTE: Script on the site doesn't quite work, see my comments there.

The query differences between MySQL and sqlite3 are often minor but enough
to warrant the two classes.  There may be better ways to this beside 
having two classes, maybe a string write function that builds the query 
string for each type.  Something to think about.

TODO: If the sqlit3 db file doesn't exist we should create a db with it's schema.
'''


import sys,os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))
import load_config as config
import locale
import gettext
import logging

locale.setlocale(locale.LC_ALL, '')
APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

#logger = logging.getLogger("librarian")
logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s', level=logging.DEBUG)
#logging.disable(logging.INFO)

# Get system platform
plat = sys.platform

# Get the real location of this script
iamhere = os.path.dirname( os.path.realpath( __file__ ) )
#print "I am here",iamhere

# Read the config file
config = config.load_config() # For file based config

try:
  db_user = config.db_user
  db_pass = config.db_pass
  db_base = config.db_base
  db_host = config.db_host
  db_lite = config.lite_db
  use = config.use # What DB type to use
except: 
  print "\nThere There is some error in the config file.\nCannot continue!\n\n "
  quit()
print "Module ",use


########################################################################
class sqlite:
  ''' 
  Database queries for sqlite.

  '''  
  import sqlite3
  
  def __init__(self):
    if not os.path.exists(db_lite): #Create the db with schema
      self.create_db()

    self.con = self.sqlite3.connect(db_lite)
    self.con.row_factory = self.sqlite3.Row
    self.cur = self.con.cursor()
    logging.info("This connection is using sqlite3")
    
  def __del__(self):
    try:
      self.con.commit() # Prpbably not neede with close.
      self.con.close()
    except: pass
    
  def create_db(self):
    '''Create the DB with schema.
    The query is the schema file.  We shouldn't get this far with a
    missing config file.  The user is prompted to edit one.   The lite_db
    name shouls be left alone.
    
    schema created with:
    sqlite books.db, derived from the MySQL DB
    .output books.db.schema
    .schema
    .quit
    
    '''
    f = open("books.db.schema", "r")
    for line in f:
      self.cur.execute(line)
    pass
    
    
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
  
  def get_book_count_by_isbn(self, bar):
    self.cur.execute("SELECT COUNT(*) as count FROM books WHERE isbn = '%s';" % bar)
    return  self.cur.fetchone()[0]
  
  def get_qrcode_count(self, isbn):
    self.cur.execute("SELECT COUNT(*) as count FROM qrcodes WHERE caption = '%s';" % "ISBN: "+str(self.abook.id))
    return self.cur.fetchone()[0] 
    
  def get_borrowed_books(self):
    ''' 
    Get a list of books that have been borrowed.
    
    '''
    command = "select * from books, borrows where books.id = borrows.book \
                      and i_date is null;"
    self.cur.execute(command)
    return self.cur.fetchall()
    #return mysql().get_borrowed_books()
  
  def get_borrowed_book_by_id(self, bid):
    self.cur.execute("select * FROM  borrows where i_date is null and borrows.book='%s'" % bid)
    return self.cur.fetchone()
  
  def get_book_borrower_by_book_id(self,bid):
    self.cur.execute("select borrowers.name, borrows.o_date FROM  borrows, borrowers \
      where i_date is null and borrows.book='%s' \
      AND borrows.borrower=borrowers.id;" % bid)
    return self.cur.fetchone()
    
    
  def get_borrowers_borrowed_books(self):
    self.cur.execute("SELECT title, author, name, o_date FROM books, \
        borrows, borrowers WHERE books.id = borrows.book \
        AND borrows.borrower=borrowers.id AND i_date is null \
        ORDER BY o_date;")
    return self.cur.fetchall() 
    
    
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
               ('%% %s %%' % search_string, '%% %s %%' % search_string))
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
    self.con.commit()
         
  def insert_unique_author(self, authors):
    '''
    Insert author(s) ensuring uniqueness.
    
    '''
    self.cur.execute("INSERT OR IGNORE INTO authors(name) values('%s');" % authors)
    self.con.commit()
     
  def get_by_id(self, book_id):
    ''' 
    Search for book on its ID.  NB. This is NOT its ISBN
    NB The normal parameter substitution doesn't seem to work here  getting:
    Incorrect number of bindings supplied. The current statement uses 1, and there are N supplied.
    errors if the number has more than one digit.  N = number of digits. 
    '''
    self.cur.execute("SELECT * FROM  books where id = '%s';" % book_id)
    return self.cur.fetchall()
  
  def get_one_borrower(self,bid):
    logging.info(bid)
    self.cur.execute("SELECT * from borrowers where id = '%s';" % bid)
    return self.cur.fetchone() 
    
    
  def update_book(self, title, authors, abstract, year, publisher, city, mtype, bid):
    self.cur.execute("UPDATE books SET title = '%s', author = '%s',abstract = '%s', \
          year = '%s', publisher = '%s', city = '%s',mtype = '%s' WHERE id = '%s'" % \
        (title, authors, abstract,year,publisher, city, mtype, bid))
    self.con.commit()   
    
  def add_borrow(self, id, bid):
    ''' Insert a borrower into the borrows table.
    '''
    self.cur.execute("INSERT INTO borrows(book, borrower, o_date) \
                  VALUES('%s','%s',DATETIME('NOW'));" %  (id, bid))
    self.con.commit()
    
  def update_borrows(self, id, bid):
    return self.cur.execute("UPDATE borrows SET i_date = DATETIME('now') \
          WHERE book = '%s' AND borrower = '%s' AND i_date IS NULL" % \
          (id, bid)) 
          
  def add_new_borrower(self, name, contact, notes):
    self.cur.execute("INSERT INTO borrowers(name,contact,notes) VALUES('%s','%s','%s');" % \
          (name,contact, notes))
    self.con.commit()
  
  def update_borrower(self,name, contact , notes, bid):
    self.cur.execute("UPDATE borrowers set name='%s', contact='%s' ,notes='%s' where id = '%s';" % \
          (name, contact, notes, bid))
    self.con.commit()
    
  def remove_book(bid):
    ''' remove a book/copy from the db.  This just decrements the copy 
    counter until copies = 0 then we remove the entry completely.
    '''
    self.cur.execute("UPDATE books SET copies = copies-1 WHERE id = '%s';" % bid)
    self.cur.execute("DELETE FROM books WHERE copies = 0;")  
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
    logging.info("This connection is using MySQL")
    
  def get_all_books(self):
    ''' 
    Get all of the books and return a list.
    
    '''
    command = "SELECT * FROM books WHERE copies > 0 order by author;"
    self.cur.execute(command)
    return  self.cur.fetchall()
  
  
  def get_book_count_by_isbn(self, bar):
    self.cur.execute("SELECT COUNT(*) as count FROM books WHERE isbn = %s;" , bar)
    return  self.cur.fetchone()[0]
  
  def get_book_borrower_by_book_id(self,bid):
    self.cur.execute("select borrowers.name, borrows.o_date FROM  borrows, borrowers \
      where i_date is null and borrows.book='%s' \
      AND borrows.borrower=borrowers.id;" % bid)
    return self.cur.fetchone() 
    
    
  def get_qrcode_count(self, isbn):
    self.cur.execute("SELECT COUNT(*) as count FROM qrcodes WHERE caption = %s;" , "ISBN: "+str(self.abook.id))
    return self.cur.fetchone()[0] 
    
  def get_borrowed_books(self):
    ''' 
    Get a list of books that have been borrowed.
    
    '''
    command = "select * from books, borrows where books.id = borrows.book \
                      and i_date is null;"
    self.cur.execute(command)
    return self.cur.fetchall()
    
  def get_borrowed_book_by_id(self, bid):
    self.cur.execute("select * FROM  borrows where i_date is null and borrows.book=%s", bid)
    return self.cur.fetchone()
    return 
   
  def get_borrowers_borrowed_books(self):
    self.cur.execute("SELECT title, author, name, o_date FROM books, \
        borrows, borrowers WHERE books.id = borrows.book \
        AND borrows.borrower=borrowers.id AND i_date is null \
        ORDER BY o_date;")
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
  
  def get_one_borrower(self,bid):
    logging.info(bid)
    self.cur.execute("SELECT * from borrowers where id = %s;", bid)
    return self.cur.fetchone()
    
  def search_books(self, search_string):
    ''' 
    Get books based on author and title search.
    
    '''
    self.cur.execute("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s", \
        [('%% %s %%' % search_string), ('%% %s %%' % search_string)])
    return  self.cur.fetchall()
    
  def get_by_id(self, book_id):
    ''' Search for book on its ID.  NB. This is NOT its ISBN
    
    '''
    self.cur.execute ("SELECT * FROM  books where id = %s;",book_id)
    return self.cur.fetchall()

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
       
  def update_book(self, title, authors, abstract, year, publisher, city, mtype, bid):
    self.cur.execute("UPDATE books SET title = %s, author = %s,abstract = %s, \
          year = %s, publisher = %s, city = %s,mtype = %s WHERE id = %s", \
        (title, authors, abstract,year,publisher, city, mtype, bid))  
        
  def add_borrow(self, id, bid):      
    self.cur.execute("INSERT INTO borrows(book, borrower, o_date) \
      SELECT %s, %s, now() FROM DUAL WHERE NOT EXISTS \
      (SELECT 1 FROM borrows WHERE book = %s AND borrower = %s AND i_date IS NULL);",
      [id, bid,id, bid])
      
  def add_new_borrower(self, name, contact, notes):
    self.cur.execute("INSERT INTO borrowers(name,contact,notes) VALUES(%s,%s,%s);",
          (name,contact, notes))
          

    
  
  def update_borrower(self, name, contact, notes, bid):
    self.cur.execute("UPDATE borrowers set name=%s, contact=%s ,notes=%s where id = %s;",
          (name,contact, notes, bid))
    
    
      
  def update_borrows(self, id, bid):
    return self.cur.execute("UPDATE borrows SET i_date = NOW() \
          WHERE book = %s AND borrower = %s AND i_date IS NULL",
          [id, bid])
          
  def remove_book(bid):
    ''' remove a book/copy from the db.  This just decrements the copy 
    counter until copies = 0 then we remove the entry completely.
    '''
    self.cur.execute("UPDATE books set copies = copies-1 WHERE id = %s;",bid)
    self.cur.execute("DELETE FROM books WHERE copies=0;")
    
    
    
########################################################################      
class calibre:
  '''
  DB queries for Calibre database.  Note that many.some users will not 
  have Caliber installed so this has to fail quietly.  Could just return
  empty results.
  
  '''
  try: import calibre
  except: pass
  def __init__(self):
    self.e_books = self.calibre.calibre()
    
  def get_all_calibre(self):
    try:return self.e_books
    except: return[]
  
########################################################################
class xml():
  '''
  I'm unlkely ever to implement XML data storage but I'll out this here
  in case some other massochist wants to. :)
  ''' 
  def __init__(self):
    pass_
    
########################################################################    

''' In order to make a runtime decision about which class we are going
to inherit from we need to do...

See http://code.activestate.com/recipes/285262-create-objects-from-variable-class-names/
'''
object = globals()[use] # use is the class name from the config file

class sql(object):
  '''Inherit the approriate class methods here depending on how
  we are constructed.  Object is whatever class name we provide.
  To use:
  
  from db_queries import sql as sql
  foo = sql()
  
  '''

########################################################################    

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
  
