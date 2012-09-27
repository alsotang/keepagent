# coding=utf-8
from Crypto.Cipher import AES
import os

BLOCK_SIZE = AES.block_size

cipher = None

def init(key):
    '''
    @key key要求是32字节的str
    '''
    global cipher
    cipher = AES.new(key)


def pad(data):
    patlen = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + (patlen - 1) * ' ' + chr(patlen)

def unpad(data):
    patlen = ord(data[-1])
    return data[:-patlen]

def encrypt(data):
    return cipher.encrypt(pad(data))
    
def decrypt(data):
    return unpad(cipher.decrypt(data))

if __name__ == '__main__':
    import hashlib
    key = hashlib.md5(os.urandom(128)).hexdigest() # 随机生成一个32 bytes的key
    print key
    init(key) # 32 bytes 的str
    data = 'hello world' * 10
    print decrypt(encrypt(data))

