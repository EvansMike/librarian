#!/bin/env python
# Test file for database query refactoring.
# TODO: Everything.
# First create a sqlite3 database from mysql db
# ./mysql2sqlite3 books -p | sqlite3 books.db

import load_config as config
import sys
import os
import unittest
import subprocess


yes = {'yes','y', 'ye', ''}
no = {'no','n'}
# Clone to a test database
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


class TestAll(unittest.TestCase):
    import mysql_queries
    import sqlite_queries
    def setUp(self):
        '''try:
            subprocess.Popen('mysqladmin create test_books -h localhost -u '+ db_user + ' -p' + db_pass, shell = True)
            subprocess.Popen('mysqldump -h localhost -u '+ db_user + ' -p' + db_pass + '  books \
                | mysql -h localhost -u '+ db_user + ' -p' + db_pass + 'test_books', shell = True)
        except:
            raise
            quit(1)'''
        try:
            self.db1 = self.mysql_queries.mysql()
            self.db2 = self.sqlite_queries.sqlite()
        except:
            raise
            quit(1)
    
    '''def tearDown(self):
        subprocess.Popen('mysqladmin drop test_books -h localhost -u '+ db_user + ' -p' + db_pass, shell = True)
    '''
        
    def test_get_all_books(self):
        r1, numrows1 = self.db1.get_all_books()
        r2, numrows2 = self.db2.get_all_books()
        print  numrows1, numrows2
        self.assertEqual(numrows1,numrows2)
        self.assertTrue(numrows1 == numrows2)

    def test_get_book_count_by_isbn(self):
        bar = '9780099422273'
        c1 = self.db1.get_book_count_by_isbn(bar)
        c2 = self.db2.get_book_count_by_isbn(bar)
        print c1, c2
        self.assertEqual(c1,c2)

    def test_get_borrowed_books(self):
        c1 = self.db1.get_borrowed_books()
        c2 = self.db2.get_borrowed_books()
        print len(c1), len(c2)
        self.assertEqual(len(c1), len(c2))

    def test_search_books(self):
        c1 = self.db1.search_books('empire')
        c2 = self.db2.search_books('empire')
        print len(c1), len(c2)
        self.assertEqual(len(c1), len(c2))


    def test_get_book_borrower_by_book_id(self):
        bid = 979
        c1 = self.db1.get_book_borrower_by_book_id(bid)
        c2 = self.db1.get_book_borrower_by_book_id(bid)
        print c1['name'], c2['name']
        self.assertEqual(c1['name'], c2['name'])
        
    def test_get_borrowed_book_by_id(self):
        bid = 979
        c1 = self.db1.get_borrowed_book_by_id(bid)
        c2 = self.db2.get_borrowed_book_by_id(bid)
        print c1['id'], c2['id']
        self.assertEqual(c1['id'], c2['id'])
        
    def test_get_borrower_by_id(self):
        bid = 5
        c1 = self.db1.get_borrower_by_id(bid)
        c2 = self.db2.get_borrower_by_id(bid)
        print c1['name'], c2['name']
        self.assertEqual(c1['name'], c2['name'])
        
    def test_get_borrowers_borrowed_books(self):
        c1 = self.db1.get_borrowers_borrowed_books()
        c2 = self.db2.get_borrowers_borrowed_books()
        print len(c1), len(c2)
        self.assertEqual(len(c1), len(c2))

        
    def test_get_borrows(self):
        bid = 180
        copies = 10
        c1 = self.db1.get_borrows(bid, copies)
        c2 = self.db2.get_borrows(bid, copies)
        print len(c1), len(c2)
        self.assertEqual(len(c1), len(c2))
        
    def test_get_all_borrowers(self):
        c1 = self.db1.get_all_borrowers()
        c2 = self.db2.get_all_borrowers()
        print len(c1), len(c2)
        self.assertEqual(len(c1), len(c2))
        
    def test_get_one_borrower(self):
        bid = 38
        c1 = self.db1.get_one_borrower(bid)
        c2 = self.db2.get_one_borrower(bid)
        self.assertEqual(c1['name'], c2['name'])
        
    def test_get_borrowing_history(self):
        c1 = self.db1.get_borrowing_history()
        c2 = self.db2.get_borrowing_history()
        print len(c1), len(c2)
        self.assertEqual(len(c1), len(c2))
        
    def test_get_by_id(self):
        bid = 222
        c1 = self.db1.get_by_id(bid)
        c2 = self.db2.get_by_id(bid)
        self.assertEqual(c1['title'], c2['title'])

    def test_get_locations(self):
        c1 = self.db1.get_locations()
        c2 = self.db2.get_locations()
        print len(c1), len(c2)
        self.assertEqual(len(c1), len(c2))
        
    def test_get_location_by_isbn(self):
        isbn = '9780099422273'
        c1 = self.db1.get_location_by_isbn(isbn)
        c2 = self.db2.get_location_by_isbn(isbn)
        print c1[0]['room'], c2[0]['room']
        self.assertEqual(c1[0]['room'], c2[0]['room'])

        
    '''
    #DANGER WILL ROBINSON, DANGER AHEAD!
    def test_insert_unique_author(self):
        authors = "Mike Test"
        self.db1.clone_table_to_test(authors)
        self.db2.clone_table_to_test(authors)
        c1 = self.db1.insert_unique_author(authors)
        c2 = self.db2.insert_unique_author(authors)
        
    def test_insert_book_object(self):
        import book
        book = book.Book()
        c1 = self.db1.insert_book_object(book)
        c2 = self.db2.insert_book_object(book)

    def test_update_book(self):
        import book
        book = book.Book()
        bid = None
        c1 = self.db1.update_book(book, bid)
        c2 = self.db2.update_book(book, bid)
        
    def test_update_book_location(self):
        bid = None
        location = None
        c1 = self.db1.update_book_location(bid, location)
        c2 = self.db2.update_book_location(bid, location)

    def test_add_borrow(self):
        bid = None
        c1 = self.db1.add_borrow(id, bid)
        c2 = self.db2.add_borrow(id, bid)
        
    def test_add_new_borrower(self):
        c1 = self.db1.add_new_borrower(name, contact, notes)
        c2 = self.db2.add_new_borrower(name, contact, notes)
        
    def test_update_borrower(self):
        name = None
        contact = None
        notes = None
        bid = None
        c1 = self.db1.update_borrower(name, contact, notes, bid)
        c2 = self.db2.update_borrower(name, contact, notes, bid)
        
    def test_update_borrows(self):
        bid = None
        c1 = self.db1.update_borrows(id, bid)
        c2 = self.db2.update_borrows(id, bid)
        
    def test_remove_book(self):
        bid = None
        c1 = self.db1.remove_book(bid)
        c2 = self.db2.remove_book(bid)
        
    def test_add_location(self):
        room = None
        self = None
        c1 = self.db1.add_location(room, shelf)
        c2 = self.db2.add_location(room, shelf)
    '''

if __name__ == '__main__':
    question = "Confirm that you are using a COPY of your data y|n\n# "
    sys.stdout.write(question)
    choice = raw_input().lower().strip()
    if choice in no:
        print "Stopping"
    print "OK. On your head be it"
    sys.argv.append('--verbose') # Make it run verbosely (hacky).
    unittest.main()

'''
list of queries to test: (from mysql_queries.py)
  #def get_all_books(self):
  #def get_book_count_by_isbn(self, bar):
  #def get_book_borrower_by_book_id(self,bid):
  #def get_borrowed_books(self):
  #def get_borrowed_book_by_id(self, bid):
  #def get_borrower_by_id(self, bid):
  #def get_borrowers_borrowed_books(self):
  #def get_borrows(self, bid, copies):
  #def get_all_borrowers(self):
  #def get_one_borrower(self,bid):
  #def get_borrowing_history(self):
  #def search_books(self, search_string):
  #def get_by_id(self, book_id):
  DANGER WILL ROBINSON DANGER AHEAD
  def insert_unique_author(self, authors):
  def insert_book_object(self, book):
  def update_book(self, book, bid):
  def update_book_location(self, bid, location):
  def add_borrow(self, id, bid):
  def add_new_borrower(self, name, contact, notes):
  def update_borrower(self, name, contact, notes, bid):
  def update_borrows(self, id, bid):
  def remove_book(self, bid):
  def add_location(self, room, shelf):
  def get_locations(self):
  def get_location_by_isbn(self ,isbn):
'''
