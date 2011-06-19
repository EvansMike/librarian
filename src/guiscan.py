#!/bin/env python
'''
Usage:
printf "$(python barscan.py)"
Requires:
zbar-pygtk
biblio.webquery
'''
# TODO we don't always get a title and author from a single lookup
# need to test this and try alternate lookup.
# TODO Needs a live internet connection!  No good for portable apps. without wireless.
# Need a db update app.

import zbar
import webbrowser
from biblio.webquery.xisbn import XisbnQuery
import biblio.webquery
import qrencode
import MySQLdb
import sys
import ConfigParser
import logging
import load_config
import gettext

_ = gettext.gettext

logger = logging.getLogger("barscan")
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

config = load_config.load_config()
db_user = config.db_user
db_pass = config.db_pass
db_base = config.db_base
db_host = config.db_host



################## BEGIN scanner class #################################
class scanner:
  ''' Scanner class. Scans books, queries isbndb and adds book to database, or CSV'''
  def __init__(self):
    qr_img = ""
    vid_dev = "/dev/video0" # Need to scan for this and make it work in windows?
    builder = gtk.Builder()
    builder.add_from_file("ui/gui.glade")
    self.window = builder.get_object("window1")
    builder.connect_signals(self)
    self.text_view = builder.get_object("textview1")
    self.qr_img = builder.get_object("image1")
    self.bibrecord = biblio.webquery.bibrecord.BibRecord
    try:
      self.db = MySQLdb.connect(db=db_base,  passwd = db_pass);
    except:
      print (_("No database connection.  Check ")) + config_file
      self.db = False
    if self.db:
      self.cur = self.db.cursor()

    scanner = zbar.Processor()
    buff = self.text_view.get_buffer()
    buff.set_text(_("To begin press scan."))
    self.text_view.set_buffer(buff)
    try: self.device = '/dev/video0'
    except:self.device = '/dev/video1'
    # create a Processor
    self.proc = zbar.Processor()
    # configure the Processor
    self.proc.parse_config('enable')
    # initialize the Processor
    self.proc.init(self.device)
    gtk.main()


  def on_button_scan_clicked(self, widget):
    buff = self.text_view.get_buffer()
    # enable the preview window
    self.proc.init(self.device)
    self.proc.visible = True
    # read at least one barcode (or until window closed)
    self.proc.process_one()
    # hide the preview window
    self.proc.visible = False
    try:
      for symbol in self.proc.results:
        bar = symbol.data
        logging.info(bar)
        a = XisbnQuery()
        book = a.query_bibdata_by_isbn(bar) # TODO: Make work for CDs and DVDs
        nn = book.pop()
        self.bibrecord = nn
        print nn.id
        print nn.title
        print nn.authors[0]
        print nn.abstract
        print nn.type
        print nn.publisher
        print nn.city
        print nn.year
        logging.info(nn.authors)
        buff.set_text( str(nn.id) + "\n" + str(nn.title) +  "\n" + str(nn.authors[0]))
    except:
      buff.set_text (_("Dodgy scan, retry?"))
      self.text_view.set_buffer(buff)
      return
    # DONE Check if exists and increment book count if so.
    self.cur.execute("SELECT COUNT(*) as count FROM books WHERE isbn = %s;",str(nn.id))
    count = self.cur.fetchone()[0]
    if count > 0:
      buff.insert_at_cursor (_("\n\nYou already have " + str(count) + " in the database!\n"))
    self.text_view.set_buffer(buff)

    # Do the QR thang
    qr = qrencode.encode('ISBN:'+ bar + ' TITLE:' + str(nn.title) + ' AUTHORS:' + str(nn.authors))
    # Rescale using the size and add a 1 px border
    size = qr[1]
    qr = qrencode.encode_scaled('ISBN:'+ bar + ' TITLE:' + str(nn.title) + ' AUTHORS:' + str(nn.authors), (size*3)+2)
    img = qr[2]
    img.save('../ISBN:' + bar + '.png', 'png')
    self.qr_img.set_from_file('../ISBN:' + bar + '.png')

  def on_button_remove_clicked(self, widget):
    # Remove a scanned book from the database.  Why?
    print "You removed this book."
    buff = self.text_view.get_buffer()
    try:
      self.cur.execute("DELETE FROM books WHERE isbn = %s;", str(self.bibrecord.id))
      buff.insert_at_cursor (_( "\n\nYou removed this book."))
      self.text_view.set_buffer(buff)
    except:
      buff.insert_at_cursor (_( "\n\nCould not remove book!"))
      self.text_view.set_buffer(buff)

  def on_button_add_clicked(self, widget):

    #TODO Check if exists and increment copy counter if so.
    #try:
    result = self.cur.execute ("SELECT * FROM books WHERE isbn = %s;",str(self.bibrecord.id))
    logging.info(result)
    if result == 0 :
      self.cur.execute("INSERT INTO books(title, author, isbn,abstract, year, publisher, city, copies) VALUES(%s, %s, %s,%s,%s,%s,%s,%s);", \
    (str(self.bibrecord.title), str(self.bibrecord.authors), str(self.bibrecord.id), str(self.bibrecord.abstract),str(self.bibrecord.year),str(self.bibrecord.publisher),str(self.bibrecord.city),1))
    else:
      self.cur.execute("UPDATE books set copies = copies+1 WHERE isbn = %s;",str(self.bibrecord.id))
    buff = self.text_view.get_buffer()
    buff.insert_at_cursor(_( "\n\nYou added this book."))
    self.text_view.set_buffer(buff)
    print "You added this book."
    #except:
    #  buff = self.text_view.get_buffer()
    #  buff.insert_at_cursor( "\n\nBook add failed for some reason.")
    # print "Book add failed."

  def append_text(self, text):
    pass

  def get_book_data(self):
    #self.scanner
    pass


  def gtk_main_quit(self, widget):
    # Quit when we destroy the GUI only if main application, else don't quit
    if __name__ == "__main__":
      gtk.main_quit()
      quit(0)
    else:
      self.window.hide()
    pass
################## END scanner class ###################################



# we start here.
if __name__ == "__main__":
	app = scanner()
	#gtk.main()

