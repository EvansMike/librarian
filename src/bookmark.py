#!/bin/env python3
# -*- coding: utf-8 -*-
'''
Print a bookmark using the Epson receipt printer
The paper is 80mm wide.
The bookmark will include the following information:
- Date of purchase
_ Name of book
- Author of book
- Owner of book

Not necessarily in that or order though

'''

from . import book
import cups
from .db_queries import sql as sql
import logging
import MySQLdb
import MySQLdb.cursors
from . import messages
import os
import sys
import tempfile


# Set up debugging output level
logging.basicConfig(level=logging.INFO, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
'''if args.verbose:
    logging.disable(logging.DEBUG)
elif args.debug:
    pass
else:
    logging.disable(logging.DEBUG)
    logging.disable(logging.INFO)
'''
DEBUG = logging.debug
INFO  = logging.info




class Bookmark():
    def __init__(self):
        self.book = None # We'll get this later
        return


    def print_bookmark(self):
        '''
        Options for Epson Thermal Receipt printer are:
        PageSize/Media Size: RP82.5x297 RP80x297 RP60x297 RP58x297 RP82.5x2000 *RP80x2000 RP60x2000 RP58x2000 A4 LT Custom.WIDTHxHEIGHT
        TmxPrintSpeed/Print Speed: Auto 1 2 3 *4
        TmxPaperReduction/Paper Reduction: Off *Top Bottom Both
        TmxPaperSource/Paper Source: DocFeedCut DocFeedNoCut DocNoFeedCut DocNoFeedNoCut PageFeedCut *PageFeedNoCut PageNoFeedCut
        TmxPrinterType/Printer Type: *ThermalReceipt
        Resolution/Resolution: *180x180dpi 203x203dpi 162x162dpi 144x144dpi 126x126dpi 108x108dpi 90x90dpi 72x72dpi 68x68dpi 48x48dpi 0182x182dpi 0162x162dpi 0142x142dpi 0121x121dpi 0102x102dpi 081x81dpi 077x77dpi 056x56dpi
        TmxFeedPitch/Pitch of Feed: *180.0 203.2 360.0 406.4
        TmxMaxBandWidth/Maximum Band Width: 360 384 416 420 436 *512 576 640
        TmxBandLines/Band Lines: *256
        TmxSpeedControl/Speed Control: *0,0,0,0 -1,-1,-1,-1 9,7,4,1 10,7,4,1 11,8,4,1 13,9,5,1
        TmxBuzzerControl/Buzzer: *Off Before After
        TmxSoundPattern/Sound Pattern: Internal *A B C D E
        TmxBuzzerRepeat/Buzzer Repeat: *1 2 3 5
        TmxDrawerControl/Cash Drawer: *None Drawer#1,Before Drawer#1,After Drawer#2,Before Drawer#2,After
        TmxPulseOnTime/Pulse On Time: *20,10,100 40,20,100 60,30,120 80,40,160 100,50,200 120,60,240
        '''
        filename = "spool"
        with open(filename, 'w') as sp:
            sp.write("  MIKE'S LIBRARY BOOKMARK\n\n")
            sp.write("ISBN: 0713661682\n")
            sp.write("Author: Rob Mundle\n")
            sp.write("Title: Fatal Storm - The 54th Sydney to Hobart Yacht Race\n")
            sp.write("Owner: Mike Evans\n")
            sp.write("Purchase Date: 2022-04-02\n\n")
            sp.write("Borrower: Med Barker\n")
            sp.write("Borrowed: 2018-06-14 14:47:11\n\n\n\n")
        epson_paper = {'Resolution':'180x180dpi','TmxMaxBandWidth':'640','PageSize':'Custom.190x300','TmxFeedPitch':'180.0','TmxPaperSource':'DocFeedNoCut'}
        conn = cups.Connection()
        printers = conn.getPrinters()
        conn.setDefault('USB(ESDPRT001)_TM-T88V') # This need to be better. Probably a dialog.
        DEBUG(conn.printFile(conn.getDefault(), filename, " ", epson_paper))
        os.remove(filename) # No longer needed
        return


    def get_book_by_id():
        #self.book = ...
        return





if __name__ == '__main__':
    bookmark = Bookmark()
    bookmark.print_bookmark()
