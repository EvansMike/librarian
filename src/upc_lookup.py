#!/bin/env python
# -*- coding: utf-8 -*-
'''
lookup a product using its upc
Example: https://api.upcitemdb.com/prod/trial/lookup?upc=5035822011717
upcitemdb.com allows 100 requests per day for free with no sign up required.
See https://www.upcitemdb.com/wp/docs/main/development/api-rate-limits/
'''
import requests
import json
import logging
from datetime import datetime
from xmlrpc.client import ServerProxy,Error
logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
DEBUG = logging.debug

class UPCLookup(object):
    
    def get_response(self, code, upc_key): #https://www.upcdatabase.com
        '''
        Example lookup result.
        {'ean': '7321900187220', 'status': 'success',
        'noCacheAfterUTC': <DateTime '2022-03-04T06:14:37' at 0x7f91723db760>,
        'pendingUpdates': 0, 'description': 'Space Cowboys', 'issuerCountry': 'Sweden',
        'found': True, 'lastModifiedUTC': <DateTime '2011-04-30T06:05:37' at 0x7f9172379220>,
        'message': 'Database entry found', 'size': '1 DVD', 'issuerCountryCode': 'se'}
        '''
        #return None
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
        if result ['found']:
            return result
        return None

    




if __name__ == '__main__':
    lookup = UPCLookup()
    r = lookup.get_response("7321900187220", api_key)
    print (json.dumps(r.json(), indent=2, sort_keys=True))
