#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ZengXu'
__mtime__ = '2018-9-10'
"""
import time
import sys
now = lambda :time.time()

def f(a,b,*,c='c',d='d'):
    print("a={}".format(a))
    print("b={}".format(b))
    print("c={}".format(c))
    print("d={}".format(d))

def move(n, a, b, c):
    if n==1:
        print("{}==>{}".format(a,c))
    else:
        move(n-1,a,c,b)
        move(1,a,b,c)
        move(n-1,b,a,c)

def findMinAndMax(L):
    maxnum = None
    minnum = None
    if L:
        maxnum = L[0]
        minnum = L[0]
        for i in range(1,len(L)):
            if L[i]>maxnum:
                maxnum = L[i]
            elif L[i]<minnum:
                minnum = L[i]
    return (minnum,maxnum)


def triangles():
    L=[1]
    while True:
        yield L
        L = [1] + [L[i] + L[i + 1] for i in range(len(L) - 1)] + [1]

def my_triangles():
    level = 1
    arr = []
    while True:
        arr2 = []
        if(len(arr) == 0):
            arr.append(1)
            yield  [1,]
            continue
        elif(len(arr) == 1):
            arr.append(1)
        else:
            arr2.append(1)
            for i in range(0,len(arr)-1):
                arr2.append(arr[i]+arr[i+1])
            arr2.append(1)
            arr = arr2[:]
        yield arr

if __name__ == '__main__':
    start = now()
    ll = (1)
    print(ll)
    print("Time span:{:.3f}".format(now()-start))
