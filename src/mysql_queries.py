# This file refactored out from  db_queries.py
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


################################################################################
class mysql:
  '''
  Database queries for MySQL

  '''
  import MySQLdb
  import MySQLdb.cursors
  import warnings

  warnings.filterwarnings('ignore', category=MySQLdb.Warning)
  def __init__(self):
    self.db = self.MySQLdb.connect(host=db_host, db=db_base,  passwd = db_pass)
    self.cur = self.db.cursor(self.MySQLdb.cursors.DictCursor)
    #logging.info("This connection is using MySQL")

  def get_all_books(self):
    '''
    Get all of the books and return a list.

    '''
    command = "SELECT *  FROM books b INNER JOIN books_to_authors ba ON (b.id = ba.book_id) \
    INNER JOIN book_authors a ON (ba.author_id = a.author_id) \
    WHERE copies > 0 \
    GROUP BY b.title ORDER BY author_last, author_ordinal;"
    numrows = self.cur.execute(command)
    return  self.cur.fetchall(), numrows


  def get_book_count_by_isbn(self, bar):
    self.cur.execute("SELECT COUNT(*) as count FROM books WHERE isbn = %s;" , (bar,))
    return  int (self.cur.fetchone()['count'])

  def get_book_borrower_by_book_id(self,bid):
    self.cur.execute("select borrowers.name, borrows.o_date FROM  borrows, borrowers \
      where i_date is null and borrows.book='%s' \
      AND borrows.borrower=borrowers.id;" % bid)
    return self.cur.fetchone()

  def get_borrowed_books(self):
    '''
    Get a list of books that have been borrowed. plus those lent to me.
    TODO Lent to me books.
    '''
    import getpass
    user = getpass.getuser()
    self.cur.execute ("select * from  books, borrows  where  (books.owner!=%s \
    AND books.borrower_id IS NULL) \
    OR  (books.id = borrows.book AND  borrows.i_date IS NULL) \
    GROUP BY books.id;",  (user,))
    return self.cur.fetchall()

  def get_borrowed_book_by_id(self, bid):
    self.cur.execute("select * FROM  borrows where i_date is null and borrows.book=%s", (bid,))
    return self.cur.fetchone()
    return

  def get_borrower_by_id(self, bid):
    self.cur.execute("select * FROM  borrows where id = %s;",(bid,))
    return self.cur.fetchone()

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
    self.cur.execute("SELECT * from borrowers where id = %s;", (bid,))
    return self.cur.fetchone()

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
    self.cur.execute ("SELECT * FROM  books where id = %s;",(book_id,))
    return self.cur.fetchone()

  def insert_unique_author(self, authors):
    '''
    Insert author(s) ensuring uniqueness.
    This just emits a warning about Duplicate entry if it fails.
    This should probably be caught and dealt with.
    '''
    return self.cur.execute("INSERT IGNORE INTO authors(name) values(%s);", (authors,))

  def insert_book_object(self, book):
    ''' Insert a book's details directly from a book object
    @param book.  A book object.
    @return Result of insert
    '''
    self.cur.execute("INSERT INTO books(title, author, isbn,abstract, \
      year, publisher, city, copies, mtype, add_date, owner, rating) \
      VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", \
      (book.title, book.authors, book.isbn, book.abstract, \
      book.year, book.publisher, book.city, 1, book.mtype, book.add_date, book.owner, book.rating))
    self.db.commit()

    self.cur.execute("SELECT LAST_INSERT_ID()")
    last_book_id = self.cur.fetchone()
    last_book_id = last_book_id['LAST_INSERT_ID()']
    split_suthors = book.authors.split(",")
    ordinal = 0
    for author in split_suthors:
        if author == '' : continue
        last = author.split()[-1]
        first = " ".join(author.split()[0:-1])
        print "Ordinal = ", ordinal, author, first, last
        self.cur.execute("INSERT IGNORE INTO book_authors(author_last, author_first) \
                    VALUES(%s, %s)", (last, first))
        self.db.commit()
        self.cur.execute("SELECT author_id FROM book_authors WHERE author_last=%s \
            AND author_first=%s",(last, first))
        last_author_id = self.cur.fetchone()
        last_author_id = last_author_id['author_id']

        self.cur.execute("INSERT INTO books_to_authors(book_id, author_id, author_ordinal) \
            VALUES(%s,%s,%s)", (last_book_id,last_author_id,  ordinal))
        self.db.commit()
        ordinal += 1

    return  last_book_id

  def update_book(self, book, bid):
    self.cur.execute("UPDATE books SET title = %s, author = %s,abstract = %s, \
          year = %s, publisher = %s, city = %s,mtype = %s, owner = %s, location = %s, rating = %s,\
          value = %s WHERE id = %s", \
          (book.title, book.authors, book.abstract,book.year,book.publisher, \
          book.city, book.mtype, book.owner, book.where, book.rating, book.value, bid))
    self.db.commit()

  def update_book_location(self, bid, location):
    self.cur.execute("UPDATE books SET location = %s WHERE id = %s;", (location, bid))
    self.db.commit()


  def add_borrow(self, id, bid):
    self.cur.execute("INSERT INTO borrows(book, borrower, o_date) \
      SELECT %s, %s, now() FROM DUAL WHERE NOT EXISTS \
      (SELECT 1 FROM borrows WHERE book = %s AND borrower = %s AND i_date IS NULL);",
      [id, bid,id, bid])
    self.db.commit()

  def add_new_borrower(self, name, contact, notes):
    self.cur.execute("INSERT INTO borrowers(name,contact,notes) VALUES(%s,%s,%s);",
          (name,contact, notes))
    self.db.commit()


  def update_borrower(self, name, contact, notes, bid):
    self.cur.execute("UPDATE borrowers set name=%s, contact=%s ,notes=%s where id = %s;",
          (name,contact, notes, bid))
    self.db.commit()


  def update_borrows(self, id, bid):
    return self.cur.execute("UPDATE borrows SET i_date = NOW() \
          WHERE book = %s AND borrower = %s AND i_date IS NULL",
          [id, bid])
    self.db.commit()

  def remove_book(self, bid):
    ''' remove a book/copy from the db.  This just decrements the copy
    counter until copies = 0 then we remove the entry completely.
    '''
    self.cur.execute("UPDATE books set copies = copies-1 WHERE id = %s;",(bid,))
    self.cur.execute("DELETE FROM books WHERE copies=0;")

  def add_location(self, room, shelf):
    '''
    Add a new location to the database.
    create table locations(id int auto_increment primary key, room text, shelf text);
    '''
    print room,shelf
    print self.cur.execute("INSERT INTO locations(room,shelf) VALUES(%s, %s);",(room, shelf))
    self.db.commit()
    return

  def get_locations(self):
    self.cur.execute("SELECT * FROM locations")
    return self.cur.fetchall()

  def get_location_by_isbn(self ,isbn):
    self.cur.execute("SELECT * FROM locations WHERE id = (SELECT location \
            FROM books WHERE isbn = %s);",\
            (isbn,))
    return self.cur.fetchall()

########################################################################
