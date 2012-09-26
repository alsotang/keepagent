#! /usr/bin/env python
# coding=utf-8

import base64
import json
import zlib
import os

version = 'v1.0.1'

protocol = 'keepagent v1'

deadlineRetry = (2, 3, 5, 20)

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


if __name__ == '__main__':
    pass




    




