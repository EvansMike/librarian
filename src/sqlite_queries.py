# This file refactored out from  db_queries.py
# WARNING! The queries in here have not been kept in sync with those in mysql_queries.py
# TODO: fix this situation and use these files in place of db_queries.py
# TODO: Write test code for ALL the queries to confirm the same behaviour.

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
DEBUG = logging.debug
INFO = logging.info

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
    command = "SELECT *  FROM books b INNER JOIN books_to_authors ba ON (b.id = ba.book_id) \
    INNER JOIN book_authors a ON (ba.author_id = a.author_id) \
    WHERE copies > 0 \
    GROUP BY b.title ORDER BY author_last, author_ordinal;"
    self.cur.execute(command)
    rows = self.cur.fetchall()
    return rows, len(rows)

  def get_book_count_by_isbn(self, bar):
    self.cur.execute("SELECT COUNT(*) as count FROM books WHERE isbn = '%s';" % bar)
    return  self.cur.fetchone()[0]

  def get_borrowed_books(self):
    '''
    Get a list of books that have been borrowed.

    '''
    import getpass
    user = getpass.getuser()
    command = ("select * from  books, borrows  where  (books.owner!='%s' \
    AND books.borrower_id IS NULL) \
    OR  (books.id = borrows.book AND  borrows.i_date IS NULL) \
    GROUP BY books.id;" % user)
    #command = "select * from books, borrows where books.id = borrows.book \
    #                  and i_date is null;"
    self.cur.execute(command)
    return self.cur.fetchall()

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

  def get_borrower_by_id(self, bid):
    self.cur.execute("select * FROM  borrowers where id = ?;",(bid,))
    return self.cur.fetchone()

  def get_borrows(self, bid, copies):
    ''' Differing syntax for sqlite'''
    self.cur.execute("SELECT * FROM borrows where book = ? AND i_date IS NULL \
        AND o_date IS NOT NULL LIMIT ?;", (bid,copies))
    return self.cur.fetchall()

  def get_borrowing_history(self):
    ''' Get all the books ever borrowed, by whome, when and for how long.
    TODO; This properly.
    '''
    self.cur.execute ("SELECT borrows.id, title, author, name, o_date, i_date \
                        FROM books, borrows, borrowers \
                        WHERE books.id = borrows.book \
                        AND borrows.borrower=borrowers.id  \
                        AND name != 'tester' \
                        ORDER BY o_date;")
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


  def insert_book_object(self, book):
    ''' Insert a book's details directly from a book object
    @param book.  A book object.
    @return Result of insert
    '''
    self.cur.execute("INSERT INTO books(title, author, isbn,abstract, \
      year, publisher, city, copies, mtype, owner, add_date) \
      VALUES(?, ?, ?,?,?,?,?,?,?,?,?);", \
        (book.title, book.authors, book.isbn, book.abstract, book.year,
        book.publisher, book.city, 1, book.mtype, book.owner, book.add_date))
    self.con.commit()
    self.cur.execute("SELECT LAST_INSERT_ROWID()") #
    return self.cur.fetchone()
    return

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
    return self.cur.fetchone()

  def get_one_borrower(self,bid):
    logging.info(bid)
    self.cur.execute("SELECT * from borrowers where id = '%s';" % bid)
    return self.cur.fetchone()


  def update_book(self, title, authors, abstract, year, publisher, city, mtype, owner, bid):
    self.cur.execute("UPDATE books SET title = '%s', author = '%s',abstract = '%s', \
          year = '%s', publisher = '%s', city = '%s',mtype = '%s', owner = '%s' WHERE id = '%s'" % \
        (title, authors, abstract,year,publisher, city, mtype, owner, bid))
    return self.con.commit()

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

  def remove_book(self,bid):
    ''' remove a book/copy from the db.  This just decrements the copy
    counter until copies = 0 then we remove the entry completely.
    '''
    self.cur.execute("UPDATE books SET copies = copies-1 WHERE id = '%s';" % bid)
    self.cur.execute("DELETE FROM books WHERE copies = 0;")
    self.con.commit()

  def add_location(self, room, shelf):
    '''
    Add a new location to the database.
    '''
    self.cur.execute("INSERT INTO locations(room,shelf) VALUES(%s, %s);",room, shelf)

#######################################################################
