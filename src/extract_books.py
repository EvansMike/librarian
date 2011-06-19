#!/bin/env python

import parser

infile = "../Your Order with Amazon.co.uk (#202-0064800-2077403).mbox"

f = open(infile, 'r')

for line in f:
  if str.isdigit(line[0]):
   
    
    l2 = f.next()
    splits = l2.split(";")
    try:
      title = line.split("\"")[1]
      auth = splits[0]
      medium = splits[1]
      if medium == " Hardcover" or medium == " Paperback":
	print title + ", "+ auth + ", "+ medium
    
    except:
      pass