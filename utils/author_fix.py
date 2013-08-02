#!/bin/env python
'''
Parse the current authors table into a new TNF authors table.


'''

import sys,os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))
import load_config as config
import locale
import gettext
import logging
import MySQLdb
import MySQLdb.cursors
import book

locale.setlocale(locale.LC_ALL, '')
APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext




# Read the config file
config = config.load_config() # For file based config
db_user = config.db_user
db_pass = config.db_pass
db_base = config.db_base
db_host = config.db_host

db = MySQLdb.connect(host=db_host, db=db_base,  passwd = db_pass)
cur = db.cursor(MySQLdb.cursors.DictCursor)

def parse_isbn_books():
    '''
    Attempt to parse the current file.
    '''
    cur.execute("DELETE FROM books_to_authors") # Clean the tables
    cur.execute("DELETE FROM book_authors") # Clean the tables
    cur.execute("DELETE FROM new_books") # Clean the tables

    command = "SELECT id, isbn FROM books where isbn !='' ORDER BY id;" # LIMIT for testing
    numrows = cur.execute(command)
    books = cur.fetchall()
    complex_names = []
    for mybook in books:
        fix_by_isbn(mybook['isbn'])
        

def parse_non_isbn_books():
    db = MySQLdb.connect(host=db_host, db=db_base,  passwd = db_pass)
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    # Now the books with no ISBNs
    cur.execute("SELECT * FROM books where isbn ='' ORDER BY id;")
    # etc.
    books = cur.fetchall()
    for abook in books:
        print abook['title']


    return;

def fix_by_isbn(isbn):
    '''
    Put a book into the new table format.
    '''
    abook = book.book()
    abook.webquery(mybook['isbn'])

    authors = abook.authors
    print "" ## Debug
    print abook.__dict__ ## Debug
    cur.execute("INSERT INTO new_books(title, author, isbn,abstract, \
      year, publisher, city, copies, mtype, add_date, owner) \
      VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", \
      (abook.title, abook.authors, abook.isbn, abook.abstract, \
      abook.year, abook.publisher, abook.city, 1, abook.mtype, abook.add_date, abook.owner))
    db.commit()
    cur.execute("SELECT LAST_INSERT_ID()")
    last_book_id = cur.fetchone()
    last_book_id = last_book_id['LAST_INSERT_ID()']
    #print "last_book_id = ",last_book_id
    split_suthors = authors.split(",")
    ordinal = 0
    print abook.title, abook.authors
    for author in split_suthors:
        if author == '' : continue
        last = author.split()[-1]
        first = author.split()[0]
        #print "Ordinal = ", ordinal, author, first, last
        cur.execute("INSERT IGNORE INTO book_authors(author_last, author_first) \
                    VALUES(%s, %s)", (last, first))
        #last_author_id = cur.execute("SELECT author_id FROM book_authors ORDER BY author_id DESC LIMIT 0 , 1")
        db.commit()
        cur.execute("SELECT LAST_INSERT_ID()")
        last_author_id = cur.fetchone()
        last_author_id = last_author_id['LAST_INSERT_ID()']

        cur.execute("INSERT INTO books_to_authors(book_id, author_id, author_ordinal) \
            VALUES(%s,%s,%s)", (last_book_id,last_author_id,  ordinal))
        db.commit()
        ordinal += 1
  return
  



''' Run main if called directly.'''
if __name__ == "__main__":
    parse_non_isbn_books()
    #app = librarian()
    #gtk.main()
