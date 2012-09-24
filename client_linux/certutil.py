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


class CertUtil(object):
    CA = None
    CALock = threading.Lock()
    EXPIRE_DELAY = 60*60*24*365*10 # 10 years

    CERT_SUBJECTS = crypto.X509Name(crypto.X509().get_subject())
    CERT_SUBJECTS.C = 'CN'
    CERT_SUBJECTS.ST = 'SiChuan'
    CERT_SUBJECTS.L = 'SiChuan Univ.'
    CERT_SUBJECTS.OU = 'KeepAgent Branch'

    @classmethod
    def loadPEM(cls, pem, method):
        methods = ('load_certificate', 'load_privatekey')
        return getattr(crypto, methods[method])(crypto.FILETYPE_PEM, pem)

    @classmethod
    def dumpPEM(cls, obj, method):
        methods = ('dump_certificate', 'dump_privatekey')
        return getattr(crypto, methods[method])(crypto.FILETYPE_PEM, obj)

    @classmethod
    def createPKey(cls):
        pkey = crypto.PKey()
        pkey.generate_key(crypto.TYPE_RSA, 1024)
        return pkey

    @classmethod
    def createCert(cls, host, digest='sha1'):
        cert = crypto.X509() # 得到一个X509对象
        cert.set_version(0)
        cert.set_serial_number( int(time.time() * 10000000) ) # 序号，不重复即可。

        #证书有效与过期时间
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter( cls.EXPIRE_DELAY )

        cert.set_issuer( cls.CA[0].get_subject() ) # 得到CA的信息

        subjects = crypto.X509Name(cls.CERT_SUBJECTS)
        subjects.O = host
        subjects.CN = host
        cert.set_subject(subjects)

        pubkey = cls.createPKey()
        cert.set_pubkey(pubkey)

        cert.sign(cls.CA[1], digest)

        return (cls.dumpPEM(cert, 0), cls.dumpPEM(pubkey, 1))
    
    @classmethod
    def getCertificate(cls, host):
        certFile = os.path.join(lib.basedir, 'certs/%s.crt' % host)
        keyFile = os.path.join(lib.basedir, 'certs/%s.key' % host)

        if os.path.exists(certFile):
            return (certFile, keyFile)
        else:
            with cls.CALock:
                if not os.path.exists(certFile):
                    logging.info('generate certificate for %s', host)
                    cert, pkey = cls.createCert(host)
                    lib.writeBinFile(certFile, str(cert))
                    lib.writeBinFile(keyFile, str(pkey))
        return (certFile, keyFile)

    @classmethod
    def init(cls):
        certFile = os.path.join( lib.basedir, 'CA.crt') 
        keyFile = os.path.join( lib.basedir, 'CA.key')
        cacert = lib.readBinFile(certFile)
        cakey = lib.readBinFile(keyFile)
        cls.CA = (cls.loadPEM(cacert, 0), cls.loadPEM(cakey, 1))

if __name__ == '__main__':
    # 不要随便运行这段代码，运行后将生成新的CA相关文件，需要把浏览器中的CA文件删除后
    # 重新导入新生成的。
    CASubjects = crypto.X509Name(CertUtil.CERT_SUBJECTS)
    CASubjects.OU = 'KeepAgent Root'
    CASubjects.O = 'KeepAgent'
    CASubjects.CN = 'KeepAgent CA'


    def makeCA():
        '''得到一对新的CA.crt与CA.key'''

        cert = crypto.X509()
        cert.set_version(0)
        cert.set_serial_number(0)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(CertUtil.EXPIRE_DELAY)
        cert.set_issuer(CASubjects)
        cert.set_subject(CASubjects)

        pubkey = CertUtil.createPKey()
        cert.set_pubkey(pubkey)
        cert.sign(pubkey, 'sha1')
        return (CertUtil.dumpPEM(cert, 0), CertUtil.dumpPEM(pubkey, 1))

    for f in os.listdir('certs'):
        os.remove( os.path.join('certs', f))

    certFile = os.path.join(lib.basedir, 'CA.crt')
    keyFile = os.path.join(lib.basedir, 'CA.key')

    cert, key = makeCA()
    lib.writeBinFile(certFile, cert)
    lib.writeBinFile(keyFile, key)
    














    



