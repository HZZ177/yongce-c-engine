# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: car.py
@Description: 车辆信息相关校验
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
from urllib.parse import urljoin

import allure
from dateutil import rrule
from dateutil.parser import parse
from common import filepath, util
from common.configLog import logger
from common.db_tool import DbTool
from common.encryption import aes_decrypt
# from common.getCloudDataByFormal import cloud
from common.processYaml import Yaml
from common.request import request
from common.util import get_json_data_by_path, format_request_data_extend
from testCases.Public import park
from testCases.Public.public import get_user_token, get_user_info, get_postpaid_info, process_mms, get_user_info_by_mms


@util.catch_exception
@util.retry_fun
@allure.step("检验【{car_No}】的临时账单")
def check_order_temp(car_No):
    """
    校验6.x车场临时账单
    :param car_No: 车牌号
    :param ps_id:
    :param lot_id:
    :return: 有无欠费记录  True/False
    """
    yaml_data = process_mms(filepath.OWEBILLBYMMS)
    yaml_data["request_data"]["lpn"] = car_No
    res = request.mms_request(yaml_data)
    mms_result_dic = res.json()
    if mms_result_dic["code"] == 2000:
        logger.info("× 此次校验失败 ,车辆存在6.x车场临时欠费记录")
        return False
    else:
        logger.info("✔ 此次校验成功 ,车辆不存在6.x车场临时欠费记录")
        return True


@util.catch_exception
@util.retry_fun
@allure.step("检验【{user_id}】的会员中心账单")
def check_order(user_id, timeout=5):
    """
    校验会员中心账单
    :param user_id:  用户id
    :param ps_id:
    :param lot_id:
    :return: 有无欠费记录  True/False
    """
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    read_data = Yaml(filepath.OWEORDER, 0)
    db_data = read_data.allDb
    db_name = db_data[0][0].get("db")
    query_datas = read_data.allQuery
    db_obj = DbTool(db_data[0][0])
    for query_data in query_datas:
        if query_data[0]['id'] == 1:
            table_name = query_data[2].get("tableName")
            keyword_list = query_data[2].get("keyword")
            order_sql = f"select {','.join(keyword_list)} from {table_name} where PP_USER_ID='{user_id}';"
    endtime = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < endtime:
        # 测试环境检查
        if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
            order_result = db_obj.get_data_by_sql(sql=order_sql)
            if not len(order_result):
                break
            else:
                time.sleep(0.5)
        # 正式环境检查
        elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
            db_name = filepath.CONF.get('advanced', 'pro_pla_db')
            # order_result = cloud.select(filepath.CONF.get('advanced', 'example'), db_name, order_sql)
            if not len(order_result["data"]["rows"]):
                order_result = order_result["data"]["rows"]
                break
            else:
                time.sleep(0.5)
    if len(order_result):
        logger.info(f"用户【{user_id}】存在id为【{order_result[0][0]}】的欠费账单！")
        return False
    elif not len(order_result):
        logger.info(f"✔ 此次校验成功, 用户【{user_id}】，无欠费账单！")
        return True
    else:
        raise Exception(f"连接库【{db_name}】查询用户欠费账单出错！")


@util.catch_exception
@util.retry_fun
@allure.step("将【{user_id}】的车牌【{carNo}】开通为老会员")
def open_old_vip(carNo, user_id):
    """
    开通会员
    :param carNo:需开通车牌号

    """
    read_data = Yaml(filepath.OPENVIP, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["lpn"] = carNo
            request_data = json.dumps(request_data)
            res = request.request(method=method, url=url, data=request_data, headers=headers, timeout=10)
            result_dic = res.json()
            if result_dic["code"] == 5000 and "暂时无法开通后付费" in result_dic["message"]:
                logger.info(f"用户【{user_id}】开通老会员失败！")
            elif result_dic["code"] == 5000 and "该车辆已开通后付费" in result_dic["message"]:
                logger.info(f"车牌【{carNo}】已开通后付费")
            elif result_dic["code"] != 2000:
                raise Exception(logger.error(f"开通老会员出错！，错误返回为【{result_dic}】"))
            else:
                logger.info(f"✔ 用户【{user_id}】开通老会员成功！")
            return result_dic


@util.catch_exception
@util.retry_fun
@allure.step("将【{user_id}】的车牌【{carNo}】开通为新会员")
def open_vip_v2(carNo, user_id, origin, packageCode):
    """
    开通新会员
    :param user_id:
    :param origin: 开通来源 05:标准开通  UT:老会员升级
    :param carNo:需开通车牌号

    """
    read_data = Yaml(filepath.OPENVIPV2, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["lpn"] = carNo
            request_data["origin"] = origin
            request_data["packageCode"] = packageCode
            request_data = json.dumps(request_data)
            res = request.request(method=method, url=url, data=request_data, headers=headers, timeout=10)
            result_dic = res.json()
            if result_dic["code"] == 5000 and "暂时无法开通后付费" in result_dic["message"]:
                logger.info("开通新会员失败！")
            elif result_dic["code"] != 2000:
                raise Exception(logger.error(f"开通新会员出错！，错误返回为【{result_dic}】"))
            else:
                logger.info(f"✔ 调用开通新会员接口成功！，涉及用户为【{user_id}】，来源为【{origin}】，套餐为【{packageCode}】")
            return result_dic


@util.catch_exception
@util.retry_fun
@allure.step("通过速停车接口关闭【{user_id}】的会员")
def close_vip(user_id):
    """
    关闭会员
    :param user_id:

    """
    read_data = Yaml(filepath.CLOSEVIP, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    headers["app-id"] = filepath.CONF.get("postpay", "app-id")
    headers["secret-key"] = filepath.CONF.get("postpay", "secret-key")
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            vip_info = get_vip_info(user_id)
            if not vip_info:
                raise Exception(f"未查询到用户【{user_id}】的会员信息！")
            id = vip_info[0]
            request_data["id"] = id
            request_data["userId"] = user_id
            request_data = json.dumps(request_data)
            res = request.request(method=method, url=url, data=request_data, headers=headers, timeout=10)
            result_dic = res.json()
            if result_dic["code"] != 2000:
                raise Exception(logger.error(f"关闭会员出错！，错误返回为【{result_dic}】"))
            else:
                logger.info(f"✔ 用户【{user_id}】关闭会员成功！")
            return result_dic


@util.catch_exception
@util.retry_fun
@allure.step("通过连接数据库查询【{user_id}】的会员信息")
def get_vip_info(user_id):
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.VIPINFOBYDB, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                user_id = user_id
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE USER_ID='{user_id}' and VALID = 'Y';"
                token_result = db_obj.get_data_by_sql(sql=token_sql)
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        read_data = Yaml(filepath.VIPINFOBYDB, 0)
        db_name = filepath.CONF.get('advanced', 'pro_pla_db')
        query_datas = read_data.allQuery
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                user_id = user_id
                token_sql = f"SELECT {','.join(keyword_list)} FROM {db_name}.{table_name} WHERE USER_ID='{user_id}' and VALID = 'Y';"
                # token_result = \
                # cloud.get_data_by_sql(filepath.CONF.get('advanced', 'example'), db_name, token_sql)["data"]["rows"]
    if not len(token_result):
        logger.info(f"未查询到用户【{user_id}】的会员信息！")
        return False
    return token_result[0]


@util.catch_exception
@util.retry_fun
@allure.step("通过连接数据库查询【{user_id}】的新会员表信息")
def get_vip_info_v2(user_id, old_vip_id):
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.VIPINFOBYDBV2, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                user_id = user_id
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE pp_credit_payment_id='{old_vip_id}';"
                token_result = db_obj.get_data_by_sql(sql=token_sql)
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        read_data = Yaml(filepath.VIPINFOBYDBV2, 0)
        db_name = filepath.CONF.get('advanced', 'pro_post_db')
        query_datas = read_data.allQuery
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                user_id = user_id
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE pp_credit_payment_id='{old_vip_id}';"
                # token_result = \
                # cloud.get_data_by_sql(filepath.CONF.get('advanced', 'example'), db_name, token_sql)["data"]["rows"]
    if not len(token_result):
        logger.info(f"未查询到用户【{user_id}】的新会员表信息！")
        return False
    return token_result[0]


@util.catch_exception
@util.retry_fun
@allure.step("通过连接数据库【{user_id}】的检验新旧会员表状态")
def check_vip_by_db(user_id):
    old_result = get_vip_info(user_id)
    if not old_result:
        logger.info(f"检验用户【{user_id}】的旧会员表状态失败,用户旧会员表中没有开通数据!")
        return False
    else:
        logger.info(f"检验用户【{user_id}】的旧会员表状态成功")
        new_result = get_vip_info_v2(user_id, old_result[0])
        if not new_result:
            logger.info(f"检验用户【{user_id}】的新会员表状态失败,用户新会员表中没有开通数据!")
            return False
        else:
            logger.info(f"检验用户【{user_id}】的新会员表状态成功")
            return True


@util.catch_exception
@util.retry_fun
@allure.step("检验【{user_id}】的会员状态")
def check_vip(user_id):
    """
    检查会员状态
    :param user_id: 用户id
    :param ps_id:
    :param lot_id:
    :return: 是否为会员  True/False
    """
    result_dic = get_postpaid_info(user_id)
    if result_dic["data"]["vipStatus"]:
        logger.info(f"✔ 用户【{user_id}】为会员")
        return True
    elif result_dic["data"]["vipStatus"] == 0:
        logger.info(f"× 用户【{user_id}】为非会员")
        return False
    elif result_dic["code"] != 2000:
        raise Exception(logger.error("查询后付费设置信息接口出错！"))
    else:
        raise Exception(logger.error("查询用户会员状态出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("检验【{car_No}】的后付费在场记录")
def get_OnPark_info(car_No):
    """
    得到后付费在场记录信息
    :param car_No:
    :param ps_id:
    :param lot_id:
    """
    yaml_data = process_mms(filepath.ONPARKBYMMS)
    yaml_data["request_data"]["plateNumber"] = car_No
    res = request.mms_request(yaml_data)
    mms_result_dic = res.json()
    if mms_result_dic["code"] == 2000:
        logger.info(f"查询中台接口，车辆【{car_No}】的后付费在场记录成功！")
    else:
        raise Exception(logger.error("查询中台后付费在场信息接口出错！"))
    return mms_result_dic


@util.catch_exception
@util.retry_fun
@allure.step("检验【{car_No}】的在场记录")
def check_OnPark(car_No):
    """

    :param car_No:车牌号
    :param ps_id:
    :param lot_id:
    :return: 车辆有无在场记录 True/False
    """
    mms_result_dic = get_OnPark_info(car_No)
    if len(mms_result_dic["data"]) == 0:
        logger.info(f"✔ 【{car_No}】车辆无在场记录")
        return True
    else:
        logger.info(f"× 【{car_No}】车辆存在在场记录")
        return False


@util.catch_exception
@util.retry_fun
@allure.step("删除【{carNo}】在车场【{lot_id}】后付费在场记录")
def del_OnPark(carNo, lot_id):
    """
    删除后付费在场记录
    :param car_No:车牌号

    """
    onPark_info = get_OnPark_info(carNo)
    if onPark_info["data"]:
        comeTime = onPark_info["data"][0]["comeTime"]
        comeTimeArray = time.localtime(comeTime/1000)
        comeTime = time.strftime("%Y-%m-%d %H:%M:%S", comeTimeArray)
        yaml_data = process_mms(filepath.DELONPARKBYMMS)
        yaml_data["request_data"]["plateNumber"] = carNo
        yaml_data["request_data"]["lotId"] = lot_id
        yaml_data["request_data"]["comeTime"] = comeTime
        res = request.mms_request(yaml_data)
        mms_result_dic = res.json()
        if mms_result_dic["code"] == 2000:
            logger.info(f"清除车辆【{carNo}】的后付费在场记录成功！")
        elif mms_result_dic["code"] == 5000 and "影响行数为0" in mms_result_dic["message"]:
            logger.info(f"清除车辆【{carNo}】的后付费在场记录失败, 未查询到相关在场记录！")
        else:
            raise Exception(logger.error("查询中台后付费在场删除接口出错！"))
    else:
        logger.info(f"车辆【{carNo}】的无后付费在场记录，无需清理")


@util.catch_exception
@util.retry_fun
@allure.step("增加【{carNo}】在车场【{lot_id}】后付费在场记录")
def add_OnPark(carNo, lot_id, user_id, wx_appId, offset_time=9):
    """
    增加后付费在场记录
    :param car_No:车牌号

    """
    comeTime = int(time.time()) - offset_time*60
    comeTimeArray = time.localtime(comeTime)
    comeTime = time.strftime("%Y-%m-%d %H:%M:%S", comeTimeArray)
    yaml_data = process_mms(filepath.ADDONPARKBYMMS)
    yaml_data["request_data"]["appId"] = wx_appId
    yaml_data["request_data"]["ppUserId"] = user_id
    user_wx_info = get_user_info_by_mms(user_id)
    yaml_data["request_data"]["openId"] = [wxAuthInfos["wxOpenId"] for wxAuthInfos in user_wx_info["wxAuthInfos"] if wxAuthInfos["wxAppId"] == wx_appId][0]
    yaml_data["request_data"]["plateNumber"] = carNo
    yaml_data["request_data"]["lotId"] = lot_id
    yaml_data["request_data"]["comeTime"] = comeTime
    yaml_data["request_data"] = json.dumps(yaml_data.get("request_data"), ensure_ascii=False).encode("utf-8")
    res = request.mms_request(yaml_data)
    mms_result_dic = res.json()
    if mms_result_dic["code"] == 2000:
        logger.info(f"增加车辆【{carNo}】的后付费在场记录成功！")
    else:
        raise Exception(logger.error("查询中台后付费在场删除接口出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("检查【{carNo}】在车场【{lot_id}】能否被授权")
def check_postpaid_rights(carNo, lot_id, user_id, wx_appId):
    """
    查询后付费能否被授权
    :param car_No:车牌号

    """
    comeTime = int(time.time())
    comeTimeArray = time.localtime(comeTime)
    comeTime = time.strftime("%Y-%m-%d %H:%M:%S", comeTimeArray)
    yaml_data = process_mms(filepath.ONRIGHTSBYMMS)
    yaml_data["request_data"]["appId"] = wx_appId
    yaml_data["request_data"]["ppUserId"] = user_id
    user_wx_info = get_user_info_by_mms(user_id)
    yaml_data["request_data"]["openId"] = [wxAuthInfos["wxOpenId"] for wxAuthInfos in user_wx_info["wxAuthInfos"] if wxAuthInfos["wxAppId"] == wx_appId][0]
    yaml_data["request_data"]["plateNumber"] = carNo
    yaml_data["request_data"]["lotId"] = lot_id
    yaml_data["request_data"]["comeTime"] = comeTime
    yaml_data["request_data"] = json.dumps(yaml_data.get("request_data"), ensure_ascii=False).encode("utf-8")
    res = request.mms_request(yaml_data)
    mms_result_dic = res.json()
    if mms_result_dic["code"] == 2000:
        logger.info(f"【{carNo}】允许被后付费授权！")
        return True
    elif mms_result_dic["code"] == 5000:
        logger.info(f"【{carNo}】在车场【{lot_id}】已有授权，不允许被后付费授权！")
        return False
    else:
        raise Exception(logger.error("查询中台查询后付费能否被授权接口出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("检验【{carNo}】是否为用户【{user_id}】后付费绑定车牌")
def check_after_binding(carNo, user_id):
    """

    :param user_id:
    :param carNo:车牌
    :return: 用户是否绑定车牌  True/False
    """
    result_dic = get_postpaid_info(user_id)
    if len(result_dic["data"]["userPostpaidLpns"]) == 0:
        logger.info(f"× 车牌【{carNo}】不是后付费绑定车牌")
        return False
    elif len(result_dic["data"]["userPostpaidLpns"]) > 0:
        logger.info(f"✔ 车牌【{carNo}】是后付费绑定车牌")
        return True
    elif result_dic["code"] != 2000:
        raise Exception(logger.error("查询后付费设置信息接口出错！"))
    else:
        raise Exception(logger.error("查询后付费绑定车牌出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("增加【{carNo}】为用户【{user_id}】后付费绑定车牌")
def add_after_binding(carNo, user_id):
    """
    增加后付费车辆
    :param user_id:
    :param carNo:车牌
    """
    read_data = Yaml(filepath.ADDPOSTLPN, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["lpn"] = carNo
            res = request.request(method=method, url=url, params=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 5000 and result_dic["message"] == "您已添加后付费车辆无法再次添加":
                logger.info(f"用户【{user_id}】,已添加【{carNo}】为后付费车牌")
                return False
            elif result_dic["code"] == 5000 and "车牌已被他人绑定为先出场后付费车牌" in result_dic["message"].replace(" ", ""):
                logger.info(f"【{carNo}】已被他人添加为后付费可用车牌！！！")
                return False
            elif result_dic["code"] == 2000:
                logger.info(f"用户【{user_id}】,成功添加【{carNo}】为后付费车牌")
                return True

            else:
                raise Exception(logger.error("调用增加后付费车牌接口出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("将【{carNo}】从用户【{user_id}】后付费绑定车牌中移除")
def remove_after_binding(carNo, user_id):
    """
    移除后付费车辆
    :param user_id:
    :param carNo:车牌
    """
    read_data = Yaml(filepath.REMOVEPOSTLPN, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["lpn"] = carNo
            res = request.request(method=method, url=url, params=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 5000 and result_dic["message"] == "未有此车辆，无法移除":
                logger.info(f"用户【{user_id}】,未添加【{carNo}】为后付费车牌,无需移除")
            elif result_dic["code"] == 2000:
                logger.info(f"用户【{user_id}】,成功将【{carNo}从后付费车牌中移除")
            else:
                raise Exception(logger.error("调用移除后付费车牌接口出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("得到用户【user_id】的禁用车场列表")
def get_disable_lot_list(user_id):
    """

    :param user_id:用户id
    :param lot_id: 车场id
    :return:
    """
    read_data = Yaml(filepath.DISABLELOT, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            res = request.request(method=method, url=url, headers=headers)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                return result_dic["data"]
            else:
                raise Exception(logger.error(f"查询禁用车场接口出错！报错信息为【{result_dic}】"))



@util.catch_exception
@util.retry_fun
@allure.step("检验用户【user_id】是否禁用车场【{lot_id}】")
def check_disable_lot(user_id, lot_id):
    """

    :param user_id:用户id
    :param lot_id: 车场id
    :return:
    """
    read_data = Yaml(filepath.DISABLELOT, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            res = request.request(method=method, url=url, headers=headers)
            result_dic = res.json()
            if len(result_dic["data"]) == 0:
                logger.info("✔ 用户【%s】未禁用车场【%s】" % (user_id, lot_id))
                return True
            elif not [disable_lot for disable_lot in result_dic["data"] if disable_lot["lotId"] == str(lot_id)]:
                logger.info("✔ 用户【%s】未禁用车场【%s】" % (user_id, lot_id))
                return True
            elif [disable_lot for disable_lot in result_dic["data"] if disable_lot["lotId"] == str(lot_id)]:
                logger.info("× 用户【%s】已禁用车场【%s】" % (user_id, lot_id))
                return False
            elif result_dic["code"] != 2000:
                raise Exception(logger.error("查询用户禁用车场接口出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("编辑用户的禁用车场信息：【{user_id}|{lot_id}|{ps_id}】||1、增加，2、删除")
def edit_disable_lot(user_id, lot_id, ps_id, origin="02"):
    """

    :param origin: "01：后台添加,02:车主添加"  默认02
    :param ps_id: 用例id 1增加 2删除
    :param user_id:用户id
    :param lot_id: 车场id
    :return:
    """
    read_data = Yaml(filepath.EDITDISABLELOT, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == ps_id:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["lotId"] = lot_id
            request_data["origin"] = origin
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers)
            result_dic = res.json()
            if result_dic["code"] == 2000 and "增加" in sec:
                logger.info("✔ 用户【%s】禁用车场【%s】成功, origin为【%s】" % (user_id, lot_id, origin))
            elif result_dic["code"] == 2000 and "删除" in sec:
                logger.info("✔ 用户【%s】解除车场【%s】的禁用成功" % (user_id, lot_id))
            elif result_dic["code"] == 5000 and "该车场已被您加入车场黑名单" == result_dic["message"]:
                logger.info("用户【%s】已禁用车场【%s】，无需再次禁用" % (user_id, lot_id))
            elif result_dic["code"] == 5000 and "该车场不在您的车场黑名单上" == result_dic["message"]:
                logger.info("用户【%s】未禁用车场【%s】，无需移除" % (user_id, lot_id))
            else:
                raise Exception(logger.error("调用增加/删除用户禁用车场接口出错！"))


@allure.step("绑定用户【{user_id}】默认车牌为【{car_No}】")
def bind_car_no(car_No, user_id):
    read_data = Yaml(filepath.BINDCARNO, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["lpn"] = car_No
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers)
            res_dic = res.json()
            if res_dic["code"] != 2000:
                raise Exception(logger.error(f"调用增加用户默认车牌接口出错！,错误信息为【{res_dic}】"))
            else:
                logger.info(f"用户【{user_id}】的默认车牌成功换绑为【{car_No}】")


@util.catch_exception
@util.retry_fun
@allure.step("检验用户【{car_No}】是否为用户【{user_id}】的隐私车牌")
def check_privacy_car(car_No, user_id):
    """

    :param car_No: 车牌
    :param user_id: 用户id
    :return:
    """
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.PRIVACYCAR, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])

        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                user_id = user_id
                privacy_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE PLATE_NUMBER='{car_No}';"
                privacy_result = db_obj.get_data_by_sql(sql=privacy_sql)

    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        read_data = Yaml(filepath.PRIVACYCAR, 0)
        db_name = filepath.CONF.get('advanced', 'pro_post_db')
        query_datas = read_data.allQuery
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                privacy_sql = f"SELECT {','.join(keyword_list)} FROM {db_name}.{table_name} WHERE PLATE_NUMBER='{car_No}';"
                # privacy_result_dic = cloud.get_data_by_sql(filepath.CONF.get('advanced', 'example'), db_name, privacy_sql)
                # privacy_result = privacy_result_dic["data"]["rows"]
    if len(privacy_result) == 0:
        logger.info("✔ 用户非隐私车牌")
        return True
    else:
        if privacy_result[0][0] == user_id:
            logger.info("✔ 用户为隐私车牌用户，且为本人")
            return True
        else:
            logger.info("× 车辆【%s】为隐私车牌，但非本人【%s】" % (car_No, user_id))
            return False


@util.catch_exception
@util.retry_fun
@allure.step("检验用户【{user_id}】是否为在信用付黑名单中")
def check_vip_black_list(user_id, car_No):
    """

    :param car_No:
    :param user_id:
    :return: 用户是否在信用付黑名单中  True/False
    """
    read_data = Yaml(filepath.PAYMENTBLACKLIST, 5)
    headers = read_data.headers
    headers["app-id"] = filepath.CONF.get("postpay", "app-id")
    headers["secret-key"] = filepath.CONF.get("postpay", "secret-key")
    url = read_data.url
    datas = read_data.allData
    method = read_data.method
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['request_data']["userId"] = user_id
            query_data[2]['request_data']["commonLpn"] = car_No
            res = request.request(url=url, data=json.dumps(query_data[2]['request_data']), method=method,
                                  headers=headers)
            result_dic = res.json()
            if "未有此用户" in result_dic["message"] and result_dic["code"] == 5000:
                logger.info(f"✔ 用户【{user_id}】不在信用付黑名单中")
                return True, result_dic
            elif len(result_dic["data"]) > 0:
                logger.info(f"× 用户【{user_id}】在信用付黑名单中")
                return False, result_dic


@util.catch_exception
@util.retry_fun
@allure.step("添加用户【{user_id}】至信用付黑名单中")
def add_vip_black_list(user_id, car_No):
    """
    增加用户至信用付黑名单
    :param car_No:
    :param user_id:
    :return:
    """
    phone = get_user_info(user_id)["data"]["phone"]
    read_data = Yaml(filepath.ADDPAYMENTBLACKLIST, 5)
    headers = read_data.headers
    headers["app-id"] = filepath.CONF.get("postpay", "app-id")
    headers["secret-key"] = filepath.CONF.get("postpay", "secret-key")
    url = read_data.url
    datas = read_data.allData
    method = read_data.method
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['request_data']["userId"] = user_id
            query_data[2]['request_data']["commonLpn"] = car_No
            query_data[2]['request_data']["phone"] = phone
            res = request.request(url=url, data=json.dumps(query_data[2]['request_data']), method=method,
                                  headers=headers)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"✔ 成功将用户【{user_id}】添加入信用付黑名单中")
            elif result_dic["code"] == 5000 and "已存在" in result_dic["message"]:
                logger.info(f"用户【{user_id}】已在信用付黑名单中，无需添加")
            else:
                raise Exception(logger.error("调用增加信用付黑名单接口错误！"))


@util.catch_exception
@util.retry_fun
@allure.step("将用户【{user_id}】从信用付黑名单中删除")
def del_vip_black_list(user_id, car_No):
    """
    从信用付黑名单中将用户删除
    :param car_No:
    :param user_id:
    :return: 用户是否在信用付黑名单中  True/False
    """
    result = check_vip_black_list(user_id, car_No)
    if result[0]:
        logger.info(f"用户【{user_id}】不在信用付黑名单中，无需删除")
        return
    id = result[1]["data"]["id"]
    read_data = Yaml(filepath.DELPAYMENTBLACKLIST, 5)
    headers = read_data.headers
    headers["app-id"] = filepath.CONF.get("postpay", "app-id")
    headers["secret-key"] = filepath.CONF.get("postpay", "secret-key")
    url = read_data.url
    datas = read_data.allData
    method = read_data.method
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['request_data']["id"] = id
            res = request.request(url=url, data=json.dumps(query_data[2]['request_data']), method=method,
                                  headers=headers)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"✔ 已经用户【{user_id}】移除出信用付黑名单")
            elif result_dic["code"] == 5000 and "未有此用户" in result_dic["message"]:
                logger.info(f"用户【{user_id}】不在信用付黑名单中，无需移除")
            else:
                raise Exception(logger.error("调用删除用户信用付黑名单接口出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("检验【{carNo}】是否在bi黑名单中")
def check_bi_black_list(carNo):
    """

    :param carNo:车牌
    :return: 用户是否在BI黑名单中  True/False
    """
    read_data = Yaml(filepath.BIBLACK, 6)
    url = read_data.url
    datas = read_data.allData
    headers = read_data.headers
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['carPlateNum'] = carNo
            res = request.get(url=url, params=query_data[2], headers=headers)
            car_No = carNo
            result_dic = res.json()
            if not result_dic['data']:
                logger.info(f"✔ 车牌【{car_No}】不在bi人车黑名单中")
                return True
            elif result_dic['data'] == car_No:
                logger.info(f"× 车牌【{car_No}】在bi人车黑名单中")
                return False
            else:
                raise Exception(logger.error("人车模型接口请求失败"))


@util.catch_exception
@util.retry_fun
@allure.step("插入【{carNo}】至bi黑名单中")
def insert_bi_black_list(carNo):
    """
    将车牌插入人车模型黑名单中
    :param carNo:车牌
    :return:
    """
    read_data = Yaml(filepath.INSERTBIBLACK, 6)
    url = read_data.url
    datas = read_data.allData
    headers = read_data.headers
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['carPlateNum'] = carNo
            res = request.post(url=url, data=json.dumps(query_data[2]), headers=headers)
            car_No = carNo
            result_dic = res.json()
            if result_dic['code'] == 200:
                logger.info(f"✔ 车牌【{car_No}】已插入bi人车黑名单中")
            else:
                raise Exception(logger.error("插入用户投诉重度黑名单记录接口请求失败"))


@util.catch_exception
@util.retry_fun
@allure.step("将【{carNo}】从bi黑名单中移除")
def remove_bi_black_list(carNo):
    """
    将车牌移除人车模型黑名单
    :param carNo:车牌
    :return:
    """
    read_data = Yaml(filepath.REMOVEBIBLACK, 6)
    url = read_data.url
    datas = read_data.allData
    headers = read_data.headers
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['carPlateNum'] = carNo
            res = request.post(url=url, data=json.dumps(query_data[2]), headers=headers)
            car_No = carNo
            result_dic = res.json()
            if result_dic['code'] == 200:
                logger.info(f"✔ 车牌【{car_No}】已从bi人车黑名单中移除")
            elif result_dic['code'] == 5000 and result_dic['message'] == "此车牌不属于投诉重度黑名单":
                logger.info(f"车牌【{car_No}】不在bi人车黑名单中，无需移除")
            else:
                raise Exception(logger.error("插入用户投诉重度黑名单记录接口请求失败"))


@util.catch_exception
@util.retry_fun
@allure.step("检验【{carNo}】是否符合人车模型 v2")
def check_car_bi_data(carNo, lotId):
    """

    :param carNo:车牌
    :param lotId: 车场id
    :return: 用户是否符合人车模型条件标准  True/False
    """
    read_data = Yaml(filepath.BICARDATA, 6)
    url = read_data.url
    datas = read_data.allData
    headers = read_data.headers
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['carPlateNum'] = carNo
            query_data[2]['lotId'] = lotId
            lot_id = lotId
            car_No = carNo
            lot_special_score = park.get_model_level_limit(lot_id)
            res = request.get(url=url, params=query_data[2], headers=headers)
            result_dic = res.json()
            if result_dic["data"]['userLevel'] < lot_special_score and result_dic["data"]['passFlag']:
                logger.info(f"✔ 车牌【{car_No}】符合人车模型条件")
                return True
            elif not result_dic["data"]['passFlag'] or result_dic["data"]['userLevel'] > lot_special_score:
                logger.info(f"× 车牌【{car_No}】不符合人车模型条件")
                return False
            else:
                raise Exception(logger.error("人车模型接口请求失败"))


@util.catch_exception
@util.retry_fun
@allure.step("检验【{carNo}】是否符合人车模型 v1")
def check_car_bi_data_v1(carNo, lotId):
    """

    :param carNo:车牌
    :param lotId: 车场id
    :return: 用户是否符合人车模型条件标准  True/False
    """
    read_data = Yaml(filepath.BICARDATA_V1, 6)
    url = read_data.url
    datas = read_data.allData
    headers = read_data.headers
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['plateNum'] = carNo
            lot_id = lotId
            car_No = carNo
            lot_modelWeightLimit = park.get_model_weight_limit(lot_id)
            res = request.get(url=url, params=query_data[2], headers=headers)
            result_dic = res.json()
            if not result_dic["data"]:
                logger.info(f"× 车牌【{car_No}】没有人车模型v1数据")
                return False
            elif float(result_dic["data"]['firstUserWeight']) >= lot_modelWeightLimit:
                logger.info(f"✔ 车牌【{car_No}】符合人车模型条件")
                return True
            elif float(result_dic["data"]['firstUserWeight']) < lot_modelWeightLimit:
                logger.info(f"× 车牌【{car_No}】不符合人车模型条件")
                return False
            else:
                raise Exception(logger.error("人车模型_v1 接口请求失败"))


@util.catch_exception
@util.retry_fun
@allure.step("检验用户【{user_id}】分层是否满足发送后付费体验版邀请")
def check_user_group(user_id):
    """

    :param user_id: 用户id
    :return: 检查用户分层是否满足发送后付费体验版邀请 True/False
    """
    read_data = Yaml(filepath.ABTEST, 5)
    url = read_data.url
    datas = read_data.allData
    headers = read_data.headers
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['userId'] = user_id
            res = request.get(url=url, params=query_data[2], headers=headers)
            result_dic = res.json()
            if result_dic["data"]['allowInvitePostpaidExperience']:
                logger.info(f"✔ 用户【{user_id}】属于能被邀请后付费体验版的分层用户")
                return True
            elif not result_dic["data"]['allowInvitePostpaidExperience']:
                logger.info(f"× 用户【{user_id}】不属于能被邀请后付费体验版的分层用户")
                return False
            else:
                raise Exception(logger.error("查询用户功能分流接口请求失败"))


@util.catch_exception
@util.retry_fun
@allure.step("通过user，检验用户【{user_id}】与车场【{lot_id}】是否在同一城市")
def check_city_by_user(user_id, lot_id):
    user_info_dic = get_user_info_by_mms(user_id)
    lot_cityNo = park.get_lot_city(lot_id)
    if user_info_dic["ppUserInfo"]["city"] == str(lot_cityNo):
        logger.info(f"✔ 车牌【{user_info_dic['ppUserInfo']['commonLpn']}】与车场【{lot_id}】在同一城市")
        return True
    elif user_info_dic["ppUserInfo"]["city"] != str(lot_cityNo):
        logger.info(f"× 车牌【{user_info_dic['ppUserInfo']['commonLpn']}】与车场【{lot_id}】不同一城市")
        return False
    else:
        raise Exception(logger.error("通过用户信息查询城市信息出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("通过后付费信息，检验用户【{user_id}】与车场【{lot_id}】是否在同一城市")
def check_city_by_post(carNo, lot_id, user_id):
    """
    通过后付费车场配置检验用户城市与车场城市
    :param user_id:
    :param carNo:
    :param lot_id:
    :return:
    """
    result_dic = get_postpaid_info(user_id)
    lot_cityNo = park.get_lot_city(lot_id)
    if len(result_dic["data"]["userPostpaidCities"]) == 0:
        raise Exception(logger.error(f"未查询到【{carNo}】的默认城市信息"))
    elif [user_city for user_city in result_dic["data"]["userPostpaidCities"] if user_city["cityId"] == lot_cityNo]:
        logger.info(f"✔ 车牌【{carNo}】与车场【{lot_id}】在同一城市")
        return True
    elif not [user_city for user_city in result_dic["data"]["userPostpaidCities"] if user_city["cityId"] == lot_cityNo]:
        logger.info(f"× 车牌【{carNo}】与车场【{lot_id}】不同一城市")
        return False
    elif result_dic["code"] != 2000:
        raise Exception(logger.error("查询后付费设置信息接口出错！"))
    else:
        raise Exception(logger.error("查询城市信息出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("更改用户【{user_id}后付费城市为【city_id】")
def edit_post_city(user_id, city_id):
    """
    更改后付费车牌可用城市
    :param city_id:
    :param user_id:
    :return:
    """
    read_data = Yaml(filepath.EDITPOSTCITY, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = [city_id]
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers)
            result_dic = res.json()
            if result_dic['code'] == 2000:
                logger.info(f"✔ 修改后付费用户【{user_id}】可用城市为【{city_id}】成功")
            else:
                raise Exception(logger.error("调用保存后付费城市接口出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("更改用户【{user_id}】默认城市为【{city_id}】")
def edit_user_city(user_id, city_id):
    """
    更改用户默认城市
    :param city_id:
    :param user_id:
    :return:
    """
    read_data = Yaml(filepath.EDITUSERCITY, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["cityId"] = city_id
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers)
            result_dic = res.json()
            if result_dic['code'] == 2000:
                logger.info(f"✔ 修改用户【{user_id}】的默认城市为【{city_id}】成功")
            else:
                raise Exception(logger.error("调用保存后付费城市接口出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("通过通过中台接口得到【{user_id}】的open_id")
def get_user_info_by_mms(user_id):
    """
    通过中台接口得到用户信息open_id
    :param user_id:
    :param wx_appId:
    :return:
    """
    yaml_data = process_mms(filepath.USERINFOBYMMS)
    yaml_data["request_data"]["ppUserId"] = user_id
    yaml_data["request_data"] = json.dumps(yaml_data.get("request_data"), ensure_ascii=False).encode("utf-8")
    res = request.mms_request(yaml_data)
    mms_result_dic = res.json()
    if mms_result_dic["code"] == 2000:
        return mms_result_dic
    else:
        raise Exception(logger.error("调用中台查询用户信息接口出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("检验【{user_id}】的订阅信息")
def check_user_wx(user_id, wx_appId):
    """
    用户订阅信息校验
    :param user_id:
    :return:
    """
    read_data = Yaml(filepath.USERWX, 4)
    url = read_data.url
    datas = read_data.allData
    headers = read_data.headers
    mms_result_dic = get_user_info_by_mms(user_id)
    wx_OpenId_list = [wxAuthInfos["wxOpenId"] for wxAuthInfos in mms_result_dic["wxAuthInfos"] if wxAuthInfos["wxAppId"] == wx_appId]
    if len(mms_result_dic["wxAuthInfos"]) == 0:
        logger.info(f"× 用户【{user_id}】未通过微信信息校验")
        return False
    elif wx_OpenId_list:
        logger.info(f"✔ 用户【{user_id}】通过微信信息校验")
        openid = wx_OpenId_list[0]
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['openid'] = openid
            v = format_request_data_extend(query_data[2]['access_token'], key_data=wx_appId)
            query_data[2]['access_token'] = dict(get_json_data_by_path(v, get_wx_token())).get("access_token")
            res = request.get(url=url, params=query_data[2], headers=headers, timeout=10)
            result_dic = res.json()
            if result_dic["subscribe"] == 0:
                logger.info(f"× 用户【{user_id}】未通过微信订阅公众号校验")
                return False
            elif result_dic["subscribe"] == 1:
                logger.info(f"✔ 用户【{user_id}】通过微信订阅公众号校验")
                return True
            else:
                raise Exception(logger.error("请求微信接口返回code错误"))


@util.catch_exception
@util.retry_fun
@allure.step("得到微信的原始token")
def get_wx_token():
    read_data = Yaml(filepath.GETWXTOKEN, 4)
    url = read_data.url
    datas = read_data.allData
    headers = read_data.headers
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            res = request.get(url=url, headers=headers, timeout=10)
            init_token = res.text
            if init_token:
                aes_key = filepath.CONF.get("aes", "encryptionKey")
                aes_iv = filepath.CONF.get("aes", "IV")
                data = aes_decrypt(aes_key, aes_iv, init_token)
                data = data[:data.rfind('}')+1]
                return data
            else:
                raise Exception(logger.error("得到微信原始token为空"))


@util.catch_exception
@util.retry_fun
def check_onpark_less30():
    """
    用户在场30min内校验
    :return:
    """
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        return True
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        pass


@util.catch_exception
@allure.step("检查出场结果")
def check_carout(carNo):
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    endtime = datetime.datetime.now() + datetime.timedelta(seconds=5)
    while datetime.datetime.now() < endtime:
        if check_OnPark(carNo):
            # 测试环境检查(如果是测试环境将临时订单时间提前)
            if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
                pass
                # order.update_Bill(carNo, min=5)
            return True
        else:
            time.sleep(0.5)
    return False


@util.catch_exception
@util.retry_fun
@allure.step("通过连接数据库查询套餐卷【{packageCode}】对应的配置id")
def get_send_plan_config_id(packageCode):
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.GETSENDPLANCONFIGID, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE package_code='{packageCode}';"
                token_result = db_obj.get_data_by_sql(sql=token_sql)
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        read_data = Yaml(filepath.GETSENDPLANCONFIGID, 0)
        db_name = filepath.CONF.get('advanced', 'pro_post_db')
        query_datas = read_data.allQuery
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE package_code='{packageCode}';"
                # token_result = \
                # cloud.get_data_by_sql(filepath.CONF.get('advanced', 'example'), db_name, token_sql)["data"]["rows"]
    if not len(token_result):
        logger.info(f"未查询到套餐卷【{packageCode}】的配置信息！")
        return False
    return token_result[0]


@util.catch_exception
@util.retry_fun
@allure.step("通过连接数据库查询配置id【{config_id}】对应的配置")
def get_send_plan_config(config_id):
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.GETSENDPLANCONFIG, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE CVC_ID='{config_id}';"
                token_result = db_obj.get_data_by_sql(sql=token_sql)
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        read_data = Yaml(filepath.GETSENDPLANCONFIG, 0)
        db_name = filepath.CONF.get('advanced', 'pro_post_db')
        query_datas = read_data.allQuery
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE CVC_ID='{config_id}';"
                # token_result = \
                # cloud.get_data_by_sql(filepath.CONF.get('advanced', 'example'), db_name, token_sql)["data"]["rows"]
    if not len(token_result):
        logger.info(f"未查询到配置id【{config_id}】的配置信息！")
        return False
    return token_result


@util.catch_exception
@util.retry_fun
@allure.step("通过速停车接口得到用户【{user_id}】的优惠券发放计划")
def get_send_plan(user_id):
    read_data = Yaml(filepath.GETSENDPLAN, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            res = request.request(method=method, url=url, params=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                if not len(result_dic["data"]):
                    raise Exception(logger.error(f"查询用户询用户【{user_id}】优惠券发放计划为空,用户可能为非会员!"))
                else:
                    logger.info(f"查询用户【{user_id}】优惠券发放计划成功")
                    return result_dic["data"]
            else:
                raise Exception(logger.error("查询用户出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("校验用户【{user_id}】的优惠券发放计划")
def check_send_plan(packageCode, user_id):
    order_id = get_vip_order_info("204350188868616197")[0][0]
    config_id = get_send_plan_config_id(packageCode)[0]
    db_config_dic = {}
    for db_config in get_send_plan_config(config_id):
        db_config_dic[db_config[0]] = db_config[1]
    send_plan = get_send_plan(user_id)
    send_plan_check_list = []
    couponInfo_dic = {}
    for send_plan_item in send_plan:
        if send_plan_item.get("orderNo") == order_id:
            planSendTime = send_plan_item.get("planSendTime")
            planSendTimeArray = time.localtime(planSendTime / 1000)
            planSendTime = time.strftime("%Y-%m-%d %H:%M:%S", planSendTimeArray)
            sendStatus = send_plan_item.get("sendStatus")
            couponInfo = send_plan_item.get("couponInfo")
            for couponInfo_item in couponInfo:
                couponInfo_dic[couponInfo_item.get("couponName")] = couponInfo_item.get("couponCount")
            send_plan_check_list.append([planSendTime, sendStatus, couponInfo_dic])
    for send_plan_check_point in send_plan_check_list:
        month_count = rrule.rrule(rrule.MONTHLY, dtstart=datetime.date.today(),
                                  until=parse(send_plan_check_point[0])).count()
        if month_count == 1 and send_plan_check_point[1] == 1:
            if db_config_dic == send_plan_check_point[2]:
                logger.info(f"校验订单【{order_id}】,当月下发优惠券成功")
            else:
                logger.error(f"校验订单【{order_id}】,校验当月下发优惠券失败!")
                return False
        elif month_count <= 12 and send_plan_check_point[1] == 0:
            if db_config_dic == send_plan_check_point[2]:
                logger.info(f"校验校验订单【{order_id}】,第{month_count}月下发优惠券成功")
            else:
                logger.error(f"校验校验订单【{order_id}】,第{month_count}月下发优惠券失败!")
                return False
        else:
            logger.error(f"校验校验订单【{order_id}】,优惠卷下发计划失败!")
            return False
    return True


@util.catch_exception
@util.retry_fun
@allure.step("通过连接数据库查询用户【{user_id}】开通会员的订单id")
def get_vip_order_info(user_id):
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.OPENVIPINFOBYDB, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE USER_ID='{user_id}' ORDER BY CREATE_TIME desc;"
                token_result = db_obj.get_data_by_sql(sql=token_sql)
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        read_data = Yaml(filepath.OPENVIPINFOBYDB, 0)
        db_name = filepath.CONF.get('advanced', 'pro_post_db')
        query_datas = read_data.allQuery
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE USER_ID='{user_id}' ORDER BY CREATE_TIME desc;"
                # token_result = \
                # cloud.get_data_by_sql(filepath.CONF.get('advanced', 'example'), db_name, token_sql)["data"]["rows"]
    if not len(token_result):
        logger.info(f"未查询到用户【{user_id}】的订单信息！")
        return False
    return token_result


@util.catch_exception
@util.retry_fun
@allure.step("修改用户【{user_id}】的优惠券可用车牌为【{carNo}】")
def modify_vip_lpn(user_id, carNo):
    read_data = Yaml(filepath.MODIFYLPN, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["lpn"] = carNo
            res = request.request(method=method, url=url, params=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 5000 and "不是会员" in result_dic["message"]:
                logger.info("修改会员优惠券可用车牌失败，用户还不是会员！")
                return False
            elif result_dic["code"] != 2000:
                raise Exception(logger.error(f"修改会员优惠券可用车牌出错！，错误返回为【{result_dic}】"))
            else:
                logger.info(f"修改用户【{user_id}】会员优惠券可用车牌为【{carNo}】成功！")
                return True


@util.catch_exception
@util.retry_fun
@allure.step("通过连接数据库查询用户【{user_id}】的信用分")
def get_score_db(user_id):
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.GETCREDITSCOREBYDB, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE user_id='{user_id}' and score_type = '1' order by create_time desc;"
                token_result = db_obj.get_data_by_sql(sql=token_sql)
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        read_data = Yaml(filepath.GETCREDITSCOREBYDB, 0)
        db_name = filepath.CONF.get('advanced', 'pro_post_db')
        query_datas = read_data.allQuery
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE user_id='{user_id}' and score_type = '1' order by create_time desc;"
                # token_result = \
                # cloud.get_data_by_sql(filepath.CONF.get('advanced', 'example'), db_name, token_sql)["data"]["rows"]
    if not len(token_result):
        logger.info(f"未查询到用户【{user_id}】的信用分信息！")
        return False
    return token_result


@util.catch_exception
@util.retry_fun
@allure.step("通过速停车接口得到用户【{user_id}】的信用分")
def get_score(user_id):
    read_data = Yaml(filepath.GETCREDITSCORE, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            res = request.request(method=method, url=url, params=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                if not result_dic["data"]["score"]:
                    logger.info(f"查询用户【{user_id}】的信用分为空")
                    return False
                else:
                    logger.info(f"查询用户【{user_id}】的信用分为{result_dic['data']['score']}")
                    return result_dic['data']['score']
            else:
                raise Exception(logger.error("查询用户信用分出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("检查【{user_id}】的信用分变化")
def check_user_score(user_id, expect_score, timeout=20):
    endtime = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < endtime:
        api_score = get_score(user_id)
        db_score = get_score_db(user_id)[0][0]
        if api_score == expect_score and db_score == expect_score:
            logger.info(f"校验用户【{user_id}】信用分数据变化成功！！")
            return True
        else:
            time.sleep(2)
    logger.info(f"超过{timeout}s,信用分仍未变化，校验失败！！！")
    return False


@util.catch_exception
@util.retry_fun
@allure.step("通过速停车接口更改用户【{user_id}】的后付费状态")
def change_postpaid_status(user_id):
    read_data = Yaml(filepath.CHANGEPOSTPAIDSTATUS, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            res = request.request(method=method, url=url, params=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"更改用户【{user_id}】的后付费状态成功！")
            else:
                raise Exception(logger.error(f"更改用户【{user_id}】的后付费状态出错！出错原因为【{result_dic}】"))


@util.catch_exception
@util.retry_fun
@allure.step("通过速停车接口将用户【{user_id}】的后付费状态置为失效")
def set_postpaid_to_failure(user_id):
    read_data = Yaml(filepath.SETPOSTPAIDFAILURE, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            res = request.request(method=method, url=url, params=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"将用户【{user_id}】的后付费状态置为失效成功！")
            else:
                raise Exception(logger.error(f"将用户【{user_id}】的后付费状态置为失效出错！出错原因为【{result_dic}】"))


@util.catch_exception
@util.retry_fun
@allure.step("通过速停车接口将用户【{user_id}】的后付费用户置为旧用户")
def set_postpaid_to_old(user_id):
    read_data = Yaml(filepath.SETPOSTPAIDUSERTOOLD, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["userId"] = user_id
            res = request.request(method=method, url=url, params=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"将用户【{user_id}】的后付费用户置为旧用户成功！")
            else:
                raise Exception(logger.error(f"将用户【{user_id}】的后付费用户置为旧用户出错！出错原因为【{result_dic}】"))


@util.catch_exception
@util.retry_fun
@allure.step("通过连接数据库查询用户【{user_id}】的后付费额度、状态信息")
def get_postpaid_info_db(user_id):
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.GETPOSTPAIDINFOBYBD, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE user_id='{user_id}'order by create_time desc;"
                token_result = db_obj.get_data_by_sql(sql=token_sql)
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        read_data = Yaml(filepath.GETPOSTPAIDINFOBYBD, 0)
        db_name = filepath.CONF.get('advanced', 'pro_post_db')
        query_datas = read_data.allQuery
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE user_id='{user_id}'order by create_time desc;"
                # token_result = \
                # cloud.get_data_by_sql(filepath.CONF.get('advanced', 'example'), db_name, token_sql)["data"]["rows"]
    if not len(token_result):
        logger.info(f"未查询到用户【{user_id}】的后付费信息！")
        return False
    return token_result


@util.catch_exception
@util.retry_fun
@allure.step("检查用户【{user_id}】的后付费额度和状态变化")
def check_user_postpaid(user_id, expect_limit, expect_status, timeout=10):
    endtime = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < endtime:
        api_res = get_postpaid_info(user_id)
        db_res = get_postpaid_info_db(user_id)
        api_status = api_res["data"]["onState"]
        api_limit = api_res["data"]["creditLimit"]
        db_status = True if db_res[0][2] == 2 else False
        db_limit = db_res[0][1]
        if api_limit == expect_limit and db_limit == expect_limit and api_status == expect_status and db_status == expect_status:
            logger.info(f"校验用户【{user_id}】的后付费额度和状态变化成功！！")
            return True
        else:
            time.sleep(2)
    logger.info(f"超过{timeout}s,后付费额度和状态变化仍校验失败！！！，接口数据为【{api_res}】, 数据库数据为【{db_res}】")
    return False


@util.catch_exception
@util.retry_fun
@allure.step("通过连接数据库查询用户【{user_id}】的后付费变更信息")
def get_postpaid_change_info_db(user_id):
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    user_postpaid_id = get_postpaid_info_db(user_id)[0][0]
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.GETPOSTPAIDCHANGEINFO, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE user_postpaid_id='{user_postpaid_id}'order by id desc;"
                token_result = db_obj.get_data_by_sql(sql=token_sql)
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        read_data = Yaml(filepath.GETPOSTPAIDCHANGEINFO, 0)
        db_name = filepath.CONF.get('advanced', 'pro_post_db')
        query_datas = read_data.allQuery
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE user_postpaid_id='{user_postpaid_id}'order by id desc;"
                # token_result = \
                # cloud.get_data_by_sql(filepath.CONF.get('advanced', 'example'), db_name, token_sql)["data"]["rows"]
    if not len(token_result):
        logger.info(f"未查询到用户【{user_id}】的后付费变更信息！")
        return False
    return token_result


@util.catch_exception
@util.retry_fun
@allure.step("通过用户【{user_id}】token,得到城市【{cityId}】,后付费车场状态为【{enablePostPaid}】的车场列表")
def get_postpaid_park_list(user_id, cityId, enablePostPaid):
    """
    增加后付费车辆
    :param user_id:
    :param carNo:车牌
    """
    read_data = Yaml(filepath.POSTPAIDPARKLIST, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["cityId"] = cityId
            request_data["enablePostPaid"] = enablePostPaid
            request_data = json.dumps(request_data)
            res = request.request(method=method, url=url, data=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"查询后付费车场列表成功")
                return result_dic["data"]
            else:
                raise Exception(logger.error("调用查询后付费车场列表接口出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("通过用户【{user_id}】token,得到经纬度为【{latitude}，{longitude}】的寻找车场列表")
def get_find_park_list(user_id, latitude, longitude):
    """
    增加后付费车辆
    :param user_id:
    :param carNo:车牌
    """
    read_data = Yaml(filepath.FINDPARKINGLOTS, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["latitude"] = latitude
            request_data["longitude"] = longitude
            request_data = json.dumps(request_data)
            res = request.request(method=method, url=url, data=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"查询寻找车场列表成功")
                return result_dic["data"]
            else:
                raise Exception(logger.error(f"调用查询寻找车场列表接口出错！，出错原因为【{result_dic}】"))


@util.catch_exception
@util.retry_fun
@allure.step("通过用户【{user_id}】token,得到车场banner展示列表")
def get_banner_park_list(user_id, cityId, enablePostPaid, keyword):
    """
    增加后付费车辆
    :param user_id:
    :param carNo:车牌
    """
    read_data = Yaml(filepath.BANNERPARKINGLOTS, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["cityId"] = cityId
            request_data["enablePostPaid"] = enablePostPaid
            request_data["keyword"] = keyword
            request_data = json.dumps(request_data)
            res = request.request(method=method, url=url, data=request_data, headers=headers, timeout=60)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                logger.info(f"查询寻找车场列表成功")
                return result_dic["data"]["pageResult"]["records"]
            else:
                raise Exception(logger.error(f"调用查询寻找车场列表接口出错！，出错原因为【{result_dic}】"))


def get_pika_data(key: str, env: str = "test") -> dict:
    """
    得到pika数据
    :param key: 需要查询的key
    :param env: 环境 test/prod 默认test
    :return:
    """
    read_data = Yaml(filepath.GETPIKADATA, 0)  # 要区分请求环境，使用0来解析yaml
    url = read_data.url
    domain = "https://biopen-test.keytop.cn/" if env == "test" else "https://biopen.keytop.cn/"
    url = urljoin(domain, url)
    datas = read_data.allData
    headers = read_data.headers
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["key"] = key
            res = request.get(url=url, params=request_data, headers=headers)
            result_dic = res.json()
            if result_dic["code"] == 200 and result_dic["data"]:
                return eval(result_dic["data"])
            else:
                logger.error(f"❌ 获取pika数据接口失败！！！错误为【{result_dic}】")
                return {}


def update_pika_data(key, value, env="test"):
    """
    得到pika数据
    :param key: 需要修改的key
    :param value: 修改值
    :param env: 环境 test/prod 默认test
    :return:
    """
    read_data = Yaml(filepath.UPDATEPIKADATA, 0)  # 要区分请求环境，使用0来解析yaml
    url = read_data.url
    domain = "https://biopen-test.keytop.cn/" if env == "test" else "https://biopen.keytop.cn/"
    url = urljoin(domain, url)
    datas = read_data.allData
    headers = read_data.headers
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2].get("request_data")
            request_data["key"] = key
            request_data["value"] = json.dumps(value)
            res = request.post(url=url, data=json.dumps(request_data), headers=headers)
            result_dic = res.json()
            if result_dic["code"] == 2000:
                return True
            else:
                logger.error(f"❌ 修改pika数据接口失败！！！错误为【{result_dic}】")
                return False


def process_user_portrait(key: str, env, **kwargs):
    """
    处理并修改的pika数据
    :param key:
    :param env:
    :param kwargs: 需修改的键值对
    :return:
    """
    key_map = {"inCommonUseLot": "l", "retainedSituation": "s"}
    pika_data = get_pika_data(key, env)
    if not pika_data:
        res = {
            "data": f"查询【{env}】环境用户【{key.split('UP:')[1]}】用户画像数据为空!!",
            "resultCode": 500
        }
        return False, res
    for i, v in kwargs.items():
        if i == "inCommonUseLot" and v != "":
            v = v.replace("\\", "")
        pika_data[key_map[i]] = v
    update_res = update_pika_data(key, pika_data, env)
    if not update_res:
        res = {
            "data": f"修改【{env}】环境用户【{key.split('UP:')[1]}】用户画像数据失败!!"
        }
        return False, res
    res = {
        "data": f"修改【{env}】环境用户【{key.split('UP:')[1]}】用户画像数据成功!!"
    }
    return True, res


if __name__ == '__main__':
    # car_No = filepath.CONF.get('car', 'special_carNo')
    car_No = filepath.CONF.get('car', 'after_carNo')
    # user_id = filepath.CONF.get('car', 'special_user')
    user_id = filepath.CONF.get('car', 'after_user')
    lot_id = filepath.CONF.get("advanced", "lotId")
    # wx_id = filepath.CONF.get('car', 'wx_appId')
    # # print(get_user_info_by_mms("8430572e622d4319ad5d8ac0b2e0b376"))
    # add_OnPark("川AS8888", lot_id, "8430572e622d4319ad5d8ac0b2e0b376", wx_id)
    # del_OnPark("川AS8888", lot_id)
    # print(check_postpaid_rights("川AS8888", lot_id, "8430572e622d4319ad5d8ac0b2e0b376", wx_id))
    # del_vip_black_list(user_id, car_No)
    # check_vip_black_list(user_id, car_No)
    # edit_disable_lot(user_id, lot_id, 2)
    # open_old_vip("川AA8888", "204350188868616197")
    # check_vip("204350188868616197")
    # close_vip("204350188868616197")
    # check_vip("204350188868616197")
    # print(open_vip_v2("川AA8888", "204350188868616197", "05", "01"))
    # print(get_vip_info_v2("204350188868616197", "e1ebb57e90004791a9ad996379c8a5b3"))
    # check_vip("204350188868616197")
    # close_vip("204350188868616197")
    # check_vip("204350188868616197")
    # print(get_vip_info("221473484736737586"))
    # check_send_plan("01", "204350188868616197")
    # print(get_postpaid_info("204350188868616197"))
    # print(json.loads(get_wx_token()))
    # print(open_vip_v2("川AA8888", "204350188868616197", "05", "01"))
    # check_vip("204350188868616197")
    # modify_vip_lpn("204350188868616197", "川AHJH888")
    # print(get_score_db("204350188868616197")[0][0])
    # print(get_score("204350188868616197"))
    # print(check_user_score("204350188868616197", 275))
    # change_postpaid_status("90127049743683904")
    # print(get_postpaid_info_db("90127049743683904"))
    # check_user_postpaid("90127049743683904", 3000, True)
    # print(get_postpaid_change_info_db("204350188868616197"))
    # print(get_postpaid_info("204350188868616197"))
    # print(get_user_info("90127049743683904"))
    # bind_car_no("川AV8888", "90127049743683904")
    # print(get_postpaid_park_list("204350188868616197", "235", True))
    # get_disable_lot_list("90127049743683904")
    # set_postpaid_to_old("204350188868616197")
    # data = get_pika_data("UP:203905054163279872")
    # print(data)
    # test_data = "{\"v1\":[{\"lot_cnt\":46,\"lot_id\":\"996000386\",\"lot_nature_code\":\"16\"},{\"lot_cnt\":1,\"lot_id\":\"6963\",\"lot_nature_code\":\"00\"}],\"v2\":[{\"cash_sum\":2461,\"lot_id\":\"996000386\",\"lot_nature_code\":\"16\"},{\"cash_sum\":1200,\"lot_id\":\"6963\",\"lot_nature_code\":\"00\"}],\"v3\":[{\"lot_cnt\":18,\"lot_id\":\"996000386\",\"lot_nature_code\":\"16\"}],\"v4\":[{\"lot_cnt\":32,\"lot_id\":\"996000386\",\"lot_nature_code\":\"16\"}]}"
    # print(type(test_data))
    # data['l'] = test_data
    # print(data['l'])
    # update_pika_data("UP:203905054163279872", data)
    # data = '{\\"v1\\":[{\\"lot_cnt\\":46,\\"lot_id\\":\\"996000386\\",\\"lot_nature_code\\":\\"16\\"},{\\"lot_cnt\\":1,\\"lot_id\\":\\"6963\\",\\"lot_nature_code\\":\\"00\\"}],\\"v2\\":[{\\"cash_sum\\":2461,\\"lot_id\\":\\"996000386\\",\\"lot_nature_code\\":\\"16\\"},{\\"cash_sum\\":1400,\\"lot_id\\":\\"6963\\",\\"lot_nature_code\\":\\"00\\"}],\\"v3\\":[{\\"lot_cnt\\":18,\\"lot_id\\":\\"996000386\\",\\"lot_nature_code\\":\\"16\\"}],\\"v4\\":[{\\"lot_cnt\\":32,\\"lot_id\\":\\"996000386\\",\\"lot_nature_code\\":\\"16\\"}]}}'
    # print(json.dumps(data.replace("\\", "")))
    json = '{\"v1\":[{\"lot_cnt\":46,\"lot_id\":\"996000386\",\"lot_nature_code\":\"16\"},{\"lot_cnt\":1,\"lot_id\":\"6963\",\"lot_nature_code\":\"00\"}],\"v2\":[{\"cash_sum\":2461,\"lot_id\":\"996000386\",\"lot_nature_code\":\"16\"},{\"cash_sum\":1200,\"lot_id\":\"6963\",\"lot_nature_code\":\"00\"}],\"v3\":[{\"lot_cnt\":18,\"lot_id\":\"996000386\",\"lot_nature_code\":\"16\"}],\"v4\":[{\"lot_cnt\":32,\"lot_id\":\"996000386\",\"lot_nature_code\":\"16\"}]}'
    print(eval(json))

    # "{\"v1\":[{\"lot_cnt\":7,\"lot_id\":\"769013704\",\"lot_nature_code\":\"00\"},{\"lot_cnt\":1,\"lot_id\":\"9078\",\"lot_nature_code\":\"16\"}],\"v2\":[{\"cash_sum\":14,\"lot_id\":\"769013704\",\"lot_nature_code\":\"00\"},{\"cash_sum\":1,\"lot_id\":\"9078\",\"lot_nature_code\":\"16\"}],\"v4\":[{\"lot_cnt\":7,\"lot_id\":\"769013704\",\"lot_nature_code\":\"00\"}]}"