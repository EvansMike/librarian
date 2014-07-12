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

def fix_books():
    cur.execute("DELETE FROM books_to_authors") # Clean the tables
    db.commit() 
    cur.execute("DELETE FROM book_authors") # Clean the tables
    db.commit()
    cur.execute("DELETE FROM new_books") # Clean the tables
    db.commit()
    
    db = MySQLdb.connect(host=db_host, db=db_base,  passwd = db_pass)
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM books ORDER BY id;")

    books = cur.fetchall()
    for abook in books:
        last_book_id = abook['id']
        split_suthors = abook['author'].split(",")
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




''' Run main if called directly.'''
if __name__ == "__main__":
    fix_books()
    
