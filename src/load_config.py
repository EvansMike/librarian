#!/bin/env python
# Get config data from hidden/secret file

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
  db_user = "foo"
  def __init__(self):

    config_file = "db_conf.cfg"
    config = ConfigParser.ConfigParser()
    try:
      config.read(config_file)
    except:
      print "Cannot read config file, exiting.\n"
      # Print a blank config file and inform the luser
      d = gtk.Dialog()
      d.add_buttons(gtk.STOCK_OK, 1)

      # Pop up a message
      label = gtk.Label(_('No config file found. Please edit ') + config_file)
      label.show()
      d.vbox.pack_start(label)
      answer = d.run()
      d.destroy()

      f = open(config_file,"w")
      # Write a dummy config file if one doesn't exist
      f.write('[database]\nUSER = username\nPASSWD = password\nDB = db_name\nDBHOST = hostname\n\
      \n# Define relative path to Calibre database, Users home dir will be\
      automatically determined.\n[calibre]\nCALIBRE_DB\n')
      os.fchmod(f.fileno(),stat.S_IREAD|stat.S_IWRITE)
      f.close()
      del f

    # Now read the file
    self.db_user = config.get('database','USER')
    self.db_pass = config.get('database','PASSWD')
    self.db_base = config.get('database','DB')
    self.db_host = config.get('database','DBHOST')
    self.calibre_db = config.get('calibre','CALIBRE_DB')



  def print_config(self):
    '''Print the config data to stout.  Take care not to divulge secret data!'''
    print self.db_user
    print self.db_pass
    print self.db_base
    print self.db_host

# For testing
if __name__ == "__main__":
  app = load_config()
  app.print_config()
  print app.get_config()



