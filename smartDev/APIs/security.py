#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""light protocol handle
by Kobe Gong. 2018-4-19
"""

import base64
import binascii
import hashlib
import hmac
import struct

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Cipher import AES
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5


def pad_msg(text):
    pad_data = 16 - len(text) % 16
    if pad_data == 0:
        pad_data = 16
    #print('lem is: %d, pad len is: %d' % (len(text), pad_data))
    return text.encode('utf-8') + (chr(pad_data) * pad_data).encode('utf-8')


def unpad_msg(text):
    pad_data = text[-1]
    try:
        len = int(pad_data)
        print('len is: %d' % len)
    except Exception as e:
        print('except: %s' % e)
        return text

    if len <= 16 and text.endswith(struct.pack('B', len) * len):
        return text[0:-len]
    else:
        return text


def AES_CBC_encrypt(key, plain_msg, usebase64=False):
    print('encrypt key: %s' % key)
    if isinstance(key, bytes):
        pass
    else:
        key = key.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    msg = cipher.encrypt(pad_msg(plain_msg))

    if usebase64:
        msg = msg.encode('base64').rstrip()
        msg = msg.replace('\n', '')

    return msg


def AES_CBC_decrypt(key, ciphered_msg, usebase64=False):
    print('decrypt key: %s' % key)
    if isinstance(key, bytes):
        pass
    else:
        key = key.encode('utf-8')
    if usebase64:
        to_decipher_str = ciphered_msg.decode('base64')
    else:
        to_decipher_str = ciphered_msg

    cipher = AES.new(key, AES.MODE_ECB)
    msg = cipher.decrypt(to_decipher_str)
    return unpad_msg(msg)


if __name__ == '__main__':
    #############################################################
    # check AES_CBC_encrypt and AES_CBC_decrypt
    default_key = b'1234567890123456'
    content = b'w23456787654567\x02'
    ciphered = AES_CBC_encrypt(default_key, content)
    plain_content = AES_CBC_decrypt(default_key, ciphered)
    print(content)
    print(ciphered)
    print(plain_content)
    print(binascii.hexlify(ciphered).upper())
    #############################################################
