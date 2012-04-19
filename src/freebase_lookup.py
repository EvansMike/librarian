#!/bin/env python
# Derived from: http://www.freebase.com/docs/mql/ch04.html


import sys            # Command-line arguments, etc.
import simplejson     # JSON encoding.
import urllib         # URI encoding.
import urllib2        # High-level URL content fetching.

# These are some constants we'll use.
SERVER = 'api.freebase.com'              # Metaweb server
SERVICE = '/api/service/mqlread'         # Metaweb service


class freebase_cd:
  def __init__(self):
    pass
    
  def get_album_id(self, artist, album):
    album_id = None# Compose our MQL query as a Python data structure.
    # The query is an array in case multiple bands share the same name.
    query = [{'type': '/music/artist',       # Our MQL query in Python.
              'name': artist,                  # Place the band in the query.
              'album': [{ 'name': album,      # None is Python's null.
                          'release_date': None,
                          'id':None,
                          'sort': 'release_date' }]}]

    # Put the query in an envelope
    envelope = {
        'query': query,              # The query property specifies the query.
        'escape': False              # Turns off HTML escaping.
        }

    # These five lines are the key code for using mqlread
    encoded = simplejson.dumps(envelope)            # JSON encode the envelope.
    params = urllib.urlencode({'query':encoded})    # Escape request parameters.
    url ='http://%s%s?%s' % (SERVER,SERVICE,params) # The URL to request.
    f = urllib2.urlopen(url)                        # Open the URL as a file.
    response = simplejson.load(f)                   # Read and JSON parse response.

    # Check for errors and exit with a message if the query failed.
    if response['code'] != '/api/status/ok':                   # If not okay...
        error = response['messages'][0]                        # First msg object.
        sys.exit('%s: %s' % (error['code'], error['message'])) # Display code,msg.

    # No errors, so handle the result
    result = response['result']           # Open the response envelope, get result.

    # Check the number of matching bands
    if len(result) == 0:
        sys.exit('Unknown band')
    elif len(result) > 1:
        print "Warning: multiple bands named " + band + ". Listing first only."

    result = result[0]                    # Get first band from array of matches.
    if not result['album']:               # Exit if band has no albums
        sys.exit(band + ' has no known albums.')
        
    #result = result[0]                    # Get first band from array of matches.
    for album in result['album']:         # Loop through the result albums.
        name = album['name']              # Album name.
        date = album['release_date']      # Release date timestamp or null.
        album_id = album['id']            #Album ID
        if not date: date = ''            
        else: date = ' [%s]' % date[0:4]  # Just the 4-digit year in brackets.
        print "%s - %s" % (name.encode('iso-8859-1','ignore'), date)       # Print name and date.
        #self.get_tracks(str(name), str(album_id))

    return album_id
    
    
  def get_tracks(self, alid):
    ''' return a dictionary of tracks.
    
    '''
    query = {
        'type': "/music/album",
        'id': alid,
        # Get track names and lengths, sorted by index
        "releases" : [{'track': [{'name':None, 'length':None, 'index':None, 'sort':"index"}]}]
    };
    
    # Put the query in an envelope
    envelope = {
        'query': query,              # The query property specifies the query.
        'escape': False              # Turns off HTML escaping.
        }

    # These five lines are the key code for using mqlread
    encoded = simplejson.dumps(envelope)            # JSON encode the envelope.
    params = urllib.urlencode({'query':encoded})    # Escape request parameters.
    url ='http://%s%s?%s' % (SERVER,SERVICE,params) # The URL to request.
    f = urllib2.urlopen(url)                        # Open the URL as a file.
    response = simplejson.load(f)                   # Read and JSON parse response.

    # Check for errors and exit with a message if the query failed.
    if response['code'] != '/api/status/ok':                   # If not okay...
        error = response['messages'][0]                        # First msg object.
        sys.exit('%s: %s' % (error['code'], error['message'])) # Display code,msg.

    # No errors, so handle the result
    result = response['result']           # Open the response envelope, get result.
    #return result

    tracklist = result["releases"]
    tracklist = tracklist[0]
    tracklist = tracklist['track']
    
    return tracklist
    
  def run_test(self):
    '''
    Do a test query and make sure result is correct    
    
    '''
    alid = self.get_album_id("Kate Bush", "The Kick Inside")
    tracks = self.get_tracks(alid)
    for track in tracks:
      print track
    return True # On success
################### END CLASS freebase_cd ##############################

#Test malarky
if __name__ == "__main__":
  app = freebase_cd()
  app.run_test()
