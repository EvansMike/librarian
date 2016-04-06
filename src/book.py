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
# Define a book object
# TODO: No longer sure about storing the number oc copies of a book as
# that would prevent me from storing the scanned (or when I bought) the
# book.


import datetime
import getpass


class Book:
    ''' Define book properties here '''
    def __init__(self):
        self.id = ''
        self.isbn = ''
        self.authors = ''
        self.edited = False
        self.title = ''
        self.issue = '' # For comics etc.
        self.sale_price = 0.00
        self.condition = ''
        self.publisher = ''
        self.abstract = ''
        self.mtype = ''
        self.year = ''
        self.city = ''
        self.copies = 0
        self.where = 0 # Which shelf is it on?
        self.add_date = datetime.date.today()
        self.borrower_id = None
        self.owner = getpass.getuser() # Assume owner is current logged in person
        self.rating = 0 # Stars out of 5?

    def print_book(self):
        ## Return some book details as a string for printing.  Mostly a debug thing.
        bookstring = self.isbn + "\n" + self.authors + "\n" + self.title
        return bookstring

    def add_details(self,details_list):
        ''' A simple interface to add all details in one go.  Obviously order
        of the elements is important! id and copies are determined by the
        database after insertion.  The order is:
        isbn, authors, title, abstract, mtype, publisher, year, city
        Empty fields are allowed.
        '''
        try:
            self.isbn = details_list[0]
            self.authors = details_list[1]
            self.title = details_list[2]
            self.publisher = details_list[5]
            self.abstract = details_list[4]
            self.mtype = details_list[3]
            self.year = details_list[6]
            self.city = details_list[7]
            self.copies = details_list[8]
            self.where = details_list[9]
            self.edited = details_list[10]
        except: return -1
        return 0

    def compare(self, book):
        ''' Determine if two books differ.  Return 0 if same.'''
        err_num = 0
        err_num += (self.isbn != book.isbn) * 1
        err_num += (self.authors != book.authors) * 2
        err_num += (self.title != book.title) * 4
        err_num += (self.publisher != book.publisher) * 8
        err_num += (self.abstract != book.abstract) * 16
        err_num += (self.mtype != book.mtype) * 32
        #err_num += (self.year != book.year) * 64
        err_num += (self.city != book.city) * 128
        err_num += (self.mtype != book.mtype) * 256
        err_num += (self.where != book.where) * 512
        err_num += (self.owner != book.owner) * 1024
        err_num += (self.rating != book.rating) * 2048
        return err_num

    def is_empty(self):
        test =  self.isbn + self.authors + self.title + self.publisher \
            + self.abstract + self.mtype + self.city +  self.mtype + str(self.where) \
            + self.owner + str(self.rating)
        if test == '': return True
        else: return False

    def webquery(self,isbn):
        data = self.lookup(isbn)
        self.abstract = data['abstract']
        self.id = data['id']
        self.isbn = data['isbn']
        self.title = data['title']
        self.authors = str(data['authors'][0])
        self.mtype = data['type']
        self.publisher = str(data['publisher'])
        self.city = data['city']
        self.year = data['year']
        self.edited = data['edited']
        
    def lookup(self, isbn):
        import lookup_books
        lookup = lookup_books.BookLookup()
        data = lookup.xisbn(str(isbn))
        return data
########### END CLASS book ################

# Test harness
if __name__ == "__main__":
    abook = Book() 
    abook.webquery("1565924339")
    print abook.__dict__
    print ""
    abook.webquery("0130104949")
    print abook.__dict__
    print ""
    abook.webquery("057109659X")
    print abook.__dict__
    print ""
    del abook
