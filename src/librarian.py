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

A (in)complete home book collection manager.
'''

import MySQLdb
import MySQLdb.cursors
import sys
import load_config
import logging
import book
import locale
import gettext
import popen2

locale.setlocale(locale.LC_ALL, '')
APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

logger = logging.getLogger("librarian")
logging.basicConfig(format='%(module)s: LINE %(lineno)d: %(levelname)s:%(message)s', level=logging.DEBUG)

version = "0.0.5"

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

# Read the config file

config = load_config.load_config()
db_user = config.db_user
db_pass = config.db_pass
db_base = config.db_base
db_host = config.db_host

NULL, ALL, BORROWED = range(3)

################## START librarian #####################################
class librarian:
  def __init__(self):
	print _("Version: "),version
	builder = gtk.Builder()
	builder.add_from_file("ui/librarian.glade")
	builder.connect_signals(self)

	self.treeview  = builder.get_object('treeview1')
	self.booklist = builder.get_object("liststore1")
	self.status1 = builder.get_object("status1")
	'''
	column = gtk.TreeViewColumn('isbn', gtk.CellRendererText(), text=0)
	column.set_clickable(True)
	column.set_resizable(True)
	column.set_sort_column_id(0)
	self.treeview.append_column(column)
	'''
	column = gtk.TreeViewColumn(_('Author'), gtk.CellRendererText(), text=1)
	column.set_clickable(True)
	column.set_sort_indicator(True)
	column.set_resizable(True)
	column.set_visible(True)
	self.treeview.append_column(column)
	column.set_sort_column_id(1)

	column = gtk.TreeViewColumn(_('Title'), gtk.CellRendererText(), text=2)
	column.set_clickable(True)
	column.set_resizable(True)
	self.treeview.append_column(column)
	column.set_sort_column_id(2)

	self.get_book_list(1)
	self.status1.set_text("Version:" + version)

	self.booklist.set_sort_column_id(1, gtk.SORT_ASCENDING)

	gtk.main()


  def get_book_list(self, selection):
		#print selection
		self.booklist.clear()
		if selection == ALL:
			command = "SELECT * FROM books WHERE copies > 0 order by author;"
			self.status1.value = "All Books"
		elif selection == BORROWED:
			#command = "SELECT * FROM books where location IS NOT NULL AND location != 0 AND copies > 0 ORDER BY isbn;"
			command = "select * from books, borrows where books.id = borrows.book and i_date is null;"
		else:
			return
		#try:
		db = MySQLdb.connect(host=db_host, db=db_base,  passwd = db_pass)
		#except:
		#  print "No database connection.  Check some stuff"
		#  db = False

		if db:
			cur = db.cursor(MySQLdb.cursors.DictCursor)
			cur.execute(command)
			result = cur.fetchall()
			#print result
			for row in result:
				if row['author'] != None:
					name=row['author']
					#.strip('[').strip(']')
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
				self.booklist.append([row['isbn'], author, row['title'],
				row['abstract'], row['publisher'], row['city'], str(row['year']),
				row['id'], row['copies']])

		# Some test code
		'''
		books = list ()
		item = self.booklist.get_iter_first ()
		while ( item != None ):
			books.append (self.booklist.get_value (item,1))
			item = self.booklist.iter_next(item)
		print books
		'''
  def on_button_all_clicked(self, widget):
	# Display all books
	self.get_book_list(1)

  def on_button_loaned_clicked(self, widget):
	# Display all books on loan
	self.get_book_list(BORROWED)

  def on_button_scan_clicked(self, widget):
	# Open the scan thang
	logging.info("Do the scan thang")
	from guiscan import scanner
	s = scanner()
	scanner.on_button_scan_clicked(s)
	self.get_book_list(ALL) # All books


  def on_button_query_clicked(self, widget):
	from add_edit import add_edit
	## Get a book for editing.  SHOULD be devolved to add_edit !!
	foo,iter = self.treeview.get_selection().get_selected()
	#logging.info(iter)
	if iter:
		# Get the data
		bid = self.booklist.get_value(iter,7) # id better perhaps?
		adder = add_edit()
		#logging.info(adder)
		adder.populate(bid)
		adder.display()

	else:
		adder = add_edit()
		adder.display()
	self.get_book_list(1) # Repopulate book list.

	def printer(self):
		''' Print the currently displayed list. self.treeview'''
		# Simple sample print command
		#popen2.popen4("lpr -P [printer] " + output_file)

		pass


  def gtk_main_quit(self, widget):
    # Quit when we destroy the GUI
    if __name__ == "__main__":
	  gtk.main_quit()
	  quit(0)


#################### END librarian #####################################
#################### START printer #####################################
class printer:
	''' Print the currently displayed book list.
	This could be a save to file, as html or pdf too I guess.
	'''
	def format(self):
		pass
	def printer(self):
		pass
###################### END printer #####################################

if __name__ == "__main__":
	app = librarian()

