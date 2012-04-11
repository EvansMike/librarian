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
''' Get, set config data using gconf.  This should make the app portable
across OS,s and ensure config data are available wherever the app is started
from.
'''

import amazonproduct
import gconf_config


config = gconf_config.gconf_config() 
if config:
  AWS_KEY = config.az_key
  SECRET_KEY = config.az_skey

  
DVD_EAN='5051429101095' # Sample DVD EAN
CD_EAN = '5014293611725' # Sample CD EAN
BOOK_EAN = '9780596001704' # Sample book EAN

class DVDlookup:
  '''
  Get DVD data from Amazon.
  TODO: Handle cases where no data are returned.
  '''
  def __init__(self):
    # Get the keys from gconf, or some secret location
    self.api = amazonproduct.API(AWS_KEY, SECRET_KEY, 'uk')
  
  def lookup(self, EAN):
    if EAN:
      try:
        dvd = self.api.item_lookup(EAN, AssociateTag='aztag-20', IdType='EAN', SearchIndex="DVD") # For a DVD
        self.Title = dvd.Items.Item.ItemAttributes.Title
        self.Manufacturer = dvd.Items.Item.ItemAttributes.Manufacturer
        self.Actor = dvd.Items.Item.ItemAttributes.Actor
        self.Director = dvd.Items.Item.ItemAttributes.Director
        self.ProductGroup = dvd.Items.Item.ItemAttributes.ProductGroup
        return 0 # Success
      except:
        #raise
        return 1

  def test_look(self):
    if self.lookup(DVD_EAN) != 1:
      assert self.Title == "The Butterfly Effect - Director's Cut [DVD]"
      print self.Title
      print self.Manufacturer
      print self.Director
      print self.Actor
      print self.ProductGroup
    
class CDlookup():
  ''' Get CD data from Amazon.
  TODO: Get track listing
  TODO: Handle cases where no data are returned.
  
  '''
  def __init__(self):
    # Get the keys from gconf, or some secret location
    self.api = amazonproduct.API(AWS_KEY, SECRET_KEY, 'uk')
    
  def lookup(self, EAN):
    if EAN:
      try:
        cd = self.api.item_lookup(EAN, AssociateTag='aztag-20', IdType='EAN', SearchIndex="Music") # For a CD
        self.Title = cd.Items.Item.ItemAttributes.Title
        self.Artist = cd.Items.Item.ItemAttributes.Artist
        self.Manufacturer = cd.Items.Item.ItemAttributes.Manufacturer
        self.ProductGroup = cd.Items.Item.ItemAttributes.ProductGroup
        return 0 #On success
      except:
        #raise
        return 1
    
  def test_look(self):
    if self.lookup(CD_EAN) != 1:
      #assert self.Title == "Ain't Nothing Like the Real Thing"
      print self.Title
      print self.Artist
      print self.Manufacturer
      print self.ProductGroup

    
class Booklookup():
  ''' Get CD data from Amazon.
  TODO: Get track listing
  TODO: Handle cases where no data are returned.
  
  '''
  def __init__(self):
    # Get the keys from gconf, or some secret location
    self.api = amazonproduct.API(AWS_KEY, SECRET_KEY, 'uk')
    
  def lookup(self, EAN):
    if EAN:
      try:
        book = self.api.item_lookup(EAN, AssociateTag='aztag-20', IdType='EAN', SearchIndex="Music") # For a CD
        self.Title = book.Items.Item.ItemAttributes.Title
        self.Author = book.Items.Item.ItemAttributes.Author
        self.Manufacturer = book.Items.Item.ItemAttributes.Manufacturer
        self.ProductGroup = book.Items.Item.ItemAttributes.ProductGroup
        return 0 #On success
      except:
        #raise
        return 1
    
  def test_look(self):
    if self.lookup(CD_EAN) != 1:
      #assert self.Title == "Ain't Nothing Like the Real Thing"
      print self.Title
      print self.Author
      print self.Manufacturer
      print self.ProductGroup    

    
    
# Test malarky
if __name__ == "__main__":
  dvd = DVDlookup()
  dvd.test_look()
  cd = CDlookup()
  cd.test_look()
