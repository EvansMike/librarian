#!/bin/env/python
import urllib2 urllib

# build opener with HTTPCookieProcessor
o = urllib2.build_opener( urllib2.HTTPCookieProcessor() )
urllib2.install_opener( o )

# assuming the site expects 'user' and 'pass' as query params
p = urllib.urlencode( { 'username': 'me', 'password': 'mypass' } )

# perform login with params
f = o.open( 'http://www.mysite.com/login/',  p )
data = f.read()
f.close()

# second request should automatically pass back any
# cookies received during login... thanks to the HTTPCookieProcessor
f = o.open( 'http://www.mysite.com/protected/area/' )
data = f.read()
f.close()

