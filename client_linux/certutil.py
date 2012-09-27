#! /usr/bin/env python
# coding=utf-8

import threading
import lib
import sys
import logging
import time
import os

try:
    from OpenSSL import crypto
except ImportError:
    logging.error('You should install `OpenSSL`, run `sudo pip install pyopenssl` or other command depends on your system.')
    sys.exit(-1)


CA = None
CALock = threading.Lock()
EXPIRE_DELAY = 60*60*24*365*10 # 10 years

# 网站证书的subjects
CERT_SUBJECTS = crypto.X509Name(crypto.X509().get_subject())
CERT_SUBJECTS.C = 'CN'
CERT_SUBJECTS.ST = 'SiChuan'
CERT_SUBJECTS.L = 'SiChuan Univ.'
CERT_SUBJECTS.OU = 'KeepAgent Branch'

# CA证书的subjects
CA_SUBJECTS = crypto.X509Name(CERT_SUBJECTS)
CA_SUBJECTS.OU = 'KeepAgent Root'
CA_SUBJECTS.O = 'KeepAgent'
CA_SUBJECTS.CN = 'KeepAgent CA'

def readBinFile(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    return content

def writeBinFile(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)

def loadPEM(pem, method):
    methods = ('load_certificate', 'load_privatekey')
    return getattr(crypto, methods[method])(crypto.FILETYPE_PEM, pem)


def dumpPEM(obj, method):
    methods = ('dump_certificate', 'dump_privatekey')
    return getattr(crypto, methods[method])(crypto.FILETYPE_PEM, obj)


def createPKey():
    pkey = crypto.PKey()
    pkey.generate_key(crypto.TYPE_RSA, 1024)
    return pkey


def createCert(host, digest='sha1'):
    cert = crypto.X509() # 得到一个X509对象
    cert.set_version(0)
    cert.set_serial_number( int(time.time() * 10000000) ) # 序号，不重复即可。

    #证书有效与过期时间
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(EXPIRE_DELAY )

    cert.set_issuer(CA[0].get_subject() ) # 得到CA的信息

    subjects = crypto.X509Name(CERT_SUBJECTS)
    subjects.O = host
    subjects.CN = host
    cert.set_subject(subjects)

    pubkey = createPKey()
    cert.set_pubkey(pubkey)

    cert.sign(CA[1], digest)

    return (dumpPEM(cert, 0), dumpPEM(pubkey, 1))


def getCertificate(host):
    certFile = os.path.join(lib.basedir, 'certs/%s.crt' % host)
    keyFile = os.path.join(lib.basedir, 'certs/%s.key' % host)

    if os.path.exists(certFile):
        return (certFile, keyFile)
    else:
        with CALock:
            if not os.path.exists(certFile):
                logging.info('generate certificate for %s', host)
                cert, pkey = createCert(host)
                writeBinFile(certFile, str(cert))
                writeBinFile(keyFile, str(pkey))
    return (certFile, keyFile)


def init():
    certFile = os.path.join( lib.basedir, 'CA.crt') 
    keyFile = os.path.join( lib.basedir, 'CA.key')
    cacert = readBinFile(certFile)
    cakey = readBinFile(keyFile)
    global CA
    CA = (loadPEM(cacert, 0), loadPEM(cakey, 1))

def makeCA():
    '''得到一对新的CA.crt与CA.key'''

    cert = crypto.X509()
    cert.set_version(0)
    cert.set_serial_number(0)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(EXPIRE_DELAY)
    cert.set_issuer(CA_SUBJECTS)
    cert.set_subject(CA_SUBJECTS)

    pubkey = createPKey()
    cert.set_pubkey(pubkey)
    cert.sign(pubkey, 'sha1')
    return (dumpPEM(cert, 0), dumpPEM(pubkey, 1))

if __name__ == '__main__':
    # 不要随便运行这段代码，运行后将生成新的CA相关文件，需要把浏览器中的CA文件删除后
    # 重新导入新生成的。

    for f in os.listdir('certs'):
        if f.endswith('.md'): continue
        os.remove( os.path.join('certs', f))

    certFile = os.path.join(lib.basedir, 'CA.crt')
    keyFile = os.path.join(lib.basedir, 'CA.key')

    cert, key = makeCA()
    writeBinFile(certFile, cert)
    writeBinFile(keyFile, key)
    














    



