#! /usr/bin/env python
# coding=utf-8

import SocketServer
import BaseHTTPServer
import logging
import yaml
import json
import urllib2
import socket

import lib

config = yaml.load(open('config.yaml')) # config is a `dict`
config = lib.JSDict(config)  # turn `dict` to JavaScript-style object


# TODO: connect to Google BeiJing
gaeServer = ('http://%s.appsp0t.com/' % config.appid if not config.isDev else 'http://localhost:8080/')

class LocalProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    # refer to: https://developers.google.com/appengine/docs/python/urlfetch/overview
    forbidden_headers = ('host', 'vary', # content-length, 
                         'via', 'x-forwarded-for', 'x-proxyuser-iP')
    
    def do_GET(self):
        # headers is a dict-like object, it doesn't have `iteritems` method.
        req_headers = dict(self.headers)  # dict
        req_headers = dict((h, v) for h, v in req_headers.iteritems() if h.lower() not in self.forbidden_headers)

        logging.debug('req_headers: %s' % str(req_headers))
        req_body_len = int(req_headers.get('content-length', 0))
        req_body = self.rfile.read(req_body_len) # bin or str
        logging.debug('req_body: %s', req_body) 

        req_payload = {
            'command': self.command, # str
            'path': self.path, # str
            'headers': json.dumps(req_headers), # json
            'payload': lib.btoa(req_body), # str
        }

        res_status_code = 500
        res_headers = {}
        res_content = ''

        logging.debug('req_payload: %s' % (req_payload))
        try: # TODO: add deadline; try 3 times
            res = urllib2.urlopen(gaeServer, lib.dumpDict(req_payload))

            result = lib.loadDict( res.read() )
            logging.debug('result: %s' % result)

            res_status_code = result.status_code
            res_headers = json.loads(result.headers)
            res_content = lib.atob(result.content)

        except urllib2.URLError, e: # TODO: add more error handlers
            logging.error(e)
        
        try:
            self.send_response(res_status_code) # 200 or or 301 or 404
            for k, v in res_headers.iteritems():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(res_content)
        except socket.error, e:
            logging.error(e)

    def do_POST(self):
        return self.do_GET()



class LocalProxyServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer): 
    daemon_threads = True
    allow_reuse_address = True
    

def init_info():
    return (
        '#' * 50 +
'''
        KeepAgent: %s
        Listening Adress: %s
        Appid: %s
''' % (config.version, 'localhost:7808', config.appid) + 
        '#' * 50
        )


def main():
    print init_info() 

    logging.basicConfig(level=(logging.DEBUG if config.isDev else logging.INFO), 
                        format='%(levelname)s - - %(asctime)s %(message)s',
                        datefmt='[%b %d %H:%M:%S]'
                       )
    server_address = ('', 7808)

    httpd = LocalProxyServer(server_address, LocalProxyHandler)
    httpd.serve_forever()

    


if __name__ == '__main__':
    main()

