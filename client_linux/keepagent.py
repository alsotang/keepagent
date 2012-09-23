#! /usr/bin/env python
# coding=utf-8

# Inspired by and based on [GoAgent](https://code.google.com/p/goagent/).

import SocketServer
import BaseHTTPServer
import logging
import json
import urllib2
import socket
import ssl

import lib
import config
from certutil import CertUtil

class LocalProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    # refer to: https://developers.google.com/appengine/docs/python/urlfetch/overview
    forbidden_headers = ('host', 'vary', # content-length, 
                         'via', 'x-forwarded-for', 'x-proxyuser-iP')
    
    def do_GET(self):

        # headers is a dict-like object, it doesn't have `iteritems` method.
        req_headers = dict(self.headers)  # dict
        req_headers = dict((h, v) for h, v in req_headers.iteritems() if h.lower() not in self.forbidden_headers)

        self.log_request(200)
        logging.info('req_headers: %s' % req_headers)

        req_body_len = int(req_headers.get('content-length', 0))
        req_body = self.rfile.read(req_body_len) # bin or str

        payload = {
            'command': self.command, # str
            'path': self.path, # str
            'headers': json.dumps(req_headers), # json
            'payload': lib.btoa(req_body), # str
        }



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


    def do_CONNECT(self): 
        host, _, port = self.path.rpartition(':')
        
        hostCert, hostKey = CertUtil.getCertificate(host)

        self.log_request(200)
        self.connection.sendall('%s 200 OK\r\n\r\n' % self.protocol_version)

        self._oripath = self.path

        logging.info(self.path)
        
        self.connection = ssl.wrap_socket(self.connection, hostKey, hostCert, True)
        self.rfile = self.connection.makefile('rb', self.rbufsize)
        self.wfile = self.connection.makefile('wb', self.wbufsize)
        self.raw_requestline = self.rfile.readline(8192)

        self.parse_request()

        logging.info(dict(self.headers))
        #if 'host' in self.headers:
            #self.path = 'https://%s:%s%s' % (self.headers['Host'].partition(':')[0], port or 443, self.path)
        #else:
        if self.path[0] == '/':
            if 'Host' in self.headers:
                self.path = 'https://%s:%s%s' % (self.headers['Host'].partition(':')[0], port or 443, self.path)
            else:
                self.path = 'https://%s%s' % (self._oripath, self.path)
            self.requestline = '%s %s %s' % (self.command, self.path, self.protocol_version)

        logging.info(self.path)

        self.do_GET()
        
        




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
    
    CertUtil.init()

    server_address = ('', config.listen_port)
    httpd = LocalProxyServer(server_address, LocalProxyHandler)
    print 'server is running...'
    httpd.serve_forever()

    


if __name__ == '__main__':
    main()

