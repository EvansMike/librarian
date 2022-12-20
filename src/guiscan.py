#!/bin/env python3
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

# TODO Needs a live internet connection!  No good for portable apps. without wireless.
#   Need a db update app.
#     Biblio lookup returns a list of authors.
import evdev
from evdev import categorize
import faulthandler
import pyzbar as zbar
import webbrowser
import platform
import MySQLdb
import sys, os
from .import load_config as config
import logging
import gettext
from . import book
import datetime
from .db_queries import sql as sql
import getpass
import threading
import signal
import barcodenumber

_ = gettext.gettext

logger = logging.getLogger("barscan")
logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s', level=logging.DEBUG)
DEBUG = logging.debug
INFO = logging.info


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk

dev = None
ep = None


# Read the config file
config = config.load_config() # For file based config
db_user = config.db_user
db_pass = config.db_pass
db_base = config.db_base
db_host = config.db_host
# Do we produce a QR code?
QR_CODE = config.qr_code

# For DVD lookups etc.
upc_key = config.upc_key


if QR_CODE:
    try:
        import qrencode # Only if available AND required
    except:
        QR_CODE = False

system = platform.system() # What are we running on.

################## BEGIN scanner class #################################
class Scanner(object):
    ''' Scanner class. Scans books, queries isbndb and adds book to database,
    or CSV.  This will work stand alone hence the separate database query
    and inserts that don't rely on librarian.py.

    '''
    def __init__(self):
        faulthandler.enable()
        signal.signal(signal.SIGINT, self.on_sig_int)
        self.closing = False
        self.dev = None
        self.ep = None
        self.abook = book.Book()
        qr_img = ""
        #vid_dev = "/dev/video0" # Need to scan for this and make it work in windows?
        builder = gtk.Builder()
        self.gladefile = os.path.join(os.path.dirname(__file__),"ui/gui.glade")
        builder.add_from_file(self.gladefile)
        self.window = builder.get_object("window1")
        builder.connect_signals(self)
        self.text_view = builder.get_object("textview1")
        self.qr_img = builder.get_object("image1")
        self.button_scan = builder.get_object("button_scan")
        self.cur = None
        self.owner = getpass.getuser() # Assume the logged in person owns the book.
        try:
            self.db = MySQLdb.connect(user=db_user, host=db_host, db=db_base,  passwd = db_pass);
        except:
            print (_("No database connection.  Check config file"))
            self.db = False
        if self.db:
            self.cur = self.db.cursor()
        self.scanner = None
        DEBUG(self.scanner)
        self.scanner = self.find_hid_scanner()
        DEBUG(self.scanner)
        self.window.show()
        if self.scanner:
            self.button_scan.set_sensitive(False)
            thread = threading.Thread(target=self.real_scanner)
            thread.setDaemon = True
            thread.start()
        else:
            # Use a web cam TODO
            pass
        gtk.main()



################################################################################
    def find_hid_scanner(self):
        '''
        Do make sure to close the scanner on exit and exit the hid api when the window closes.
        by putting:
        self.scanner.close()
        hid.hidapi_exit()
        in the window close method.
        I only have the one scanner to test this adding scanners will be up to
        future coders.
        There should probably be an array of 'product_id' to match against, defined above somewhere.
        '''
        device_name = "Symbol Bar Code Scanner"
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        for d in devices:
            DEBUG(d)
            if device_name in d.name:
                print("Found device " + d.name)
                device = d
                self.scanner = device
                return device
        return None

################################################################################
    def real_scanner(self):
        '''
        This will run when a real scanner is attached
        '''
        barcode = ""
        print ("Reading barcodes from device")
        while True:
            event = self.scanner.read_one()
            if event != None:
                if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                    keycode = categorize(event).keycode
                    #DEBUG(keycode)
                    if keycode == 'KEY_ENTER':
                        #DEBUG(barcode)
                        #DEBUG(barcodenumber.check_code_upc(barcode))
                        #DEBUG(barcodenumber.check_code_isbn(barcode))
                        #DEBUG(barcodenumber.check_code_ean13(barcode))
                        if barcodenumber.check_code_isbn(barcode):
                            self.add_book(None, barcode)
                            break
                        elif barcodenumber.check_code_ean13(barcode):
                            self.add_dvd(None, barcode)
                            INFO("Not an ISBN, a DVD or CD perhaps")
                            break
                    else:
                        barcode += keycode[4:]
        return

                
################################################################################
    def on_button_scan_clicked(self, widget):
        ''' Do the scan, query the database and store the results.
        TODO: Need to find better way to enumerate cameras.
        TODO: Need to find how to do this on Windoze, gstreamer for both?
        TODO: If we already have a book display its location.
        '''
        ## Is there a real scanner attached?
        if self.scanner:
            return
        proc = None
        db_query = sql()
        device = None
        buff = self.text_view.get_buffer()
        buff.set_text(_("To begin press scan."))
        self.text_view.set_buffer(buff)
        if system == "Linux":
            try:
                for i in self.getVideoDevices(): # Get the first found device.
                    device = i[1]
                    if device: break
            except:
                buff.set_text (_("Cannot find camera on this Operating system."))
                self.text_view.set_buffer(buff)
                del buff,proc
                return ## No video device
        elif system == "Windows":
                # TODO: Windows camera stuff.
            pass
        else:
            # TODO: Write code for other systems.  Others can do this perhaps.
            buff.set_text (_("Cannot find camera on this Operating system."))
            self.text_view.set_buffer(buff)
            del buff,proc
            return
        INFO(device)
        # create a Processor
        proc = zbar.Processor()
        # configure the Processor
        proc.parse_config('enable')
        buff = self.text_view.get_buffer()
        # enable the preview window
        proc.init(device)
        proc.visible = True
        # Read one barcode (or until window closed)
        if proc.process_one():
            logging.info(proc.results)
            for symbol in proc.results:
                bar = symbol.data
                self.add_book(proc, bar)

                
################################################################################
    def add_book(self, proc, isbn):
        '''
        TODO: This needs refactoring. See Bug-344 for why.
        '''
        DEBUG(isbn)
        db_query = sql()
        # Check if exists
        data = db_query.get_by_isbn(isbn)
        self.abook.id = ''
        if data: # It does exist in the DB.
            count = len(data)
            DEBUG(count) 
            try:
                location = self.getBookLocation(isbn)
                DEBUG(location)
                if count > 0:
                    buff = self.text_view.get_buffer()
                    buff.set_text("")
                    self.text_view.set_buffer(buff)
                    title = data[0]['title']
                    author = data[0]['author']
                    self.abook.id = data[0]['id']
                    self.abook.isbn = isbn
                    buff.insert_at_cursor (_(f"{title} by {author}\nYou already have {str(count)} copies!\n\
                        Located at:\n{location}\n"))
                    self.text_view.set_buffer(buff)
            except Exception as e:
                raise
                DEBUG(e)
        else: # It doesn't exist in the DB.
            try: 
                if self.abook.webquery(isbn) != None:
                    INFO(self.abook.print_book())
                    buff = self.text_view.get_buffer()
                    buff.set_text(self.abook.print_book())
                    self.text_view.set_buffer(buff)
        
                else:
                    buff = self.text_view.get_buffer()
                    buff.set_text (_("No data returned, retry?"))
                    self.text_view.set_buffer(buff)
                # hide the preview window
                if proc: proc.visible = False
            except Exception as e:
                raise
                buff = self.text_view.get_buffer()
                buff.set_text(f"No book with ISBN {isbn} found")
                #buff.set_text(repr(e.message))
                self.text_view.set_buffer(buff)
                DEBUG(e)
        self.real_scanner()
        

################################################################################
    def add_dvd(self, proc, ean):
        '''
        Add the DVD and open the dialog to edit the details.
        @param = None
        @param ean
        '''
        # Check if exists and increment book count if so.
        db_query = sql()
        count = db_query.get_book_count_by_isbn(ean)
        DEBUG(count)
        buff = self.text_view.get_buffer()
        buff.set_text("")
        self.text_view.set_buffer(buff)
        if count == 0:
            from . import upc_lookup
            lookup = upc_lookup.UPCLookup()
            data = lookup.get_response(ean, upc_key)
            DEBUG(data)
            if data:
                buff.set_text(f"{data['description']}")
                self.text_view.set_buffer(buff)
                self.abook.title = data['description']
                self.abook.isbn = ean
                self.abook.mtype = data['mtype']
            else:
                buff.set_text(f"This EAN: {ean}, has not been registered with\nhttps://www.upcdatabase.com\nPlease consider adding it to their database.")
                self.text_view.set_buffer(buff)
                self.abook.isbn = ean
                self.abook.mtype = 'DVD'
                self.abook.title = ''
        else:
            data = db_query.get_by_isbn(ean)[0]
            buff.set_text(f"This item already exists in the database\n{data['title']}, {data['mtype']}")
            self.text_view.set_buffer(buff)
            #self.abook.title = data['title']
            #self.abook.isbn = data['ean']
            #self.abook.mtype = 'DVD'
        self.abook.owner = self.owner
        self.real_scanner()
       

################################################################################
    def getBookLocation(self, isbn):
        db_query = sql()
        location_string = ""
        result = db_query.get_location_by_isbn(isbn) # Could be multiple but unlikely
        DEBUG(result)
        for row in result:
            print (row)
            location_string += f"{row['room']} : {row['shelf']} \n"
        return location_string


     ###############################################################################
    ''' '''
    def getVideoDevices(self):
        ''' Enumerate all connected video devices. '''
        videoDevices = []
        for dev in os.listdir("/dev/v4l/by-id"):
            try:
                yield([
                    " ".join(dev.split("-")[1].split("_")),
                    os.path.join("/dev/v4l/by-id", dev)
                ])
            except:
                yield([
                    dev,
                    os.path.join("/dev/v4l/by-id", dev)
                ])
            videoDevices.append(dev)
        DEBUG( videoDevices)
        return videoDevices


################################################################################
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
        from .db_queries import sql as sql
        db_query = sql()
        if QR_CODE:
            import getpass
            user = getpass.getuser()
            # Do the QR thang
            qr_data = f"ISBN: {str(self.abook.id)}; \
                TITLE: {str(self.abook.title)}; \
                AUTHORS: {str(self.abook.authors)}; \
                OWNER: {user};"
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


     ###############################################################################
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
            print (track)

        return tracks # Dictionary e.g. {'index': 12, 'length': 214.773, 'name': 'The Kick Inside'}


################################################################################
    def on_button_edit_clicked(self, widget):
        '''
        Process the book and open the add edit dialog.
        '''
        from .add_edit import add_edit
        buff = self.text_view.get_buffer()
        db_query = sql()

        # If a book in already in the DB do this
        if self.abook.id != '':
            DEBUG(self.abook.id)
            adder = add_edit()
            adder.populate(self.abook.id)
            adder.display()
            
        else: 
            # Book object should be populated but not in the DB yet.
            last_id = db_query.insert_book_object(self.abook)
            DEBUG(last_id);
            # We should check this for success
            if last_id == 0:
                print ("Failed to add book to database.")
                buff.insert_at_cursor (_( "\n\nCould not add this book!"))
                self.text_view.set_buffer(buff)
                return
            buff = self.text_view.get_buffer()
            buff.insert_at_cursor(_( f"\n\nYou added this {str(self.abook.mtype)}.\n"))
            self.text_view.set_buffer(buff)
            self.make_qr_code()
            INFO (f"You have added this {str(self.abook.mtype)} to the database.")
            # Open add_edit so we can add any more details like location.
            adder = add_edit()
            adder.populate(last_id)
            adder.display()
            
        # Clear the display and create a fresh book.
        buff.set_text("")
        self.text_view.set_buffer(buff)
        self.abook = book.Book() # New fresh book.



################################################################################
    def append_text(self, text):
        pass


################################################################################
    def get_book_data(self):
        #self.scanner
        pass

    def on_sig_int(self):
        self.scanner.close()
        gtk_main_quit(False)
################################################################################
    def gtk_main_quit(self, widget):
        # Quit when we destroy the GUI only if main application, else don't quit
        if __name__ == "__main__":
            print("Quitting GUIScan.")
            try:
                self.scanner.close()
            except:
                pass
            gtk.main_quit()
            self.closing = True
            quit(0)
        else:
            try:
                self.scanner.close()
            except:
                pass
            self.window.hide()
            del self
        pass
################## END scanner class ###########################################



# we start here.
if __name__ == "__main__":
    #pass
    app = Scanner()
