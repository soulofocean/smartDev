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

class A:
    def __init__(self):
        self.a = 223
    def fun(self):
        print("AAA")
class B:
    def __init__(self):
        myA = A()
        self.myAself = A()
    # def fun(self):
    #     print("BBB")
    def fun2(self):
        self.myAself.fun()


if __name__ =='__main__':
    # sss1 = b'HDXM0000000000000APP19621017201832FCDBDA2010\x01\x00\x00\x03_\x00\x00\x00&\x00\x00\x0b\x90{"Command":"COM_DEV_REGISTER","Result":0,"jimao":{"k":"v"}}'
    sss1 = b'HDXM1017201832FCDBDA200000000000000000000000\x00\x00\x00\x00\x02\x00\x00\x00\xd4\x00\x00a\xeb{"Command": "COM_DEV_REGISTER", "Data": [{"Type": 0, "deviceID": "1017201832FCDBDA2000", "manufacturer": "HDIOT", "ip": "192.168.0.235", "mac": "32FCDBDA2000", "mask": "255.255.255.0", "version": "S905X_X9PRO"}]}'
    mmm = re.search(b'"Command":*.?"(\w+)"',sss1)
    print(mmm.span())
    cmd = mmm.group(1).decode()
    print(cmd)
    print(b'"Data":' in sss1)
    # sss2 = '{"intent":{"category":"EVERGRANDE.blender","intentType":"custom","rc":0,"semanticType":0,"service":"EVERGRANDE.blender","uuid":"cid73649bff@dx000b10e3ee3d010009","vendor":"EVERGRANDE","version":"14.0","semantic":[{"entrypoint":"ent","hazard":false,"intent":"setPBJMode","score":1.0,"slots":[{"begin":0,"end":2,"name":"noMeanBegin","normValue":"please","value":"请你"},{"begin":3,"end":6,"name":"categoryName","normValue":"破壁机","value":"料理机"},{"begin":7,"end":9,"name":"ModeName","normValue":"模式","value":"模式"},{"begin":11,"end":12,"name":"adjust","normValue":"打开","value":"调"},{"begin":13,"end":15,"name":"mode","normValue":"浓汤","value":"煮汤"},{"begin":15,"end":17,"name":"ModeName","normValue":"模式","value":"功能"}],"template":"{noMeanBegin}{enable}{categoryName}的{ModeName}{forMe}{adjust}到{mode}{ModeName}"}],"state":null,"sid":"cid73649bff@dx000b10e3ee3d010009","text":"中文"}}'
    sss2 = '{"intent":{"category":"EVERGRANDE.blender","intentType":"custom","rc":0,"semanticType":0,"service":"EVERGRANDE.blender","uuid":"cid73649bff@dx000b10e3ee3d010009","vendor":"EVERGRANDE","version":"14.0","semantic":[{"entrypoint":"ent","hazard":false,"intent":"setPBJMode","score":1.0,"slots":[{"begin":0,"end":2,"name":"noMeanBegin","normValue":"please","value":"请你"},{"begin":3,"end":6,"name":"categoryName","normValue":"破壁机","value":"料理机"},{"begin":7,"end":9,"name":"ModeName","normValue":"模式","value":"模式"},{"begin":11,"end":12,"name":"adjust","normValue":"打开","value":"调"},{"begin":13,"end":15,"name":"mode","normValue":"浓汤","value":"煮汤"},{"begin":15,"end":17,"name":"ModeName","normValue":"模式","value":"功能"}],"template":"{noMeanBegin}{enable}{categoryName}的{ModeName}{forMe}{adjust}到{mode}{ModeName}"}],"state":null,"sid":"cid73649bff@dx000b10e3ee3d010009","text":"请你把料理机的模式给我调到煮汤功能"}}'
    mmm2 = re.search('"text":"(\w+)"', sss2)
    print(mmm2.group(1))
    exit(666)
    bb = B()
    bb.myAself.fun()
    exit(666)
    for i in range(10):
        if not i&0x1:
            print("i:{}是偶数".format(i))
    exit(666)
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