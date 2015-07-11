#!/bin/env python
# -*- coding: utf-8 -*-

import requests
#import logging
#logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
#DEBUG = logging.debug


class BookLookup(object):

    def retry(func):
        ''' decorator function to retry'''
        
        def retried_func(*args, **kwargs):
            MAX_TRIES = 3
            tries = 0
            while True:
                resp = func(*args, **kwargs)
                if resp.status_code != 200 and tries < MAX_TRIES:
                    tries += 1
                    continue
                break
            return resp
        return retried_func

    def google_desc(self, isbn):
        url = "https://www.googleapis.com/books/v1/volumes?q=isbn+{isbn}"\
          "&fields=items/volumeInfo(description)"\
          "&maxResults=1".format(isbn=isbn)
        r = None
        while True:
            r = requests.get(url)
            if r.status_code == 200:
                break
        content = r.json()
        return content['items'][0]['volumeInfo']['description'].encode('utf8')
    
    #@retry
    def xisbn(self, isbn):
        url = 'http://xisbn.worldcat.org/webservices/xid/isbn/{isbn}?'\
        'method=getMetadata&format=json&fl=title,author,year,publisher,lang,city'.format(isbn=isbn)
        r = None
        while True:
            r = requests.get(url)
            if r.status_code == 200:
                break
        content = r.json()
        content = content['list'][0]
        book = {}
        book['isbn'] = isbn
        book['id'] = isbn
        book['title'] = content['title']
        buf = content['author']
        book['authors'] = [x.strip('. ') for x in buf.split(';')]
        book['publisher'] = content['publisher']
        book['city'] = content['city']
        book['year'] = content['year']
        book['language'] = content['lang']
        book['edited'] = ''
        book['type'] = ''
        book['abstract'] = self.google_desc(isbn)
        return book


if __name__ == '__main__':
    lookup = BookLookup()
    data = lookup.xisbn("0130104949")
    print data
    data = lookup.xisbn("1565924339")
    print data
