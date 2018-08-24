#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""devices sim
by Kobe Gong. 2018-1-15
"""

import asyncio
import copy
import datetime
import decimal
import json
import logging
import os
import random
import re
import shutil
import struct
import sys
import threading
import time
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from importlib import import_module

import APIs.common_APIs as common_APIs
from APIs.common_APIs import bit_clear, bit_get, bit_set, protocol_data_printB
from basic.log_tool import MyLogger
from basic.task import Task
from protocol.light_protocol import SDK


class BaseSim(SDK):
    __metaclass__ = ABCMeta

    def update_msgst(self, command, direct):
        if command in self.msgst:
            pass
        else:
            self.msgst[command] = {
                'req': 0,
                'rsp': 0,
            }

        self.msgst[command][direct] += 1

    def set_item(self, item, value):
        if item in self.__dict__:
            self.__dict__[item] = value
        else:
            self.LOG.error("Unknow item: %s" % (item))

    def add_item(self, item, value):
        try:
            setattr(self, item, value)
        except:
            self.LOG.error("add item fail: %s" % (item))

    def status_show(self):
        for item in sorted(self.__dict__):
            if item.startswith('_'):
                self.LOG.warn("%s: %s" % (item, str(self.__dict__[item])))

        self.LOG.warn('~' * 10)
        for msg_code in self.msgst:
            self.LOG.warn("%s:" % (msg_code))
            self.LOG.warn("\t\t\treq: %d" % (self.msgst[msg_code]['req']))
            self.LOG.warn("\t\t\trsp: %d" % (self.msgst[msg_code]['rsp']))
            self.LOG.warn("-" * 30)

    def to_to_send_msg(self, msg, ack=b'\x01'):
        self.update_msgst(json.loads(msg)['Command'], 'req')
        return self.to_send_data(self.msg_build(msg, ack))

    def status_report_monitor(self):
        need_send_report = False
        if not hasattr(self, 'old_status'):
            self.old_status = defaultdict(lambda: {})
            for item in self.__dict__:
                if item.startswith('_'):
                    self.LOG.yinfo("need check item: %s" % (item))
                    self.old_status[item] = copy.deepcopy(self.__dict__[item])

        for item in self.old_status:
            if self.old_status[item] != self.__dict__[item]:
                need_send_report = True
                self.old_status[item] = copy.deepcopy(self.__dict__[item])

        if need_send_report:
            self.send_msg(self.get_event_report(), ack=b'\x00')


class Door(BaseSim):
    def __init__(self, config_file, logger, N=0, tt=None, encrypt_flag=0, self_ip = None):
        super(Door, self).__init__(logger, encrypt_flag=encrypt_flag)
        module_name = "protocol.config.%s" % config_file
        mod = import_module(module_name)
        self.sim_config = mod
        self.LOG = logger
        self.N = N
        self.tt = tt
        self.encrypt_flag = encrypt_flag
        self.attribute_initialization()
        self.device_id = self._deviceID
        self.msgst = defaultdict(lambda: {})
        if self_ip:
            self._ip = self_ip

        # state data:
        self.task_obj = Task('Washer-task', self.LOG)
        self.dev_register = False
        self.command_list = getattr(self.sim_config, "Command_list")
        #self.create_tasks()

        self.msgs = []
        for msg_name in self.test_msgs["msgs"]:
            tmp_msg = msg_name.split('.')
            if tmp_msg[0] == 'COM_UPLOAD_DEV_STATUS':
                msg = self.get_upload_status()
            elif tmp_msg[0] == 'COM_UPLOAD_RECORD':
                msg = self.get_upload_record(tmp_msg[-1])
            elif tmp_msg[0] == 'COM_UPLOAD_EVENT':
                msg = self.get_upload_event(tmp_msg[-1])

            for i in range(self.test_msgs["msgs"][msg_name]):
                self.msgs.append(msg)
        self.msgs *= self.test_msgs["round"]
        random.shuffle(self.msgs)



    async def run_forever(self):
        sleep_s = self.test_msgs["interval"]
        if self.tt:
            sleep_s = self.tt
        sleep_s /= 1000.0
        now = lambda : time.time()
        start = now()
        self.LOG.warn("Sleep_second is {}".format(sleep_s))
        while True:
            await self.msg_dispatch()
            await self.schedule()
            await self.send_data_once()
            if(now()-start>=30):
                await self.to_send_heartbeat()
                start = now()
            if self.tt:
                await asyncio.sleep(self.tt / 1000.0)
            else:
                await asyncio.sleep(self.test_msgs["interval"] / 1000.0)

    def create_tasks(self):
        self.task_obj.add_task(
            'status maintain', self.status_maintain, 10000000, 100)

        self.task_obj.add_task('monitor status report',
                               self.status_report_monitor, 10000000, 1)

        self.task_obj.add_task(
            'heartbeat', self.to_send_heartbeat, 1000000, 1000)

    async def msg_dispatch(self):
        try:
            if self.dev_register == False:
                pass
            else:
                msg = self.msgs.pop()
                self.to_to_send_msg(msg, ack=b'\x00')
        except:
            pass

    def status_maintain(self):
        for item in self.SPECIAL_ITEM:
            if "maintain" not in self.SPECIAL_ITEM[item]["use"]:
                continue
            if self.__dict__[item] != self.SPECIAL_ITEM[item]["init_value"]:
                tmp_item = '_current_time_' + item
                if '_current_time_' + item in self.__dict__:
                    if self.__dict__[tmp_item] > 0:
                        self.set_item(tmp_item, self.__dict__[tmp_item] - 1)
                        if self.__dict__[tmp_item] <= 0:
                            self.set_item(
                                tmp_item, self.SPECIAL_ITEM[item]["wait_time"])
                            self.set_item(
                                item, self.SPECIAL_ITEM[item]["init_value"])
                    else:
                        self.set_item(
                            item, self.SPECIAL_ITEM[item]["init_value"])
                else:
                    self.add_item('_current_time_' + item,
                                  self.SPECIAL_ITEM[item]["wait_time"])

    def status_report_monitor(self):
        need_send_report = False
        if not hasattr(self, 'old_status'):
            self.old_status = defaultdict(lambda: {})
            for item in self.__dict__:
                if item in self.SPECIAL_ITEM and "report" in self.SPECIAL_ITEM[item]["use"]:
                    self.LOG.yinfo("need check item: %s" % (item))
                    self.old_status[item] = copy.deepcopy(self.__dict__[item])

        for item in self.old_status:
            if self.old_status[item] != self.__dict__[item]:
                need_send_report = True
                self.old_status[item] = copy.deepcopy(self.__dict__[item])

        if need_send_report:
            self.send_msg(self.get_upload_status(), ack=b'\x00')

    def to_register_dev(self):
        if self.dev_register:
            self.LOG.info(common_APIs.chinese_show("设备已经注册"))
        else:
            self.LOG.info(common_APIs.chinese_show("发送设备注册"))
            self.to_to_send_msg(json.dumps(self.get_send_msg('COM_DEV_REGISTER')), ack=b'\x00')

    async def to_send_heartbeat(self):
        self.LOG.info('to_send_heartbeat')
        if self.dev_register:
            self.to_to_send_msg(json.dumps(self.get_send_msg('COM_HEARTBEAT')), ack=b'\x00')

    def get_upload_status(self):
        # self.LOG.info(common_APIs.chinese_show("设备状态上报"))
        return json.dumps(self.get_send_msg('COM_UPLOAD_DEV_STATUS'))

    def get_upload_record(self, record_type):
        # self.LOG.info(common_APIs.chinese_show("记录上传"))
        report_msg = self.get_send_msg('COM_UPLOAD_RECORD')
        report_msg["Data"][0]["RecordType"] = record_type
        report_msg["EventCode"] = record_type
        return json.dumps(report_msg)

    def get_upload_event(self, event_type):
        # self.LOG.info(common_APIs.chinese_show("事件上报"))
        report_msg = self.get_send_msg('COM_UPLOAD_EVENT')
        report_msg["Data"][0]["EventType"] = event_type
        report_msg["EventCode"] = event_type
        return json.dumps(report_msg)

    def dev_protocol_handler(self, msg, ack=False):
        if ack:
            self.update_msgst(msg['Command'], 'rsp')
            if msg['Command'] == 'COM_DEV_REGISTER':
                if msg['Result'] == 0:
                    self.dev_register = True
                    # decrypt
                    if self.encrypt_flag:
                        self.add_item('_encrypt_key', msg['Data'][0]['aeskey'])
                    self.LOG.warn(common_APIs.chinese_show("设备已经注册"))
                    return None
                else:
                    self.dev_register = False
                    self.LOG.warn(common_APIs.chinese_show("设备注册失败"))
                    return None
            else:
                return None
        else:
            self.update_msgst(msg['Command'], 'req')

        if msg['Command'] == 'COM_HEARTBEAT':
            pass
        elif msg['Command'] in self.command_list:
            self.set_items(msg['Command'], msg)
            rsp_msg = self.get_rsp_msg(msg['Command'])
            self.update_msgst(msg['Command'], 'rsp')
            return json.dumps(rsp_msg)
        else:
            self.LOG.warn('Unknow msg: %s!' % (msg['Command']))
            return None

    def get_msg_by_command(self, command):
        command = getattr(self.sim_config, command)
        command_str = str(command)
        command_str = re.sub(r'\'TIMENOW\'', '"%s"' % datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'), command_str)
        command_str = re.sub(r'\'randint1\'', '"%s"' %
                             random.randint(0, 1), command_str)
        return eval(command_str.replace("'##", "").replace("##'", ""))

    def get_record_list(self):
        return getattr(self.sim_config, "defined_record")

    def get_event_list(self):
        return getattr(self.sim_config, "defined_event")

    def get_send_msg(self, command):
        return self.get_msg_by_command(command)['send_msg']

    def get_rsp_msg(self, command):
        return self.get_msg_by_command(command)['rsp_msg']

    def set_items(self, command, msg):
        item_dict = self.get_msg_by_command(command)['set_item']
        for item, msg_param in item_dict.items():
            msg_param_list = msg_param.split('.')
            tmp_msg = msg[msg_param_list[0]]
            for i in msg_param_list[1:]:
                if re.match(r'\d+', i):
                    i = int(i)
                tmp_msg = tmp_msg[i]
            self.set_item(item, tmp_msg)

    def attribute_initialization(self):
        attribute_params_dict = getattr(
            self.sim_config, "Attribute_initialization")
        for attribute_params, attribute_params_value in attribute_params_dict.items():
            self.add_item(attribute_params, attribute_params_value)

        self._mac = self.mac_list[self.N]
        #"_deviceID": "1005200958FCDBDA5380",
        #"_subDeviceID": "301058FCDBDA53800001",
        self._deviceID = str(self.DeviceFacturer) + \
            str(self.DeviceType) + self._mac.replace(":", '')
        self._encrypt_key = self._deviceID[-16:].encode('utf-8')
        #self._decrypt_key = self._deviceID[-16:].encode('utf-8')
        self._subDeviceID = str(self.subDeviceType) + \
            self._mac.replace(":", '') + "%04d" % (self.N + 1)
