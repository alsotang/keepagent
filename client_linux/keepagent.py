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

        # headers is a dict-like object, it doesn't have `iteritems` method, so convert it to `dict`
        req_headers = dict(self.headers)  # dict
        req_headers = dict((h, v) for h, v in req_headers.iteritems() if h.lower() not in self.forbidden_headers)
        req_headers['connection'] = 'close'

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
                urllib2.install_opener( get_g_opener('cn') ) # TODO: hk or cn, http or https
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

            res_headers['connection'] = 'close' # 这样不会对速度造成影响，反而能使很多的请求表现得更为准确。
            for k, v in res_headers.iteritems():
                try:
                    self.send_header(k, v)
                except UnicodeEncodeError: # google plus里面就遇到了v包含中文的情况
                    pass
            self.end_headers()
            self.wfile.write(res_content)
        except socket.error, e:
            # 打开了网页后，在数据到达浏览器之前又把网页关闭了而导致的错误。
            logging.error(e)

    def do_POST(self):
        return self.do_GET()

    def do_CONNECT(self): 
        host, _, port = self.path.rpartition(':')

        self.connection.sendall('%s 200 Connection established\r\n\r\n' % self.protocol_version)

        hostCert, hostKey = CertUtil.getCertificate(host)

        self._realpath = self.path

        self.request = ssl.wrap_socket(self.connection, hostKey, hostCert, True)
        self.setup()

        self.raw_requestline = self.rfile.readline(65537)

        self.parse_request()

        self.path = 'https://%s%s' % (self._realpath, self.path)

        self.do_GET()

        try:
            self.connection.shutdown(socket.SHUT_WR) # TODO: 发送相应http指令使socket关闭
        except socket.error:
            pass
        

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

gaeServer = ('http://%s.appspot.com/' % config.appid)
urllib2.install_opener( get_g_opener('cn') )


def main():
    print init_info() 
    
    CertUtil.init()

    server_address = ('', config.listen_port)
    httpd = LocalProxyServer(server_address, LocalProxyHandler)
    print 'server is running...'
    httpd.serve_forever()

    


if __name__ == '__main__':
    main()

