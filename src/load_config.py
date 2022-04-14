#!/bin/env python3
# Get config data from file
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

import sys
# Get python version
py_version = sys.version_info.major
if py_version == 2:
    import ConfigParser
if py_version == 3:
    import configparser as ConfigParser
import logging
import os, stat
import gettext
import locale



locale.setlocale(locale.LC_ALL, '')
APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

#logger = logging.getLogger("librarian")
logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s', level=logging.DEBUG)

# Get the real location of this file
iamhere = os.path.dirname( os.path.realpath( __file__ ) )
home = os.environ['HOME']

class load_config:
  ''' Load the config data for use by applications.
  If a config file is not found it writes a stub dot file to the users home directory
  and informs the user to about filling the config fields.'''
  def __init__(self):
    self.get_config()

  def get_config(self):
    config_file = home + "/.librarian.cfg"
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    if not config.sections():
      #print "Cannot read config file, exiting.\n"
      # Pop up a message
      import messages
      messages.pop_info(_('No config file found.\nA template file file has been written to disk.\nPlease edit ') 
        + config_file + _(' to contain the correct login details for your databases.\nNote that is is a hidden file'))

      f = open(config_file,"w")
      # Write a dummy config file if one doesn't exist
      #The python way, but it converts everything to LOWER case! 
      parser = ConfigParser.SafeConfigParser()
      parser.add_section('database')
      parser.add_section('calibre')
      parser.add_section('qr_code')
      parser.add_section('amazon_aws')
      parser.set('database', 'USER', 'username')
      parser.set('database', 'LIBRARIAN', 'Your librarian name')
      parser.set('database', '# Set BOOKMARKS to 1 if you want to have this facility', '0')
      parser.set('database', 'BOOKMARKS', '0')
      parser.set('database', 'PASSWD', 'password')
      parser.set('database', 'DB', 'db_name')
      parser.set('database', 'DBHOST', 'db_host')
      parser.set('database', '# DON\'T change the LITE_DB name', '')
      parser.set('database', 'LITE_DB', 'books.db')
      parser.set('database', '# Select either sqlite or mysql, Disable a type with a leading #', '')
      parser.set('database', '#use', 'sqlite')
      parser.set('database', 'use', 'mysql')
      parser.set('calibre', '# Optional: Define path to Calibre database, Users home dir will be automatically determined.', '')
      parser.set('calibre', 'CALIBRE_DB', 'calibre_db')
      parser.set('qr_code', 'QR_CODE', 'False')
      parser.set('amazon_aws','AWS_KEY','OPTIONAL AWS_KEY')
      parser.set('amazon_aws','SECRET_KEY','OPTIONAL SECRET_KEY')
      parser.set('UPCdatabase','OPTIONAL upc_key')

      
      parser.write(f)
      # Set access mode to owner only
      os.fchmod(f.fileno(),stat.S_IREAD|stat.S_IWRITE)
      f.close()
      del f

    else:
      # Now read the file
      self.db_user = config.get('database','USER')
      self.db_pass = config.get('database','PASSWD')
      self.db_base = config.get('database','DB')
      self.db_host = config.get('database','DBHOST')
      if self.db_pass == 'password': # Config file probably not edited.
          print("You need to edit the configuration file at ~/.librarian.cfg")
          quit(1) # Ideally this will open a config editor but, fuck it!
      try:
          self.librarian_name = config.get('database', 'LIBRARIAN')
      except: # Fallback to old system but warn
          print("Using login name for book owner, See git log for how to fix.")
          self.librarian_name = os.getlogin()
          pass
      try:
          self.bookmarks = config.get('database','BOOKMARKS')
      except: # Default to NOT printing bookmarks
          self.bookmarks = 0
      self.lite_db = config.get('database','LITE_DB')
      self.use = config.get('database','USE')
      self.qr_code = config.get('qr_code','QR_CODE')
      self.az_key = config.get('amazon_aws','AWS_KEY')
      self.az_skey = config.get('amazon_aws','SECRET_KEY')
      self.upc_key = config.get('UPCdatabase','upc_key')
      try:
        self.calibre_db = config.get('calibre','CALIBRE_DB')
      except:
        pass
        
  def print_config(self):
    ''' print some values for testing.  Take care not to expose secret data.
    '''
    print ("USER =", self.db_user)
    print ("PASSWD =", self.db_pass)
    print ("DBASE =", self.db_base)
    print ("DB_HOST =", self.db_host)


# For testing
if __name__ == "__main__":
  app = load_config()
  app.print_config()
