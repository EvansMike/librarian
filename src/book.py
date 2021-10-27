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
import logging

logger = logging.getLogger("barscan")
logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s', level=logging.DEBUG)
DEBUG = logging.debug
INFO = logging.info
 
class Book(object):
    values = ['normal', 'scarce', 'rare', 'v_rare', 'valuable', '1st edition']
    ''' Define book properties here '''
    def __init__(self):
        self.id = ''
        self.isbn = ''
        self.ddc = '' # Dewi Decimal classification
        self.authors = ''
        self.edited = False
        self.title = ''
        self.issue = '' # For comics etc.
        self.sale_price = 0.00
        self.condition = ''
        self.publisher = ''
        self.abstract = ''
        self.mtype = 'book' # Unless set otherwise.
        self.year = ''
        self.city = ''
        self.copies = 0
        self.where = 0 # Which shelf is it on?
        self.add_date = datetime.date.today()
        self.borrower_id = None
        self.owner = getpass.getuser() # Assume owner is current logged in person
        self.rating = 0 # Stars out of 5?
        self.value = self.values[0]; # Assume lowest value class
        self.updated = False # Book data updated locally.

    def print_book(self):
        ## Return some book details as a string for printing.  Mostly a debug thing.
        bookstring = "{}{}{}{}{}".format(self.isbn,"\n",self.authors,"\n",self.title)
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
            self.authors = details_list[1].decode("utf-8")
            self.title = details_list[2].decode("utf-8")
            self.publisher = details_list[5].decode("utf-8")
            self.abstract = details_list[4].decode("utf-8")
            self.mtype = details_list[3].decode("utf-8")
            self.year = details_list[6]
            self.city = details_list[7].decode("utf-8")
            self.copies = details_list[8]
            self.where = details_list[9].decode("utf-8")
            self.edited = details_list[10].decode("utf-8")
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
        err_num += (self.year != book.year) * 64
        err_num += (self.city != book.city) * 128
        err_num += (self.mtype != book.mtype) * 256
        err_num += (self.where != book.where) * 512
        err_num += (self.owner != book.owner) * 1024
        err_num += (self.rating != book.rating) * 2048
        err_num += (self.value != book.value) * 4076
        if err_num != 0: self.updated = True
        DEBUG(err_num)
        return err_num

    def is_empty(self):
        test =  self.isbn + self.authors + self.title + self.publisher \
            + self.abstract + self.mtype + self.city +  self.mtype + str(self.where) \
            + self.owner + str(self.rating)
        if test == '': return True
        else: return False

    def webquery(self,isbn):
        if isbn == '':
            logging.warning("No ISBN provided")
            return
        data = self.lookup(isbn)
        DEBUG(data)
        if data:
            try:self.abstract = data['abstract']
            except: self.abstract =''
            self.isbn = data['isbn']
            self.title = data['title'] 
            self.authors = str(data['authors'])
            self.mtype = data['type']
            self.publisher = str(data['publisher'])
            self.city = data['city']
            self.year = data['year']
            self.edited = data['edited']
            self.updated = True
            return data
        else:
            DEBUG(data)
            return None
        
    def lookup(self, isbn):
        from . import lookup_books
        lookup = lookup_books.BookLookup()
        data = lookup.isbnlib(str(isbn))
        if data == None:
            data = lookup.googleapi(str(isbn).strip())
        return data
########### END CLASS book ################

# Test harness
if __name__ == "__main__":
    abook = Book() 
    abook.webquery("9780241146507")
    print (abook.__dict__)
    print ("")
    abook.webquery("0130104949")
    print (abook.__dict__)
    print ("")
    abook.webquery("057109659X")
    print (abook.__dict__)
    print ("")
    del abook
