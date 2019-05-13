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

A GUI to edit a single book.
TODO:
  Fix logic for borrowers list and checkbox.  If borrowed, ONLY the borrower
  should appear in the list and the checkbox should ALWAYS reflect correct status.
  TODO: Make the GUI into a proper dialog.
'''

import usb.core
import usb.util
import MySQLdb
import sys, os
import logging
import pygtk
pygtk.require("2.0")
import gtk
from biblio.webquery.xisbn import XisbnQuery
import biblio.webquery
import book
import copy
import gettext
import datetime
import getpass
from db_queries import sql as sql

_ = gettext.gettext

#logger = logging.getLogger("barscan")
logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s', \
      level=logging.DEBUG)
DEBUG = logging.debug
INFO = logging.info

class add_edit:
  ''' Interface to manipulate book details.
  '''
  def __init__(self):
    self.borrowers = 0
    builder = gtk.Builder()
    self.gladefile = os.path.join(os.path.dirname(__file__),"ui/edit_book.glade")
    builder.add_from_file(self.gladefile)
    builder.connect_signals(self)
    self.window = builder.get_object("window_edit")
    self.isbn =  builder.get_object("entry1")
    self.author =  builder.get_object("entry2")
    self.title =  builder.get_object("entry3")
    self.publisher =  builder.get_object("entry4")
    self.year =  builder.get_object("entry5")
    self.city =  builder.get_object("entry6")
    scrolled_window =  builder.get_object("scrolledwindow1")
    self.abstract =  builder.get_object("textview_abtract") 
    self.mtype =  builder.get_object("entry8")
    self.copies = builder.get_object("entry9")
    self.lent = builder.get_object("checkbutton1")
    self.lentlist = builder.get_object("liststore1")
    self.lent_select = builder.get_object("comboboxentry1")
    self.book_owner = builder.get_object("entry_owner")
    self.add_button = builder.get_object("button_new_user") # Add a new user or edit
    self.rating_select = builder.get_object("combobox_rating")
    self.rating_liststore = builder.get_object("liststore_rating")
    self.rating_select.set_model(self.rating_liststore)
    self.where = ""
    self.add_date = False # builder.get_object("comboboxentry1") #To be added to GUI
    self.mybook = book.Book()
    self.orig_book = book.Book()
    self.status = builder.get_object("label_status")
    self.lent_date = builder.get_object("b_date")
    self.location_dropdown = builder.get_object("combobox_location")
    self.location_liststore = builder.get_object("liststore_locations")
   
    self.location_dropdown.set_model(self.location_liststore)
    self.location_dropdown.set_text_column(1)

    self.values_dropdown = builder.get_object("comboboxentry_value")
    self.values_liststore = builder.get_object("liststore_values")

    self.lent_select.set_model( self.lentlist)
    self.lent_select.set_text_column(1)
    self.o_date = ''


  def display(self):
    gtk.main()
    pass


  def on_button_close_clicked(self, widget):
    ''' Check if any changed made and pop up worning
    else close the dialog.
    '''
    updated = self.update_book()
    DEBUG(updated)
    if updated == 0:
      INFO("Closing without saving.")
      if __name__ == "__main__":
        gtk.main_quit()
      else:
        self.window.hide()
    else: # pop up an are you sure dialog.
      INFO("Opening a dialog to ask to save changes")
      dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO, "Changes have be made.\nDo you want to save changes?")
      dlg_val = dialog.run()
      dialog.destroy()
      del dialog
      self.on_destroy(widget)
      if dlg_val == gtk.RESPONSE_YES:
        INFO("Saving changes");  
        self.update_book()
        self.update_db()
        self.set_location()
      else: #no
        INFO("NOT saving changes")
        self.on_destroy(widget)


  def on_destroy(self,widget):
    if __name__ == "__main__":
      gtk.main_quit()
    else:
      self.window.hide()


  def on_button_isbn_lookup_clicked(self,widget):
    ''' Lookup the book by its ISBN
    '''
    mybook = copy.copy(self.mybook)
    try:
      INFO(self.isbn.get_text())
      mybook.webquery(self.isbn.get_text())
      if self.mybook.isbn != "":
          self.isbn.set_text(mybook.isbn)
      self.title.set_text(mybook.title)
      self.author.set_text(str(mybook.authors))
      abs_buffer = self.abstract.get_buffer()
      abs_buffer.set_text(mybook.abstract)
      self.mtype.set_text(mybook.mtype)
      self.publisher.set_text(mybook.publisher)
      self.city.set_text(mybook.city)
      self.year.set_text(mybook.year)
    except:
      pass
    if mybook.title == '':
      INFO(_("No book found"))
      d = gtk.Dialog()
      d.add_buttons(gtk.STOCK_OK, 1)
      label = gtk.Label(_('No Book found for this ISBN!'))
      label.show()
      d.vbox.pack_start(label)
      d.run()
      d.destroy()


  def populate_borrowers(self):
    ''' Get borrowers and fill in the list'''
    db_query = sql()
    #Populate borrowers combo box etc.
    self.lentlist.clear()
    result = db_query.get_all_borrowers()
    for row in result:
      self.lentlist.append([row["id"], row["name"], row["contact"]])
      self.borrowers += 1
    self.lentlist.prepend([0, "", ""])
    #Get borrows for this book up to the # of copies
    result = db_query.get_borrows(self.orig_book.id,self.orig_book.copies)
    bid = 0
    for row in result:
      bid = row["borrower"]
      book_id = row["book"]
      self.o_date = row["o_date"]
      #logging.info(bid)
    if bid != 0:
      #logging.info(bid)
      if self.orig_book.id == book_id:
        self.orig_book.copies -=1
        self.copies.set_text(str(self.orig_book.copies))
      # Set active to current borrower.
      # FIXME: This get the first borrower of a copy.  Normally not an issue
      # for personal libraries, it will be for lending libraries though.
      n = 0
      for lender in self.lentlist:
        if lender[0] == bid:
          self.lent_select.set_active(n)
          self.lent_date.set_text(str(self.o_date))
          self.lent.set_active(True)
          break
        n += 1
    else:
      self.lent_select.set_active(0)
      self.lent.set_active(False)
    pass


  def populate_locations(self):
    db_query = sql()
    locations = db_query.get_locations()
    self.location_liststore.clear()
    loc = self.mybook.where
    for where in locations:
      rs = where['room'] + ' - ' + where['shelf']
      self.location_liststore.append([where['id'], rs])
    self.location_liststore.prepend([0, ''])
    # Now set the dropdown to the books location
    n = 0
    for lid in self.location_liststore:
      if lid[0] == loc:
        self.location_dropdown.set_active(n)
        return
      n += 1


  def populate_values(self):
      for value in book.Book.values:
        self.values_liststore.append([value])
        self.values_dropdown.set_active(self.orig_book.value)
      

  def set_location(self):
    '''
    Set the book's location
    '''
    db_query = sql()
    idx = self.location_dropdown.get_active()
    if idx > 0:
      lid = self.location_liststore[idx][0]
      self.mybook.where = lid
      db_query.update_book_location(self.mybook.id, lid)
      return
      

  def populate_rating(self, rating):
    ''' Set the rating dropdown to the current book's rating'''
    # rating = 3 # Test
    self.rating_select.set_active(rating)
    return

    
  def on_button_add_location_clicked_cb(self,widget):
    '''
    Open a dialog to add a new location
    '''
    import location_editor
    dialog = location_editor.location_edit()
    dialog.run()
    # Update the combobox liststore
    self.populate_locations()
    self.status.set_text(_("Location changed."))


  def populate(self,book_id):
    db_query = sql()
    row = db_query.get_by_id(book_id)
    # Populate GUI
    if row['isbn'] != None: self.isbn.set_text(row['isbn'])
    if row['author'] != None: self.author.set_text(row['author'])
    self.title.set_text(row['title'])
    abs_buffer = self.abstract.get_buffer()
    abs_buffer.set_text(row['abstract']) 
    if row['publisher'] != None: self.publisher.set_text(row['publisher'])
    if row['city'] != None: self.city.set_text(row['city'])
    if row['year'] != None: self.year.set_text(str(row['year']))
    if row['owner'] != None: self.book_owner.set_text(str(row['owner']))
    self.mtype.set_text(str(row['mtype']))
    self.copies.set_text(str(row['copies']))

    # Populate a book object
    self.orig_book.value = row['value']
    self.orig_book.isbn =row['isbn']
    self.orig_book.id = row['id']
    self.orig_book.authors = row['author']
    self.orig_book.title = row['title']
    self.orig_book.abstract = row['abstract']
    self.orig_book.publisher = row['publisher']
    self.orig_book.city = row['city']
    self.orig_book.year = str(row['year']).strip()
    self.orig_book.copies = row['copies']
    self.orig_book.where = row['location']
    self.orig_book.owner = row['owner']
    self.orig_book.rating = row['rating']
    self.orig_book.mtype = row['mtype']
    if row['add_date'] != "":
      self.orig_book.add_date = row['add_date']
    else:
      # Dunno?  datetime.date.today() perhaps?
      pass

    self.mybook = copy.copy(self.orig_book)
    self.populate_borrowers()
    self.populate_locations()
    self.populate_rating(row['rating'])
    self.populate_values()


  def update_book(self):
    '''
    Update any changes from GUI
    @return Error value from book.compare(book)
    '''
    self.orig_book = copy.copy(self.mybook) # Make a copy
    DEBUG(self.mybook.id)
    self.mybook.isbn=self.isbn.get_text()
    self.mybook.title=self.title.get_text()
    self.mybook.authors=self.author.get_text()
    textbuffer = self.abstract.get_buffer()
    startiter, enditer = textbuffer.get_bounds()
    self.mybook.abstract = textbuffer.get_text(startiter, enditer)
    self.mybook.mtype=self.mtype.get_text()
    self.mybook.publisher=self.publisher.get_text()
    self.mybook.city = self.city.get_text().strip()
    year = None
    year = self.year.get_text()
    if year : self.mybook.year = year
    else: self.mybook.year = 0
    self.mybook.mtype = self.mtype.get_text()
    self.mybook.owner = self.book_owner.get_text()
    self.mybook.rating = self.rating_select.get_active()
    self.mybook.value = self.values_dropdown.get_active()
    self.set_location()
    # Is the book on loan and to whome?
    self.status.set_text(_("Book updated."))
    return self.orig_book.compare(self.mybook)


  def on_button_update_clicked(self, widget):
    ''' Update the database with new info or add if not already in.'''
    if self.update_book() != 0 or self.mybook.updated: # Any changes?
      DEBUG("Something changed so an update is needed.")
      self.update_db()


  def update_db(self, ):
    db_query = sql()
    book = copy.copy(self.mybook)
    DEBUG(book.id)
    result = db_query.get_by_id(book.id)
    DEBUG(result)
    if result == None: # If no book in DB, add it
    # Make sure we don't add an empty book.  We could also use this to
        if not str.isdigit(book.year.encode('ascii', 'ignore')): book.year = 0 #DB query fix for empty date field.
        book_id = db_query.insert_book_object(book)
        book.id = book_id # Update the book with it's new id from the DB.
        self.set_location()
        INFO("New book has been inserted.")
        DEBUG(book_id)
        self.status.set_text(_("New book has been inserted."))
    else:
        book_id = result['id']
        if book_id == self.mybook.id: # It already exists so we update
            #check for changes if we have a copy of the original data.
            # If the book is not empty
            INFO("Book has been updated")
            db_query.update_book(book, book.id)
            db_query.insert_unique_author(book.authors)
            self.status.set_text(_(" Book has been updated."))
    self.mybook = copy.copy(book) # So we can compare again.   
    del book


  def on_button_remove_clicked(self, widget):
    ''' Remove selected book from database '''
    db_query = sql()
    dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_YES_NO, "Are you sure you want to delete this book?")
    dlg_val = dialog.run()
    DEBUG(dlg_val)
    dialog.destroy()
    del dialog
    if dlg_val == -9:return
    db_query.remove_book(self.mybook.id)
    self.status.set_text (_(" Book has been removed."))
    INFO("Book has been removed.")


  def on_comboboxentry1_changed(self,widget):
    ''' Do things when selection is changed
    Need to check if the selected borrower has the book and set the
    checkbutton status to suit '''
    db_query = sql()
    if not self.lentlist.get_iter_first(): return # If we can't iterate then the list is empty
    foo = self.lent_select.get_active()
    bid = self.lentlist[foo][0]
    if bid > 0:
      self.add_button.set_label(_("EDIT"))
    else:
      self.lent.set_active(False)
      self.add_button.set_label(_("ADD"))
    # Get list of borrows for this book
    result = db_query.get_borrows(self.mybook.id,bid)
    if result == 0:
      self.lent.set_active(False)
    else:
       self.lent.set_active(False)


  def on_button_clear_clicked(self, widget):
    ''' Clear all the edit boxes so A new book can be entered.
    '''
    self.isbn.set_text('')
    self.author.set_text('')
    self.title.set_text('')
    textbuffer = self.abstract.get_buffer()
    textbuffer.set_text('') 
    self.publisher.set_text('')
    self.city.set_text('')
    self.year.set_text('0')
    self.copies.set_text('')
    self.lent_select.set_active(0)
    #DEBUG(getpass.getuser())
    self.book_owner.set_text(str(getpass.getuser())) # Assume the user is the book owner.
  
    # Create a new empty book
    import book
    self.orig_book = book.Book()
    self.mybook = copy.copy(self.orig_book)
    self.populate_borrowers()
    self.populate_locations()
    self.status.set_text(_("Everything cleared.  Enter new book's details."))


  def on_checkbutton1_toggled(self, widget):
    if not self.lentlist.get_iter_first():
      return
    db_query = sql()
    # Get widget state
    # Set book as borrowed or not with borrower as key.
    # What if I have two copies and they get borrowed?
    if self.lent.get_active(): # Checked
      foo = self.lent_select.get_active()
      bid = self.lentlist[foo][0]
      if bid != 0 and self.mybook.id != 0 and self.orig_book.copies > 0:
        db_query.add_borrow(self.mybook.id, bid)
        self.mybook.borrower_id = bid
        self.status.set_text(_("Book has been marked as borrowed."))
      else:
        self.status.set_text(_("Book has been NOT marked as borrowed."))
      self.lent_date.set_text(str(self.o_date))

    else: # Unchecked
      self.lent_date.set_text(str(""))
      foo = self.lent_select.get_active()
      bid = self.lentlist[foo][0]
      if bid != 0:
        result =  db_query.update_borrows(self.mybook.id, bid)
        if result:
          self.mybook.borrower_id = None
          self.status.set_text(_("Book has been marked as returned."))
        else: self.status.set_text(_("Book has been NOT marked as returned."))
    self.copies.set_text(str(self.orig_book.copies))


  def on_button_new_user_clicked(self, widget):
    ''' Add a new borrower to the database.  Need to update dropdown
    when we finish this function.  We should be able to read the contents
    of comboboxentry1(self.lent_select) and use that as a user name.

    '''
    import borrowers
    try:
      foo = self.lent_select.get_active()
      bid = self.lentlist[foo][0]
    except: bid = 0
    adder = borrowers.borrowers(bid)
    adder.run()
    self.populate_borrowers()

############## END add_edit class ######################################



# For testing or stand alone
if __name__ == "__main__":
  app = add_edit()
  app.display()
