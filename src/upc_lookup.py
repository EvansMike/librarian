#!/bin/env python
# -*- coding: utf-8 -*-
'''
lookup a product using its upc at https://www.upcdatabase.com/
or https://api.upcdatabase.org.
Ideally when one returns nothing, try the fallback.
'''
import requests
import json
import logging
from datetime import datetime
from xmlrpc.client import ServerProxy,Error
logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
DEBUG = logging.debug

class UPCLookup(object):
    
    def old_get_response(self, code, upc_key): #https://www.upcdatabase.com
        '''
        Example lookup result.
        {'ean': '7321900187220', 'status': 'success',
        'noCacheAfterUTC': <DateTime '2022-03-04T06:14:37' at 0x7f91723db760>,
        'pendingUpdates': 0, 'description': 'Space Cowboys', 'issuerCountry': 'Sweden',
        'found': True, 'lastModifiedUTC': <DateTime '2011-04-30T06:05:37' at 0x7f9172379220>,
        'message': 'Database entry found', 'size': '1 DVD', 'issuerCountryCode': 'se'}

        We only need return description, or title and media type though.
        
        '''
        if not upc_key: # You need a key.
            return
        print(len(code))
        params = {'rpc_key': upc_key}
        s = ServerProxy('https://www.upcdatabase.com/xmlrpc')
        if len(code.strip()) == 12:
            params['upc'] = code.strip()
        elif len(code.strip()) == 13:
            print(code)
            params['ean'] = code.strip()
        #DEBUG(params)
        result = s.lookup(params)
        if result ['found'] == True:
            result['mtype'] = result['size']
            return result
        #else: TODO
        #    self.fallback_get_response(code, api_key)
        return None


    def get_response(self, code, upc_key):
        '''
        upcitemdb.com claim to have 398 million items.
        No key is required for free service but the limit is 100 lookups per day.
        Which is probably fine for this use case.
        CD's are problematic as there's no artist field in the result.
        Maybe requiring another lookup in  https://gnudb.org/ or similar
        '''
        DEBUG(code)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate',
            #'user_key': 'only_for_dev_or_pro',
            #'key_type': '3scale'
        }
        resp = requests.get(f'https://api.upcitemdb.com/prod/trial/lookup?upc={code}', headers=headers)
        data = json.loads(resp.text)
        resp_headers = resp.headers
        DEBUG(f"Remaining = {resp_headers['X-RateLimit-Remaining']} requests\n")
        DEBUG(data)
        result = {}
        if data['total'] != 0:
            item = data['items'][0]
            print(f"{item['ean']}\t{item['title']}\t{item['category']}\n")
            result['description'] = item['title']
            if "DVD" in item['category']: result['mtype'] = "DVD" 
            elif "Music CDs" in item['category']: result['mtype'] = "CD"
            return result
        else:
             return None


    def add_missing(self, book):
        '''
        See Bug-343
        http://localhost/mantisbt/view.php?id=343
        '''
        return

if __name__ == '__main__':
    lookup = UPCLookup()
    r = lookup.get_response("7321900187220", api_key)
    print (json.dumps(r.json(), indent=2, sort_keys=True))
