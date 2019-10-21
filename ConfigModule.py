# coding:utf-8
# 每个进程启动时间间隔 单位秒
process_start_delay = 0.1
# 监控打印间隔，时间秒
monitor_inv_sec = 60
use_config = 'dev_config3'
dev_config = [
    {
        # 可执行程序所在文件夹
        "dev_folder": "smartDev",
        # 用来启动可执行程序的命令行，可能是python 可能是python3 也可能是 py -3和执行电脑的环境配置相关
        "cmd_arr": ("py", "-3"),
        # 要运行的可执行程序
        "dev_exe": "smart_dev.py",
        # 网关IP和端口，类型是一个元组
        "server_addr": ("10.134.195.20", 2001),
        # 启动的设备数目
        "dev_count": 1,
        # 指定模拟器的配置文件，需要和protocol下的config文件对应
        "config_file": "door_conf",
        # 注册等待时间,单位秒
        "send_pkt_delay": 30,
        # 发包超时时间：【0：发完包后收包==发包退出，-1：即使发完包也永远循环不退出，N：运行超过N秒后就退出】
        "send_pkt_timeout": 0,
        # 发包间隔 单位秒
        "pkt_period_s": 0.1,
        # 一个进程包含的协程数,由于用了Select，目前不能超过500
        "max_thread_count": 500,
        # 起始设备ID偏移量，默认为0
        "default_offset": 0,
    },
]

dev_config2 = [
    {
        # 可执行程序所在文件夹
        "dev_folder": "smartDev",
        # 用来启动可执行程序的命令行，可能是python 可能是python3 也可能是 py -3和执行电脑的环境配置相关
        "cmd_arr": ("py", "-3"),
        # 要运行的可执行程序
        "dev_exe": "smart_dev.py",
        # 网关IP和端口，类型是一个元组
        "server_addr": ("10.134.195.20", 2001),
        # 启动的设备数目
        "dev_count": 10,
        # 指定模拟器的配置文件，需要和protocol下的config文件对应
        "config_file": "park_conf2",
        # 注册等待时间,单位秒
        "send_pkt_delay": 30,
        # 发包超时时间：【0：发完包后收包==发包退出，-1：即使发完包也永远循环不退出，N：运行超过N秒后就退出】
        "send_pkt_timeout": -1,
        # 发包间隔 单位秒
        "pkt_period_s": 6,
        # 一个进程包含的协程数,由于用了Select，目前不能超过500
        "max_thread_count": 500,
        # 起始设备ID偏移量，默认为0
        "default_offset": 0,
        # 停车场专用：是否修改凭证号设置为TRUE则会动态修改偏移奇数N车牌号为N-1车牌号并延迟出口的发包，延迟时间为发包间隔的一半
        "change_creno":True
    },
]

dev_config3 = [
    {
        # 可执行程序所在文件夹
        "dev_folder": "smartDev",
        # 用来启动可执行程序的命令行，可能是python 可能是python3 也可能是 py -3和执行电脑的环境配置相关
        "cmd_arr": ("py", "-3"),
        # 要运行的可执行程序
        "dev_exe": "smart_dev.py",
        # 网关IP和端口，类型是一个元组
        "server_addr": ("10.134.195.20", 2001),
        # 启动的设备数目
        "dev_count": 1000,
        # 指定模拟器的配置文件，需要和protocol下的config文件对应
        "config_file": "publishing_conf",
        # 注册等待时间,单位秒
        "send_pkt_delay": 60,
        # 发包超时时间：【0：发完包后收包==发包退出，-1：即使发完包也永远循环不退出，N：运行超过N秒后就退出】
        "send_pkt_timeout": 0,
        # 发包间隔 单位秒
        "pkt_period_s": 5,
        # 一个进程包含的协程数,由于用了Select，目前不能超过500
        "max_thread_count": 500,
        # 起始设备ID偏移量，默认为0
        "default_offset": 0
    },
]

dev_config4 = [
    {
        # 可执行程序所在文件夹
        "dev_folder": "smartDev",
        # 用来启动可执行程序的命令行，可能是python 可能是python3 也可能是 py -3和执行电脑的环境配置相关
        "cmd_arr": ("py", "-3"),
        # 要运行的可执行程序
        "dev_exe": "smart_dev.py",
        # 网关IP和端口，类型是一个元组
        "server_addr": ("10.101.72.80", 2001),
        # 启动的设备数目
        "dev_count": 1,
        # 指定模拟器的配置文件，需要和protocol下的config文件对应
        "config_file": "publishing_conf",
        # 注册等待时间,单位秒
        "send_pkt_delay": 5,
        # 发包超时时间：【0：发完包后收包==发包退出，-1：即使发完包也永远循环不退出，N：运行超过N秒后就退出】
        "send_pkt_timeout": 0,
        # 发包间隔 单位秒
        "pkt_period_s": 1,
        # 一个进程包含的协程数,由于用了Select，目前不能超过500
        "max_thread_count": 500,
        # 起始设备ID偏移量，默认为0
        "default_offset": 0
    },
]