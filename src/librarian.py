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
  
  (c) Mike Evans <mikee@saxicola.co.uk>

A (in)complete home book collection manager.
'''

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))
import copy
import MySQLdb
import MySQLdb.cursors
import sys,os
import logging
import book
import locale
import gettext
import lib_print
import messages
import getpass
#from db_queries import calibre
#from db_queries import mysql as sql # Make this choosable for mysql and sqlite
# or 
from db_queries import sql as sql

import i18n
_ = i18n.language.gettext

#logger = logging.getLogger("librarian")
logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
#logging.disable(logging.INFO)

# Get system platform
plat = sys.platform

import version

try:
  import pygtk
  pygtk.require("2.0")
except:
  pass
try:
  import gtk
except:
  print _("GTK Not Availible")
  sys.exit(1)

NULL, ALL, BORROWED = range(3)

class splashScreen():
  def __init__(self):
    import time
    #DONT connect 'destroy' event here!
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.version = "Version: " + version.__version__
    self.window.set_title('LIBRARIAN')
    self.window.set_position(gtk.WIN_POS_CENTER)
    main_vbox = gtk.VBox(False, 3)
    self.window.add(main_vbox)
    self.image = gtk.Image()
    self.splash_image = os.path.join(os.path.dirname(__file__),"librarian.png")
    self.image.set_from_file(self.splash_image)
    self.image.show()
    self.lbl = gtk.Label(self.version)
    self.lbl.set_alignment(0.5, 0.5)
    main_vbox.pack_start(self.image, True, True)
    main_vbox.pack_start(self.lbl, True, True)
    self.window.show_all()
    while gtk.events_pending():
      time.sleep (0.01) # This forces the window to display its contents !?
      gtk.main_iteration()
      
class librarian:
  '''
  A simple book tracking program that uses a webcam to scan the barcodes
  to add books.  It also tracks borrowers and can include your e-books
  in the listings.  It doesn't track the "borrowing" of e-books. :)
  '''
  def __init__(self):
    splScr = splashScreen()

    print _("Version: "),version.__version__
    builder = gtk.Builder()
    self.gladefile = os.path.join(os.path.dirname(__file__),"ui/librarian.glade")
    builder.add_from_file(self.gladefile)
    builder.connect_signals(self)

    self.treeview  = builder.get_object('treeview1')
    #self.treeview.set_fixed_height_mode(True)
    self.booklist = builder.get_object("liststore1")
    self.status1 = builder.get_object("status1")
    '''
    column = gtk.TreeViewColumn('isbn', gtk.CellRendererText(), text=0)
    column.set_clickable(True)
    column.set_resizable(True)
    column.set_sort_column_id(0)
    self.treeview.append_column(column)
    '''

    column = gtk.TreeViewColumn(_('Medium'), gtk.CellRendererText(), text=9)
    column.set_clickable(True)
    column.set_resizable(True)
    column.set_sort_column_id(9)
    column.sizing = gtk.TREE_VIEW_COLUMN_AUTOSIZE
    self.treeview.append_column(column)

    column = gtk.TreeViewColumn(_('Author'), gtk.CellRendererText(), text=1)
    column.set_clickable(True)
    column.set_sort_indicator(True)
    column.set_resizable(True)
    column.set_visible(True)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE) 
    column.set_sort_column_id(1)
    self.treeview.append_column(column)

    column = gtk.TreeViewColumn(_('Title'), gtk.CellRendererText(), text=2)
    column.set_clickable(True)
    column.set_resizable(True)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
    column.set_sort_column_id(2)
    self.treeview.append_column(column)
    
    column = gtk.TreeViewColumn(_('Rating'), gtk.CellRendererText(), text=3)
    column.set_clickable(True)
    column.set_resizable(True)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
    column.set_sort_column_id(3)
    self.treeview.append_column(column)
    self.status1.set_text("Version:" + version.__version__)
    
    self.search_string = builder.get_object("entry_search")
    self.booklist.set_sort_column_id(1, gtk.SORT_ASCENDING)
    
    self.get_book_list(1)
    splScr.window.destroy()
    gtk.main()
    
  def on_button_print_clicked(self, widget):
    '''Print the entire book list to pdf then opens the default pdf viewer.
    TODO: Auto width columns
    This will likely be system specific
    '''
    try:
      from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
      from reportlab.lib.pagesizes import A4
      from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
      from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
      from reportlab.lib.units import mm
    except ImportError, e:
      messages.pop_info(e)
      return
    filename = "booklist.pdf"
    doc = SimpleDocTemplate(filename,pagesize=A4,
                            rightMargin=10,leftMargin=20,
                            topMargin=40,bottomMargin=18)
    Story=[]
    data = []
    styles=getSampleStyleSheet()
    text = Paragraph("long line",styles['Normal'])
    styles.add(ParagraphStyle(name='Justify', alignment=TA_LEFT))
    model = self.booklist
    myiter = model.get_iter_first()
    if myiter is not None:
      while str(myiter) != 'None':
        row = []
        if myiter is not None:
          row.append(Paragraph(model.get_value(myiter, 9),styles["Normal"]))
          row.append(Paragraph(model.get_value(myiter, 1),styles["Normal"]))
          row.append(Paragraph(model.get_value(myiter, 2),styles["Normal"]))
          row.append(Paragraph(model.get_value(myiter, 3),styles["Normal"]))
          myiter = model.iter_next(myiter)
        data.append(row)
      t=Table(data,[50,150,250,120]) # Values are cell widths
      t.hAlign='LEFT' # Move WHOLE TABLE to the left, defaults to CENTRE
      t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')])) # Apples to CELLS
      Story.append(t)
      doc.build(Story)

    # Open a reader for viewing and printing
    if os.name == "nt": # Windoze.  Not tested, I don't have Windoze :)
      os.filestart(filename)
    elif os.name == "posix": # Linux
      os.system("/usr/bin/xdg-open " + filename)

  def fill_booklist(self, result, append=False):
    ''' 
    Authors names are stored in regular text, we want so get them by
    family,first name order.  This iterates through the result and
    and appends to the liststore with the author names re-ordered.
    @param result
    @param append boolean, whether to append to list.
    '''
    db_query = sql()
    if not append: self.booklist.clear()    
    column = self.treeview.get_column(3)
    column.set_title(_('Abstract'))
    for row in result:
      # Deal with rearranging author names to last, first
      if row['author'] != None:
        name=row['author']
        name = name.split()
      else: name = ''
      if len(name) > 0 :
        author = []
        author.append(name[-1]) # Last part
        author.append(", ") # Decoration
        author.append(' '.join(name[0:-1])) # All except last part adding a space between them
        author = ''.join(author) # Join all elements into a string
      else:
        author = "N/A"
      #logging.info(author)
      abstract = row['abstract']
      # If a book is borrowed, display who by in the abtract column
      # FIXME Not working and also need to display lender.
      if row['borrower_id'] != None:
        b_book = db_query.get_book_borrower_by_book_id(row['id'])
        if b_book: abstract = b_book['name'] + " : " + str(b_book['o_date'])
      if row['owner'] != getpass.getuser():
        abstract += "  " + str(row['owner'])
         
      self.booklist.append([row['isbn'], author, row['title'],
      abstract,
      row['publisher'], row['city'], str(row['year']),
      row['id'], row['copies'], row['mtype']])
      

  def get_book_list(self, selection):
    ''' Get the book lists from the databases.

    Params:
    selection -- BORRORWED or ALL Which set to get.

    '''
    db_query = sql()
    result = {}
    #self.booklist.clear()
    num_ebooks = 0
    if selection == ALL:
      result, numrows = db_query.get_all_books()
      #logging.info(numrows)
      
      self.fill_booklist(result)
      try:
        import calibre
        e_books = calibre.calibre()
        self.booklist, num_ebooks = e_books.insert_data2(self.booklist)
      except:
        print "Cannot find any e-books.\n"
        pass # Do nothing if it's not available.
      self.status1.set_text("Book count = " + str(numrows) + ". E-book count = " +  str(num_ebooks))
    elif selection == BORROWED:
      result = db_query.get_borrowed_books()
      self.fill_booklist(result)
    



  def on_button_all_clicked(self, widget):
    '''Display all the books

    '''
    # Display all books
    self.get_book_list(1)

  def on_button_loaned_clicked(self, widget):
    '''Display the loaned out books

    '''
    # Display all books on loan
    self.get_book_list(BORROWED)
    column = self.treeview.get_column(3)
    column.set_title(_('Owner'))

  def on_button_scan_clicked(self, widget):
    '''Open the scanning dialog.

    '''
    # Open the scan thang
    #logging.info("Do the scan thang")
    from guiscan import scanner
    s = scanner()
    self.get_book_list(ALL) # All books


  def on_button_query_clicked(self, widget):
    '''Open the query dialog.

    '''
    from add_edit import add_edit
    ## Get a book for editing.  SHOULD be devolved to add_edit !!
    foo,iter = self.treeview.get_selection().get_selected()
    #logging.info(iter)
    if iter:
      # Get the data
      bid = self.booklist.get_value(iter,7)
      # If it's an e-book then we do nothing
      if bid == 0:
        import messages
        messages.pop_info(_('Cannot query e-books.  Please use calibre.' ))
        return
      adder = add_edit()
      #logging.info(adder)
      adder.populate(bid)
      adder.display()

    else:
      adder = add_edit()
      adder.display()
    self.get_book_list(1) # Repopulate book list.
    
  def on_button_search_clicked(self, widget):
    ''' Get the search string from entry_search, query the DB and display 
    the result.
    
    '''
    db_query = sql()
    search_string = self.search_string.get_text()
    if search_string == "": return
    result = db_query.search_books(search_string)
    self.fill_booklist(result,False)
    # Now search the calibre database.
    try:
      import calibre
      search = calibre.calibre()
      result = search.search_calibre(search_string, self.booklist) # search and add to booklist
    except: pass # Do nothing
    return

  def treeview1_row_activated_cb(self, widget, path, col):
    self.on_button_query_clicked(None)
    
    

  def gtk_main_quit(self, widget):
    # Quit when we destroy the GUI
    #if __name__ == "__main__":
    gtk.main_quit()
    quit(0)


#################### END librarian #####################################

''' Run main if called directly.'''
if __name__ == "__main__": 
  app = librarian()
  gtk.main()

