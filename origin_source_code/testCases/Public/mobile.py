# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: moblie.py
@Description: 跟移动端交互所需函数
@Author: huangjunhao
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
@time:2021/06/23
===================================
"""
import datetime
import json
import time

import allure

from common import filepath, util
from common.configLog import logger
from common.processYaml import Yaml
from common.request import request
from common.util import get_data_from_json_file


@util.retry_fun
@util.catch_exception
@allure.step("登录easytest平台")
def login_easytest():
    """
    登录easytest平台, 获取token
    """
    read_data = Yaml(filepath.EASYLOGIN, 7)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    # if not headers.get("accessToken"):
    #     headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                return result_dic["token"]
            else:
                raise Exception(logger.error("登录easytest平台出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("提交用例执行状态为【{status}】|||false 已结束,true 在执行,unknown 默认状态")
def post_case_status(caseNo, status):
    read_data = Yaml(filepath.POSTCASERUNNING, 7)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("token"):
        headers["token"] = get_data_from_json_file("token")
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["taskId"] = 1215
            request_data["caseNo"] = caseNo
            request_data["status"] = status
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"将用例执行状态接口状态置为{status}成功！涉及用例为{caseNo}！")
                return
            else:
                raise Exception(logger.error("提交用例执行状态出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("重置用例【{caseNo}】出场结果为【{carOutRes}】")
def post_car_out(caseNo, carOutRes):
    """
    提交出场结果
    :param caseNo:
    :param carOutRes:
    """
    read_data = Yaml(filepath.POSTCAROUT, 7)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("token"):
        headers["token"] = get_data_from_json_file("token")
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["caseNo"] = caseNo
            request_data["carOutRes"] = carOutRes
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"将出场接口状态置为{carOutRes}成功！涉及用例为{caseNo}！")
                return
            else:
                raise Exception(logger.error("提交出场结果出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("得到支付结果")
def get_car_pay():
    """

    得到支付结果
    """
    read_data = Yaml(filepath.GETCARPAY, 7)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("token"):
        headers["token"] = get_data_from_json_file("token")
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            res = request.request(method=method, url=url, params=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                return result_dic
            else:
                raise Exception(logger.error("查询支付结果出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("检查【{caseNo}】支付结果")
def check_car_pay(caseNo, wait_time=10, max_time=800):
    car_pay_result = get_car_pay()["data"]
    timeCount = 0
    while car_pay_result["carPayRes"] == "unknown":
        logger.info(f"未得到支付记录，等待{wait_time}秒后再次查询")
        time.sleep(wait_time)
        timeCount += wait_time
        car_pay_result = get_car_pay()["data"]
        if timeCount > max_time:
            logger.info(f"等待{max_time}s也未收到移动端支付结果！请前往移动端查看模拟器运行状态！")
            return False
    if car_pay_result["carPayRes"] == "true" and car_pay_result["caseNo"] == caseNo:
        logger.info("移动端支付成功！请重置支付接口！")
        post_car_pay(caseNo, "unknown")
        return True
    elif car_pay_result["carPayRes"] == "false" or car_pay_result["caseNo"] != caseNo:
        logger.info("移动端支付失败！，请查看移动端支付报告！")
        post_car_pay(caseNo, "unknown")
        return False
    else:
        raise Exception(logger.error("查询支付结果接口出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("重置用例【{caseNo}】支付结果为【{carPayRes}】")
def post_car_pay(caseNo, carPayRes):
    read_data = Yaml(filepath.POSTCARPAY, 7)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("token"):
        headers["token"] = get_data_from_json_file("token")
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["caseNo"] = caseNo
            request_data["carPayRes"] = carPayRes
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"将支付接口状态置为{carPayRes}成功！涉及用例为{caseNo}！")
                return
            else:
                raise Exception(logger.error("提交支付结果出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("重置用例【{caseNo}】场端授权结果为【{authFlag}】")
def post_local_rights(caseNo, authFlag):
    read_data = Yaml(filepath.POSTPAIDAUTH, 7)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("token"):
        headers["token"] = get_data_from_json_file("token")
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["caseNo"] = caseNo
            request_data["authFlag"] = authFlag
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"将场端授权接口状态置为{authFlag}成功！涉及用例为{caseNo}！")
                return
            else:
                raise Exception(logger.error("提交场端授权接口状态出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("得到入场通知结果")
def get_carIn_notice():
    """

    得到入场通知结果
    """
    read_data = Yaml(filepath.GETCARINNOTICE, 7)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("token"):
        headers["token"] = get_data_from_json_file("token")
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            res = request.request(method=method, url=url, params=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                return result_dic
            else:
                raise Exception(logger.error("查询入场通知结果出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("重置用例【{caseNo}】入场通知结果为【{enableStatusRemindFlag}】")
def post_carIn_notice(caseNo, enableStatusRemindFlag):
    """

    提交入场通知结果
    """
    read_data = Yaml(filepath.POSTCARINNOTICE, 7)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("token"):
        headers["token"] = get_data_from_json_file("token")
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["caseNo"] = caseNo
            request_data["enableStatusRemindFlag"] = enableStatusRemindFlag
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"将入场通知结果接口状态置为{enableStatusRemindFlag}成功！涉及用例为{caseNo}！")
                return
            else:
                raise Exception(logger.error("提交入场通知结果出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("检查【{caseNo}】入场通知结果")
def check_carIn_notice(caseNo, wait_time=10, max_time=800):
    carIn_notice_result = get_carIn_notice()["data"]
    timeCount = 0
    while carIn_notice_result["enableStatusRemindFlag"] == "unknown":
        logger.info(f"入场通知记录状态为【{carIn_notice_result['enableStatusRemindFlag']}】，等待{wait_time}秒后再次查询")
        time.sleep(wait_time)
        timeCount += wait_time
        carIn_notice_result = get_carIn_notice()["data"]
        if timeCount > max_time:
            logger.info(f"等待{max_time}s也未收到移动端入场通知结果！请前往移动端查看模拟器运行状态！")
            return False
    if carIn_notice_result["enableStatusRemindFlag"] == "true" and carIn_notice_result["caseNo"] == caseNo:
        logger.info("移动端收到入场通知！请重置入场通知接口！")
        post_carIn_notice(caseNo, "unknown")
        return True
    elif carIn_notice_result["enableStatusRemindFlag"] == "false" or carIn_notice_result["caseNo"] != caseNo:
        logger.info("移动端未收到入场通知！，请查看移动端入场通知报告！")
        post_carIn_notice(caseNo, "unknown")
        return False
    else:
        raise Exception(logger.error("查询入场通知结果接口出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("重置用例【{caseNo}】支付链接为【{payment_url}】")
def post_vip_payment_url(caseNo, payment_url):
    read_data = Yaml(filepath.POSTVIPPAYMENTURL, 7)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("token"):
        headers["token"] = get_data_from_json_file("token")
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["caseNo"] = caseNo
            request_data["url"] = payment_url
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"将支付链接置为{url}成功！涉及用例为{caseNo}！")
                return
            else:
                raise Exception(logger.error("提交支付链接出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("得到开通会员通知结果")
def get_vip_open_notice():
    """

    得到开通会员通知结果
    """
    read_data = Yaml(filepath.GETVIPPAYMENTRES, 7)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("token"):
        headers["token"] = get_data_from_json_file("token")
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            res = request.request(method=method, url=url, params=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                return result_dic
            else:
                raise Exception(logger.error("查询入场通知结果出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("检查【{caseNo}】会员开通结果")
def check_vip_open(caseNo, wait_time=10, max_time=800):
    vip_open_result = get_vip_open_notice()["data"]
    timeCount = 0
    while vip_open_result["VIPPayRes"] == "unknown":
        logger.info(f"未得到支付记录，等待{wait_time}秒后再次查询")
        time.sleep(wait_time)
        timeCount += wait_time
        vip_open_result = get_vip_open_notice()["data"]
        if timeCount > max_time:
            logger.info(f"等待{max_time}s也未收到移动端支付结果！请前往移动端查看模拟器运行状态！")
            return False
    if vip_open_result["VIPPayRes"] == "true" and vip_open_result["caseNo"] == caseNo:
        logger.info("移动端开通会员成功！请重置开通会员状态接口！")
        post_vip_payment_res(caseNo, "unknown")
        return True
    elif vip_open_result["VIPPayRes"] == "false" or vip_open_result["caseNo"] != caseNo:
        logger.info("移动端开通会员失败！，请查看移动端支付报告！")
        post_vip_payment_res(caseNo, "unknown")
        return False
    else:
        raise Exception(logger.error("查询开通会员状态接口出错！"))


@util.retry_fun
@util.catch_exception
@allure.step("重置用例【{caseNo}】开通结果为【{VIPPayRes}】")
def post_vip_payment_res(caseNo, VIPPayRes):
    read_data = Yaml(filepath.POSTVIPPAYMENTRES, 7)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("token"):
        headers["token"] = get_data_from_json_file("token")
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["caseNo"] = caseNo
            request_data["VIPPayRes"] = VIPPayRes
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"将开通结果置为{VIPPayRes}成功！涉及用例为{caseNo}！")
                return
            else:
                raise Exception(logger.error("提交开通结果出错！"))


if __name__ == '__main__':
    # login_easytest()
    # post_car_out("100001", "false")
    # print(get_car_pay())
    # post_car_pay("100004", "unknown")
    # post_local_rights("100001", "unknown")
    print(get_carIn_notice())