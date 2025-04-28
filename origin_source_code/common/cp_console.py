"""
@File    : cp_console.py
@Time    : 2021-11-19 15:20
@Author  : wangmengzhou
@Software: PyCharm
备注：老后台退费
"""

import jsonpath
import requests
import time
from flask import jsonify

# 测试环境
from common.configLog import logger

LOGIN_URL = "http://ts.keytop.cn/cp_console_test/login.jsp"
HOME_URL = "http://ts.keytop.cn/cp_console_test/page/index"
ACTION_URL = 'http://ts.keytop.cn/cp_console_test/cp_console_test/j_security_check'
LOGIN_INFO = {
    'username': 'admin',
    'password': 'ROOt@123'}
QUERY_URL_TEST = "http://ts.keytop.cn/cp_console_test/service/report/winxinPay"
# QUERY_URL_PROD = "http://console608.keytop.cn:51320/console/service/report/winxinPay"
QUERY_URL_PROD = "http://console608.keytop.cn:51320/console/service/report/winxinPay_es"
REFUND_URL_TEST = "http://ts.keytop.cn/cp_console_test/service/report/winxinPay/refund"
REFUND_URL_PROD = "http://console608.keytop.cn:51320/console/service/report/winxinPay/refund"
CARPLATENUM_LIST = ['川A8T56T', '川A07UT8', '川B99999', "川AV8888", "川AHJH444", "川AS8888", "川C666DF"]


def get_cookie_test(login_url=LOGIN_URL):
    """
    模拟测试环境登录获取cookie
    @param login_url:
    @return:
    """
    s = requests.Session()
    res = s.get(login_url)
    # 触发登录表单提交
    s.post(ACTION_URL, data=LOGIN_INFO)
    if res.status_code != 200:
        raise Exception(f"获取登录cookie出错，错误返回为【{res.text}】")
    else:
        return "JSESSIONID=" + res.cookies['JSESSIONID']


def timestamp(date):
    """
    转换时间戳函数
    @param date:
    @return: 返回对应时间戳
    """
    timeArray = time.strptime(date + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
    time_stamp = int(time.mktime(timeArray)) * 1000
    return time_stamp


def query_order(tag, carPlateNum, beginDate, endDate, cookie):
    """
    查询退费订单
    @param tag:标签
    @param carPlateNum: 车牌号
    @param beginDate: 开始时间
    @param endDate: 结束时间
    @param cookie:
    @return:
    """
    begin_timestamp = timestamp(beginDate)
    end_timestamp = timestamp(endDate)
    headers = {'cookie': cookie,
               'Accept': 'application/json'}
    params = {'carPlateNum': carPlateNum,
              'beginDate': begin_timestamp,
              'endDate': end_timestamp,
              'pageSize': 10000,
              'pageNum': 1,
              }
    if tag == 'prod':
        query_url = QUERY_URL_PROD
        if carPlateNum in CARPLATENUM_LIST:
            r = requests.get(url=query_url, headers=headers, params=params)
            print(r.text)
            r = r.json()
            order_list = jsonpath.jsonpath(r, '$.data[*]')
        else:
            order_list = 'prod环境，非测试车牌，不可操作'
    else:
        query_url = QUERY_URL_TEST
        r = requests.get(url=query_url, headers=headers, params=params)
        print(r.text)
        r = r.json()
        order_list = jsonpath.jsonpath(r, '$.data[*]')
    return order_list


def refund(tag, order_no, cash_fee, cookie):
    """
    退费
    @param tag:标签
    @param order_no: 订单号
    @param cash_fee: 费用
    @param cookie:
    @return:
    """
    if tag == 'prod':
        refund_url = REFUND_URL_PROD
    else:
        refund_url = REFUND_URL_TEST
    headers = {'cookie': cookie,
               'Accept': 'application/json'}
    params = {'orderNo': order_no,
              'refundRemark': '自动化退费',
              'refundMoney': cash_fee}
    print(refund_url)
    print(params)
    try:
        r = requests.post(url=refund_url, headers=headers, params=params)
        if r.status_code != 200:
            raise Exception
        else:
            print(r.text)
            return r.json()
    except:
        r = {'type': 'fail', 'tip': '退款请求报错'}
        print(r)
        return r


# def order_Refund(carPlateNum, beginDate, endDate):
#     cookie = get_cookie_test()
#     order_list = query_order(carPlateNum, beginDate, endDate, cookie)
#     if order_list:
#         number = len(order_list)
#         fail_list = {}
#         for i in range(number):
#             order_no = order_list[i]['ORDER_NO']
#             cash_fee = int(order_list[i]['CASH_FEE'] * 100)
#             result = refund(order_no, cash_fee, cookie)
#             if result['type'] != 'success':
#                 fail_list[order_no] = result['tip']
#             if len(fail_list) == 0:
#                 res = {
#                     "data": f"退款成功",
#                     "resultCode": 200
#                 }
#             elif len(fail_list) == number:
#                 res = {
#                     "data": f"退款失败",
#                     "order": fail_list,
#                     "resultCode": 500
#                 }
#             else:
#                 res = {
#                     "data": f"部分退款失败",
#                     "order": fail_list,
#                     "resultCode": 500
#                 }
#     else:
#         res = {
#             "data": f"所选日期范围内无订单",
#             "resultCode": 200
#         }
#
#
# order_Refund('川A8T56M', '2021-11-04', '2021-11-19')
if __name__ == '__main__':
    # pass
    cookie = get_cookie_test()
    print(cookie)
    num = 'VIP_000202207214857103'
    refund('test', num, 100, cookie)
    # order_list = query_order("test", "川AV8888", '2022-06-13', '2022-06-15', cookie)
    # print(order_list)
    # for order_info in order_list:
    #     order_info = dict(order_info)
    #     print(order_info)
    #     refund("test", order_info["ORDER_NO"], int(order_info["CASH_FEE"] * 100), cookie)
    # if order_list:
    #     if order_list == 'prod环境，非测试车牌，不可操作':
    #         res = {
    #             "data": f"prod环境，非测试车牌，不可操作",
    #             "resultCode": 500
    #         }
    #     else:
    #         number = len(order_list)
    #         fail_list = {}
    #         for i in range(number):
    #             order_no = order_list[i]['ORDER_NO']
    #             cash_fee = int(order_list[i]['CASH_FEE'] * 100)
    #             result = refund(tag, order_no, cash_fee, cookie)
    #             if result['type'] != 'success':
    #                 fail_list[order_no] = result['tip']
    #         if len(fail_list) == 0:
    #             res = {
    #                 "data": f"退款成功",
    #                 "resultCode": 200
    #             }
    #         elif len(fail_list) == number:
    #             res = {
    #                 "data": f"退款失败",
    #                 "order": fail_list,
    #                 "resultCode": 500
    #             }
    #         else:
    #             res = {
    #                 "data": f"部分订单退款失败",
    #                 "order": fail_list,
    #                 "resultCode": 200
    #             }
