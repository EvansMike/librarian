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

import usb.core
import usb.util
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
import threading
import signal
import barcode

_ = gettext.gettext

logger = logging.getLogger("barscan")
logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s', level=logging.DEBUG)
DEBUG = logging.debug
INFO = logging.info


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
        idVendor, idProduct = self.find_scanner()
        self.dev, self.ep = self.init_scanner(idVendor, idProduct )
        self.window.show()
        if self.dev:
            self.button_scan.set_sensitive(False)
            gtk.gdk.threads_init()
            thread = threading.Thread(target=self.real_scanner)
            thread.setDaemon(True)
            thread.start()
        gtk.main()
        

################################################################################
    def get_scanner(self, widget, event):
        self.window.connect( "visibility-notify-event", self.null)
        self.dev, self.ep = self.find_scanner()
        if self.dev:
            self.real_scanner()
        usb.util.dispose_resources(self.dev)
    def null(self, widget, event):
        return


################################################################################
    def find_scanner(self):
        '''
        Get the scanner by name
        @return idVendor, idProduct
        '''
        idVendor = None
        idProduct = None
        devs = usb.core.find(find_all=True)
        for dev in devs:
            try:
                DEBUG(dev.product)
                if "Bar Code" in dev.product:
                    DEBUG(hex(dev.idVendor))
                    DEBUG(hex(dev.idProduct))
                    idVendor = dev.idVendor
                    idProduct = dev.idProduct
                    return idVendor, idProduct
            except:
                pass
        return idVendor, idProduct

        
################################################################################
    def init_scanner(self, vendor_id, product_id ):
        # find our scanner device
        dev = usb.core.find(idVendor = vendor_id, idProduct = product_id) 
        DEBUG(dev)
        if not dev:
            INFO("No scanner found!")
            return (None, None)
        dev.reset()
        # was it found ?
        if dev is None:
            INFO('Device not found (meaning it is disconnected)')
            return (None, None)
        # detach the kernel driver so we can use interface (one user per interface)
        if dev.is_kernel_driver_active(0):
            try:
                dev.detach_kernel_driver(0)
                INFO("kernel driver detached")
            except usb.core.USBError as e:
                sys.exit("Could not detach kernel driver: %s" % str(e))
                #dev.reset()
        # set the active configuration; with no arguments, the first configuration
        # will be the active one
        try:
            dev.set_configuration()
        except Exception as e:
            print e
        # get an endpoint instance
        cfg = dev.get_active_configuration()
        interface_number = cfg[(0, 0)].bInterfaceNumber
        alternate_setting = usb.control.get_interface(dev, interface_number)
        intf = usb.util.find_descriptor(
              cfg, bInterfaceNumber = interface_number,
              bAlternateSetting = alternate_setting
        )

        ep = usb.util.find_descriptor(
              intf,
              # match the first OUT endpoint
              custom_match = \
              lambda e: \
                  usb.util.endpoint_direction(e.bEndpointAddress) == \
                  usb.util.ENDPOINT_IN)
        assert ep is not None
        # We don't need the scan button with a real scanner, but...
        return (dev, ep)


################################################################################
    def real_scanner(self):
        '''
        This will run when a real scanner is attached
        '''
        import re
        lu = False
        INFO("Waiting to read...")
        st = None
        DATA_SIZE = 3
        while not self.closing:
            try:
                # read data
                data = self.dev.read(self.ep.bEndpointAddress, self.ep.wMaxPacketSize * 2, 1000)
                st = ''.join(chr(i) if i > 0 and i < 128 else '' for i in data)
                st = st.rstrip()[1:]

                if not lu:
                    INFO("Waiting to read...")
                lu = True
            except usb.core.USBError as e:
                if e.args == (110,'Operation timed out') and lu:
                    if len(data) < DATA_SIZE:
                        lu = False
                        continue
                    else:
                        st = 'Nope'
                        break   # Code lu
            if st:
                regex = re.compile('[^a-zA-Z0-9]')
                st = regex.sub('', st)
                DEBUG(st)
                if len(st) == 10:
                    try:
                        DEBUG(barcode.ISBN10(st).ean)
                        barcode.ISBN10(st).ean
                        self.add_book(None, st)
                    except:
                        DEBUG ("NOT an ISBN! Is this a DVD?")
                        self.add_dvd(None, st)
                        
                elif len(st) == 13:
                    try:
                        DEBUG(barcode.ISBN13(st).ean)
                        barcode.ISBN13(st).ean
                        self.add_book(None, st)
                    except:
                        DEBUG ("NOT an ISBN! Is this a DVD?")
                        self.add_dvd(None, st)
                    
                
################################################################################
    def on_button_scan_clicked(self, widget):
        ''' Do the scan, query the database and store the results.
        TODO: Need to find better way to enumerate cameras.
        TODO: Need to find how to do this on Windoze, gstreamer for both?
        TODO: If we already have a book display its location.
        '''
        ## Is there a real scanner attached?
        if self.dev:
            self.real_scanner()
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
            del buff,proc
            return
        proc.visible = True
        # Read one barcode (or until window closed)
        if proc.process_one():
            logging.info(proc.results)
            for symbol in proc.results:
                bar = symbol.data
                self.add_book(proc, bar)

                
################################################################################
    def add_book(self, proc, isbn):
        from add_edit import add_edit
        #buff = self.text_view.get_buffer()
        DEBUG(isbn)
        db_query = sql()
        # Check if exists and increment book count if so.
        count = db_query.get_book_count_by_isbn(isbn)
        DEBUG(count)
        if count:
            try:
                location = self.getBookLocation(isbn)
                DEBUG(location)
                if count > 0 and location != None:
                    buff = self.text_view.get_buffer()
                    buff.insert_at_cursor (_("You already have " \
                        + str(count) \
                        + " copies in the database!\n It's located at: " \
                        + location \
                        + ".\n"))
                    self.text_view.set_buffer(buff)
                    return
            except Exception as e:
                DEBUG(e)
        try: 
            if self.abook.webquery(isbn) != None:
                INFO(self.abook.print_book())
                buff = self.text_view.get_buffer()
                buff.set_text(self.abook.print_book())
                self.text_view.set_buffer(buff)
            else:
                buff.set_text (_("No data returned, retry?"))
                self.text_view.set_buffer(buff)
            # hide the preview window
            if proc: proc.visible = False
        except Exception as e:
            buff = self.text_view.get_buffer()
            buff.set_text("No book with ISBN " + isbn + " found")
            #buff.set_text(repr(e.message))
            self.text_view.set_buffer(buff)
            DEBUG(e)
        self.gtk_main_quit(self, None)
        

################################################################################
    def add_dvd(self, proc, ean8):
        '''
        Add the DVD and open the dialog to edit the details.
        @param None
        @param ean8
        '''
        from add_edit import add_edit
        
        db_query = sql()
        dvd = db_query.get_by_isbn(ean8)
        if dvd:
            DEBUG(dvd)
            adder = add_edit()
            adder.populate(dvd['id'])
        else:
            import upc_lookup
            
            lookup = upc_lookup.UPCLookup()
            data = lookup.get_response(ean8).json()
            try:
                adder = add_edit()
                DEBUG(data['items'][0]['ean'])
                adder.isbn.set_text(str(data['items'][0]['ean']))
                adder.title.set_text(str(data['items'][0]['title']))
                adder.mtype.set_text("DVD/CD")
                adder.display()
            except:
                buff = self.text_view.get_buffer()
                buff.insert_at_cursor (_("This item doesn't exist!" ))
                return None
        self.gtk_main_quit(self, None)


################################################################################
    def getBookLocation(self, isbn):
        db_query = sql()
        location_string = None
        result = db_query.get_location_by_isbn(isbn) # Could be multiple but unlikely
        DEBUG(result)
        for row in result:
            print row
            location_string = row['room'] + " : " + row['shelf']

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


################################################################################
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
            print track

        return tracks # Dictionary e.g. {'index': 12, 'length': 214.773, 'name': 'The Kick Inside'}


################################################################################
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
        buff = self.text_view.get_buffer()
        db_query = sql()
        last_id = db_query.insert_book_object(self.abook)
        DEBUG(last_id);
        # We should check this for success
        if last_id == 0:
            print ("Failed to add book to database.")
            buff.insert_at_cursor (_( "\n\nCould add this book!"))
            self.text_view.set_buffer(buff)
            return
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


################################################################################
    def append_text(self, text):
        pass


################################################################################
    def get_book_data(self):
        #self.scanner
        pass

    def on_sig_int(self):
        gtk_main_quit(False)
################################################################################
    def gtk_main_quit(self, widget):
        # Quit when we destroy the GUI only if main application, else don't quit
        if __name__ == "__main__":
            gtk.main_quit()
            self.closing = True
            quit(0)
        else:
            self.window.hide()
            del self
        pass
################## END scanner class ###########################################



# we start here.
if __name__ == "__main__":
    app = Scanner()
