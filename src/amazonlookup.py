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

  
EAN='5051429101095' # sample EAN

class DVDlookup:
  def __init__(self):
    # Get the keys from gconf, or some secret location
    self.api = amazonproduct.API(AWS_KEY, SECRET_KEY, 'uk')
  
  def lookup(self, EAN):
    if EAN:
      try:
        dvd = self.api.item_lookup(EAN, AssociateTag='aztag-20', IdType='EAN', SearchIndex="DVD") # For a DVD
      except:
        raise
        return 1
      self.title = dvd.Items.Item.ItemAttributes.Title
      self.manufacturer = dvd.Items.Item.ItemAttributes.Manufacturer
      self.actor = dvd.Items.Item.ItemAttributes.Actor
      self.director = dvd.Items.Item.ItemAttributes.Director
      return 0 # Success

  def test_look(self):
    self.lookup(EAN)
    assert self.title == "The Butterfly Effect - Director's Cut [DVD]"
    print self.title
    print self.manufacturer
    print self.director
    print self.actor
    

# Test malarky
if __name__ == "__main__":
  app = DVDlookup()
  app.test_look()
