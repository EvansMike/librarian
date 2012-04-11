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
Usage:
printf "$(python barscan.py)"
Requires:
zbar-pygtk
biblio.webquery
'''
# TODO we don't always get a title and author from a single lookup
# need to test this and try alternate lookup.
# TODO Needs a live internet connection!  No good for portable apps. without wireless.
#   Need a db update app.
#   Change author name parsing.  Also parse to authors table for future normalisation.
#     Biblio lookup returns a list of authors.
# TODO: Add DVD and CDDB lookup

import zbar
import webbrowser
from biblio.webquery.xisbn import XisbnQuery
import biblio.webquery
import qrencode
import MySQLdb
import sys
#import ConfigParser
import logging
import gconf_config
import gettext
import book
import datetime

_ = gettext.gettext

logger = logging.getLogger("barscan")
logging.basicConfig(format='%(module)s: %(levelname)s:%(message)s: LINE %(lineno)d', level=logging.DEBUG)

# Do we produce a QR code?
QR_CODE = True

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

#config = gconf_config.load_config()
config = gconf_config.gconf_config()
db_user = config.db_user
db_pass = config.db_pass
db_base = config.db_base
db_host = config.db_host



################## BEGIN scanner class #################################
class scanner:
  ''' Scanner class. Scans books, queries isbndb and adds book to database,
  or CSV.  This will work stand alone hence the separate database query
  and inserts that don't rely on librarian.py.

  '''
  def __init__(self):
    self.abook = book.book()
    qr_img = ""
    #vid_dev = "/dev/video0" # Need to scan for this and make it work in windows?
    builder = gtk.Builder()
    builder.add_from_file("ui/gui.glade")
    self.window = builder.get_object("window1")
    builder.connect_signals(self)
    self.text_view = builder.get_object("textview1")
    self.qr_img = builder.get_object("image1")
    self.cur = None
    try:
      self.db = MySQLdb.connect(host=db_host, db=db_base,  passwd = db_pass);
    except:
      print (_("No database connection.  Check config file"))
      self.db = False
    if self.db:
      self.cur = self.db.cursor()




  def on_button_scan_clicked(self, widget):
    ''' Do the scan, query the database and store the results.

    '''
    buff = self.text_view.get_buffer()
    buff.set_text(_("To begin press scan."))
    self.text_view.set_buffer(buff)
    device = '/dev/video0'
    # create a Processor
    proc = zbar.Processor()
    # configure the Processor
    proc.parse_config('enable')
    buff = self.text_view.get_buffer()
    # enable the preview window
    try: proc.init(device)
    except:
      buff.set_text (_("No camera present!"))
      self.text_view.set_buffer(buff)
      return
    proc.visible = True
    # read at least one barcode (or until window closed)
    proc.process_one()

    # hide the preview window
    proc.visible = False
    logging.info(proc.results)
    

    for symbol in proc.results:
      bar = symbol.data
      logging.info(bar)
      if self.abook.webquery(bar) != 1:
        logging.info(self.abook.print_book())
        buff.set_text(self.abook.print_book())
        return
      else: # Try for a DVD lookup
        buff.set_text (_("No data returned, retry?"))
        self.text_view.set_buffer(buff)
        #logging.info(self.abook.print_book())
        buff.set_text (_("Searching for DVDs\n"))
        self.text_view.set_buffer(buff)
        import amazonlookup
        dvd_search = amazonlookup.DVDlookup()
        if dvd_search.lookup(bar) != 1:
          buff.set_text (_("Found DVD\n"))
          buff.set_text(dvd_search.title)
          self.text_view.set_buffer(buff)
        else:
          buff.set_text (_("No DVDs.\n Searching for CDs\n"))
          self.text_view.set_buffer(buff)
          cd_search = amazonlookup.CDlookup()
          if cd_search.lookup(bar) != 1:
            buff.set_text (_("CD Found\n"))
            self.text_view.set_buffer(buff)
        #return
        
    # DONE Check if exists and increment book count if so.
    self.cur.execute("SELECT COUNT(*) as count FROM books WHERE isbn = %s;",bar)
    count = self.cur.fetchone()[0]
    if count > 0:
      buff.insert_at_cursor (_("\n\nYou already have " + str(count) + " in the database!\n"))
    self.text_view.set_buffer(buff)
    del buff


  def make_qr_code(self):
    '''
    Make a QR code for the book.  This could be useful somewhere I guess.
    It contains the ISBN, title and Authors of the book.
    Maybe it should contain the owner name , yes YOU, just in case you ever need
    to split up you and your parter's books.  You know why that might be
    needed.
    TODO. Maybe print the ISBN too.
          Change output dir
    TODO: Store images in the DB
    '''
    if QR_CODE:
      import getpass
      user = getpass.getuser()
      # Do the QR thang
      qr_data = 'ISBN:'+ str(self.abook.id) \
        + ' TITLE:' +  str(self.abook.title) \
        + ' AUTHORS:' + str(self.abook.authors) \
        + " OWNER: " + user
      qr = qrencode.encode(qr_data)
      # Rescale using the size and add a 1 px border
      size = qr[1]

      qr = qrencode.encode_scaled(qr_data, (size*3)+2)
      img = qr[2]
      self.cur.execute("SELECT COUNT(*) as count FROM qrcodes WHERE caption = %s;","ISBN: "+str(self.abook.id))
      count = self.cur.fetchone()[0]
      if count == 0:
        sql = 'INSERT INTO qrcodes(caption,img) VALUES(%s,%s)' # But how to get them back out again?  See below.
        args = ("ISBN: " + str(self.abook.id), img, )
        self.cur.execute (sql, args)
        self.db.commit()
      #img.save('tmp.png', 'png')
      # Display it in the GUI
      #self.qr_img.set_from_image(img) # may need to be gtk.image
      #self.qr_img.set_from_file('tmp.png') # fix this, I don't like using tmp files
      
      '''
      Example data extraction code
      cursor.execute("SELECT Data FROM Images LIMIT 1")
      fout = open('image.png','wb')
      fout.write(cursor.fetchone()[0])
      fout.close()
      '''



  def on_button_remove_clicked(self, widget):
    '''Remove a book from the database.

    '''
    # Remove a scanned book from the database.  Why?
    print "You removed this book."
    buff = self.text_view.get_buffer()
    try:
      self.cur.execute("DELETE FROM books WHERE isbn = %s;", str(self.abook.isbn))
      buff.insert_at_cursor (_( "\n\nYou removed this book."))
      self.text_view.set_buffer(buff)
    except:
      buff.insert_at_cursor (_( "\n\nCould not remove book!"))
      self.text_view.set_buffer(buff)

  def on_button_add_clicked(self, widget):
    '''
    Add a book, DVD or CD to the database.
    DONE Check if exists and increment copy counter if so.
    Arguably I could have used "ON DUPLICATE KEY", using the isbn as the key,
    here but it may happen that several books will have empty isbn values
    for instance, books printed before ISBN was invented.
    result = self.cur.execute ("SELECT count(isbn) as count FROM books WHERE isbn = %s;",
         str(self.abook.isbn))
    TODO: Also insert DVDs and CDs, I guess, re-use some of the fields.
    '''
    a_name = str(self.abook.authors)
    self.cur.execute("INSERT IGNORE INTO authors(name) values(%s);", [a_name])
    self.cur.execute("SELECT * FROM authors WHERE name=%s;",[a_name])
    result = self.cur.fetchall()
    author_id = result[0][0]
    values = (str(self.abook.title), str(self.abook.authors), str(self.abook.id),
        str(self.abook.abstract),str(self.abook.year),
        str(self.abook.publisher),str(self.abook.city),1,author_id,
        datetime.date.today(), "Book")
    self.cur.execute("INSERT INTO books\
    (title, author, isbn,abstract, year, publisher, city, copies, author_id, add_date,mtype)\
    VALUES(%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s);", values)

    buff = self.text_view.get_buffer()
    buff.insert_at_cursor(_( "\n\nYou added this " + "book" + "."))
    self.text_view.set_buffer(buff)
    self.make_qr_code()
    print "You added this book."


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
      del self
    pass
################## END scanner class ###################################



# we start here.
if __name__ == "__main__":
	app = scanner()
	gtk.main()

