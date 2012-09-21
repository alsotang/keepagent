#! /usr/bin/env python
# coding=utf-8

import base64
import json
import zlib
import urllib2
import random

###########################
#### for common ####
###########################

version = 'v0.4.0'

isDev = 0
protocol = 'keepagent v1'

deadlineRetry = (2, 2, 5)

class JSDict(dict):
    '''convert a `dict` to a JavaScript-style object'''

    def __getattr__(self, attr):
        return self.get(attr, None)

def dumpDict(d):
    ''' d is a `dict`'''

    j = json.dumps(d)
    z = zlib.compress(j)
    return z

def loadDict(z):
    ''' z is a zlib blob'''

    j = zlib.decompress(z)
    d = json.loads(j)
    jd = JSDict(d)
    return jd



def btoa(s):
    '''convert blob to string in orther to
    be included in a JSON.
    '''

    return base64.encodestring(s)

def atob(b):
    '''inverse of `btoa`'''

    return base64.decodestring(b)



###########################
#### for client only ####
###########################

# produce a urllib2 opener use googlecn to proxy
def get_g_opener():
    import socket

    # 得到google.cn的ip集合: `googlecn_ips`
    google_cn_host = 'www.google.cn'
    results = socket.getaddrinfo(google_cn_host, None)
    googlecn_ips = set() # 不要重复的ip
    for i in results:
        ip = i[4][0]
        if ':' not in ip:
            googlecn_ips.add(ip)
    googlecn_ips = list(googlecn_ips)

    def _producer(ips):
        proxy_handler = urllib2.ProxyHandler(
            {'http': random.choice(googlecn_ips)}
            )
        g_opener = urllib2.build_opener(proxy_handler)
        return g_opener
    return _producer(googlecn_ips)

    



if __name__ == '__main__':
    pass




    




