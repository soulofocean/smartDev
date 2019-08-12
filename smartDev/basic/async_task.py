#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""sync task handle
by Kobe Gong. 2018-1-3
"""

import asyncio
import functools
import logging
import os
import re
import struct
import sys
import threading
import time

from basic.log_tool import MyLogger

LOG = MyLogger(os.path.abspath(sys.argv[0]).replace(
    'py', 'log'), clevel=logging.DEBUG, renable=False)


def xxoo(func):
    @functools.wraps(func)
    def tmp(self, *args, **kwargs):
        LOG.debug(func.__name__ + ' is called!')
        return func(self, *args, **kwargs)
    return tmp


class AsyncBase():
    @xxoo
    def __init__(self, logger=None):
        self.LOG = logger
        self.loop = asyncio.new_event_loop()
        #self.loop = asyncio.get_event_loop()

    def add_func(self, func, waittime=0):
        # self.loop.call_soon(func)
        return self.loop.call_later(waittime, func)

        #current_time = self.loop.time()
        #self.loop.call_at(current_time + 1, func)

    def show_task(self):
        for task in asyncio.Task.all_tasks():
            self.LOG.info(str(task))

    def task_proc(self):
        self.loop.run_forever()

    @xxoo
    def task_proc_thread(self):
        def run_in_another_thread(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        th = threading.Thread(target=run_in_another_thread, args=[self.loop])
        th.setDaemon(True)
        th.start()

    def add_func_to_thread(self, func):
        self.loop.call_soon_threadsafe(func)

    def add_coroutine_to_thread(self, coroutine):
        asyncio.run_coroutine_threadsafe(coroutine, self.loop)

    def make_task(self, coroutine):
        return self.loop.create_task(coroutine)
        # return asyncio.ensure_future(func)

    def make_coroutine(self, func, *args, **kwargs):
        async def do_some_work(*args, **kwargs):
            func(*args, **kwargs)
        return do_some_work(*args, **kwargs)

    def cancel_task(self, task):
        return task.cancel()

    def cancel_all_tasks(self):
        for task in asyncio.Task.all_tasks():
            task.cancel()

    def run_task_once(self, task):
        self.loop.run_until_complete(task)

    def add_callback(self, task, fun):
        task.add_done_callback(fun)

    def merge_tasks(self, tasks_list):
        return asyncio.gather(*tasks_list)

    def get_func_obj(self, func, *args, **kwargs):
        return functools.partial(func, *args, **kwargs)

    def stop_loop(self):
        self.loop.stop()

    def close_loop(self):
        self.loop.close()

    @xxoo
    async def timer(self, func, waittime=0):
        futu = asyncio.ensure_future(asyncio.sleep(waittime))
        futu.add_done_callback(func)
        await futu

