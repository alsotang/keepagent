#! /usr/bin/env python
# coding=utf-8

import SocketServer
import BaseHTTPServer
import logging
import json
import urllib2
import socket

import lib
import config

class LocalProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    # refer to: https://developers.google.com/appengine/docs/python/urlfetch/overview
    forbidden_headers = ('host', 'vary', # content-length, 
                         'via', 'x-forwarded-for', 'x-proxyuser-iP')
    
    def do_GET(self):
        # headers is a dict-like object, it doesn't have `iteritems` method.
        req_headers = dict(self.headers)  # dict
        req_headers = dict((h, v) for h, v in req_headers.iteritems() if h.lower() not in self.forbidden_headers)

        #logging.debug('req_headers: %s' % str(req_headers))
        req_body_len = int(req_headers.get('content-length', 0))
        req_body = self.rfile.read(req_body_len) # bin or str
        #logging.debug('req_body: %s', req_body) 

        payload = {
            'command': self.command, # str
            'path': self.path, # str
            'headers': json.dumps(req_headers), # json
            'payload': lib.btoa(req_body), # str
        }

        logging.debug('payload: %s' % (payload))


        # 初始化response的3个主要信息
        res_status_code = 500
        res_headers = {}
        res_content = ''

        # 向GAE获取的过程
        for i in range(3):
            try:
                res = urllib2.urlopen(gaeServer, lib.dumpDict(payload), lib.deadlineRetry[i])
            except (urllib2.URLError, socket.timeout) as e: 
                # 如果urllib2打开GAE都出错的话，就换个g_opener吧。
                urllib2.install_opener( get_g_opener('cn') )
                logging.error(e)
                continue

            if res.code == 200:  # 如果打开GAE没发生错误
                result = lib.loadDict( res.read() )
                logging.debug('result: %s' % result)

                res_status_code = result.status_code
                res_headers = json.loads(result.headers)
                res_content = lib.atob(result.content)
                break


        
        # 返回数据给浏览器的过程
        try:
            self.send_response(res_status_code) # 200 or or 301 or 404
            for k, v in res_headers.iteritems():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(res_content)
        except socket.error, e:
            # 打开了网页后，在数据到达浏览器之前又把网页关闭了而导致的错误。
            logging.error(e)

    def do_POST(self):
        return self.do_GET()



class LocalProxyServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer): 
    daemon_threads = True
    

def init_info():
    return (
        '#' * 50 +
'''
        KeepAgent version: %s
        Protocol: %s
        Listening Adress: localhost:%s
        Appid: %s
''' % (lib.version,
       lib.protocol,
       config.listen_port, 
       config.appid
      ) + 
        '#' * 50
        )

get_g_opener = lib.init_g_opener()

if lib.isDev:
    gaeServer = 'http://localhost:8080/'
else:
    gaeServer = ('http://%s.appspot.com/' % config.appid)
    urllib2.install_opener( get_g_opener('cn') )

logging.basicConfig(level=(logging.DEBUG if lib.isDev else logging.INFO), 
                    format='%(levelname)s - - %(asctime)s %(message)s',
                    datefmt='[%b %d %H:%M:%S]'
                   )

def main():
    print init_info() 

    server_address = ('', config.listen_port)
    httpd = LocalProxyServer(server_address, LocalProxyHandler)
    print 'server is running...'
    httpd.serve_forever()

    


if __name__ == '__main__':
    main()

