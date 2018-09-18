#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""light protocol handle
by Kobe Gong. 2018-1-15
"""

import asyncio
import binascii
import datetime
import json
import logging
import os
import random
import re
import struct
import sys
import time
from abc import ABCMeta, abstractmethod
from collections import defaultdict

import APIs.common_APIs as common_APIs
from APIs.common_APIs import crc, crc16, protocol_data_printB
from APIs.security import AES_CBC_decrypt, AES_CBC_encrypt


class SDK(asyncio.Protocol):
    def __init__(self, LOG, min_length=10, encrypt_flag=0):
        self.queue_in, self.queue_out = asyncio.Queue(), asyncio.Queue()
        self.min_length = min_length
        self.LOG = LOG

        self.left_data = b''
        self.encrypt_flag = encrypt_flag
        self.name = 'Device controler'
        # status data:
        # 4bytes
        self.version = b'HDXM'
        # 20bytes
        self.device_id = b'\x31\x30\x30\x34\x32\x30\x31\x36\x35\x38\x46\x43\x44\x42\x44\x38\x33\x34\x31\x45'
        # 4bytes
        self.pkg_number = b'\x00\x00\x00\x01'

    def connection_made(self, transport):
        self.transport = transport
        self.LOG.warn('connection setup success!')
        self.to_register_dev()

    def data_received(self, data):
        self.queue_in.put_nowait(data)
        self.LOG.debug(protocol_data_printB(data,title="client get data:"))
        self.LOG.debug(repr(data))

    def connection_lost(self, exc):
        self.LOG.critical('The server closed the connection!')
        self.dev_register = False

    def msg_build(self, data, ack=b'\x01'):
        #self.LOG.info("send msg: " + self.convert_to_dictstr(data))
        # need encrypt
        if self.encrypt_flag:
            data = AES_CBC_encrypt(self._encrypt_key, data)
        if isinstance(data, type(b'')):
            pass
        else:
            data = data.encode('utf-8')
        if ack == b'\x00':
            src_id = self.device_id
            dst_id = b'\x30' * 20
            self.add_pkg_number()
        else:
            src_id = self.device_id
            dst_id = b'\x30' * 20

        if isinstance(src_id, type(b'')):
            pass
        else:
            src_id = src_id.encode('utf-8')

        msg_head = self.version + src_id + dst_id + ack + self.pkg_number
        msg_length = self.get_msg_length(data)
        msg_crc16 = crc16(data)
        msg = msg_head + msg_length + b'\x00\x00' + msg_crc16 + data
        return msg

    def protocol_data_washer(self, data):
        data_list = []
        left_data = b''

        while data[0:1] != b'\x48' and len(data) >= self.min_length:
            self.LOG.warn('give up dirty data: %02x' % ord(str(data[0])))
            data = data[1:]

        if len(data) < self.min_length:
            left_data = data
        else:
            if data[0:4] == b'\x48\x44\x58\x4d':
                length = struct.unpack('>I', data[49:53])[0]
                if length <= len(data[57:]):
                    data_list.append(data[0:57 + length])
                    data = data[57 + length:]
                    if data:
                        data_list_tmp, left_data_tmp = self.protocol_data_washer(
                            data)
                        data_list += data_list_tmp
                        left_data += left_data_tmp
                    else:
                        #self.LOG.error('data field is empty!')
                        pass
                elif length >= 1 and length < 10000:
                    left_data = data
                else:
                    for s in data[:4]:
                        self.LOG.warn('give up dirty data: %02x' % ord(chr(s)))
                    left_data = data[4:]
            else:
                pass

        return data_list, left_data

    def add_pkg_number(self):
        pkg_number = struct.unpack('>I', self.pkg_number)[0]
        pkg_number += 1
        self.pkg_number = struct.pack('>I', pkg_number)

    def get_pkg_number(self, data):
        return struct.unpack('>I', data)[0]

    def set_pkg_number(self, data):
        self.pkg_number = data

    def get_msg_length(self, msg):
        return struct.pack('>I', len(msg))

    def protocol_handler(self, msg):
        ack = False
        if msg[0:4] == b'\x48\x44\x58\x4d':
            if True or msg[4 + 20:4 + 20 + 20] == self.device_id or msg[4 + 20:4 + 20 + 20] == self.device_id.encode('utf-8'):
                if msg[44:45] != b'\x00':
                    ack = True

                self.set_pkg_number(msg[45:49])
                data_length = struct.unpack('>I', msg[49:53])[0]
                crc16 = struct.unpack('>H', msg[55:57])
                # need decrypt
                if self.encrypt_flag:
                    data = json.loads(AES_CBC_decrypt(self.sim_obj._encrypt_key,
                                                      msg[57:57 + data_length]).decode('utf-8'))
                else:
                    data = json.loads(msg[57:57 + data_length].decode('utf-8'))
                #self.LOG.info("recv msg: " + self.convert_to_dictstr(data))
                rsp_msg = self.dev_protocol_handler(data, ack)
                if rsp_msg:
                    final_rsp_msg = self.msg_build(rsp_msg)
                else:
                    final_rsp_msg = 'No_need_send'
                return final_rsp_msg

            else:
                self.LOG.error('Unknow msg: %s' % (msg))
                return "No_need_send"

        else:
            self.LOG.warn('Unknow msg: %s!' % (msg))
            return "No_need_send"

    async def schedule(self):
        if self.queue_in.empty():
            pass
        else:
            ori_data = self.left_data + self.queue_in.get_nowait()
            while len(ori_data) < self.min_length:
                ori_data += self.queue_in.get_nowait()
            data_list, self.left_data = self.protocol_data_washer(ori_data)
            if data_list:
                for request_msg in data_list:
                    response_msg = self.protocol_handler(request_msg)
                    if response_msg == 'No_need_send':
                        pass
                    elif response_msg:
                        self.queue_out.put_nowait(response_msg)
                    else:
                        self.LOG.error(protocol_data_printB(
                            request_msg, title='%s: got invalid data:' % (self.name)))
            else:
                self.LOG.warn('whwer is go?')
                pass

    async def send_data_once(self, data=b''):
        if data:
            self.queue_out.put_nowait(data)

        if self.queue_out.empty():
            pass
        else:
            data = await self.queue_out.get()
            self.transport.write(data)
            self.LOG.debug(protocol_data_printB(data, title="client send data:"))
            self.LOG.debug(repr(data))

    def to_send_data(self, data):
        self.queue_out.put_nowait(data)

    def convert_to_dictstr(self, src):
        if isinstance(src, dict):
            return json.dumps(src, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

        elif isinstance(src, str):
            return json.dumps(json.loads(src), sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

        elif isinstance(src, bytes):
            return json.dumps(json.loads(src.decode('utf-8')), sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

        else:
            self.LOG.error('Unknow type(%s): %s' % (src, str(type(src))))
            return None
