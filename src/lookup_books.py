#!/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
#import logging
#logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
#DEBUG = logging.debug


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
    
    def google_desc(self, isbn):
        url = "https://www.googleapis.com/books/v1/volumes?q=isbn+{isbn} \
          &fields=items/volumeInfo(description)\
          &maxResults=1".format(isbn=isbn)
        r = self.get_response(url)
        content = r.json()
        return content['items'][0]['volumeInfo']['description'].encode('utf8')
    
    def xisbn(self, isbn):
        url = "http://xisbn.worldcat.org/webservices/xid/isbn/{isbn}? \
        method=getMetadata&format=json&fl=title,author,year,publisher,lang,city".format(isbn=isbn)
        r = self.get_response(url)
        if not r: return None
        content = r.json()
        
        content = content['list'][0]
        print (content)
        book = {}
        book['isbn'] = isbn
        book['id'] = isbn
        book['title'] = content['title']
        buf = content['author']
        book['authors'] = [x.strip('. ') for x in buf.split(';')]
        try:
            book['publisher'] = content['publisher']
            book['city'] = content['city']
            book['year'] = content['year']
            book['language'] = content['lang']
            book['edited'] = ''
        except:
            book['publisher'] = ''
            book['city'] = ''
            book['year'] = ''
            book['language'] = ''
            book['edited'] = ''
            pass
        book['type'] = 'book'
        book['abstract'] = self.google_desc(isbn)
        return book


if __name__ == '__main__':
    lookup = BookLookup()
    data = lookup.xisbn("9780241146507")
    #print data
    #data = lookup.xisbn("1565924339")
    #print data
