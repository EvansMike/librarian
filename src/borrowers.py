#!/bin/env python
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
'''
Add and edit borrowers.
'''
import gtk
import MySQLdb
import ConfigParser
import gettext
import logging
import load_config

APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

logger = logging.getLogger("barscan")
logging.basicConfig(format='%(module)s: %(levelname)s:%(message)s: LINE %(lineno)d', level=logging.DEBUG)

config = load_config.load_config()
db_user = config.db_user
db_pass = config.db_pass
db_base = config.db_base
db_host = config.db_host


class borrowers:
  def __init__(self):
    builder = gtk.Builder()
    builder.add_from_file("ui/borrowers.glade")
    self.window = builder.get_object("window1")
    self.name = builder.get_object("entry1")
    self.contact = builder.get_object("entry2")
    self.notes = builder.get_object("entry3")
    self.status = builder.get_object("status_label")
    builder.connect_signals(self)

    try:
        self.db = MySQLdb.connect(host = db_host, db=db_base,  passwd = db_pass);
    except:
      print _("No database connection.  Check ") + config_file
      self.db = False
    if self.db:
      self.cur = self.db.cursor()

    gtk.main()
    self.window.show

  def on_button_add_clicked(self, widget):
    ''' Add a borrower to the database. '''
    logging.info("Added a borrower")
    logging.info(self.name.get_text())
    if len(self.name.get_text()) > 0:
      self.cur.execute("INSERT INTO borrowers(ame.contact) VALUES(%s,%s);",
          (self.name.get_text(),self.contact.get_text()))
      self.db.commit()
      self.status.set_text("Added a borrower.")
    else:
      logging.info("Nothing to add.")
      self.status.set_text("Nothing to add.")



  def button_cancel_clicked(self, widget):
    if __name__ == "__main__":
      gtk.main_quit()
      quit(0)
    else:
      del db, cur
      self.window.hide()


  def on_window1_destroy(self, widget):
    ''' Do stuff when window is closed. '''
    if __name__ == "__main__":
      gtk.main_quit()
      quit(0)
    else:
      del db, cur
      self.window.hide()


# we start here.
if __name__ == "__main__":
	app = borrowers()

