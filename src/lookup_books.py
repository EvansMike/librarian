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
        datestring = content['items'][0]['volumeInfo']['publishedDate'].encode('utf8')
        try:
            dt = datetime.strptime(datestring, '%Y-%m-%d')
            book['year'] = dt.year
        except:
            book['year'] = 0
        try: book['city'] = content['items'][0]['volumeInfo']['city'].encode('utf8')
        except: pass
        try: book['publisher'] = content['items'][0]['volumeInfo']['publisher'].encode('utf8')
        except: pass
        try: book['abstract']  = content['items'][0]['volumeInfo']['description'].encode('utf8')
        except: pass
        book['title'] = content['items'][0]['volumeInfo']['title'].encode('utf8')
        book['type'] = 'book'
        return book

        
    def google_desc(self, isbn):
        url = "https://www.googleapis.com/books/v1/volumes?q=isbn+{isbn} \
          &fields=items/volumeInfo(description)\
          &maxResults=1".format(isbn=isbn)
        r = self.get_response(url)
        content = r.json()
        return content['items'][0]['volumeInfo']['description'].encode('utf8')


    def isbnlib(self,ISBN):
        import isbnlib
        book = {}
        formatter = isbnlib.registry.bibformatters['json']
        try:
            content = (isbnlib.meta(str(ISBN)))
        except:
            # Try googleAPIs?
            book = self.googleapi(ISBN)
            return book
        book['publisher'] = '' # These may not exist in the results
        book['city'] = ''
        book['language'] =  content['Language']
        book['edited'] = ''
        try: book['edited'] = content['Edited']
        except: pass
        
        book['isbn'] = ISBN
        book['title'] = content['Title']
        book['authors'] = ', '.join(content['Authors'])
        DEBUG(book['authors'])
        book['year'] = content['Year']
        book['publisher'] = content['Publisher'] 
        book['abstract']  = isbnlib.desc(str(ISBN)).replace('\n',' ')
        book['type'] = 'book'
        return book
        
        

if __name__ == '__main__':
    lookup = BookLookup()
    #data = lookup.isbnlib("1857988477")
    #data = lookup.isbnlib("1780893043")
    data = lookup.googleapi("1780893043")
    print (data)
