#! /usr/bin/env python
# coding=utf-8

import webapp2
import logging
import zlib
import json
import os
import base64


from google.appengine.api import urlfetch

from lib import JSDict

__version__ = 'v0.1.0'

try: # detect it's in local or on GAE
    is_dev = os.environ['SERVER_SOFTWARE'].startswith('Dev')
except:
    is_dev = False

logging.basicConfig(level=logging.INFO if not is_dev else logging.DEBUG, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%b %d %H:%M:%S]')

class MainPage(webapp2.RequestHandler):
    def get(self):
        pageText = 'This webpage is keepagent server %s.' % __version__

        self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        self.response.write(pageText)
    
    def post(self):
        request_body = zlib.decompress(self.request.body)
        request_body = json.loads(request_body)
        request_body = JSDict(request_body)

        logging.debug('request_body: %s', request_body)

        method = getattr(urlfetch, request_body.command)
        data = urlfetch.fetch(request_body.path,
                              request_body.payload,
                              method,
                              json.loads(request_body.headers)
                             )
        #gzip_stream = StringIO(data.content)
        #gzip_file = gzip.GzipFile(fileobj=gzip_stream)
        #content = gzip_file.read()

        logging.debug('#' * 20)
        logging.debug(data.status_code)
        logging.debug((data.headers))
        #logging.debug(content)


        result = {
            'status_code': data.status_code, 
            'headers': dict(data.headers),
            'content': base64.encodestring(data.content),
        }

        result = json.dumps(result)
        
        self.response.write(zlib.compress(result))




app = webapp2.WSGIApplication([('/.*', MainPage)], debug = True)
