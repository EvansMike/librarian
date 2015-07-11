#!/bin/env python
# -*- coding: utf-8 -*-


import json
import urllib
import urllib2
import logging
logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
DEBUG = logging.debug


class BookLookup(object):


    def google_desc(self, isbn):
        url = "https://www.googleapis.com/books/v1/volumes?q=isbn+{isbn}"\
          "&fields=items/volumeInfo(description)"\
          "&maxResults=1".format(isbn=isbn)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        content = json.loads(response.read())
        DEBUG(content)
        return content['items'][0]['volumeInfo']['description'].encode('utf8')

    def xisbn(self, isbn):
        url = 'http://xisbn.worldcat.org/webservices/xid/isbn/{isbn}?'\
        'method=getMetadata&format=json&fl=title,author,year,publisher,lang,city'.format(isbn=isbn)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        content = json.loads(response.read())
        DEBUG(content)
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
    descript = lookup.google_desc("0130104949")
    print data
    print descript
    data = lookup.xisbn("1565924339")
    descript = lookup.google_desc("1565924339")
    print data
    print descript
