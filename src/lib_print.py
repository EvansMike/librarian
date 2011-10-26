#!/bin/env python
# Print methods.

import cups
import os
import sys

class print.py:
  def __init__(self):
    self con =  cups.Connection()
    printer =  con.getDefault()


    pass

  def print (self, afile):
    ''' The file in this case should be a stream. '''
    if sys.platoform == 'posix':
      ''' Is this linux? '''
      con.printFile(afile)
      pass
    else:
      ''' likely Windows and some else will have to write the print mehod '''
      pass

