#!/bin/env python
'''
#import gtk # Need gtk3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
 
import logging
import gettext

import ConfigParser
import load_config
'''

try:
  import gtk
  import MySQLdb
  import ConfigParser
  import gettext
  import logging
  import load_config
except  ImportError, e:
  print e
  quit()


APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

logging.basicConfig(format='%(module)s: %(levelname)s:%(message)s: LINE %(lineno)d', level=logging.DEBUG)
#logging.disable(logging.INFO) # Uncomment to disable info messages

'''
config = load_config.load_config()
db_user = config.db_user
db_pass = config.db_pass
db_base = config.db_base
db_host = config.db_host
'''

class borrowers():

  def __init__(self,bid = 0):
    builder = Gtk.Builder()
    builder.add_from_file("ui/borrower_dialog.glade")
    self.window = builder.get_object("dialog1")
    self.name = builder.get_object("entry1")
    self.contact = builder.get_object("entry2")
    self.notes = builder.get_object("entry3")
    self.status = builder.get_object("status_label")
    self.button_cancel = builder.get_object("button_cancel")
    builder.connect_signals(self)
    self.bid = bid
    self.status.set_text("Add a borrower.")
    
    
  def run(self):
    return self.window.run()
    
  def on_button_add_clicked(self, widget):
    ''' Add a borrower to the database.

    '''
    logging.info("Added a borrower")
    logging.info(self.name.get_text())
    if len(self.name.get_text()) > 0:
      if self.bid == 0:
        self.cur.execute("INSERT INTO borrowers(name,contact,notes) VALUES(%s,%s,%s);",
          (self.name.get_text(),self.contact.get_text(), self.notes.get_text()))
      else:
         self.cur.execute("UPDATE borrowers set name=%s, contact=%s ,notes=%s where id = %s;",
          (self.name.get_text(),self.contact.get_text(), self.notes.get_text(), self.bid))
      self.db.commit()
      self.status.set_text("Added a borrower.")
    else:
      logging.info("Nothing to add.")
      self.status.set_text("Nothing to add.")
    self.button_cancel.set_label(_("CLOSE"))
    self.window.run()
  
  
# we start here.
if __name__ == "__main__":
  app = borrowers()
  app.run()
  #app.on_button_print_clicked(None)
