#!/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import logging
from datetime import datetime
logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
DEBUG = logging.debug
from . import messages

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
        data = {}
        url = f"https://www.googleapis.com/datas/v1/volumes?q=isbn+{isbn}&maxResults=1&fields=items"
        r = self.get_response(url)
        if r is  None:
            messages.pop_info('No data were returned from lookup!\n\n')
            return None
        content = r.json()
        data['publisher'] = '' # These may not exist in the results so set them to empty strings
        data['city'] = ''
        data['language'] = ''
        data['edited'] = ''
        data['isbn'] = isbn
        data['authors'] = ', '.join(content['items'][0]['volumeInfo']['authors'])
        datestring = content['items'][0]['volumeInfo']['publishedDate']
        try:
            dt = datetime.strptime(datestring, '%Y-%m-%d')
            data['year'] = dt.year
        except:
            data['year'] = 0
        try: data['city'] = content['items'][0]['volumeInfo']['city'] 
        except: pass
        try: data['publisher'] = content['items'][0]['volumeInfo']['publisher'] 
        except: pass
        try: data['abstract']  = content['items'][0]['volumeInfo']['description'].replace('\n',' ')
        except: pass
        data['title'] = content['items'][0]['volumeInfo']['title'] 
        data['type'] = 'data'
        return data

        
    def google_desc(self, isbn):
        url = "https://www.googleapis.com/books/v1/volumes?q=isbn+{isbn} \
          &fields=items/volumeInfo(description)\
          &maxResults=1".format(isbn=isbn)
        r = self.get_response(url)
        content = r.json()
        return content['items'][0]['volumeInfo']['description'] 


    def isbnlib(self,ISBN):
        import isbnlib
        from isbnlib import canonical, meta, classify
        isbn = canonical(str(ISBN))
        data = {}
        content = None
        try:
            content = meta(str(isbn)) #, service='openl')
        except:
            pass
        #    # Try googleAPIs? BROKEN
        #    data = self.googleapi(ISBN)
        #    return data
        DEBUG(content)
        if content is None:
            return
        try:
            data['publisher'] = '' # These may not exist in the results
            data['city'] = content.get('City','')
            data['language'] = content.get('Language','')
            data['edited'] = content.get('Edited','')
            data['isbn'] = ISBN
            data['title'] = content.get('Title','')
            data['authors'] = ', '.join(content['Authors'])
            data['year'] = content.get('Year',0)
            data['publisher'] = content.get('Publisher','')
            data['abstract']  = isbnlib.desc(str(ISBN)).replace('\n',' ')
            data['type'] = 'data'
            DEBUG(data)
            return data
        except Exception:
            raise
            return None
        
        

if __name__ == '__main__':
    lookup = BookLookup()
    #data = lookup.isbnlib("9781911215370")
    data = lookup.isbnlib("9780008288747")
    #data = lookup.googleapi("9781781089163")
    #print (data)
    # Try a DVD UPC
    #data = lookup.googleapi("5035822011717")
    print (data)
