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

import zbar
import webbrowser
from biblio.webquery.xisbn import XisbnQuery
import biblio.webquery
import platform
import MySQLdb
import sys, os
import load_config as config
import logging
#import load_config as gconf_config
import gettext
import book
import datetime
from db_queries import sql as sql
import getpass


_ = gettext.gettext

logger = logging.getLogger("barscan")
logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s', level=logging.DEBUG)


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
#config = gconf_config.gconf_config()
# Read the config file
config = config.load_config() # For file based config
db_user = config.db_user
db_pass = config.db_pass
db_base = config.db_base
db_host = config.db_host
# Do we produce a QR code?
QR_CODE = config.qr_code


if QR_CODE:
  try:
    import qrencode # Only if available AND required
  except:
    QR_CODE = False

system = platform.system() # What are we running on.

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
    self.gladefile = os.path.join(os.path.dirname(__file__),"ui/gui.glade")
    builder.add_from_file(self.gladefile)
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
    TODO: Need to find better way to enumerate cameras.
    TODO: Need to find how to do this on Windoze, gstreamer for both?
    '''
    db_query = sql()
    device = None
    buff = self.text_view.get_buffer()
    buff.set_text(_("To begin press scan."))
    self.text_view.set_buffer(buff)
    # This isn't really good enough but...
    if system == "Linux":
      try: device = '/dev/video0'
      except: device = '/dev/video1'
    elif system == "Windows":
      # TODO: Windows camera stuff.
      pass
    else:
      # TODO: Write code for other systems.  Others can do this perhaps.
      buff.set_text (_("Cannot find camera on this Operating system."))
      self.text_view.set_buffer(buff)
      return 
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
        try:
          import amazonlookup
          dvd_search = amazonlookup.DVDlookup()
          if dvd_search.lookup(bar) != 1:
            buff.insert_at_cursor (_("Found DVD:\n"))
            buff.insert_at_cursor(str(dvd_search.Title) + "\n")
            buff.insert_at_cursor(str(dvd_search.Director))
            self.text_view.set_buffer(buff)
            self.abook.title = str(dvd_search.Title)
            self.abook.authors = str(dvd_search.Director) # This isn't perfect and maybe I should use K-V pairs?
            self.abook.mtype = str(dvd_search.ProductGroup)
            self.abook.id = str(bar)
            self.abook.year = 0 # Should be available but ...
          else: # Do a CD search
            buff.set_text (_("No DVDs.\n Searching for CDs\n"))
            self.text_view.set_buffer(buff)
            cd_search = amazonlookup.CDlookup() # Should be able to get more data from freedb.org
            if cd_search.lookup(bar) != 1 and cd_search.Title != '' :
              buff.insert_at_cursor(_("CD Found:\n"))
              self.text_view.set_buffer(buff)
              buff.insert_at_cursor(str(cd_search.Title) + "\n")
              buff.insert_at_cursor(str(cd_search.Artist))
              self.abook.title = str(cd_search.Title)
              self.abook.authors = str(cd_search.Artist)
              self.abook.mtype = str(cd_search.ProductGroup)
              self.abook.id = str(bar)
              self.abook.year = 0 # Should be available but ... 
        except: 
          buff.set_text (_("Could not lookup DVD on Amazon"))
          self.text_view.set_buffer(buff)
        #return
        
    # DONE Check if exists and increment book count if so.
    count = db_query.get_book_count_by_isbn(bar)['count']
    logger.info(count)
    if count > 0:
      buff.insert_at_cursor (_("\n\nYou already have " + str(count) + " in the database!\n"))
    self.text_view.set_buffer(buff)
    del buff, device


  def make_qr_code(self):
    '''
    Make a QR code for the book.  This could be useful somewhere I guess.
    It contains the ISBN, title and Authors of the book.
    Maybe it should contain the owner name , yes YOU, just in case you ever need
    to split up you and your parter's books.  You know why that might be
    needed.
    TODO. Maybe print the ISBN too.
          Change output dir
    DONE: Store images in the DB
    '''
    from db_queries import sql as sql
    db_query = sql()
    if QR_CODE:
      import getpass
      user = getpass.getuser()
      # Do the QR thang
      qr_data = 'ISBN:'+ str(self.abook.id) \
        + ';TITLE:' +  str(self.abook.title) \
        + ';AUTHORS:' + str(self.abook.authors) \
        + ";OWNER:" + user
      qr = qrencode.encode(qr_data)
      # Rescale using the size and add a 1 px border
      size = qr[1]

      qr = qrencode.encode_scaled(qr_data, (size*3)+2)
      img = qr[2]

      count = db_query.get_qrcode_count(self.abook.id)
      if count == 0:
        sql = 'INSERT INTO qrcodes(caption,img) VALUES(%s,%s)' # But how to get them back out again?  See below.
        args = ("ISBN: " + str(self.abook.id), img, )
        self.cur.execute (sql, args)
        self.db.commit()
      #pixmap,mask = pixbuf.render_pixmap_and_mask()
      #img.save('tmp.png', 'png')
      # Display it in the GUI
      #self.qr_img.set_from_image(img, mask) # may need to be gtk.image
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
    db_query = sql()
    # Remove a scanned book from the database.
    print "You removed this book."
    buff = self.text_view.get_buffer()
    try:
      self.cur.execute("DELETE FROM books WHERE isbn = %s;", str(self.abook.isbn))
      buff.insert_at_cursor (_( "\n\nYou removed this book."))
      self.text_view.set_buffer(buff)
    except:
      buff.insert_at_cursor (_( "\n\nCould not remove book!"))
      self.text_view.set_buffer(buff)
  
  def get_cd_tracks(self):
    ''' Get the cd details and store then in the DB.  We can use book class
    for rest of details.
    
    '''
    import freebase_lookup
    cd_data = freebase_lookup.freebase_cd()
    year = ''
    artist = ''
    album = ''
    al_dat = cd_data.get_album_id(self.abook.authors, self.abook.title)
    alid = al_dat[0]
    self.abook.year = int(al_dat[1].strip('[] ')) # Global(ish)
    logging.info(self.abook.year)
    tracks = cd_data.get_tracks(alid) # Returns a dictionary
    album = '' # TODO: Do this maybe as we can get the album date here
    
    for track in tracks: ## DEBUG: remove me later ##
      print track
    
    return tracks # Dictionary e.g. {'index': 12, 'length': 214.773, 'name': 'The Kick Inside'}

  def on_button_add_clicked(self, widget):
    '''
    Add a book, DVD or CD to the database.
    Arguably I could have used "ON DUPLICATE KEY", using the isbn as the key,
    here but it may happen that several books will have empty isbn values
    for instance, books printed before ISBN was invented.
    result = self.cur.execute ("SELECT count(isbn) as count FROM books WHERE isbn = %s;",
         str(self.abook.isbn))
    TODO Move all DB stuff to db_queries.py
    '''
    db_query = sql()
    a_name = str(self.abook.authors)
    a_mtype = str(self.abook.mtype)
    self.cur.execute("INSERT IGNORE INTO authors(name) values(%s);", [a_name])
    self.cur.execute("SELECT * FROM authors WHERE name=%s;",[a_name])
    result = self.cur.fetchall()
    author_id = result[0][0]
    values = (str(self.abook.title), str(self.abook.authors), str(self.abook.id),
        str(self.abook.abstract),self.abook.year,
        str(self.abook.publisher),str(self.abook.city),1,author_id,
        datetime.date.today(), str(self.abook.mtype))
    self.cur.execute("INSERT INTO books\
    (title, author, isbn,abstract, year, publisher, city, copies, author_id, add_date,mtype)\
    VALUES(%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s);", values)
    self.db.commit()
    
    # Get and insert the track listing
    # TODO: Move DB stuff to db_queries
    if str(self.abook.mtype) == 'Music': 
      self.cur.execute("SELECT id FROM books WHERE title=%s AND author=%s LIMIT 1;",\
            [str(self.abook.title), str(self.abook.authors)])
      res = self.cur.fetchall()
      cdid = res[0][0]
      tracks = self.get_cd_tracks()
      for track in tracks:
        self.cur.execute("INSERT INTO cd_tracks(cdid,tracknum,trackname,tracklen) \
            VALUES(%s,%s,%s,%s);", \
            [cdid, track['index'],track['name'],str(track['length'])])
        #self.db.commit()
      self.cur.execute("UPDATE books SET year = %s WHERE id = %s",[self.abook.year, cdid])
      self.db.commit()
    buff = self.text_view.get_buffer()
    buff.insert_at_cursor(_( "\n\nYou added this " + str(self.abook.mtype) + ".\n"))
    self.text_view.set_buffer(buff)
    self.make_qr_code()
    print "You added this", str(self.abook.mtype)


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

