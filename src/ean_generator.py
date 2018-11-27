#!/bin/env python

'''
Create a list of EAN8's for use as barcode labels where an ISBN is not available.
Make a CSV list for printing and add then to the books table to ensure no duplicates.
'''


import barcode
from db_queries import sql as sql
import logging
from random import randint
import gettext
import sys


count = 1
try: count = int(sys.argv[1])
except: pass


_ = gettext.gettext

logger = logging.getLogger("barscan")
logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s', level=logging.DEBUG)
DEBUG = logging.debug
INFO = logging.info


db_query = sql()
of = open("eans.csv","w")
while count:
    ean = barcode.EAN8(str(randint(1000000, 9999999))).ean
    if len(str(ean)) != 8: continue
    if not db_query.insert_unique_isbn(ean): continue ## Insert if not existing
    print ean
    of.write(str(ean))
    of.write(",\n")
    count = count -1
of.close()
