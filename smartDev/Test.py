#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ZengXu'
__mtime__ = '2018-8-23'
"""
import asyncio
import time
import json
import sys
import re

def f1(a,b="B",*,c):
    print("a:",a)
    #print("args:",args)
    print("c:",c)
if __name__ =='__main__':
    f1("A",c="C")
    sourceStr = '<aab>abcdefg</aab>'
    # p = re.compile(r"(\w{2}(?=\w))")
    #p = re.compile(r'^<(\w+)>.*<\/\1>$')
    #p = re.compile(r"(?<=<(\w{3})>).*(?=</\1>)")
    #m = p.findall(sourceStr)
    # r2 = p.sub(testfun,sourceStr)
    # print r2
    #print(m.group(0))
    sys.exit(-666)
    s = {'text': u'\u521b\u5efa\u5bb6\u5ead', 'name': 'click', '533ab525a8760351': []}

    result = json.dumps(s, ensure_ascii=False)
    print("b=", result)
    print(json.dumps(s, ensure_ascii=False))

    sys.exit(-666)
    now = lambda: time.time()


    async def do_some_work(x):
        print("waiting:", x)
        await asyncio.sleep(x)
        print("waiting2:", x)
        #return "Done after {}s".format(x)


    async def main():
        coroutine1 = do_some_work(1)
        coroutine2 = do_some_work(2)
        coroutine3 = do_some_work(4)
        tasks = [
            asyncio.ensure_future(coroutine1),
            asyncio.ensure_future(coroutine2),
            asyncio.ensure_future(coroutine3)
        ]
        return await asyncio.wait(tasks)


    start = now()

    loop = asyncio.get_event_loop()
    done, pending = loop.run_until_complete(main())
    #for task in done:
        #print("Task ret:", task.result())

    print("Time:", now() - start)