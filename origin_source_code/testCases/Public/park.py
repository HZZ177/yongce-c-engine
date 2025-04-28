# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: park.py
@Description: 车场相关校验
@Author: huangjunhao
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
@time:2021/05/07
===================================
"""
import datetime
import json
import time

import allure

from common import util, filepath
from common.request import request
from common.configLog import logger
from common.db_tool import DbTool
from common.processYaml import Yaml


@util.catch_exception
@util.retry_fun
@allure.step("得到【{lot_id}】的车场列表信息")
def get_park_list(lot_id):
    """
    通过车场id得到车场列表信息
    :param lot_id:
    """
    read_data = Yaml(filepath.PARKLIST, 5)
    headers = read_data.headers
    headers["app-id"] = filepath.CONF.get("postpay", "app-id")
    headers["secret-key"] = filepath.CONF.get("postpay", "secret-key")
    url = read_data.url
    datas = read_data.allData
    method = read_data.method
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['request_data']["lotId"] = lot_id
            res = request.request(url=url, data=json.dumps(query_data[2]['request_data']), method=method, headers=headers)
            result_dic = res.json()
            if result_dic["code"] != 2000:
                raise Exception(logger.error("查询速停车管理车场列表信息接口出错！"))
            else:
                return result_dic


@util.catch_exception
@util.retry_fun
@allure.step("得到【{lot_id}】的车场详细信息")
def get_park_info(lot_id):
    park_list_info = get_park_list(lot_id)
    front_id = park_list_info["data"]["records"][0]["id"]
    read_data = Yaml(filepath.PARK, 5)
    headers = read_data.headers
    headers["app-id"] = filepath.CONF.get("postpay", "app-id")
    headers["secret-key"] = filepath.CONF.get("postpay", "secret-key")
    url = read_data.url
    datas = read_data.allData
    method = read_data.method
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['request_data']["id"] = front_id
            res = request.request(url=url, params=query_data[2]['request_data'], method=method,
                                  headers=headers, timeout=10)
            result_dic = res.json()
            if result_dic["code"] != 2000:
                raise Exception(logger.error("查询速停车管理车场详情信息接口出错！"))
            else:
                return result_dic


@util.catch_exception
@util.retry_fun
@allure.step("修改车场【{lot_id}】的字段【{key}】为【{value}】")
def edit_park_info(lot_id, key, value):
    """
    修改车场配置
    :param lot_id:车场id
    :param key: 需要修改的车场json的key，如果是特权放行中的内容，传入 editParkingLotPostpaidConfigParam_{key} 形式表示
    :param value: 修改后的参数
    """
    data = get_park_info(lot_id)["data"].copy()
    editParkingLotPostpaidConfigParam = data["parkingLotPostpaidConfigDetailVO"]
    area = [data["provId"], data["cityId"]]
    data["editParkingLotPostpaidConfigParam"] = editParkingLotPostpaidConfigParam
    data["area"] = area
    if "editParkingLotPostpaidConfigParam" in key:
        data["editParkingLotPostpaidConfigParam"][key.split("_")[1]] = value
    else:
        data[key] = value
    read_data = Yaml(filepath.EDITPARK, 5)
    headers = read_data.headers
    headers["app-id"] = filepath.CONF.get("postpay", "app-id")
    headers["secret-key"] = filepath.CONF.get("postpay", "secret-key")
    url = read_data.url
    datas = read_data.allData
    method = read_data.method
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            data = data
            res = request.request(url=url, data=json.dumps(data), method=method,headers=headers)
            result_dic = res.json()
            if result_dic["code"] != 2000:
                raise Exception(logger.error("修改该速停车管理车场详情信息接口出错！"))
            else:
                logger.info(f"✔ 修改车场【{lot_id}】配置【{key}】为【{value}】成功！")


@util.catch_exception
@util.retry_fun
@allure.step("检验【{lot_id}】的【{check_tag}】配置||1：缴费、2：后付费、3：特权、4：车场类型")
def check_park(lot_id, check_tag):
    """
    检验车场配置
    :param lot_id: 车场id
    :param check_tag, 1=缴费，2=后付费，3=特权
    :return: 车场配置开启状态  True/False
    """
    park_info = get_park_info(lot_id)
    if check_tag == 1:
        if park_info["data"]["enablePayment"]:
            logger.info("✔ 此次校验成功 ,车场已开启缴费功能")
            return True
        else:
            logger.info("× 车场未开启缴费功能")
            return False
    elif check_tag == 2:
        if park_info["data"]["enablePostPaid"]:
            logger.info("✔ 此次校验成功 ,车场已开启后付费功能")
            return True
        else:
            logger.info("× 车场未开启后付费功能")
            return False
    elif check_tag == 3:
        if int(park_info["data"]["parkingLotPostpaidConfigDetailVO"]["privilegeStatus"]) == 1:
            logger.info("✔ 此次校验成功 ,车场已开启特权放行功能")
            return True
        else:
            logger.info("× 未开启特权放行功能")
            return False
    elif check_tag == 4:
        if int(park_info["data"]["attrType"]) == 1:
            logger.info("✔ 此次校验成功 ,车场是速泊车场")
            return True
        elif int(park_info["data"]["attrType"]) == 2:
            logger.info("✔ 此次校验成功 ,车场是自营车场")
            return True
        else:
            logger.info("× 车场非速泊或自营车场")
            return False


@util.catch_exception
@util.retry_fun
@allure.step("得到【{lot_id}】的城市信息")
def get_lot_city(lot_id):
    park_info = get_park_info(lot_id)
    return park_info["data"]["cityId"]


@util.catch_exception
@util.retry_fun
@allure.step("得到【{lot_id}】的特权放行信用限制等级")
def get_model_level_limit(lot_id):
    park_info = get_park_info(lot_id)
    if park_info["data"]["parkingLotPostpaidConfigDetailVO"]["modelVersion"] != "v2":
        raise Exception(logger.error("此车场才用的是v1版本人车模型校验，不应使用用户信用等级进行校验！"))
    return park_info["data"]["parkingLotPostpaidConfigDetailVO"]["modelLevelLimit"]


@util.catch_exception
@util.retry_fun
@allure.step("得到【{lot_id}】的特权放行权重限制等级")
def get_model_weight_limit(lot_id):
    park_info = get_park_info(lot_id)
    if park_info["data"]["parkingLotPostpaidConfigDetailVO"]["modelVersion"] != "v1":
        raise Exception(logger.error("此车场才用的是v2版本人车模型校验，不应使用用户权重等级进行校验！"))
    return park_info["data"]["parkingLotPostpaidConfigDetailVO"]["modelWeightLimit"]


@util.catch_exception
@util.retry_fun
@allure.step("得到出场车辆支付订单信息")
def get_park_pay_info(kttoken, lot_id, carNo, out_time=0):
    read_data = Yaml(filepath.GETPARKPAYINFO, 2)
    url, headers, allData = util.get_parameter(read_data, lot_id, kttoken)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    for datas in allData:
        if datas[0]['id'] == 1:
            ps = datas[1]['ps']
            logger.info("【正在%s】" % ps)
            data = datas[2]
            data['lotCode'] = lot_id
            data['platNum'] = carNo
            data["now"] = out_time if out_time else int(time.time())
            res = request.post(url=url, headers=headers, data=data, timeout=5)
            res_dic = res.json()
            if res_dic["resultCode"] == 510 and "没有找到车辆信息" in res_dic["resultMsg"]:
                logger.info("没有该车辆的支付订单信息！")
                return False
            elif res_dic["resultCode"] == 200:
                orderNo = res_dic["data"]["orderNo"]
                payMoney = res_dic["data"]["payMoney"]
                logger.info(f"查询车辆【{carNo}】支付订单信息成功，订单号为【{orderNo}】, 支付金额为【{payMoney}】")
                return {"orderNo": orderNo, "payMoney": payMoney}
            else:
                raise Exception(f"查询车场支付订单接口错误！错误返回为{res_dic}")
            logger.info("【✔ %s完成】" % ps)


@util.catch_exception
@util.retry_fun
@allure.step("得到出场车辆支付订单信息")
def get_park_pay_info_pro(kttoken, lot_id, carNo, out_time=0):
    read_data = Yaml(filepath.GETPARKPAYINFO_PRO, 4)
    url, headers, allData = util.get_parameter(read_data, lot_id, kttoken)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    for datas in allData:
        if datas[0]['id'] == 1:
            ps = datas[1]['ps']
            logger.info("【正在%s】" % ps)
            data = datas[2]
            data['lotCode'] = lot_id
            data['platNum'] = carNo
            data["now"] = out_time if out_time else int(time.time())
            res = request.post(url=url, headers=headers, data=data, timeout=5)
            res_dic = res.json()
            if res_dic["resultCode"] == 510 and "没有找到车辆信息" in res_dic["resultMsg"]:
                logger.info("没有该车辆的支付订单信息！")
                return False
            elif res_dic["resultCode"] == 200:
                orderNo = res_dic["data"]["orderNo"]
                payMoney = res_dic["data"]["payMoney"]
                logger.info(f"查询车辆【{carNo}】支付订单信息成功，订单号为【{orderNo}】, 支付金额为【{payMoney}】")
                return {"orderNo": orderNo, "payMoney": payMoney}
            else:
                raise Exception(f"查询车场支付订单接口错误！错误返回为{res_dic}")
            logger.info("【✔ %s完成】" % ps)


@util.catch_exception
@util.retry_fun
@allure.step("支付订单【{orderNo}】")
def pay_order(kttoken, lot_id, orderNo, payMoney, carNo, pay_time=""):
    read_data = Yaml(filepath.NOTICE, 2)
    url, headers, allData = util.get_parameter(read_data, lot_id, kttoken)
    for datas in allData:
        if datas[0]['id'] == 1:
            ps = datas[1]['ps']
            logger.info("【正在%s】" % ps)
            data = datas[2]
            data['lotCode'] = lot_id
            data['orderNo'] = orderNo
            data['carPlateNum'] = carNo
            data['paidMoney'] = payMoney
            data["payTime"] = pay_time if pay_time else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            res = request.post(url=url, headers=headers, data=json.dumps(data), timeout=5)
            res_dic = res.json()
            if res_dic["resultCode"] == 200:
                logger.info(f"订单【{orderNo}】支付成功！")
                return True
            else:
                logger.error(f"订单【{orderNo}】支付失败！")
                return False


@util.catch_exception
@util.retry_fun
@allure.step("支付订单【{orderNo}】")
def pay_order_pro(kttoken, lot_id, orderNo, payMoney, carNo, pay_time=""):
    read_data = Yaml(filepath.NOTICE_PRO, 4)
    url, headers, allData = util.get_parameter(read_data, lot_id, kttoken)
    for datas in allData:
        if datas[0]['id'] == 1:
            ps = datas[1]['ps']
            logger.info("【正在%s】" % ps)
            data = datas[2]
            data['lotCode'] = lot_id
            data['orderNo'] = orderNo
            data['carPlateNum'] = carNo
            data['paidMoney'] = payMoney
            data["payTime"] = pay_time if pay_time else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            res = request.post(url=url, headers=headers, data=json.dumps(data), timeout=5)
            res_dic = res.json()
            if res_dic["resultCode"] == 200:
                logger.info(f"订单【{orderNo}】支付成功！")
                return True
            else:
                logger.error(f"订单【{orderNo}】支付失败！")
                return False


if __name__ == '__main__':
    from testCases.Public.car import check_car_bi_data
    ps_id = 4
    lot_id = filepath.CONF.get("advanced", "lotId")
    # print(check_park(ps_id, lot_id))
    # print(get_lot_city(lot_id))
    # print(get_model_level_limit(lot_id))
    # check_park(1, lot_id)
    # print(get_model_level_limit(lot_id))
    # print(get_lot_city(lot_id))
    # edit_park_info(lot_id, "enablePayment", "false")
    # edit_park_info(lot_id, "enablePostPaid", "true")
    # edit_park_info(lot_id, "editParkingLotPostpaidConfigParam_privilegeStatus", 1)
    # edit_park_info(lot_id, "editParkingLotPostpaidConfigParam_modelLevelLimit", 1)

    # check_park(lot_id, 1)
    # check_park(lot_id, 2)
    # check_park(lot_id, 3)
    # check_car_bi_data("川AV8888", lot_id)


    # get_park_list(lot_id)
    # print(db_data[0][0])
    # print(query_data)
    # print(query_data[0][2].get("tableName"))
    # get_park_list(lot_id)
    from testCases.Public import public
    kttoken = public.login("592011611")
    order_info = get_park_pay_info(kttoken, "592011611", "川AS8888")
    print(order_info)
    pay_order(kttoken, "592011611", order_info["orderNo"], order_info["payMoney"], "川AS8888")