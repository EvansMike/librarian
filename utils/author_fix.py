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
    Along with mods to biblio.webquery-0.4.3b this fixes errors in the authors
    list where simply grabbing the existing would not, without replroducing 
    the functionality of biblio.webquery.
    '''
    cur.execute("DELETE FROM books_to_authors") # Clean the tables
    db.commit() 
    cur.execute("DELETE FROM book_authors") # Clean the tables
    db.commit()
    cur.execute("DELETE FROM new_books") # Clean the tables
    db.commit()
    
    '''
    command = "SELECT id, isbn FROM books where isbn !='' ORDER BY id;" # LIMIT for testing
    numrows = cur.execute(command)
    books = cur.fetchall()
    complex_names = []
    for mybook in books:
        fix_by_isbn(mybook['isbn'])
    '''        

def parse_non_isbn_books():
    ''' 
    Subtly different. Don't try to refactor with the ISBN case.  
    See notes in  parse_isbn_books() above for why.
    '''
    db = MySQLdb.connect(host=db_host, db=db_base,  passwd = db_pass)
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    # Now the books with no ISBNs
    #cur.execute("SELECT * FROM books where isbn ='' ORDER BY id;")
    cur.execute("SELECT * FROM books ORDER BY id;")
    # etc.
    books = cur.fetchall()
    for abook in books:
        # Just copy them in to start with
        print abook['title'], abook['author'] 
        cur.execute("INSERT INTO new_books(title, author, isbn,abstract, \
          year, publisher, city, copies, mtype, add_date, owner) \
          VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", \
          (abook['title'], abook['author'], abook['isbn'], abook['abstract'], \
          abook['year'], abook['publisher'], abook['city'], 1, abook['mtype'], \
          abook['add_date'], abook['owner']))
        db.commit()
        cur.execute("SELECT LAST_INSERT_ID()")
        last_book_id = cur.fetchone()
        last_book_id = last_book_id['LAST_INSERT_ID()']
        split_suthors = abook['author'].split(",")
        # Need to update borrows table.
        cur.execute("SELECT * FROM borrows WHERE book = %s;", abook['id'])
        #print cur.rowcount
        if int (cur.rowcount) == 1:
            borrow = cur.fetchone()
            cur.execute("INSERT INTO borrows(o_date, i_date, book, borrower) \
                VALUES(%s,%s,%s,%s)",
                [borrow['o_date'], borrow['i_date'],last_book_id, borrow['borrower']])
        
        ordinal = 0
        for author in split_suthors:
            if author == '' : continue
            last = author.split()[-1]
            first = " ".join(author.split()[0:-1])
            print "Ordinal = ", ordinal, author, first, last
            cur.execute("INSERT IGNORE INTO book_authors(author_last, author_first) \
                        VALUES(%s, %s)", (last, first))
            db.commit()
            cur.execute("SELECT author_id FROM book_authors WHERE author_last=%s \
                AND author_first=%s",(last, first))
            last_author_id = cur.fetchone()
            last_author_id = last_author_id['author_id']

            cur.execute("INSERT INTO books_to_authors(book_id, author_id, author_ordinal) \
                VALUES(%s,%s,%s)", (last_book_id,last_author_id,  ordinal))
            db.commit()
            ordinal += 1
    return

def fix_by_isbn(isbn):
    '''
    Put a book into the new table format.
    '''
    abook = book.book()
    abook.webquery(isbn) # FIXME This misses DVDs and CDs.

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
        first = " ".join(author.split()[0:-1]) # everything except the last part
        #print "Ordinal = ", ordinal, author, first, last
        cur.execute("INSERT IGNORE INTO book_authors(author_last, author_first) \
                    VALUES(%s, %s)", (last, first))
        db.commit()
        cur.execute("SELECT author_id FROM book_authors WHERE author_last=%s AND author_first=%s",(last, first))
        last_author_id = cur.fetchone()
        last_author_id = last_author_id['author_id']

        cur.execute("INSERT INTO books_to_authors(book_id, author_id, author_ordinal) \
            VALUES(%s,%s,%s)", (last_book_id,last_author_id,  ordinal))
        db.commit()
        ordinal += 1
    return
  



''' Run main if called directly.'''
if __name__ == "__main__":
    parse_isbn_books()
    parse_non_isbn_books()
    #fix_by_isbn('1857239547')
    #app = librarian()
    #gtk.main()
