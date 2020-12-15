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

Pop up messages handlers.
'''

import os, stat
import sys
import gettext
import locale

py_version = sys.version_info.major


if py_version == 3:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk as gtk
else:
    import gtk

_ = gettext.gettext

additional_text = ''

def pop_no_config_file(additional_text):
  d = gtk.Dialog()
  d.add_buttons(gtk.STOCK_OK, 1)
  label = gtk.Label(_('No config file found. Please edit ') + config_file)
  label.show()
  d.vbox.pack_start(label, True, True, 0)
  answer = d.run()
  d.destroy()

def pop_info(text):
  d = gtk.Dialog()
  d.add_buttons(gtk.STOCK_OK, 1)
  label = gtk.Label(text)
  label.show()
  d.vbox.pack_start(label, True, True, 0)
  answer = d.run()
  d.destroy()
  return answer
