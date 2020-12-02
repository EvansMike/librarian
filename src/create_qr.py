#!/bin/env python
import qrencode
import zbar
import MySQLdb



try:
  db = MySQLdb.connect(db='books',  passwd = 'pu5tu1e');
except:
  print ("No database connection")
  db = False
#db= False # debugging
if db: cur = db.cursor()

cur.execute("select * from books;")
#rows = cur.fetchall()

row = cur.fetchone() 
while row is not None:
    title = row[1]
    authors = row[2]
    bar = row[3]
    qr = qrencode.encode('ISBN:'+ str(bar) + ' TITLE:' + str(title) + ' AUTHORS:' + str(authors))
    size = qr[1]
    #print size
    qr = qrencode.encode_scaled('ISBN:'+ str(bar) + ' TITLE:' + str(title) + ' AUTHORS:' + str(authors), size*2)
    img = qr[2]
    size = qr[1]
    #print size
    print (str(bar))
    img.save('../ISBN:' + str(bar) + '.png', 'png')
    row = cur.fetchone()




db.close()
