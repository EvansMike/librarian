#!/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import logging
from datetime import datetime
#logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
DEBUG = logging.debug


class BookLookup(object):

    def get_response(self, url):
        ''' Get and test the response.
        @param The url of the request.
        @return The response.
        '''
        retries = 3 # Try this mnay times
        while retries:
            r = requests.get(url)
            if r.status_code == 200:
                return r
            retries -= 1
        return None

    def googleapi(self, isbn):
        book = {}
        url = "https://www.googleapis.com/books/v1/volumes?q=isbn+{isbn}&maxResults=1&fields=items".format(isbn=isbn)
        r = self.get_response(url)
        content = r.json()
        book['publisher'] = '' # These may not exist in the results so set them to empty strings
        book['city'] = ''
        book['language'] = ''
        book['edited'] = ''
        book['isbn'] = isbn
        book['authors'] = ', '.join(content['items'][0]['volumeInfo']['authors'])
        datestring = content['items'][0]['volumeInfo']['publishedDate']
        try:
            dt = datetime.strptime(datestring, '%Y-%m-%d')
            book['year'] = dt.year
        except:
            book['year'] = 0
        try: book['city'] = content['items'][0]['volumeInfo']['city'] 
        except: pass
        try: book['publisher'] = content['items'][0]['volumeInfo']['publisher'] 
        except: pass
        try: book['abstract']  = content['items'][0]['volumeInfo']['description'].replace('\n',' ')
        except: pass
        book['title'] = content['items'][0]['volumeInfo']['title'] 
        book['type'] = 'book'
        return book

        
    def google_desc(self, isbn):
        url = "https://www.googleapis.com/books/v1/volumes?q=isbn+{isbn} \
          &fields=items/volumeInfo(description)\
          &maxResults=1".format(isbn=isbn)
        r = self.get_response(url)
        content = r.json()
        return content['items'][0]['volumeInfo']['description'] 


    def isbnlib(self,ISBN):
        import isbnlib
        book = {}
        try:
            content = isbnlib.meta(str(ISBN))
            classi = isbnlib.classify(str(ISBN))
        except:
            # Try googleAPIs?
            book = self.googleapi(ISBN)
            return book
        print(book)
        try:
            book['publisher'] = '' # These may not exist in the results
            book['city'] = ''
            book['language'] = content['Language']
            book['language'] = ''
            try:
                book['edited'] = content['Edited']
            except:
                book['edited'] = ''
            book['isbn'] = ISBN
            book['title'] = content['Title']
            book['authors'] = ', '.join(content['Authors'])
            DEBUG(book['authors'])
            book['year'] = content['Year']
            book['publisher'] = content['Publisher'] 
            book['abstract']  = isbnlib.desc(str(ISBN)).replace('\n',' ')
            book['type'] = 'book'
            return book
        except:
            raise
            return None
        
        

if __name__ == '__main__':
    lookup = BookLookup()
    #data = lookup.isbnlib("1857988477")
    data = lookup.isbnlib("9781781089163")
    #data = lookup.googleapi("9781781089163")
    print (data)
    # Try a DVD UPC
    #data = lookup.googleapi("5035822011717")
    #print (data)
