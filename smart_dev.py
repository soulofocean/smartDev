#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""sim
by Kobe Gong. 2018-1-15
"""


import argparse
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
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
from cmd import Cmd
from collections import defaultdict

import APIs.common_APIs as common_APIs
from APIs.common_APIs import (my_system, my_system_full_output,
                              my_system_no_check, protocol_data_printB)
#from basic.async_task import AsyncBase
from basic.cprint import cprint
from basic.log_tool import MyLogger
from basic.task import Task
from protocol.light_devices import Door


class ArgHandle():
    def __init__(self):
        self.parser = self.build_option_parser("-" * 50)

    def build_option_parser(self, description):
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            '-t', '--time-delay',
            dest='tt',
            action='store',
            default=0,
            type=int,
            help='time delay(ms) for msg send to server, default time is 500(ms)',
        )
        parser.add_argument(
            '-x', '--xx',
            dest='xx',
            action='store',
            default=0,
            type=int,
            help='special device ids',
        )
        parser.add_argument(
            '-e', '--encrypt',
            dest='encrypt',
            action='store',
            default=0,
            type=int,
            help='encrypt',
        )
        parser.add_argument(
            '-p', '--server-port',
            dest='server_port',
            action='store',
            default=20001,
            type=int,
            help='Specify TCP server port, default is 20001',
        )
        parser.add_argument(
            '-i', '--server-IP',
            dest='server_IP',
            action='store',
            default='192.168.10.12',
            help='Specify TCP server IP address',
        )
        parser.add_argument(
            '--config',
            dest='config_file',
            action='store',
            default="door_conf",
            help='Specify device type',
        )
        parser.add_argument(
            '-c', '--count',
            dest='device_count',
            action='store',
            default=1,
            type=int,
            help='Specify how many devices to start, default is only 1',
        )
        parser.add_argument(
            '--self_IP',
            dest='self_IP',
            action='store',
            default=None,#'172.24.9.134',
            help='Specify TCP client IP address',
        )
        parser.add_argument(
            '--devlce_timeout',
            dest='dto',
            action='store',
            default=None,  # '172.24.9.134',
            help='Specify device timeout, the unit is second',
        )
        parser.add_argument(
            '--to',
            dest='dto',
            action='store',
            default=None,  # '172.24.9.134',
            help='Specify devices timeout seconds,None:never timeout(default),0:willnot exit until rep==rsp'
                 '[n]: will exit after [n] seconds',
        )
        return parser

    def get_args(self, attrname):
        return getattr(self.args, attrname)

    def check_args(self):
        global ipv4_list
        ipv4_list = []

        if arg_handle.get_args('self_IP'):
            ipv4s = common_APIs.get_local_ipv4()
            ip_prefix = '.'.join(arg_handle.get_args(
                'self_IP').split('.')[0:-1])
            ip_start = int(arg_handle.get_args('self_IP').split('.')[-1])
            ipv4_list = [ip for ip in ipv4s if re.search(
                r'%s' % (ip_prefix), ip) and int(ip.split('.')[-1]) >= ip_start]

            ipv4_list.sort()
            for ipv4 in ipv4_list:
                cprint.notice_p("find ip: " + ipv4)

    def run(self):
        self.args = self.parser.parse_args()
        LOG.warn("CMD line: " + str(self.args))
        self.check_args()


class MyCmd(Cmd):
    def __init__(self, logger, sim_objs=None):
        Cmd.__init__(self)
        self.prompt = "SIM>"
        self.sim_objs = sim_objs
        self.LOG = logger

    def help_log(self):
        cprint.notice_p(
            "change logger level: log {0:critical, 1:error, 2:warning, 3:info, 4:debug}")

    def do_log(self, arg, opts=None):
        level = {
            '0': logging.CRITICAL,
            '1': logging.ERROR,
            '2': logging.WARNING,
            '3': logging.INFO,
            '4': logging.DEBUG,
        }
        if int(arg) in range(5):
            for i in self.sim_objs:
                cprint.notice_p("=" * 40)
                self.sim_objs[i].LOG.set_level(level[arg])
        else:
            cprint.warn_p("unknow log level: %s!" % (arg))

    def help_st(self):
        cprint.notice_p("show state")

    def do_st(self, arg, opts=None):
        for i in range(len(self.sim_objs)):
            cprint.notice_p("-" * 20)
            self.sim_objs[i].status_show()

    def help_record(self):
        cprint.notice_p("send record:")

    def do_record(self, arg, opts=None):
        for i in self.sim_objs:
            self.sim_objs[i].send_msg(
                self.sim_objs[i].get_upload_record(int(arg)))

    def help_event(self):
        cprint.notice_p("send event")

    def do_event(self, arg, opts=None):
        for i in self.sim_objs:
            self.sim_objs[i].send_msg(
                self.sim_objs[i].get_upload_event(int(arg)))

    def help_set(self):
        cprint.notice_p("set state")

    def do_set(self, arg, opts=None):
        args = arg.split()
        for i in len(self.sim_objs):
            self.sim_objs[i].set_item(args[0], args[1])

    def default(self, arg, opts=None):
        try:
            subprocess.call(arg, shell=True)
        except:
            pass

    def emptyline(self):
        pass

    def help_exit(self):
        print("Will exit")

    def do_exit(self, arg, opts=None):
        cprint.notice_p("Exit CLI, good luck!")
        sys_cleanup()
        sys.exit()


def sys_init():
    # sys log init
    global LOG
    LOG = MyLogger(os.path.abspath(sys.argv[0]).replace(
        'py', 'log'), clevel=logging.DEBUG, renable=False)
    global cprint
    cprint = cprint(os.path.abspath(sys.argv[0]).replace('py', 'log'))

    # cmd arg init
    global arg_handle
    arg_handle = ArgHandle()
    arg_handle.run()
    LOG.info("Let's go!!!")


def sys_cleanup():
    LOG.info("Goodbye!!!")
    sys.exit()

def delallLog(doit = True):
    if doit:
        files = os.listdir(os.getcwd())
        print(files)
        for file in files:
            if( file.find(".log") != -1):
                os.remove(file)
                print("file:%s is removed" % (file,))

def getP(up,down):
    if down == 0:
        return "0.00%"
    return "{0:.2f}%".format(round(up*100/down,3))

def genReport(sims=[]):
    try:
        end = time.time()
        strTmp = "\r\n" + "="*32 + "\r\n"
        strTmp += "TotalClientNum:{}\r\n".format(arg_handle.get_args('device_count'))
        strTmp += "SendTimeDelay:{}s\r\n".format(sims[0].sleep_s)
        ts = round(end-start,3)
        strTmp += "ConsumTime:{}s\r\n".format(ts)
        totalSend = 0
        totalRcv = 0
        totalFail = 0
        detailDict = {}
        if sims:
            for s in sims:
                for cmd in s.msgst.keys():
                    #if cmd == "COM_HEARTBEAT":
                    #    continue
                    if cmd not in detailDict:
                        detailDict[cmd]={'req': 0, 'rsp': 0, 'rsp_fail': 0}
                    if("req" not in s.msgst[cmd]):
                        LOG.error(str(s.msgst[cmd]))
                    if("req" in s.msgst[cmd]):
                        detailDict[cmd]["req"] += s.msgst[cmd]["req"]
                        totalSend += s.msgst[cmd]["req"]
                    if ("rsp" in s.msgst[cmd]):
                        detailDict[cmd]["rsp"] += s.msgst[cmd]["rsp"]
                        totalRcv += s.msgst[cmd]["rsp"]
                    if ("rsp_fail" in s.msgst[cmd]):
                        detailDict[cmd]["rsp_fail"] += s.msgst[cmd]["rsp_fail"]
                        totalFail += s.msgst[cmd]["rsp_fail"]
                #strTmp += "{}\r\n".format(str(s.msgst))
        strTmp += "TotalSend:{}\t\tQPS:{}\r\n".format(totalSend,round(totalSend/ts,3))
        strTmp += "TotalRcv:{}\t\tQPS:{}\r\n".format(totalRcv,round(totalRcv/ts,3))
        strTmp += "TotalFail:{}\r\n".format(totalFail)
        strTmp += "Rcv/Send:{}\r\n".format(getP(totalRcv,totalSend))
        strTmp += "Fail/Rcv:{}\r\n".format(getP(totalFail, totalRcv))
        strTmp += "Fail/Send:{}\r\n".format(getP(totalFail, totalSend))
        strTmp += "{0}Detail{0}\r\n".format("-"*10)
        for cmd in detailDict.keys():
            strTmp += "{}\r\n".format(cmd)
            for detail in detailDict[cmd].keys():
                strTmp += "\t{}:{}\r\n".format(detail,detailDict[cmd][detail])
            strTmp += "\trsp/req:{}\r\n".format(getP(detailDict[cmd]["rsp"], detailDict[cmd]["req"]))
            strTmp += "\trsp_fail/rsp:{}\r\n".format(getP(detailDict[cmd]["rsp_fail"], detailDict[cmd]["rsp"]))
            strTmp += "\trsp_fail/req:{}\r\n".format(getP(detailDict[cmd]["rsp_fail"], detailDict[cmd]["req"]))
        strTmp += "=" * 32 + "\r\n"
        return strTmp
    except (ValueError) as Argument:
        LOG.error(Argument)

if __name__ == '__main__':
    delallLog()
    sys_init()
    loop = asyncio.get_event_loop()
    if arg_handle.get_args('device_count') > 1:
        log_level = logging.WARN
    else:
        log_level = logging.INFO

    sims = []
    start = time.time()
    for i in range(arg_handle.get_args('device_count')):
        dev_LOG = MyLogger('dev_sim_%d.log' % (
            arg_handle.get_args('xx') + i), clevel=log_level, flevel=logging.DEBUG, fenable=False)
        self_addr = None
        self_ip = None
        if ipv4_list:
            id = i % len(ipv4_list)
            #self_addr = (ipv4_list[id], random.randint(
                #arg_handle.get_args('server_port'), 65535))
            self_addr = (ipv4_list[id], 0)
            dev_LOG.warn('self addr is: %s' % (str(self_addr)))

        if self_addr:
            self_ip = self_addr[0]
        device_timeout = arg_handle.get_args('dto')
        if not device_timeout == None:
            device_timeout = int(device_timeout)
        configfile = arg_handle.get_args('config_file')
        sendInterval = arg_handle.get_args('tt')
        encryptflag = arg_handle.get_args('encrypt')
        serverIP = arg_handle.get_args('server_IP')
        serverPort = arg_handle.get_args('server_port')
        coro = loop.create_connection(lambda: Door(config_file=configfile, logger=dev_LOG,
                                                   N=arg_handle.get_args('xx') + i,tt=sendInterval,
                                                   encrypt_flag=encryptflag, self_ip=self_ip,
                                                   lp=loop,to=device_timeout),
                                      serverIP, serverPort)
        transport, protocol = loop.run_until_complete(coro)
        asyncio.ensure_future(protocol.run_forever())
        sims.append(protocol)

    loop.run_forever()
    loop.close()
    LOG.warn("All devices is stop!")
    #COM_HEARTBEAT
    LOG.warn(genReport(sims))

    #my_cmd = MyCmd(logger=LOG, sim_objs=sims)
    #my_cmd.cmdloop()
    sys_cleanup()
