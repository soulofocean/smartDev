#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ZengXu'
__mtime__ = '2018-9-10'
"""
import time
import sys
import random

now = lambda: time.time()


def f(a, b, *, c='c', d='d'):
    print("a={}".format(a))
    print("b={}".format(b))
    print("c={}".format(c))
    print("d={}".format(d))


def move(n, a, b, c):
    if n == 1:
        print("{}==>{}".format(a, c))
    else:
        move(n - 1, a, c, b)
        move(1, a, b, c)
        move(n - 1, b, a, c)


def findMinAndMax(L):
    maxnum = None
    minnum = None
    if L:
        maxnum = L[0]
        minnum = L[0]
        for i in range(1, len(L)):
            if L[i] > maxnum:
                maxnum = L[i]
            elif L[i] < minnum:
                minnum = L[i]
    return (minnum, maxnum)


def triangles():
    L = [1]
    while True:
        yield L
        L = [1] + [L[i] + L[i + 1] for i in range(len(L) - 1)] + [1]


def my_triangles():
    level = 1
    arr = []
    while True:
        arr2 = []
        if (len(arr) == 0):
            arr.append(1)
            yield [1, ]
            continue
        elif (len(arr) == 1):
            arr.append(1)
        else:
            arr2.append(1)
            for i in range(0, len(arr) - 1):
                arr2.append(arr[i] + arr[i + 1])
            arr2.append(1)
            arr = arr2[:]
        yield arr


def str_increase(orgin_str: str, offset: int, prefix_len: int = 0, split_sign=":"):
    """将orgin_str前prefix_len保留，后续位加上offset返回新的MAC地址字符串，prefix_len为0时默认保留原长度减掉偏移长度的字符串"""
    # 替换了分隔符后的MAC地址
    mac_str = orgin_str.replace(split_sign, "")
    # 替换了分隔符后的MAC地址长度
    str_len = len(mac_str)
    # 偏移字符串的长度
    int_len = len(str(offset))
    # 真实的便宜量部分的字符串长度
    real_prefix_len = prefix_len
    if prefix_len == 0:
        # 保留原长度减掉偏移长度的字符串
        real_prefix_len = str_len - int_len
    if real_prefix_len <= 0:
        raise NotImplementedError("Not support real_prefix_len({}) <= 0".format(real_prefix_len))
    # 确定真实前缀后计算偏移字符串长度，保证拼接后MAC长度不变
    int_len = str_len - real_prefix_len
    if int_len <= 0:
        raise NotImplementedError("Not support int_len({}) <= 0".format(int_len))
    # 按照前缀长度获取前缀
    prefix_str = mac_str[:real_prefix_len]
    # 获取数字部分字符串
    num_str = mac_str[real_prefix_len:]
    # 计算偏移后的MAC字符串后半截
    result_int = int(num_str) + int(offset)
    result_int_len = len(str(result_int))
    # 如果后半截算出来长度比原偏移字符串长证明有进位，会覆盖前缀或者让MAC地址变长，此处暂不支持进位的处理
    if result_int_len > int_len:
        raise NotImplementedError("Not support result_int_len({}) > int_len({})".format(result_int_len, int_len))
    # 获取新MAC拼接的字符串格式化字符
    format_str = "{{}}{{:0{}d}}".format(int_len)
    result_str = format_str.format(prefix_str, result_int)
    return result_str


if __name__ == '__main__':
    start = now()
    print("Time span:{:.3f}".format(now() - start))
