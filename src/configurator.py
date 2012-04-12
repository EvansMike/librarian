#!/bin/env python
'''
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
  MA 02110-1301, USA.

A GUI for setting up database and Amazon configuration tokens.
'''

import sys
#import ConfigParser
import logging
import gconf_config
import gettext
import datetime

_ = gettext.gettext

logger = logging.getLogger("configurator")
logging.basicConfig(format='%(module)s: %(levelname)s:%(message)s: LINE %(lineno)d', level=logging.DEBUG)

try:
	import pygtk
	pygtk.require("2.0")
except:
	pass
try:
	import gtk
except:
	print_("GTK Not Availible")
	sys.exit(1)

config = gconf_config.gconf_config()

  pass
  
class configurator:
  
  
  def __init__(self):
    self.load_settings()
    pass
    
    
  def load_settings(self):
    ''' Try to load exsisting settings and populate GUI.
    if there are errors then it's likely this is a first time run and we
    need to create the settings.  
    TODO: We shouldn't destroy existing settings however.
    '''
    try:
      self.db_user = config.db_user
      self.db_pass = config.db_pass
      self.db_base = config.db_base
      self.db_host = config.db_host
      self.AWS_KEY = config.az_key
      self.SECRET_KEY = config.az_skey
    except: # Means the settings don't exist so we have to create them
      config.test_config() # Not a good method name is it?
      self.load_settings() # Now try again
    
  def save_settings(self):
    pass


   
# Test and stand alone malarky
if __name__ == "__main__":
  app = configurator()
  gtk.main()
