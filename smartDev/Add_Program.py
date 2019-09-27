# coding:utf-8
import requests
import json
import time

def get_login_token():
    url = 'http://10.134.195.20:81/scp-st-usermgmtcomponent/admin/login'
    post_data = "username=admin&password=YWRtaW4%3D"
    headers = {
        u'Accept-Language': u'zh-CN,zh;q=0.9,en;q=0.8',
        u'FrontType': u'scp-admin-ui',
        u'Accept': u'application/json, text/plain, */*',
        u'Content-Type': u'application/x-www-form-urlencoded'
    }
    resv_msg: requests.Response = requests.post(url=url, data=post_data, headers=headers)
    print("response_code:{}".format(resv_msg.status_code))
    login_dict = json.loads(resv_msg.text)
    token = login_dict['data']['token']
    return token


def insert_RC(rcname: str, tk: str):
    url = 'http://10.134.195.20:81/scp-st-informationreleaseapp/schedule/insert'
    post_data = u'''{"uuid":"","scheduleName":"#name#","scheduleType":"daily","programNo":"5fea308048a94d70840ff25f0befda36","beginDate":"2019-09-26","endDate":"2019-10-27","dailySchedule":{"playSpan":["11:00:00","12:00:00"]},"weekSchedule":[{"dayOfWeek":"星期一","id":"1","playSpan":null},{"dayOfWeek":"星期二","id":"2","playSpan":null},{"dayOfWeek":"星期三","id":"3","playSpan":null},{"dayOfWeek":"星期四","id":"4","playSpan":null},{"dayOfWeek":"星期五","id":"5","playSpan":null},{"dayOfWeek":"星期六","id":"6","playSpan":null},{"dayOfWeek":"星期日","id":"7","playSpan":null}],"scheduleModel":"normal"}'''
    post_data = post_data.replace("#name#", rcname)
    headers = {
        u'Accept-Language': u'zh-CN,zh;q=0.9',
        u'FrontType': u'scp-admin-ui',
        u'Accept': u'application/json, text/plain, */*',
        u'Content-Type': u'application/json',
        u'Authorization': tk
    }
    resv_msg: requests.Response = requests.post(url=url, data=post_data.encode('utf-8'), headers=headers)
    print("response_code:{}".format(resv_msg.status_code))
    print(resv_msg.text)


def publish_RC(tk: str, dev_count: int):
    url = 'http://10.134.195.20:81/scp-st-informationreleaseapp/schedule/publish'
    # "1017201832FCDBDA1000":"we","1017201832FCDBDA1001":"we","1017201832FCDBDA1002":"we"
    longStr = ""
    for i in range(1000, 1000 + dev_count):
        longStr += '"1017201832FCDBDA{:04d}":"we",'.format(i)
    print("l1:{}".format(longStr))
    longStr = longStr[:-1]
    print("l2:{}".format(longStr))
    post_data = '{{"uuid":"a0fe449f2666434fa4a1e994d84889fc","scheduleId":"a0fe449f2666434fa4a1e994d84889fc","terminalNoMap":{{{}}},"scheduleModel":"1"}}'.format(
        longStr)
    # post_data = post_data.replace("#name#", rcname)
    print("pd={}".format(len(post_data)))
    headers = {
        u'Accept-Language': u'zh-CN,zh;q=0.9',
        u'FrontType': u'scp-admin-ui',
        u'Accept': u'application/json, text/plain, */*',
        u'Content-Type': u'application/json',
        u'Authorization': tk
    }
    resv_msg: requests.Response = requests.post(url=url, data=post_data.encode('utf-8'), headers=headers)
    print("response_code:{}".format(resv_msg.status_code))
    print(resv_msg.text)


if __name__ == '__main__':
    token = get_login_token()
    print(token)
    while True:
        publish_RC(token,1000)
        time.sleep(5)

