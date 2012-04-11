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
'''
''' Get, set config data using gconf.  This should make the app portable
across OS,s and ensure config data are available wherever the app is started
from.
'''

#TODO: Gconf schema, maybe?

import sys
import logging
import os, stat
import gettext
import locale
import gconf
import base64 # For trivial password hiding


locale.setlocale(locale.LC_ALL, '')
APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

logger = logging.getLogger("barscan")
logging.basicConfig(format='%(module)s: %(levelname)s:%(message)s: LINE %(lineno)d', level=logging.DEBUG)

class gconf_config():
  ''' Load the config data for use by applications.
  If a config file is not found it writes a stub file to the current dir
  and informs the user to about filling the config fields.'''
  def __init__(self):
    print "init\n"
    self.client = gconf.client_get_default()
    self.get_config()
    #else: self.test_config() # TODO: Write setup dialog.
    
  def save_config(self):
    ''' Save config values to gconf. '''
    pass
  
  def test_config(self):
    '''write new default values to config. 
    TODO: Obvioslsy users will not be expected to edit these values in their gconf tree.
    TODO: Write a config interface.'''
    # Test if alredy exists, don't overwrite!
    if self.client.dir_exists("/apps/librarian") == False: 
      print "Creating new config file.\n"
      
      gvalue_str = gconf.Value(gconf.VALUE_STRING)  
        
      self.client.add_dir("/apps/librarian",gconf.CLIENT_PRELOAD_NONE)
      gvalue_str.set_string('username')
      self.client.set('/apps/librarian/USER', gvalue_str)
      gvalue_str.set_string('password')
      self.client.set('/apps/librarian/PASSWD', gvalue_str)
      gvalue_str.set_string('localhost')
      self.client.set('/apps/librarian/DBHOST', gvalue_str)
      gvalue_str.set_string('books')
      self.client.set('/apps/librarian/DBASE',gvalue_str)
      gvalue_str.set_string('Calibre_Library/metadata.db')
      self.client.set('/apps/librarian/CALIBRE_DB',gvalue_str)
      gvalue_str.set_string('aws_key')
      self.client.set('/apps/librarian/AZKEY',gvalue_str)
      gvalue_str.set_string('az_secret_key')
      self.client.set('/apps/librarian/AXSKEY',gvalue_str)
    
    if self.client.dir_exists("/apps/librarian") == False: 
      print "Cannot create gconf entries!"
      return False
    else: return True
    
  def create_schema(self):
    ''' Create schema for key values '''
    print "Creating schemas.\n"
    self.client.add_dir("/schemas/apps/librarian",gconf.CLIENT_PRELOAD_NONE)
    user_schema = gconf.Schema()
    passwd_schema = gconf.Schema()
    dbhost_schema = gconf.Schema()
    dbase_schema = gconf.Schema()
    az_aws_key = gconf.Schema()
    az_secret_key = gconf.Schema()
    
    user_schema.set_owner("librarian")
    passwd_schema.set_owner("librarian")
    dbhost_schema.set_owner("librarian")
    dbase_schema.set_owner("librarian")
    az_aws_key.set_owner("librarian")
    az_secret_key.set_owner("librarian")
    
    user_schema.set_type("string")
    passwd_schema.set_type("string")
    dbhost_schema.set_type("string")
    dbase_schema.set_type("string")
    az_aws_key.set_type("string")
    az_secret_key.set_type("string")

    self.client.set_schema("/schemas/apps/librarian/USER",user_schema)
    self.client.set_schema("/schemas/apps/librarian/PASSWD",passwd_schema)
    self.client.set_schema("/schemas/apps/librarian/DBHOST",dbhost_schema)
    self.client.set_schema("/schemas/apps/librarian/DBASE",dbase_schema)
    self.client.set_schema("/schemas/apps/librarian/AZKEY",az_aws_key)
    self.client.set_schema("/schemas/apps/librarian/AZSKEY",az_secret_key)
    
    
  def get_config(self):
    '''  '''
    try:
      self.db_user = self.client.get('/apps/librarian/USER').to_string()
      self.db_pass = self.client.get('/apps/librarian/PASSWD').to_string()
      #self.db_pass = base64.b64decode(self.client.get('/apps/librarian/PASSWD').to_string()) #Need to implement GUI first.
      self.db_host = self.client.get('/apps/librarian/DBHOST').to_string()
      self.db_base = self.client.get('/apps/librarian/DBASE').to_string()
      self.calibre_db = self.client.get('/apps/librarian/CALIBRE_DB').to_string()
      self.db_base = self.client.get('/apps/librarian/AZKEY').to_string()
      self.db_base = self.client.get('/apps/librarian/AZSKEY').to_string()
    except: # Couldn't find the config settings
      print "\nCannot find setup data.  Writing default values.\n"
      print "You will need to run the config thingy.\n"
      #TODO: Pop up a config window here
      self.test_config() # TODO: remove when pop up window done.
      self.get_config()
      raise
      
    
     
  def print_config(self):
    ''' print some values for testing.
    '''
    print "USER =", self.client.get('/apps/librarian/USER').to_string()
    print "PASSWD =", self.client.get('/apps/librarian/PASSWD').to_string()
    print "DBHOST =", self.client.get('/apps/librarian/DBHOST').to_string()
    print "DBASE =", self.client.get('/apps/librarian/DBASE').to_string()
    print "CALIBRE_DB =", self.client.get('/apps/librarian/CALIBRE_DB').to_string()
  
# test harness.  Write and read some default config values.
if __name__ == "__main__":
  app = gconf_config()
  #if state: app.print_config()
  app.create_schema()
  #state = app.test_config()
