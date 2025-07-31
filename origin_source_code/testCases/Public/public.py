# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: public.py
@Description: 公用函数校验
@Author: huangjunhao
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
@time:2021/04/29
===================================
"""
import datetime
import hashlib
import json
import traceback
import uuid
from urllib import parse
import time
from common.db_tool import db_obj, DbTool
import allure
from common import filepath, util, entrances
from common.configLog import logger
# from common.getCloudDataByFormal import cloud
from common.processYaml import Yaml
from common.request import request
from common.util import get_data_from_json_file, save_response_to_json_file
from testCases.Public.mobile import post_local_rights


@util.catch_exception
@allure.step("上线设备【{clientIps}】")
def loopOnLine(clientIps: list, service_ip):
    """
    设备上线失败重试
    parameter:
        clientIps: 设备ip列表

    return:
        devices: 全部dspclient对象字典

    """
    devices = dict()
    logger.info("【正在上线全部设备】")
    for client_ip in clientIps:
        device = entrances.on_Line(client_ip, service_ip)
        devices[client_ip] = device
        # logger.info("【devices长度：%s！, clientIps长度: %s】", len(devices), len(clientIps))
    if len(devices) == len(clientIps):
        logger.info("【全部设备上线成功！】")
    return devices


@util.catch_exception
@allure.step("下线设备【{devices}】")
def offAllLine(devices):
    """
    下线全部设备
    parameter:
        devices: 全部dspclient对象字典
    return:
    """
    logger.info("【正在下线全部设备】")
    for client_ip, device in devices.items():
        entrances.off_Line(client_ip, device)
    logger.info("【✔ 下线全部设备完成】")


@util.catch_exception
@allure.step("{plateno}压地感")
def car_in_out(device, plateno, serial=None, isetc=None, etcno=None, color=None, recog=None, carstyle=None, dataType=None, openType=None, over_msg='Z', timeout=10):
    """
    模拟压地感
    parameter:
        device: dspclient对象
        plateno: 车牌号码
        serial: 序列号
        isetc: 默认为None
        etcno: 卡票号
        color: 颜色
        recog: 识别度
        carstyle: 默认为None
        dataType: 默认为None
        openType: 默认为None
        over_msg: 结束指令
        timeout: 超时时间
    return:
    """

    serial = serial if serial else filepath.CONF.get('advanced', 'serial')
    isetc = isetc if isetc else int(filepath.CONF.get('advanced', 'isetc'))
    etcno = etcno if etcno else filepath.CONF.get('advanced', 'etcno')
    color = color if color else int(filepath.CONF.get('advanced', 'color'))
    carstyle = carstyle if carstyle else int(filepath.CONF.get('advanced', 'carStyle'))
    recog = recog if recog else int(filepath.CONF.get('advanced', 'recogIn'))
    dataType = dataType if dataType else int(filepath.CONF.get('advanced', 'dataType'))
    openType = openType if openType else int(filepath.CONF.get('advanced', 'openType'))
    device.send_img(serial, plateno, carstyle, isetc, etcno, recog,
                  color, dataType, openType, i_cap_time=datetime.datetime.now())
    device.find_over(over_msg, timeout)


@util.catch_exception
@util.retry_fun
@allure.step("校验【{car_No}】的入场记录表")
def check_car_comes(car_No, timeout=5):
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    read_data = Yaml(filepath.CARCOMES, 1)
    query_data = read_data.allQuery
    table_name_list = query_data[0][2].get("tableName").split("_")
    table_name_list.insert(1, f"{filepath.CONF.get('advanced', 'lotId')}")
    table_name = "_".join(table_name_list)
    keyword_list = query_data[0][2].get("keyword")
    cloud_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE carNo = '{car_No}';"
    endtime = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < endtime:
        # 测试环境检查
        if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
                cloud_result = db_obj.get_data_by_sql(sql=cloud_sql)
                if len(cloud_result):
                    break
                else:
                    time.sleep(0.5)
        # 正式环境检查
        elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
            pass
            # cloud_result = cloud.select(lot_id=filepath.CONF.get('advanced', 'lotId'), sql=cloud_sql)["data"]["rows"]
            # if len(cloud_result):
            #     break
            # else:
            #     time.sleep(0.5)
    if not len(cloud_result):
        logger.info(f"✔ 【{car_No}】车辆无入场记录")
        return True
    elif len(cloud_result) > 0:
        logger.info(f"✔ 【{car_No}】车辆存在入场记录")
        return False
    else:
        raise Exception(logger.error("查询车场云端入场表记录出错！！！"))
    # if len(cloud_result) > 1:
    #     raise Exception(logger.error(f"{query_data[0][1].get('ps')}，车辆后付费信息不唯一"))
    # elif len(cloud_result) == 0:
    #     logger.info("× 此次校验失败 未查找到车场云端授权，此次入场未进行后付费授权")
    #     if caseNo:
    #         post_local_rights(caseNo, "false")
    #     return False
    # elif cloud_result[0][0] == 0 and cloud_result[0][2] != file_code:
    #     logger.info(f"✔ 此次校验成功 车场云端授权校验成功，存储验证code为【{file_code}】，云端code为【{cloud_result[0][2]}】")
    #     return True
    # elif cloud_result[0][0] == 0 and cloud_result[0][2] == file_code:
    #     logger.info(f"× 此次校验失败 车场云端授权为上一次的授权，存储验证code为【{file_code}】，云端code为【{cloud_result[0][2]}】")
    #     if caseNo:
    #         post_local_rights(caseNo, "false")
    #     return False
    # else:
    #     if caseNo:
    #         post_local_rights(caseNo, "false")
    #     raise Exception(logger.error("此次车场云端授权校验出错！"))


@util.catch_exception
@util.retry_fun
@allure.step("校验【{car_No}】的云端授权")
def check_cloud_rights(car_No, timeout, caseNo=""):
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    read_data = Yaml(filepath.CLOUDRIGHTS, 1)
    query_data = read_data.allQuery
    table_name_list = query_data[0][2].get("tableName").split("_")
    table_name_list.insert(1, f"{filepath.CONF.get('advanced', 'lotId')}")
    table_name = "_".join(table_name_list)
    keyword_list = query_data[0][2].get("keyword")
    cloud_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE carNo = '{car_No}';"
    endtime = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < endtime:
        # 测试环境检查
        if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
                cloud_result = db_obj.get_data_by_sql(sql=cloud_sql)
                if len(cloud_result) and cloud_result[0][2] != get_data_from_json_file(car_No):
                    break
                else:
                    time.sleep(0.5)
        # 正式环境检查
        elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
            pass
            # cloud_result = cloud.select(lot_id=filepath.CONF.get('advanced', 'lotId') , sql=cloud_sql)
            # if len(cloud_result["data"]["rows"]) and cloud_result["data"]["rows"][0][2] != get_data_from_json_file(car_No):
            #     cloud_result = cloud_result["data"]["rows"]
            #     break
            # else:
            #     cloud_result = cloud_result["data"]["rows"]
            #     time.sleep(0.5)
    file_code = get_data_from_json_file(car_No)
    if len(cloud_result) > 1:
        raise Exception(logger.error(f"{query_data[0][1].get('ps')}，车辆后付费信息不唯一"))
    elif len(cloud_result) == 0:
        logger.info("× 此次校验失败 未查找到车场云端授权，此次入场未进行后付费授权")
        if caseNo:
            post_local_rights(caseNo, "false")
        return False
    elif cloud_result[0][0] == 0 and cloud_result[0][2] != file_code:
        logger.info(f"✔ 此次校验成功 车场云端授权校验成功，存储验证code为【{file_code}】，云端code为【{cloud_result[0][2]}】")
        return True
    elif cloud_result[0][0] == 0 and cloud_result[0][2] == file_code:
        logger.info(f"× 此次校验失败 车场云端授权为上一次的授权，存储验证code为【{file_code}】，云端code为【{cloud_result[0][2]}】")
        if caseNo:
            post_local_rights(caseNo, "false")
        return False
    else:
        if caseNo:
            post_local_rights(caseNo, "false")
        raise Exception(logger.error("此次车场云端授权校验出错！"))


@util.catch_exception
@allure.step("得到【{car_No}】的场端信息")
def get_local_rights_info(car_No):
    """
    得到场端信息
    :param car_No:
    :param timeout:
    """
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    car_No = car_No
    port = filepath.CONF.get('advanced', 'ServerDBPort')
    server_ip = "http://" + server_ip + f":{port}"
    read_data = Yaml(filepath.LOCALRIGHTS, 0)
    url = parse.urljoin(server_ip, read_data.url)
    headers = read_data.headers
    query_data = read_data.allQuery
    table_name = query_data[0][2].get("tableName")
    keyword_list = query_data[0][2].get("keyword")
    local_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE carNo = '{car_No}';"
    data = {
        "db": filepath.CONF.get('advanced', 'DBName'),
        "sql": local_sql
    }
    res = request.post(url=url, data=json.dumps(data), headers=headers)
    result_dic = res.json()
    util.checkResultCode(result_dic)
    return result_dic


@util.catch_exception
@allure.step("校验【{car_No}】的场端授权")
def check_local_rights(car_No, timeout, caseNo=""):
    """
    场端授权校验
    :param car_No:
    :param timeout:
    :return:
    """
    endtime = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < endtime:
        result_dic = get_local_rights_info(car_No)
        if len(result_dic.get("data")) and result_dic["data"][0][2] != get_data_from_json_file(car_No):
            break
        else:
            time.sleep(0.5)
    file_code = get_data_from_json_file(car_No)
    if len(result_dic.get("data")) > 1:
        raise Exception(logger.error("查询车场本地端，车辆后付费信息不唯一"))
    elif len(result_dic.get("data")) == 0:
        logger.info("× 此次校验失败 未查找到车场场端授权，此次入场未进行后付费授权")
        if caseNo:
            post_local_rights(caseNo, "false")
        return False
    elif result_dic.get("data")[0][0] == 0 and result_dic.get("data")[0][2] != file_code:
        logger.info(f"✔ 此次校验成功 车场本地端授权校验成功，存储验证code为【{file_code}】，场端同步code为【{result_dic.get('data')[0][2]}】")
        save_response_to_json_file(car_No, result_dic.get("data")[0][2])
        return True
    elif result_dic.get("data")[0][0] == 0 and result_dic.get("data")[0][2] == file_code:
        logger.info(f"× 此次校验失败 车场场端授权为上一次的授权，存储验证code为【{file_code}】，场端同步code为【{result_dic.get('data')[0][2]}】")
        if caseNo:
            post_local_rights(caseNo, "false")
        return False
    else:
        if caseNo:
            post_local_rights(caseNo, "false")
        raise Exception(logger.error("此次车场场端授权校验出错！"))


@util.catch_exception
@allure.step("登录【{lot_id}】的统一平台")
def login(lot_id):
    """
    统一平台登录
    parameter:
        lot_id: 车场id
    return:
    """
    logger.info("【正在进行统一平台登录】")
    read_data = Yaml(filepath.LOGIN, 1)
    url, headers, allData = util.get_parameter(read_data, lot_id)
    for datas in allData:
        if datas[0]['id'] == 1:
            sec = datas[1]['ps']
            data = datas[2]
    res = request.post(url=url, headers=headers, data=json.dumps(data), timeout=5)
    util.checkResultCode(res.json())
    kttoken = res.json()['data']['ktToken']
    logger.info("【✔ 统一平台登录完成】")
    return kttoken


@util.catch_exception
@allure.step("调用云端接口同步【{lot_id}】的云端场端信息")
def channel_send(kttoken, lot_id, ps_id):
    """
    直接通过通道调用云端接口
    parameter:
        kttoken: kttoken
        lot_id: 车场id
        ps_id: 测试用例id
    return:
    """
    read_data = Yaml(filepath.CHANNELSEND, 3)
    reqid = str(uuid.uuid1())
    url, headers, allData = util.get_parameter(read_data, lot_id, kttoken)
    for datas in allData:
        if datas[0]['id'] == ps_id:
            ps = datas[1]['ps']
            logger.info("【正在%s】" % ps)
            data = datas[2]
            data['reqId'] = reqid
            data['parkId'] = lot_id
            base_data = util.access_data_new(data, lot_id, reqid)
    res = request.post(url=url, headers=headers, data=json.dumps(base_data), timeout=5)
    util.checkResultCode(res.json())
    logger.info("【✔ %s完成】" % ps)


@allure.step("得到用户【{user_id}】的token")
def get_user_token(user_id):
    """
    :return: 从数据库得到用户的token
    """
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.USERTOKEN, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                user_id = user_id
                token_sql = f"SELECT {','.join(keyword_list)} FROM {table_name} WHERE pp_user_id='{user_id}';"
                token_result = db_obj.get_data_by_sql(sql=token_sql)
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        read_data = Yaml(filepath.USERTOKEN, 0)
        db_name = filepath.CONF.get('advanced', 'pro_pla_db')
        query_datas = read_data.allQuery
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                sec = query_data[1]['ps']
                table_name = query_data[2].get("tableName")
                keyword_list = query_data[2].get("keyword")
                user_id = user_id
                token_sql = f"SELECT {','.join(keyword_list)} FROM {db_name}.{table_name} WHERE pp_user_id='{user_id}';"
                # token_result = cloud.get_data_by_sql(filepath.CONF.get('advanced', 'example'), db_name, token_sql)["data"]["rows"]
    return token_result[0][0]


@util.catch_exception
@util.retry_fun
@allure.step("得到用户【{user_id}】的相关信息")
def get_user_info(user_id):
    read_data = Yaml(filepath.USERINFO, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = json.dumps(query_data[2].get("request_data"))
            res = request.request(method=method, url=url, data=request_data, headers=headers)
            result_dic = res.json()
            if result_dic["code"] != 2000:
                raise Exception(logger.error("查询用户信息接口出错！"))
            else:
                logger.info(f"✔ 查询用户【{user_id}】信息成功！")
            return result_dic


@util.catch_exception
@util.retry_fun
@allure.step("通过中台接口，得到用户【{user_id}】的相关信息")
def get_user_info_by_mms(user_id, env="test"):
    yaml_data = process_mms(filepath.USERINFOBYMMS, env)
    yaml_data["request_data"]["ppUserId"] = user_id
    yaml_data["request_data"] = json.dumps(yaml_data.get("request_data"), ensure_ascii=False).encode("utf-8")
    res = request.mms_request(yaml_data)
    result_dic = res.json()
    if result_dic["code"] != 2000:
        raise Exception(logger.error("查询中台用户信息接口出错！"))
    else:
        logger.info(f"✔ 调用中台接口，查询用户【{user_id}】用户信息成功！")
    return result_dic


@util.catch_exception
@allure.step("处理中台的yaml文件")
def process_mms(yaml_file, env):
    """
    处理中台yaml文件
    :param env: 环境
    :param yaml_file:
    :return:
    """
    if env == "test":
        mms = {
            "host-address": "https://mms-test.keytop.cn",
            "app-id": "cn.keytop.stc.pp.cp-region",
            "app-key": "6182484814727F1504B6B1E328E576F1",
            "route-type": "GATE_WAY",
            "connectTimeout": 22000,
            "socketTimeout": 22000
        }
    else:
        mms = {
            "host-address": "http://mms.keytop.cn",
            "app-id": "cn.keytop.stc.cp.cp",
            "app-key": "a14db16b9ce82d8537e526baba5708ab",
            "route-type": "SERVICE_MESH",
            "connectTimeout": 12000,
            "socketTimeout": 12000
        }
    read_data = Yaml(yaml_file, 0)
    timestamp = time.mktime(datetime.datetime.now().timetuple())
    yaml_data = read_data.read_yaml()
    headers = read_data.headers
    method = yaml_data["method"]
    sid = "".join((yaml_data.get("server"), yaml_data.get("url")))
    headers["sid"] = sid
    headers["appId"] = mms["app-id"]
    headers["timestamp"] = str(int(timestamp))
    dt = sid + headers['version'] + str(int(timestamp)) + mms["app-key"]
    sign = hashlib.sha256()
    sign.update(dt.encode('utf-8'))
    headers["sign"] = sign.hexdigest()
    request_data = read_data.allData[0][2]["request_data"]
    url = mms["host-address"]
    data = request_data
    timeOut = 60
    return {"url": url, "headers": headers, "request_data": data, "timeOut": timeOut, "method": method}


@util.catch_exception
@util.retry_fun
@allure.step("得到【{user_id}】的后付费信息")
def get_postpaid_info(user_id):
    """
    得到后付费设置信息
    :param user_id:
    :return:
    """
    read_data = Yaml(filepath.POSTSETTING, 5)
    url = read_data.url
    method = read_data.method
    datas = read_data.allData
    headers = read_data.headers
    if not headers.get("accessToken"):
        headers["accessToken"] = get_user_token(user_id)
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = json.dumps(query_data[2].get("request_data"))
            res = request.request(method=method, url=url, data=request_data, headers=headers, timeout=10)
            result_dic = res.json()
            if result_dic["code"] != 2000:
                raise Exception(logger.error("查询后付费配置信息接口出错！"))
            else:
                logger.info(f"✔ 查询用户【{user_id}】后付费配置信息成功！")
            return result_dic


@util.catch_exception
@util.retry_fun
@allure.step("增加【{user_id}】进入【{ps_id}】类型的白名单||1：可被邀请、2：不可被邀请")
def add_flow_whitelist(ps_id, user_id):
    """
    增加用户白名单
    :param ps_id: 用例id 1增加可被邀请 2增加不可被邀请
    :param user_id:
    """
    read_data = Yaml(filepath.ADDWHITELIST, 5)
    headers = read_data.headers
    headers["app-id"] = filepath.CONF.get("postpay", "app-id")
    headers["secret-key"] = filepath.CONF.get("postpay", "secret-key")
    url = read_data.url
    datas = read_data.allData
    method = read_data.method
    white_id = ""
    for query_data in datas:
        if query_data[0]['id'] == ps_id:
            sec = query_data[1]['ps']
            query_data[2]['request_data']["operator"] = sec
            query_data[2]['request_data']["userId"] = user_id
            if sec == "自动化添加可被邀请白名单":
                white_id = filepath.CONF.get("car", "invited_id")
            elif sec == "自动化添加不可被邀请白名单":
                white_id = filepath.CONF.get("car", "not_invited_id")
            query_data[2]['request_data']["flowId"] = white_id
            res = request.request(url=url, data=json.dumps(query_data[2]['request_data']), method=method,
                                  headers=headers)
            result_dic = res.json()
            if result_dic["code"] == 5000 and result_dic["message"] == "此用户已添加此类型白名单":
                raise Exception(logger.error("用户已添加此类型白名单,无法重复添加"))
            elif result_dic["code"] != 2000:
                raise Exception(logger.error("添加用户白名单信息接口出错！"))
            else:
                logger.info(f"✔ 用户【{user_id}】成功添加入白名单【{white_id}】中！")


@util.catch_exception
@util.retry_fun
@allure.step("将【{user_id}】从【{ps_id}】类型的白名单中移除||1：可被邀请、2：不可被邀请")
def del_flow_whitelist(ps_id, user_id):
    """
    删除白名单
    :param ps_id: 用例id 1删除可被邀请 2删除不可被邀请
    :param user_id:
    """
    read_data = Yaml(filepath.DELWHITELIST, 5)
    headers = read_data.headers
    headers["app-id"] = filepath.CONF.get("postpay", "app-id")
    headers["secret-key"] = filepath.CONF.get("postpay", "secret-key")
    url = read_data.url
    datas = read_data.allData
    method = read_data.method
    white_id = ""
    for query_data in datas:
        if query_data[0]['id'] == ps_id:
            sec = query_data[1]['ps']
            if sec == "删除可被邀请白名单":
                white_id = filepath.CONF.get("car", "invited_id")
            elif sec == "删除不可被邀请白名单":
                white_id = filepath.CONF.get("car", "not_invited_id")
            white_list_info = query_flow_whitelist(white_id, user_id)
            query_data[2]['request_data']["id"] = white_list_info["data"]["records"][0]["id"]
            res = request.request(url=url, params=query_data[2]['request_data'], method=method,
                                  headers=headers)
            result_dic = res.json()
            if result_dic["code"] != 2000:
                raise Exception(logger.error("删除流量白名单接口出错！"))
            else:
                logger.info(f"成功删除用户【{user_id}】的流量白名单，白名单id为【{white_id}】")


@util.catch_exception
@util.retry_fun
@allure.step("分页查询白名单列表信息")
def query_flow_whitelist(flowId, user_id):
    """
    分页查询白名单列表信息
    :param flowId: 白名单流量id
    :param user_id:
    :return:
    """
    read_data = Yaml(filepath.QUERYWHITELIST, 5)
    headers = read_data.headers
    headers["app-id"] = filepath.CONF.get("postpay", "app-id")
    headers["secret-key"] = filepath.CONF.get("postpay", "secret-key")
    url = read_data.url
    datas = read_data.allData
    method = read_data.method
    for query_data in datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            query_data[2]['request_data']["flowId"] = flowId
            query_data[2]['request_data']["userId"] = user_id
            res = request.request(url=url, data=json.dumps(query_data[2]['request_data']), method=method,
                                  headers=headers)
            result_dic = res.json()
            white_id = result_dic["data"]["records"][0]["flowId"]
            if result_dic["code"] != 2000:
                raise Exception(logger.error("查询速停车管理车场列表信息接口出错！"))
            elif len(result_dic["data"]["records"]) == 0:
                raise Exception(logger.error(f"用户【{user_id}】未出于任何白名单下，请先添加白名单！"))
            elif int(white_id) != int(flowId):
                raise Exception(logger.error(f"用户【{user_id}】处于白名单【{white_id}】下，而非需要查询的白名单【{flowId}】！"))
            else:
                return result_dic


if __name__ == '__main__':
    from testCases.Public.car import check_user_group
    # get_user_info_by_mms("9b110a77b47646b895172dd200641f13")
    # print(get_user_token("c9ee7aab9de04fd48d45dd4ae85578e5"))
    # print(get_user_token("9b110a77b47646b895172dd200641f13"))
    # print(get_user_token("204350188868616197"))
    # print(get_user_token("8430572e622d4319ad5d8ac0b2e0b376"))

    # add_flow_whitelist(2, "9b110a77b47646b895172dd200641f13")
    # check_user_group("9b110a77b47646b895172dd200641f13")
    # del_flow_whitelist(2, "9b110a77b47646b895172dd200641f13")
    # add_flow_whitelist(1, "9b110a77b47646b895172dd200641f13")
    # check_user_group("9b110a77b47646b895172dd200641f13")
    # del_flow_whitelist(1, "9b110a77b47646b895172dd200641f13")
    # check_cloud_rights("川AV8888", 3)
    # print(get_user_token("204350188868616197"))
    # print(get_user_token("90127049743683904"))
    # print(process_mms(filepath.OWEBILLBYMMS))
    # print(login("280025535"))
    # check_car_comes("川AV8888")
    # login("9078")
    # login("280025535")
    # login("769013704")
    login("592011611")
