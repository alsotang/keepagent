#! /usr/bin/env python
# coding=utf-8

import base64
import json
import zlib
import urllib2
import random
import os

###########################
#### for common ####
###########################

version = 'v1.0.0'

protocol = 'keepagent v1'

deadlineRetry = (2, 2, 5)

basedir = os.path.dirname(__file__)

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

def readBinFile(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    return content

def writeBinFile(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)

# 初始化并返回一个 get_g_opener 闭包函数，调用该函数会随机返回一个google的ip
def init_g_opener():
    import socket

    # 得到google.cn的ip集合: `googlecn_ips`
    google_cn_host = 'google.cn'
    google_hk_host = 'google.com.hk'

    def get_ips(host):
        '''由域名得到相应的ip列表'''

        results = socket.getaddrinfo(host, None)
        ips = set() # 不要重复的ip
        for i in results:
            ip = i[4][0]
            if ':' not in ip:
                ips.add(ip)
        ips = list(ips)
        return ips

    google_cn_ips = get_ips(google_cn_host)
    google_hk_ips = get_ips(google_hk_host)

    def get_g_opener(loc = 'cn'):
        '''返回一个使用google_cn或者google_hk作为代理的urllib2 opener'''

        proxy_handler = urllib2.ProxyHandler(
            # 从google_cn_ips 或者 google_hk_ips 随机选择一个IP出来
            {'http': random.choice( (google_cn_ips if loc == 'cn' else google_hk_ips) )}
            )
        g_opener = urllib2.build_opener(proxy_handler)
        return g_opener

    return get_g_opener

    



if __name__ == '__main__':
    pass




    




