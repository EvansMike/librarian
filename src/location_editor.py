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

Edit and store the locations of your books.

'''

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))
from db_queries import sql as sql
import logging
import book
import gettext
#import load_config

try:
  import pygtk
  pygtk.require("2.0")
except:
  pass
try:
  import gtk
except:
  print ("GTK Not Availible")
  sys.exit(1)
  
  
APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext


logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s', level=logging.DEBUG) 



class location_edit():
  '''
  Edit the locations table.  This will be used to populate a dropdown
  in the book details dialog.  Room and shelf are stored in separate 
  tables but will be presented together in the book details dialog dropdown.
  '''
  
  def __init__(self):
    builder = gtk.Builder()
    self.gladefile = os.path.join(os.path.dirname(__file__),"ui/location_editor.glade")
    builder.add_from_file(self.gladefile)
    self.window = builder.get_object("location_dialog")
    self.room_entry = builder.get_object("entry_room")
    self.shelf_entry = builder.get_object("entry_shelf")
    builder.connect_signals(self)
    self.populate_dialog()
    self.window.show()
     
     
  def run(self):
    self.window.run()
    self.window.destroy() 
    
    
  def populate_dialog(self):
    '''
    Fill in the boxes.  With awsome emptiness.
    '''
    return
    
  def on_save_clicked_cb(self, widget):
    '''
    Save any updates to the database.
    '''
    db_query = sql()
    room = self.room_entry.get_text()
    shelf = self.shelf_entry.get_text()
    if shelf == '' or room == '': 
      logging.info("Nothing to save")
      self.run() # Re-run else we close.
      return
    logging.info("Saving: "+room+", "+shelf)
    db_query.add_location(room, shelf)
    # Dont close, just re-run the dialog
    self.run()
    
  def on_close_clicked_cb(self,widget):
    '''
    Ignore any input and close the dialog.
    '''
    logging.info("Closing")
 
         
    
    
''' Run main if called directly.'''
if __name__ == "__main__":
  app = location_edit()
