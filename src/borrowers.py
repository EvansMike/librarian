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
TODO: Do the edit part.
TODO: Need to re-write this as a dialog
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

  
#from db_queries import mysql as sql # Make this choosable for mysql and sqlite
# or 
from db_queries import sql as sql

APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s', level=logging.DEBUG)
#logging.disable(logging.INFO) # Uncomment to disable info messages


config = load_config.load_config()
db_user = config.db_user
db_pass = config.db_pass
db_base = config.db_base
db_host = config.db_host


class borrowers():
  def __init__(self,bid = 0):
    builder = gtk.Builder()
    builder.add_from_file("ui/borrower_dialog.glade")
    self.window = builder.get_object("dialog1")
    self.name = builder.get_object("entry1")
    self.contact = builder.get_object("entry2")
    self.notes = builder.get_object("entry3")
    self.status = builder.get_object("status_label")
    self.button_cancel = builder.get_object("button_cancel")
    builder.connect_signals(self)
    self.bid = bid
    logging.info(bid)
    self.populate()

  def run(self):
    self.window.run()
    #self.populate()
    self.window.destroy()
    
  def populate(self):
    '''If we are passed a bid > 0 populate the dialog.

    '''
    db_query = sql()
    logging.info(self.bid)
    if self.bid > 0:
      result = db_query.get_one_borrower(self.bid)
      self.name.set_text(result[1])
      self.contact.set_text(result[2])
      self.notes.set_text(str(result[3]))



  def on_button_add_clicked(self, widget):
    ''' Add a borrower to the database.

    '''
    db_query = sql()
    logging.info("Added a borrower")
    logging.info(self.name.get_text())
    if len(self.name.get_text()) > 0:
      if self.bid == 0:
        db_query.add_new_borrower(self.name.get_text(),self.contact.get_text(), self.notes.get_text())
      else:
        db_query.update_borrower(self.name.get_text(),self.contact.get_text(), self.notes.get_text(), self.bid)
      self.status.set_text("Added a borrower.")
    else:
      logging.info("Nothing to add.")
      self.status.set_text("Nothing to add.")
    self.button_cancel.set_label(_("CLOSE"))

  def on_button_print_clicked(self,widget):
    ''' Create a pdf of the current users.  Optionally open the default
    reader for viewing and printing of the document.

    '''
    db_query = sql()
    try:
      import time, os
      from reportlab.lib.enums import TA_LEFT
      from reportlab.lib.pagesizes import A4
      from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
      from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
      from reportlab.lib.units import mm
    except ImportError, e:
      print e
      messages.pop_info(e)
      return
    
    
    filename = "borrowers.pdf"
    doc = SimpleDocTemplate(filename,pagesize=A4,
                            rightMargin=72,leftMargin=72,
                            topMargin=72,bottomMargin=18)
    Story=[]
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_LEFT))
    Story.append(Paragraph("Book Borrowers and their Books", styles["Normal"]))
    Story.append(Spacer(1, 12))

    ptext = ''
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))
    # Get the data
    db_query.get_borrowers_borrowed_books()
    for row in result:
      ptext = row[2] + " -- " + row[1] + " -- " + row[0] + " -- Borrowed: " + row[3].strftime('%Y %b %d')
      Story.append(Paragraph(ptext, styles["Normal"]))
    
    doc.build(Story)

    # Open a reader
    if os.name == "nt": # Windoze
      os.filestart(filename)
    elif os.name == "posix": # Linux
      os.system("/usr/bin/xdg-open " + filename)


  def button_cancel_clicked(self, widget):
    if __name__ == "__main__":
      gtk.main_quit()
      quit(0)
    else:
      #del db, cur
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
  app.run()
  #app.on_button_print_clicked(None)
