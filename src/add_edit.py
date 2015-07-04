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
    #logging.debug(scrolled_window)
    self.abstract =  builder.get_object("textview_abtract") 
    #logging.debug(self.abstract)
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
    self.mybook = book.book()
    self.orig_book = book.book()
    self.status = builder.get_object("label_status")
    self.lent_date = builder.get_object("b_date")
    self.location_dropdown = builder.get_object("combobox_location")
    self.location_liststore = builder.get_object("liststore_locations")
    self.location_dropdown.set_model(self.location_liststore)
    self.location_dropdown.set_text_column(1)

    self.lent_select.set_model( self.lentlist)
    self.lent_select.set_text_column(1)

    self.o_date = ''


  def display(self):
    gtk.main()
    pass

  def on_button_close_clicked(self, widget):
    ''' Check if any changed made and pop up worning
    else close the dialog.
    FIXME:  Don't show the dialog if there have been no changes.
    '''
    updated = self.update_book()
    if updated == 0:
      logging.info("Closing without saving.")
      if __name__ == "__main__":
        gtk.main_quit()
      else:
        self.window.hide()
    else: # pop up an are you sure dialog.
      logging.info(updated)
      logging.info("Opening a dialog to ask to save changes")
      dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO, "Changes have be made.\nDo you want to save changes?")
      dlg_val = dialog.run()
      dialog.destroy()
      del dialog
      self.on_destroy(widget)
      if dlg_val == -9: # yes
        self.update_book()
      else: #no
        self.on_button_update_clicked(widget)
        self.on_destroy(widget)


  def on_destroy(self,widget):
    if __name__ == "__main__":
      gtk.main_quit()
    else:
      self.window.hide()


  def isbn_lookup(self,widget):
    ''' Lookup the book on XisbnQuery
      returns biblio.webquery.bibrecord.BibRecord
      update the database and close the window
    '''
    try:
      logging.info(self.isbn.get_text())
      self.mybook.webquery(self.isbn.get_text())
      self.isbn.set_text(self.mybook.isbn)
      self.title.set_text(self.mybook.title)
      self.author.set_text(str(self.mybook.authors))
      textbuffer = self.mybook.abstract
      abs_buffer.set_text(self.mybook.abstract) 
      self.mtype.set_text(self.mybook.mtype)
      self.publisher.set_text(self.mybook.publisher)
      self.city.set_text(self.mybook.city)
      self.year.set_text(self.mybook.year)
    except:
      logging.info(_("No book found"))
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
      #self.lent_select.append_text(row[1])
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
      #self.lentlist.prepend([0, "", ""])
      self.lent_select.set_active(0)
      self.lent.set_active(False)
    pass

  def populate_locations(self):
    db_query = sql()
    locations = db_query.get_locations()
    self.location_liststore.clear()
    loc = self.mybook.where
    #logging.info(loc)
    for where in locations:
      rs = where['room'] + ' - ' + where['shelf']
      self.location_liststore.append([where['id'], rs])
      #logging.info(where['id'])
    self.location_liststore.prepend([0, ''])
    # Now set the dropdown to the books location
    n = 0
    for lid in self.location_liststore:
      #logging.debug([loc, lid[0],n])
      if lid[0] == loc:
        self.location_dropdown.set_active(n)
        return
      n += 1

  def set_location(self):
    '''
    Set the book's location
    '''
    db_query = sql()
    idx = self.location_dropdown.get_active()
    #logging.info(idx)
    if idx > 0:
      lid = self.location_liststore[idx][0]
      #logging.debug(lid)
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
    #logging.debug(book_id)
    row = db_query.get_by_id(book_id)
    #logging.info(result)
    #for row in result:
    # Populate GUI
    if row['isbn'] != None: self.isbn.set_text(row['isbn'])
    if row['author'] != None: self.author.set_text(row['author'])
    self.title.set_text(row['title'])
    abs_buffer = self.abstract.get_buffer()
    #logging.debug(abs_buffer)
    abs_buffer.set_text(row['abstract']) 
    if row['publisher'] != None: self.publisher.set_text(row['publisher'])
    if row['city'] != None: self.city.set_text(row['city'])
    if row['year'] != None: self.year.set_text(str(row['year']))
    if row['owner'] != None: self.book_owner.set_text(str(row['owner']))
    self.mtype.set_text(str(row['mtype']))
    self.copies.set_text(str(row['copies']))

    # Populate a book object
    self.orig_book.isbn =row['isbn']
    self.orig_book.id = row['id']
    self.orig_book.authors = row['author']
    self.orig_book.title = row['title']
    self.orig_book.abstract = row['abstract']
    self.orig_book.publisher = row['publisher']
    self.orig_book.city = row['city']
    self.orig_book.year = row['year']
    self.orig_book.copies = row['copies']
    self.orig_book.where = row['location']
    self.orig_book.owner = row['owner']
    self.orig_book.rating = row['rating']
    #logging.info(self.orig_book.where)
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


  def update_book(self):
    ''' Update any changes from GUI
    @return Error value from book.compare(book)
    '''
    self.orig_book = copy.copy(self.mybook) # Make a copy
    self.mybook.isbn=self.isbn.get_text()
    self.mybook.title=self.title.get_text()
    self.mybook.authors=self.author.get_text()
    textbuffer = self.abstract.get_buffer()
    startiter, enditer = textbuffer.get_bounds()  
    self.mybook.abstract=textbuffer.get_text(startiter, enditer) 
    self.mybook.mtype=self.mtype.get_text()
    self.mybook.publisher=self.publisher.get_text()
    self.mybook.city=self.city.get_text()
    self.mybook.mtype=self.mtype.get_text()
    self.mybook.owner=self.book_owner.get_text()
    self.mybook.rating = self.rating_select.get_active()
    #logging.debug(self.mybook.rating)
    #logging.debug(self.rating_select.get_active())
    self.set_location()
    #self.mybook.add_date=self.add_date.get_text() #TODO
    if self.year.get_text() != '' : self.mybook.year=self.year.get_text()

    #logging.info(self.mybook.year)
    # Is the book on loan and to whome?
    self.status.set_text(_("Book updated."))
    return self.orig_book.compare(self.mybook)

  def on_button_update_clicked(self, widget):
    ''' Update the database with new info or add if not already in.'''
    if self.update_book() != 0: # Any changes?
      logging.debug("Something changed so an update is needed.")
      self.update_db()
      self.set_location()

  def update_db(self):
    db_query = sql()
    book = copy.copy(self.mybook)
    #logging.info(self.orig_book.compare(book))
    result = db_query.get_by_id(book.id)
    logging.debug(result)
    logging.debug(book.is_empty())
    if book.is_empty(): return # Do nothing if no data
    if result == None: # If no book in DB, add it
    # Make sure we don't add an empty book.  We could also use this to
      if not str.isdigit(book.year): book.year = 0 #DB query fix for empty date field.
      #book.owner = getpass.getuser() # Assume owner is current logged in person
      db_query.insert_book_object(book)
      #db_query.insert_unique_author(book.authors)

      self.status.set_text(_(" Book has been inserted."))
      self.orig_book = copy.copy(book) # So we can compare again.

    #check for changes if we have a copy of the original data.
    # If the book is not empty
    else:
      logging.info("Something changed so an update is needed")
      #self.update_book()
      db_query.update_book(book, book.id)
      #logging.info(book.mtype)
      db_query.insert_unique_author(book.authors)
      self.status.set_text(_(" Book has been updated."))
      self.orig_book = copy.copy(book) # So we can compare again.
    del book

  def on_button_remove_clicked(self, widget):
    ''' Remove selected book from database '''
    db_query = sql()
    #logging.info(str(self.mybook.id) + " about to be removed.")
    dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_YES_NO, "Are you sure you want to delete this book?")
    dlg_val = dialog.run()
    logging.debug(dlg_val)
    dialog.destroy()
    del dialog
    if dlg_val == -9:return
    db_query.remove_book(self.mybook.id)
    self.status.set_text (_(" Book has been removed."))
    logging.info("Book has been removed.")

  def on_comboboxentry1_changed(self,widget):
    ''' Do things when selection is changed
    Need to check if the selected borrower has the book and set the
    checkbutton status to suit '''
    db_query = sql()
    if not self.lentlist.get_iter_first(): return # If we can't iterate then the list is empty
    foo = self.lent_select.get_active()
    bid = self.lentlist[foo][0]
    #logging.info(bid)
    if bid > 0:
      self.add_button.set_label(_("Edit"))
    else:
      self.lent.set_active(False)
      self.add_button.set_label(_("Add"))
    # Get list of borrows for this book
    result = db_query.get_borrows(self.mybook.id,bid)
    #logging.info(result)
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
    self.year.set_text('')
    self.copies.set_text('')
    self.lent_select.set_active(0)
    # Create a new empty book
    import book
    self.orig_book = book.book()
    self.mybook = copy.copy(self.orig_book)
    self.populate_borrowers()
    self.populate_locations()
    self.status.set_text(_("Everything cleared.  Enter new book's details."))


  def on_checkbutton1_toggled(self, widget):
    if not self.lentlist.get_iter_first():
      return
    db_query = sql()
    #logging.info(widget)
    # Get widget state
    # Set book as borrowed or not with borrower as key.
    # What if I have two copies and they get borrowed?
    if self.lent.get_active(): # Checked
      foo = self.lent_select.get_active()
      bid = self.lentlist[foo][0]
      #logging.info(bid)
      if bid != 0 and self.mybook.id != 0 and self.orig_book.copies > 0:
        db_query.add_borrow(self.mybook.id, bid)
        self.mybook.borrower_id = bid
        self.status.set_text(_("Book has been marked as borrowed."))
        #self.orig_book.copies -= 1
      else:
        self.status.set_text(_("Book has been NOT marked as borrowed."))
        #self.lent.set_active(False)
      self.lent_date.set_text(str(self.o_date))

    else: # Unchecked
      self.lent_date.set_text(str(""))
      foo = self.lent_select.get_active()
      bid = self.lentlist[foo][0]
      if bid != 0:
        result =  db_query.update_borrows(self.mybook.id, bid)
        if result:
          #self.orig_book.copies += 1
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

