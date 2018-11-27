#!/bin/env python

import barcode
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

of = open("eans.csv","w")
while count:
    ean = barcode.EAN8(str(randint(1000000, 9999999))).ean
    if len(str(ean)) != 8: continue
    print ean
    of.write(str(ean))
    of.write(",\n")
    count = count -1
of.close()
