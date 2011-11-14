#!/bin/env python
'''
Import e-books from calibre database avoiding duplicates
Run with calibre-debug -e import_calibre.py
'''
import sys
import site

#sys.path.append("/opt/calibre/lib/python2.7/site-packages")
#site.USER_SITE="/opt/calibre/lib/python2.7/site-packages"

import calibre
import calibre.library

calibre.library.db("")
base = calibre.library.database.LibraryDatabase("/home/mikee/Calibre_Library/metadata.db")
authors = base.all_authors()
titles = base.all_titles()
author_title = dict(zip(authors, titles))

for t,a in  map(None,titles, authors):
  print t,a
