#!/bin/env python
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
'''
Move all the db queries here.  There will be equivalent queries for both
MySQL and SQLite so the user can choose either storage type from the setup
dialog. (NB Write setup dialog.)
'''

import MySQLdb
import MySQLdb.cursors
import sys,os
import load_config


class sqlite():
  ''' 
  Database queries for sqlite.

  '''  
  def __init(self):
    pass
  
  pass
  

class mysql():
  '''
  Database queries for MySQL
  
  '''
  def __init(self):
    pass
  pass
  

# Test harness starts here
if __name__ == "__main__":
  lite = sqlite()
  my = mysql()
  
