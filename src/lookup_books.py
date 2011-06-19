#!/bin/env python

from biblio.webquery.xisbn import XisbnQuery
from biblio.webquery.loc import LocQuery
from biblio.webquery.isbndb import IsbndbQuery
from biblio.webquery import isbndb
import zbar

isbnd_key = "QIAZBUIF"

'''Some test code'''
a = XisbnQuery()
print(a.query_bibdata_by_isbn('9780600352815'))

foo=IsbndbQuery(isbnd_key)
book = foo.query_bibdata_by_isbn('0708835783')
nn = book.pop()
nn.id
nn.title


data = ['']
book = foo.query_service("title","Beginning Python",data)
print book

