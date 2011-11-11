#!/bin/env python
# Print methods.

import cups
import os
import sys
import pipes

class printer:
  def __init__(self):
    self.con =  cups.Connection()
    self.printer =  self.con.getDefault()

    pass

  def print_strings (self, afile):
    if not afile:
      return
    if sys.platform == 'linux2':
      ''' Is this linux? '''
      self.con.printFile(self.printer, afile, "", {"PageSize":"A4"})
      pass
    else:
      ''' Likely Windows so some else will have to write the print method '''

      pass

  def test_print(self):
    ''' Print this file '''
    self.con.printFile(self.printer, "lib_print.py", "", {"Font":"Helvetica-Narrow",
          "PrintoutMode":"Draft","PageSize":"A4", "FontSize":"8"})

    pass


# Test harness
if __name__ == "__main__":
  app = printer()
  app.test_print()
