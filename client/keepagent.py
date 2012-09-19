#! /usr/bin/env python
# coding=utf-8

import SocketServer
import BaseHTTPServer
import logging
import yaml
import json
import urllib2
import zlib
import base64

from lib import JSDict

config = yaml.load(open('config.yaml'))
config = JSDict(config)  


gaeServer = ('http://%s.appsp0t.com/' % config.appid if not config.isDebug else 'http://localhost:8080/')

class LocalProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    # refer to: https://developers.google.com/appengine/docs/python/urlfetch/overview
    forbidden_headers = ('Content-Length', 'Host', 'Vary', 
                         'Via', 'X-Forwarded-For', 'X-ProxyUser-IP')
    
    def do_GET(self):
        headers = dict(self.headers)
        headers = dict((h, v) for h, v in headers.iteritems() if h not in self.forbidden_headers)
        payload_len = int(headers.get('Content-Length', 0))
        payload = {
            'path': self.path,
            'payload': self.rfile.read(payload_len), # TODO: treat payload as string. It will throw err if binary.
            'command': self.command,
            'headers': json.dumps(headers),
        }
        payload = json.dumps(payload)

        #logging.debug('payload: ', payload)

        try:
            res = urllib2.urlopen(gaeServer, zlib.compress(payload))
            data = zlib.decompress(res.read())
            data = JSDict(json.loads(data)) # TODO: encode and decode
        except urllib2.URLError, e:
            data = ''
            data.status_code = 404
            logging.error(e)
        
        self.send_response(data.status_code)
        for k, v in data.headers.iteritems():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(base64.decodestring(data.content))



class LocalProxyServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer): 
    daemon_threads = True
    allow_reuse_address = True
    

def init_info():
    return (
        '#' * 20 +
'''
KeepAgent: %s
Listening Adress: %s
Appid: %s
''' % (config.version, 'localhost:8964', config.appid) + 
    '#' * 20
        )


def main():
    print init_info() 

    logging.basicConfig(level=(logging.DEBUG if config.isDebug else logging.INFO), 
                        format='%(levelname)s - - %(asctime)s %(message)s',
                        datefmt='[%b %d %H:%M:%S]'
                       )
    server_address = ('', 8964)

    httpd = LocalProxyServer(server_address, LocalProxyHandler)
    httpd.serve_forever()

    


if __name__ == '__main__':
    main()

