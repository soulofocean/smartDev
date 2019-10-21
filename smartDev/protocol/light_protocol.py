#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""light protocol handle
by Kobe Gong. 2018-1-15
"""

import asyncio
import json
import re
import struct
import time
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
        self.msgst = defaultdict(lambda: {})

    def connection_made(self, transport):
        self.transport = transport
        self.LOG.warn('connection setup success!')
        self.to_register_dev()

    def data_received(self, data):
        self.queue_in.put_nowait(data)
        self.LOG.debug(protocol_data_printB(data, title="client get data:"))
        command = self.get_cmd_from_pkt(data)
        self.LOG.debug("RECV_CMD:{}".format(command))
        if command and b'"Result":' in data:
            # 收到的带有回复的才去计算时延，否则计算时延无意义
            self.init_msgst_dict(command)
            self.msgst[command]['time_info'].recv_update()
        self.LOG.debug("RECV:{}".format(data.__repr__()))

    def connection_lost(self, exc):
        self.LOG.critical('The server closed the connection!')
        if exc:
            self.LOG.critical('[{}]connection_lost exc:{}'.format(type(exc), repr(exc)))
        self.dev_register = False
        loop = asyncio.get_event_loop()
        while True:
            try:
                # print(time.time())
                peer_info = self.transport.get_extra_info('socket').getpeername()
                if peer_info and len(peer_info) == 2:
                    # print('peer_info:',peer_info)
                    # 10秒后重连
                    time.sleep(10)
                    # 此处出了异常很可能不会捕获到，想要捕获到需要研究或者试试直接操作get_extra_info获取到的socket对象进行重连？
                    asyncio.create_task(loop.create_connection(lambda: self, peer_info[0], peer_info[1]))
                else:
                    raise AssertionError("get peer_info error.")
            except Exception as ex:
                print("EX:{}".format(ex.__repr__()))
            else:
                break

    def msg_build(self, data, ack=b'\x01'):
        # self.LOG.info("send msg: " + self.convert_to_dictstr(data))
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
                        # self.LOG.error('data field is empty!')
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
            if True or msg[4 + 20:4 + 20 + 20] == self.device_id or msg[4 + 20:4 + 20 + 20] == self.device_id.encode(
                    'utf-8'):
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
                # self.LOG.info("recv msg: " + self.convert_to_dictstr(data))
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
        while self.getStopConition() == False:
            if self.queue_in.empty():
                pass
            else:
                ori_data = self.left_data + self.queue_in.get_nowait()
                while len(ori_data) < self.min_length:
                    ori_data += self.queue_in.get_nowait()
                data_list, self.left_data = self.protocol_data_washer(ori_data)
                if data_list:
                    for request_msg in data_list:
                        # print("rsv:{}".format(request_msg))
                        # self.LOG.info("rsv:{}".format(request_msg))
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
            await asyncio.sleep(self.procInv)

    async def send_data_once(self, data=b''):
        if data:
            self.queue_out.put_nowait(data)

        if self.queue_out.empty():
            pass
        else:
            data = await self.queue_out.get()
            self.transport.write(data)
            self.LOG.info(protocol_data_printB(data, title="client send data:"))
            self.LOG.info(repr(data))

    async def send_data_loop(self):
        while self.getStopConition() == False:
            if self.queue_out.empty():
                pass
            else:
                data = await self.queue_out.get()
                command = self.get_cmd_from_pkt(data)
                self.LOG.debug("SEND_CMD:{}".format(command))
                if command and b'"Result":' not in data:
                    # 发送ACK包的时候不需要计算时延，也不需要重置发送时间
                    self.init_msgst_dict(command)
                    self.msgst[command]['time_info'].send_update()
                # print("send:{}".format(data))
                self.transport.write(data)
                self.LOG.debug(protocol_data_printB(data, title="client send data:"))
                self.LOG.debug("SEND:{}".format(repr(data)))
            await asyncio.sleep(self.procInv)

    def to_send_data(self, data):
        self.queue_out.put_nowait(data)

    def convert_to_dictstr(self, src):
        if isinstance(src, dict):
            return json.dumps(src, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

        elif isinstance(src, str):
            return json.dumps(json.loads(src), sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

        elif isinstance(src, bytes):
            return json.dumps(json.loads(src.decode('utf-8')), sort_keys=True, indent=4, separators=(',', ': '),
                              ensure_ascii=False)

        else:
            self.LOG.error('Unknow type(%s): %s' % (src, str(type(src))))
            return None

    def get_cmd_from_pkt(self, pkt: bytes):
        try:
            m = re.search(b'"Command":.*?"(\w+)"', pkt)
            if m:
                return m.group(1)
            return None
        except Exception as e:
            self.LOG.error("get_cmd_from_pkt exception:{}".format(repr(e)))
            return None

    def init_msgst_dict(self, command):
        if command in self.msgst:
            pass
        else:
            self.msgst[command] = {
                'req': 0,
                'rsp': 0,
                'rsp_fail': 0,
                'time_info': common_APIs.msgst_time_info()
            }
