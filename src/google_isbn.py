#!/bin/env python
'''
From:
http://lateral.netmanagers.com.ar/weblog/posts/quick-hack-to-catalog-your-books.html
'''

import sys
import time
import gdata.books.service
import json

def get_book_info(isbn):
    print "Looking for ISBN:", isbn
    google_books = gdata.books.service.BookService()
    result = google_books.search('ISBN %s '%isbn)
    data = [x.to_dict() for x in result.entry]
    if not data:
        print "No results"
        return
    title = data[0]['title']
    with open(title+'.json','w') as f:
        f.write(json.dumps(data))
    print "Book info for '%s' is '%s'" %(isbn, title)

if __name__ == "__main__":
    while True:
        isbn = sys.stdin.readline().strip()
        if isbn:
            get_book_info(isbn)
        time.sleep(1)
