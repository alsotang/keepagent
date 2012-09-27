#! /usr/bin/env python
# coding=utf-8

# to alsotang: git commit时记得修改crypt_key和version

import base64
import json
import zlib
import os

try:
    import cipher
    #如果修改了crypt_key，记得重新上传server。
    crypt_key = ''
    if crypt_key:
        cipher.init(crypt_key)
except ImportError, e:
    cipher = None

version = 'v1.1.0'

###

protocol = 'keepagent v2'

deadlineRetry = (2, 3, 5, 60)

basedir = os.path.dirname(__file__)

def encrypt(blob):
    if cipher and crypt_key:
        return '1' + cipher.encrypt(blob)
    return '0' + blob

def decrypt(blob):
    if blob[0] == '0':
        return blob[1:]
    else:
        return cipher.decrypt(blob[1:])

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
    text = 'hello world ' * 10
    print decrypt(encrypt(text))



    




