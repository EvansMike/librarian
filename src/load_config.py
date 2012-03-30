#!/bin/env python
# Get config data from hidden/secret file
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
import ConfigParser
import logging
import gtk
import os, stat
import gettext
import locale



locale.setlocale(locale.LC_ALL, '')
APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

logger = logging.getLogger("barscan")
logging.basicConfig(format='%(module)s: %(levelname)s:%(message)s: LINE %(lineno)d', level=logging.DEBUG)


class load_config:
  ''' Load the config data for use by applications.
  If a config file is not found it writes a stub file to the current dir
  and informs the user to about filling the config fields.'''
  def __init__(self):
    self.get_config()

  def get_config(self):
    config_file = "db_conf.cfg"
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    if not config.sections():
      #print "Cannot read config file, exiting.\n"
      # Pop up a message
      import messages
      messages.pop_info(_('No config file found.\nA template file file has been written to disk.\nPlease edit ') 
        + config_file + _('to contain the correct login details for your databases.'))

      f = open(config_file,"w")
      # Write a dummy config file if one doesn't exist
      '''
      #The python way, but it converts everything to LOWER case!  I don't want that.
      parser = ConfigParser.SafeConfigParser()
      parser.add_section('database')
      parser.add_section('calibre')
      parser.set('database', 'USER', 'username')
      parser.set('database', 'PASSWD', 'password')
      parser.set('database', 'DB', 'db_name')
      parser.set('calibre', '# Optional: Define path to Calibre database, Users home dir will be automatically determined.', '')
      parser.set('calibre', 'CALIBRE_DB', 'calibre_db')
      parser.write(f)
      '''
      # The dirty way.  Preserves case.  Probably not cross OS safe.
      f.write('[database]\nUSER = username\nPASSWD = password\nDB = db_name\nDBHOST = hostname\n\
      \n# Optional: Define path to Calibre database, Users home dir will be\
      automatically determined.\n[calibre]\nCALIBRE_DB = calibre_db\n')
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
      try:
        self.calibre_db = config.get('calibre','CALIBRE_DB')
      except:
        pass


# For testing
if __name__ == "__main__":
  app = load_config()
  app.print_config()
  print app.get_config()



