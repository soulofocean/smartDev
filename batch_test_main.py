# coding=utf-8
import subprocess
import math
import time
import logging
import json
import gevent
from gevent import monkey
import ConfigModule

monkey.patch_all()
# 每个进程启动时间间隔 单位秒
process_start_delay = ConfigModule.process_start_delay
# 监控打印间隔，时间秒
monitor_inv_sec = ConfigModule.monitor_inv_sec
my_dev_config = eval("ConfigModule.{}".format(ConfigModule.use_config))


# dev_config = [
#     {
#         # 可执行程序所在文件夹
#         "dev_folder": "smartDev",
#         # 用来启动可执行程序的命令行，可能是python 可能是python3 也可能是 py -3和执行电脑的环境配置相关
#         "cmd_arr": ("py", "-3"),
#         # 要运行的可执行程序
#         "dev_exe": "smart_dev.py",
#         # 网关IP和端口，类型是一个元组
#         "server_addr": ("10.134.195.20", 2001),
#         # 启动的设备数目
#         "dev_count": 1,
#         # 指定模拟器的配置文件，需要和protocol下的config文件对应
#         "config_file": "door_conf",
#         # 注册等待时间,单位秒
#         "send_pkt_delay": 30,
#         # 发包超时时间：【0：发完包后收包==发包退出，-1：即使发完包也永远循环不退出，N：运行超过N秒后就退出】
#         "send_pkt_timeout": 0,
#         # 发包间隔 单位秒
#         "pkt_period_s": 1,
#         # 一个进程包含的协程数,由于用了Select，目前不能超过500
#         "max_thread_count": 500,
#         # 起始设备ID偏移量，默认为0
#         "default_offset": 0,
#     },
#     # {
#     #     "dev_type" : 2029,
#     #     "dev_count" : 2,
#     #     "dev_exe" : "sipClientPerf.exe",
#     #     "dev_folder":"T2029",
#     #     "pkt_num": 1,
#     #     "pkt_period_s": 1,
#     #     "max_thread_count": 300,
#     #     "default_offset": 0,
#     #     "send_pkt_delay": 20
#     # }
# ]


def get_avg_list(orgin_num: int, max_num: int):
    """线程负载均衡计算和分配
    orgin_num:需要启动的总线程数
    max_num:一个进程允许的最大线程数"""
    # 返回的列表为做了负载均衡后的每个进程拥有的线程数
    avg_list = []
    if orgin_num == 0 or max_num == 0:
        return avg_list
    if orgin_num <= max_num:
        avg_list.append(orgin_num)
    else:
        group_num = math.ceil(orgin_num / max_num)
        div_num = orgin_num // group_num
        mod_num = orgin_num % group_num
        logging.debug("{}={}*{}+{}".format(orgin_num, group_num, div_num, mod_num))
        for i in range(group_num):
            if i < mod_num:
                avg_list.append(div_num + 1)
            else:
                avg_list.append(div_num)
    return avg_list


# cd smartDev&&py -3 smart_dev.py -i 10.101.70.100 -p 2001 -c 2 --config door_conf -disp_delay 10 --to 0
#                                 -t 1000 -x 0 -monitor_s 300 --index 0
# cd 路径&&[解释器] [文件名] -i [网关IP] -p [网关接口] -c [启动设备数] --config [配置文件] -disp_delay [发包延迟时间:秒]
#                            -to [发包超时:秒] -t [发包间隔:毫秒] -x [设备MAC偏移] -monitor_s [监控打印间隔:秒]
#                            --index [命令窗口ID]
def get_start_arg_list(dev_config):
    '''获取subprocess运行的参数列表'''
    arg_list = []
    # 为每个窗口分配的全局ID
    global_cmd_id = 0
    for dev_dict in dev_config:
        dev_folder = dev_dict["dev_folder"]
        cmd_arr = dev_dict["cmd_arr"]
        file_name = dev_dict["dev_exe"]
        server_addr = dev_dict["server_addr"]
        dev_c = dev_dict["dev_count"]
        config_file = dev_dict["config_file"]
        send_pkt_delay = dev_dict["send_pkt_delay"]
        send_pkt_timeout = dev_dict["send_pkt_timeout"]
        pkt_period_ms = int(dev_dict["pkt_period_s"] * 1000)
        default_offset = dev_dict["default_offset"]
        max_thread_count = dev_dict["max_thread_count"]
        change_creno = False
        if "change_creno" in dev_dict:
            change_creno = dev_dict["change_creno"]
        dev_avg_list = get_avg_list(dev_c, max_thread_count)
        dev_offset = 0
        for dev_avg_c in dev_avg_list:
            arg_tmp = list()
            arg_tmp.append("cd")
            arg_tmp.append("{}&&{}".format(dev_folder, cmd_arr[0]))
            if (len(cmd_arr) > 1):
                arg_tmp.extend(cmd_arr[1:])
            arg_tmp.append(file_name)
            arg_tmp.extend(["-i", "{}".format(server_addr[0])])
            arg_tmp.extend(["-p", "{}".format(server_addr[1])])
            arg_tmp.extend(["-c", "{}".format(dev_avg_c)])
            arg_tmp.extend(["--config", "{}".format(config_file)])
            arg_tmp.extend(["-disp_delay", "{}".format(send_pkt_delay)])
            arg_tmp.extend(["--to", "{}".format(send_pkt_timeout)])
            arg_tmp.extend(["-t", "{}".format(pkt_period_ms)])
            arg_tmp.extend(["-x", "{}".format(default_offset + dev_offset)])
            arg_tmp.extend(["-monitor_s", "{}".format(monitor_inv_sec)])
            arg_tmp.extend(["--index", "{}".format(global_cmd_id)])
            # change_creno
            arg_tmp.extend(["-change_creno", "{}".format(change_creno)])
            arg_list.append(arg_tmp)
            dev_offset += dev_avg_c
            global_cmd_id += 1
            # arg_list.append(["cd",
            #                  "{}&&{}".format(dev_folder,cmd_arr),
            #                  "-3",
            #                  "{}".format(file_name),
            #                  "-c",
            #                  "{}".format(dev_avg_c),
            #                  "-x",
            #                  "{}".format(dev_offset)
            #                  # "{}".format(dev_type),
            #                  # "{}".format(dev_avg_c),
            #                  # "{}".format(pkt_period_ms),
            #                  # "{}".format(pkt_num),
            #                  # "{}".format(default_offset + dev_offset),
            #                  # "{}".format(send_pkt_delay),
            #                  # "{}".format(monitor_inv_sec)
            #                  ])
            # dev_offset += dev_avg_c
    return arg_list


class MonitorType:
    '''监控数据在此合并'''

    def __init__(self, monitor_id):
        self.monitor_id = monitor_id
        self.totalRegisterOK = 0
        self.totalSendCount = 0
        self.totalHBCount = 0
        self.totalRsv200okCount = 0
        self.totalRsvFailCount = 0
        self.totalTimeSpent = 0
        self.subTotalSendCount = 0
        self.subTotalHBCount = 0
        self.subTotalRsv200okCount = 0
        self.subTotalRsvFailCount = 0
        self.subTotalTimeSpent = 0

        self.subSendQps = 0
        self.subRcvQps = 0
        self.subRealQps = 0
        self.totalSendQps = 0
        self.totalRcvQps = 0
        self.totalRealQps = 0

    def __repr__(self):
        '''重载下默认的打印函数，打印更多东西，DEBUG用'''
        return str(self.__dict__)

    def getSubSendQps(self):
        """计算一个统计周期内的发送QPS"""
        if (self.subTotalTimeSpent == 0):
            return 0
        return self.subTotalSendCount / self.subTotalTimeSpent

    def getTotalSendQps(self):
        '''计算运行开始至今的发送QPS'''
        if (self.totalTimeSpent == 0):
            return 0
        return self.totalSendCount / self.totalTimeSpent

    def getSubRsvQps(self):
        '''计算一个统计周期内的接收QPS'''
        if (self.subTotalTimeSpent == 0):
            return 0
        return (self.subTotalRsvFailCount + self.subTotalRsv200okCount) / self.subTotalTimeSpent

    def getTotalRsvQps(self):
        '''计算运行至今的接收QPS'''
        if (self.totalTimeSpent == 0):
            return 0
        return (self.totalRsvFailCount + self.totalRsv200okCount) / self.totalTimeSpent

    def getSubRealQps(self):
        '''计算一个统计周期内的网关发送200的QPS'''
        if (self.subTotalTimeSpent == 0):
            return 0
        return self.subTotalRsv200okCount / self.subTotalTimeSpent

    def getTotalRealQps(self):
        '''计算启动以来网关发送200的QPS'''
        if (self.totalTimeSpent == 0):
            return 0
        return self.totalRsv200okCount / self.totalTimeSpent

    def getSubSuccessRate(self):
        '''计算一个周期内的报文成功率'''
        if (self.subTotalSendCount == 0):
            return 0
        return self.subTotalRsv200okCount / self.subTotalSendCount

    def getTotalSuccessRate(self):
        '''计算启动以来的报文成功率'''
        if (self.totalSendCount == 0):
            return 0
        return self.totalRsv200okCount / self.totalSendCount

    def resetNum(self):
        '''重置各项统计数据'''
        self.totalRegisterOK = 0
        self.totalSendCount = 0
        self.totalHBCount = 0
        self.totalRsv200okCount = 0
        self.totalRsvFailCount = 0
        self.totalTimeSpent = 0
        self.subTotalSendCount = 0
        self.subTotalHBCount = 0
        self.subTotalRsv200okCount = 0
        self.subTotalRsvFailCount = 0
        self.subTotalTimeSpent = 0

        self.subSendQps = 0
        self.subRcvQps = 0
        self.subRealQps = 0
        self.totalSendQps = 0
        self.totalRcvQps = 0
        self.totalRealQps = 0


def ConvertStrToDict(lineStr: str, resutlDict: dict):
    '''将收到的字符串转换为字典或者打印出来'''
    if lineStr and len(lineStr) > 0:
        # print(lineStr)
        tmpDict = dict()
        try:
            # 疑似字典，尝试转换
            if "{" in lineStr:
                tmpDict = json.loads(lineStr)
                # 转换成功，进行数据获取
                logging.info(tmpDict)
                index = tmpDict['cmd_index']
                totalRegisterOK = tmpDict['reg_ok_num']
                # sendAliveNum = tmpDict['sendAliveNum']
                sendTotalNum = tmpDict['total_req']
                recv200OkNum = tmpDict['total_rsp'] - tmpDict['total_rsp_fail']
                recvFailNum = tmpDict['total_rsp_fail']
                totalConsumTime = tmpDict['time_spent']
                if index in resutlDict:
                    monitorInfo = resutlDict[index]
                    # monitorInfo.subTotalHBCount = sendAliveNum - monitorInfo.totalHBCount
                    monitorInfo.subTotalSendCount = sendTotalNum - monitorInfo.totalSendCount
                    monitorInfo.subTotalRsv200okCount = recv200OkNum - monitorInfo.totalRsv200okCount
                    monitorInfo.subTotalRsvFailCount = recvFailNum - monitorInfo.totalRsvFailCount
                    monitorInfo.subTotalTimeSpent = totalConsumTime - monitorInfo.totalTimeSpent
                    monitorInfo.totalRegisterOK = totalRegisterOK
                    # monitorInfo.totalHBCount = sendAliveNum
                    monitorInfo.totalSendCount = sendTotalNum
                    monitorInfo.totalRsv200okCount = recv200OkNum
                    monitorInfo.totalRsvFailCount = recvFailNum
                    monitorInfo.totalTimeSpent = totalConsumTime
                    # logging.info("resutlDict[{}]={}".format(index,resutlDict[index]))
                else:
                    monitorInfo = MonitorType(index)
                    monitorInfo.totalRegisterOK = totalRegisterOK
                    # monitorInfo.totalHBCount = sendAliveNum
                    monitorInfo.totalSendCount = sendTotalNum
                    monitorInfo.totalRsv200okCount = recv200OkNum
                    monitorInfo.totalRsvFailCount = recvFailNum
                    monitorInfo.totalTimeSpent = totalConsumTime
                    # monitorInfo.subTotalHBCount = sendAliveNum
                    monitorInfo.subTotalSendCount = sendTotalNum
                    monitorInfo.subTotalRsv200okCount = recv200OkNum
                    monitorInfo.subTotalRsvFailCount = recvFailNum
                    monitorInfo.subTotalTimeSpent = totalConsumTime
                    resutlDict[index] = monitorInfo
            # 不是字典，直接打印
            else:
                logging.info(lineStr)
        # 转换失败或者其他异常打印出来
        except Exception as ex1:
            logging.error("ProcessLineStr Exception:{}".format(ex1.__repr__()))


def GenReport(resultDict: dict, sleep_sec: float, console_num: int):
    """打印出来报告 resultDict:报告数据来源 sleep_sec:生成报告间隔时间"""
    info = MonitorType(-1)
    while 1:
        global monitor_run
        if (monitor_run == 0):
            break
        if resultDict:
            lastTime = info.totalTimeSpent
            info.resetNum()
            for k, v in resultDict.items():
                info.subTotalSendCount += v.subTotalSendCount
                info.subTotalRsv200okCount += v.subTotalRsv200okCount
                info.subTotalRsvFailCount += v.subTotalRsvFailCount
                info.totalSendCount += v.totalSendCount
                info.totalRsv200okCount += v.totalRsv200okCount
                info.totalRsvFailCount += v.totalRsvFailCount
                info.totalRegisterOK += v.totalRegisterOK
                info.subSendQps += v.getSubSendQps()
                info.subRcvQps += v.getSubRsvQps()
                info.subRealQps += v.getSubRealQps()
                if info.totalTimeSpent < v.totalTimeSpent:
                    info.totalTimeSpent = v.totalTimeSpent
                # info.totalSendQps += v.getTotalSendQps()
                # info.totalRcvQps += v.getTotalRsvQps()
                # info.totalRealQps += v.getTotalRealQps()
            info.subTotalTimeSpent = info.totalTimeSpent - lastTime
            logging.info('=' * 60)
            logging.info("{}{}{}".format('-' * 23, 'Real Time Data', '-' * 23))
            # logging.info('-' * 60)
            logging.info('{:30}:{:29}'.format("PeriodSendCount", info.subTotalSendCount))
            logging.info('{:30}:{:29}'.format("PeriodRsvSuccessCount", info.subTotalRsv200okCount))
            logging.info('{:30}:{:29}'.format("PeriodRsvFailCount", info.subTotalRsvFailCount))
            logging.info('{:30}:{:29.2%}'.format("PeriodSuccessRate", info.getSubSuccessRate()))
            logging.info('{:30}:{:29.2f}'.format("PeriodSendQps", info.subSendQps))
            logging.info('{:30}:{:29.2f}'.format("PeriodRcvQps", info.subRcvQps))
            logging.info('{:30}:{:29.2f}'.format("PeriodRealQps", info.subRealQps))
            logging.info('{:30}:{:29.2f}'.format("PeriodTimeSpent", info.subTotalTimeSpent))
            logging.info('-' * 60)
            logging.info("{}{}{}".format('-' * 25, 'Total Data', '-' * 25))
            # logging.info('-' * 60)
            logging.info('{:30}:{:29}'.format("totalRegisterOK", info.totalRegisterOK))
            logging.info('{:30}:{:29}'.format("totalSendCount", info.totalSendCount))
            logging.info('{:30}:{:29}'.format("totalRsvSuccessCount", info.totalRsv200okCount))
            logging.info('{:30}:{:29}'.format("totalRsvFailCount", info.totalRsvFailCount))
            logging.info('{:30}:{:29.2%}'.format("totalSuccessRate", info.getTotalSuccessRate()))
            logging.info('{:30}:{:29.2f}'.format("totalTimeSpent", info.totalTimeSpent))
            # logging.info('{:30}:{:29.2f}'.format("totalSendQps", info.totalSendQps))
            # logging.info('{:30}:{:29.2f}'.format("totalRcvQps", info.totalRcvQps))
            # logging.info('{:30}:{:29.2f}'.format("totalRealQps", info.totalRealQps))
            logging.info('-' * 60)
            logging.info('=' * 60)
        else:
            logging.info("Waiting for data...")
            time.sleep(console_num * (1+process_start_delay))
            continue
        time.sleep(sleep_sec)
    logging.info('GenReport quit')


def ProcessConsoleMsg(clist, resultDict):
    """将各个控制台中的标准输出流汇总到resultDict中 clist:控制台对象列表 resultDict:存放结果数据的字典"""
    needbreak = 0
    while 1:
        needbreak = 1
        for i, c in enumerate(clist):
            line = c.stdout.readline()
            if line and len(line) > 0:
                lineStr = line.decode('gbk').replace('\r', '').replace('\n', '')
                ConvertStrToDict(lineStr, resultDict)
                # logging.info("{}:{}".format(i,c.poll()))
            if c.poll() is None:
                # 只要还有一个命令行没结束，此函数都不会推出
                needbreak &= 0
        if needbreak == 1:
            # 所有命令行结束，函数推出
            break
    global monitor_run
    monitor_run = 0


if __name__ == "__main__":
    # 用来打印报告的字典
    resultDict = dict()
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)10s.%(msecs)03d][%(filename)s line:%(lineno)03d][%(levelname)-5s]%(message)s',
                        datefmt='%F %T')
    arg_list = get_start_arg_list(my_dev_config)
    clist = []
    for i, arg in enumerate(arg_list):
        logging.info("[i={}] arg = {}".format(i, arg))
        child = subprocess.Popen(arg, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        clist.append(child)
        time.sleep(process_start_delay)
        logging.debug('=' * 60)
    monitor_run = 1
    g1 = gevent.spawn(ProcessConsoleMsg, clist, resultDict)
    g2 = gevent.spawn(GenReport, resultDict, monitor_inv_sec, len(arg_list))
    gevent.joinall([g1, g2])
    logging.info('main End')
