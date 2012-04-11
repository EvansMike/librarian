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

AWS_KEY = 'AKIAIJ4MEUULUTHOJPLA'
SECRET_KEY = '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' ## Needs to be hidden in gconf

api = amazonproduct.API(AWS_KEY, SECRET_KEY, 'uk')

#foo = api.item_lookup('5051429101095', AssociateTag='aztag-20') # For a Book, but we already have books sorted so...
foo = api.item_lookup('5051429101095', AssociateTag='aztag-20', IdType='EAN', SearchIndex="DVD") # For a DVD

foo.Items.Item.ItemAttributes.Title
foo.Items.Item.ItemAttributes.Manufacturer #DVD
foo.Items.Item.ItemAttributes.Actor #DVD
foo.Items.Item.ItemAttributes.Director  #DVD

class DVDlookup:
  def __init__(self):
    # Get the keys from gconf, or some secret location
    self.api = amazonproduct.API(AWS_KEY, SECRET_KEY, 'uk')
  
  def lookup(self, EAN):
    dvd = api.item_lookup(EAN, AssociateTag='aztag-20', IdType='EAN', SearchIndex="DVD") # For a DVD
    self.title = dvd.Items.Item.ItemAttributes.Title
    self.manufacturer = Items.Item.ItemAttributes.Manufacturer
    self.actor = Items.Item.ItemAttributes.Actor
    self.director = Items.Item.ItemAttributes.Director
