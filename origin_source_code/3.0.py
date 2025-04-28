# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: 3.0.py
@Description: 文件路径管理
@Author: huangjunhao
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
@time:2021/04/29
===================================
"""
import ast
import datetime
import os
import random
import re
import sqlite3
import traceback
from time import sleep
from urllib.parse import quote, urljoin

import flask
import json
from flask import jsonify, make_response, send_from_directory
import requests

from common import filepath
from common.configLog import logger
from common.dspClient import DspClient
from common.my_nacos import MyNaCosClient
from common.util import get_host_ip
from common.cp_console import query_order, get_cookie_test
from common.cp_console import refund
# from testCases.Api.check_tables import check_tables
# from testCases.Api import check_tables_new
from testCases.Api import check_tables_new
from testCases.Api.stc_api import get_user_token
from testCases.Public import car, park, public
from testCases.Public.public import login
import random
from flask import Flask, jsonify, request
from flasgger import Swagger, swag_from
import socket
server = flask.Flask(__name__)
my_nacos_client = MyNaCosClient()
# swagger_config = Swagger.DEFAULT_CONFIG
# swagger_config["title"] = "成都测试用接口"
# swagger_config["description"] = "目前包含出入车、模拟计费、获得微信token等"
# swagger_config["version"] = "1.0.0"
# swagger_config["host"] = get_host_ip()
# swagger_config = {
#     "headers": [
#         ],
#         "specs": [
#             {
#                 "endpoint": 'apispec_2',
#                 "route": '/apispec_2.json',
#                 "rule_filter": lambda rule: True,  # all in
#                 "model_filter": lambda tag: True,  # all in
#             }
#         ],
#     "static_url_path": "/flasgger_static",
#     # "static_folder": "static",  # must be set by user
#     "swagger_ui": True,
#     "specs_route": "/doc/"
# }
template_config = {
  "info": {
    "title": "成都测试用接口",
    "description": "目前包含出入车、模拟计费、获得微信token等",
    "version": "1.0.0",
    "host": get_host_ip()
  }
}
# Swagger(server, config=swagger_config)
Swagger(server, template=template_config)
# Swagger(server)
car_in_out_config = {"fail_count": 5, "wait_time": 10}
api_config = dict()


# 当服务配置发生变化
def config_update(args):
    global api_config
    # print("配置发生变化！！！")
    api_config = my_nacos_client.get_config_yaml(filepath.CONF.get("nacos", "api_data_id"),
                                                 filepath.CONF.get("nacos", "api_group"))
    # print('new data->', api_config)


def get_onPark(lotId, carNo, ktToken, StartTime="", EndTime=""):
    now = datetime.datetime.now()
    zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
    StartTime = zeroToday.strftime("%Y-%m-%d %H:%M:%S")
    EndTime = lastToday.strftime("%Y-%m-%d %H:%M:%S")
    data_dic = {"lotCode": lotId,
                "downloadId": "",
                "pageSize": 10,
                "currentPage": 1,
                "carNo": carNo,
                "comeTimeStart": StartTime,
                # "comeTimeStart": "2021/08/02 00:00:00",
                "totalCount": "0,",
                "comeTimeEnd": EndTime
                # "comeTimeEnd": "2021/08/02 23:59:59"
                }
    headers = {"content-type": "application/json", "kt-token": ktToken, "kt-lotcodes": lotId}
    if lotId in api_config.get("test_support_lotId"):
        url = api_config.get("car_come_domain").get("test")
    elif lotId in api_config.get("prod_support_lotId"):
        url = api_config.get("car_come_domain").get("prod")
    else:
        raise Exception(f"暂不支持车场【{lotId}】")
    res = requests.post(url=url, headers=headers,data=json.dumps(data_dic))
    if res.status_code != 200:
        raise Exception("查询在场接口出错！")
    return res.json()


@server.route('/get_wx_token', methods=['post'])
@swag_from(filepath.GETWXTOKENAPI)
def get_wx_token():
    """
    得到微信token api
    """
    data = json.loads(flask.request.data)
    wx_id = data.get("wx_id")
    if wx_id not in ('wxed9d3e6dc4a3704f', 'wx88f62889b30261ac'):
        res = {
            "data": "Not find %s wx_id" % wx_id,
            "resultCode": 500
        }
    else:
        wx_token_all = json.loads(car.get_wx_token())
        wx_token = wx_token_all.get(wx_id)
        if wx_token:
            res = {"data": {"token": wx_token.get("access_token"),
                            "expireTime": wx_token.get("expireTime")},
                   "resultCode": 200}
        else:
            res = {
                "data": f"from【{wx_id}】 get wx_token is null",
                "resultCode": 500
            }
    return jsonify(res)


@server.route('/device_On', methods=['post'])
@swag_from(filepath.DEVICEONAPI)
def device_On():
    """
    设备上线api
    """
    data = json.loads(flask.request.data)
    server_ip = data.get("server_ip") or "192.168.0.202"
    device_list = data.get("clientIps")
    if not device_list:
        res = {
            "data": "clientIps is []",
            "resultCode": 500
        }
    else:
        devices = public.loopOnLine(device_list, server_ip)
        # res = {
        #     "devices": devices
        # }
        # print(json.dumps(res))
        if len(devices) == len(device_list):
            res = {
                "data": f"所有设备上线成功!!",
                "resultCode": 200
            }
    return jsonify(res)
    # dsp_obj_in = DspClient(server_ip, 5001, device_ip, client_port=0)
    # dsp_obj_in.connect()


@server.route('/device_Off', methods=['post'])
@swag_from(filepath.DEVICEOFFAPI)
def device_Off():
    """
    设备下线api
    """
    data = json.loads(flask.request.data)
    server_ip = data.get("server_ip") or "192.168.0.202"
    device_list = data.get("clientIps")
    if not device_list:
        res = {
            "data": "clientIps is []",
            "resultCode": 500
        }

    devices = public.loopOnLine(device_list, server_ip)
    try:
        public.offAllLine(devices)
        res = {
            "data": f"所有设备下线成功!!",
            "resultCode": 200
        }
    except Exception as e:
        res = {
            "data": f"所有设备下线失败!!，失败信息为【{e}】",
            "resultCode": 500
        }

    return jsonify(res)


@server.route('/car_In', methods=['get'])
@swag_from(filepath.CARINAPI)
def car_In():
    """
    入车api
    """
    data = flask.request.args
    server_ip = data.get("server_ip") or "192.168.0.202"
    car_no = data.get("car_no") or ""
    lot_id = data.get("lot_id") or "996000386"
    car_color = data.get("car_color") or 3
    recognition = data.get("recognition") or 1000
    i_serial = data.get("i_serial") or random.randint(0, 999999999)
    # if not server_ip or not car_no:
    #     res = {
    #         "data": "Not find car_no",
    #         "resultCode": 500
    #     }
    if not server_ip:
        res = {
            "data": "Not find server_ip",
            "resultCode": 500
        }
    else:
        api_url = "/unity/service/open/app/login"
        if lot_id in api_config.get("test_support_lotId") and server_ip in api_config.get("test_support_ips"):
            url = urljoin(api_config.get("unity_login_domain").get("test"), api_url)
            device_ip = "192.168.0.86"
        elif lot_id in api_config.get("prod_support_lotId") and server_ip in api_config.get("prod_support_ips"):
            url = urljoin(api_config.get("unity_login_domain").get("prod"), api_url)
            device_ip = "192.168.0.88"
        else:
            res = {
                "data": f"暂不支持车场【{lot_id}】",
                "resultCode": 500
            }
            return jsonify(res)
        # 统一平台登录
        headers = {"content-type": "application/json", "kt-lotcodes": lot_id}
        data = {"code": "", "expireDay": 0, "loginWay": "", "mobileCode": "0592", "phone": "19182295006"}
        ktToken = requests.post(url=url, headers=headers, data=json.dumps(data)).json()['data']['ktToken']
        in_out_fail_count = 0
        while in_out_fail_count < car_in_out_config["fail_count"]:
            dsp_obj_in = DspClient(server_ip, 5001, device_ip, client_port=0)
            dsp_obj_in.connect()
            dsp_obj_in.send_img(str(i_serial), car_no, 0, 0, "", int(recognition), int(car_color), 0, 0, i_cap_time=datetime.datetime.now())
            in_out_fail_tag = 0
            endtime = datetime.datetime.now() + datetime.timedelta(seconds=car_in_out_config["wait_time"])
            while datetime.datetime.now() < endtime:
                mms_result_dic = get_onPark(lot_id, car_no, ktToken)
                if mms_result_dic["data"]["vos"] == []:
                    sleep(1)
                    continue
                elif mms_result_dic["data"]["vos"][0]["carNo"] == car_no:
                    res = {
                        "data": f"【{car_no}】入场成功, 重试次数为【{in_out_fail_count}】",
                        "resultCode": 200
                    }
                    in_out_fail_tag = 1
                    break
                else:
                    sleep(1)
                    continue
            if in_out_fail_tag:
                dsp_obj_in.close()
                break
            dsp_obj_in.close()
            in_out_fail_count += 1
        if in_out_fail_count >= car_in_out_config["fail_count"]:
            res = {
                "data": f"【{car_no}】入场失败！, 重试【{in_out_fail_count}】次后车辆仍未在场",
                "resultCode": 500
            }
    return jsonify(res)


@server.route('/car_Out', methods=['get'])
@swag_from(filepath.CAROUTAPI)
def car_Out():
    """
    出车api
    """
    data = flask.request.args
    server_ip = data.get("server_ip") or "192.168.0.202"
    car_no = data.get("car_no") or ""
    lot_id = data.get("lot_id") or "996000386"
    car_color = data.get("car_color") or 3
    recognition = data.get("recognition") or 1000
    i_serial = data.get("i_serial") or random.randint(0, 999999999)
    # if not server_ip or not car_no:
    #     res = {
    #         "data": "Not find car_no",
    #         "resultCode": 500
    #     }
    if not server_ip:
        res = {
            "data": "Not find server_ip",
            "resultCode": 500
        }
    else:
        api_url = "/unity/service/open/app/login"
        if lot_id in api_config.get("test_support_lotId") and server_ip in api_config.get("test_support_ips"):
            url = urljoin(api_config.get("unity_login_domain").get("test"), api_url)
            device_ip = "192.168.0.87"
        elif lot_id in api_config.get("prod_support_lotId") and server_ip in api_config.get("prod_support_ips"):
            url = urljoin(api_config.get("unity_login_domain").get("prod"), api_url)
            device_ip = "192.168.0.89"
        else:
            res = {
                "data": f"暂不支持车场【{lot_id}】",
                "resultCode": 500
            }
            return jsonify(res)
        # 统一平台登录
        headers = {"content-type": "application/json", "kt-lotcodes": lot_id}
        data = {"code": "", "expireDay": 0, "loginWay": "", "mobileCode": "0592", "phone": "19182295006"}
        ktToken = requests.post(url=url, headers=headers, data=json.dumps(data)).json()['data']['ktToken']
        in_out_fail_count = 0
        while in_out_fail_count < car_in_out_config["fail_count"]:
            dsp_obj_out = DspClient(server_ip, 5001, device_ip, client_port=0)
            dsp_obj_out.connect()
            dsp_obj_out.send_img(str(i_serial), car_no, 0, 0, "", int(recognition), int(car_color), 0, 0, i_cap_time=datetime.datetime.now())
            in_out_fail_tag = 0
            endtime = datetime.datetime.now() + datetime.timedelta(seconds=car_in_out_config["wait_time"])
            while datetime.datetime.now() < endtime:
                mms_result_dic = get_onPark(lot_id, car_no, ktToken)
                if mms_result_dic["data"]["vos"] == []:
                    res = {
                        "data": f"【{car_no}】出场成功, 重试次数为【{in_out_fail_count}】",
                        "resultCode": 200
                    }
                    in_out_fail_tag = 1
                    break

                else:
                    sleep(1)
                    continue
            if in_out_fail_tag:
                dsp_obj_out.close()
                break
            dsp_obj_out.close()
            in_out_fail_count += 1
        if in_out_fail_count >= car_in_out_config["fail_count"]:
            res = {
                "data": f"【{car_no}】出场失败！, 重试【{in_out_fail_count}】次后车辆仍在场",
                "resultCode": 500
            }
    return jsonify(res)


@server.route('/PayOrder', methods=['get'])
@swag_from(filepath.PAYORDERAPI)
def Pay_Order():
    """
    支付普通订单api
    """
    data = flask.request.args
    server_ip = data.get("server_ip") or "192.168.0.202"
    car_no = data.get("car_no")
    lot_id = data.get("lot_id") or "996000386"

    if not server_ip or not car_no:
        res = {
            "data": "Not find car_no",
            "resultCode": 500
        }
    else:
        api_url = "/unity/service/open/app/login"
        if lot_id in api_config.get("test_support_lotId") and server_ip in api_config.get("test_support_ips"):
            # 统一平台登录
            url = urljoin(api_config.get("unity_login_domain").get("test"), api_url)
            print(url)
            headers = {"content-type": "application/json", "kt-lotcodes": lot_id}
            data = {"code": "", "expireDay": 0, "loginWay": "", "mobileCode": "0592", "phone": "19182295006"}
            ktToken = requests.post(url=url, headers=headers, data=json.dumps(data)).json()['data']['ktToken']
            # 模拟缴费
            order_info = park.get_park_pay_info(ktToken, lot_id, car_no)
            if order_info:
                if park.pay_order(ktToken, lot_id, order_info["orderNo"], order_info["payMoney"], car_no):
                    res = {
                        "data": f"【{car_no}】的订单【{order_info['orderNo']}】支付普通停车费【{order_info['payMoney']}】成功！",
                        "resultCode": 200
                    }
                else:
                    res = {
                        "data": f"【{car_no}】的订单【{order_info['orderNo']}】支付失败！",
                        "resultCode": 500
                    }
            else:
                res = {
                    "data": f"未查询到【{car_no}】的普通支付订单！！",
                    "resultCode": 500
                }
        elif lot_id in api_config.get("prod_support_lotId") and server_ip in api_config.get("prod_support_ips"):
            # 统一平台登录
            url = urljoin(api_config.get("unity_login_domain").get("prod"), api_url)
            headers = {"content-type": "application/json", "kt-lotcodes": lot_id}
            data = {"code": "", "expireDay": 0, "loginWay": "", "mobileCode": "0592", "phone": "19182295006"}
            ktToken = requests.post(url=url, headers=headers, data=json.dumps(data)).json()['data']['ktToken']
            # 模拟缴费
            order_info = park.get_park_pay_info_pro(ktToken, lot_id, car_no)
            if order_info:
                if park.pay_order_pro(ktToken, lot_id, order_info["orderNo"], order_info["payMoney"], car_no):
                    res = {
                        "data": f"【{car_no}】的订单【{order_info['orderNo']}】支付普通停车费【{order_info['payMoney']}】成功！",
                        "resultCode": 200
                    }
                else:
                    res = {
                        "data": f"【{car_no}】的订单【{order_info['orderNo']}】支付失败！",
                        "resultCode": 500
                    }
            else:
                res = {
                    "data": f"未查询到【{car_no}】的普通支付订单！！",
                    "resultCode": 500
                }
        else:
            res = {
                "data": f"暂不支持支付车场【{lot_id}】的普通支付订单！！",
                "resultCode": 500
            }
    return jsonify(res)


@server.route('/order_Refund', methods=['get'])
@swag_from(filepath.REFUNDAPI)
def order_Refund():
    """
    退停车费api
    """
    data = flask.request.args
    tag = data.get('tag') or 'test'
    carPlateNum = data.get('carPlateNum')
    beginDate = data.get('beginDate')
    endDate = data.get('endDate')
    cookie = data.get('cookie') if data.get('cookie') else get_cookie_test()
    order_list = query_order(tag, carPlateNum, beginDate, endDate, cookie)
    if order_list:
        if order_list == 'prod环境，非测试车牌，不可操作':
            res = {
                "data": f"prod环境，非测试车牌，不可操作",
                "resultCode": 500
            }
        else:
            number = len(order_list)
            fail_list = {}
            for i in range(number):
                print(order_list[i])
                # order_no = order_list[i]['ORDER_NO']
                order_no = order_list[i]['orderNo']
                # cash_fee = int(order_list[i]['CASH_FEE'] * 100)
                cash_fee = int(order_list[i]['cashFee'])
                result = refund(tag, order_no, cash_fee, cookie)
                if result['type'] != 'success':
                    fail_list[order_no] = result['tip']
            if len(fail_list) == 0:
                res = {
                    "data": f"退款成功",
                    "resultCode": 200
                }
            elif len(fail_list) == number:
                res = {
                    "data": f"退款失败",
                    "order": fail_list,
                    "resultCode": 500
                }
            else:
                res = {
                    "data": f"部分订单退款失败",
                    "order": fail_list,
                    "resultCode": 200
                }
    else:
        res = {
            "data": f"所选日期范围内无订单",
            "resultCode": 500
        }
    return jsonify(res)


@server.route('/checkDbTables', methods=['get'])
@swag_from(filepath.CHECKDBTABLES)
def checkDbTables():
    """
    比对库表
    @return:
    """
    data = flask.request.args
    project = data.get('project')
    csrftoken = data.get('csrftoken')
    sessionid = data.get('sessionid')
    print(project)
    if not project and not csrftoken and not sessionid:
        res = {
            "data": "project,csrftoken,sessionid is required",
            "resultCode": 500
        }
    else:
        try:
            if project == "cpc":
                check_tables_new.check_tables(project, csrftoken, sessionid)
            else:
                pass
                # check_tables(project)
            if os.path.isfile(filepath.CHECKREPORT):
                filePath, name = os.path.split(filepath.CHECKREPORT)
                res = make_response(send_from_directory(directory=filePath, path=filePath, filename=name, as_attachment=True))
                res.headers["Content-Disposition"] = "attachment; filename={0}".format(quote(name))
                return res
        except Exception as e:
            res = {
                "data": f"系统异常【{e}】",
                "resultCode": 500
            }
    return jsonify(res)


@server.route('/getUserToken', methods=['get'])
@swag_from(filepath.GETUSERTOKEN)
def getUserToken():
    """
    得到用户token
    @return:
    """
    data = flask.request.args
    userId = data.get('userId')
    env = data.get('env') or 'test'
    # print(project)
    if not userId:
        res = {
            "data": "userId is required",
            "resultCode": 500
        }
    elif env not in ("test", "pro"):
        res = {
            "data": f"env 【{env}】is Not allowed",
            "resultCode": 500
        }
    else:
        try:
            access_token = get_user_token(userId, env)
            res = {
                "message": f"查找用户【{userId}】的accessToken成功！",
                "data": f"access_token为【{access_token}】",
                "resultCode": 200
            }
            return res
        except Exception as e:
            res = {
                "data": f"系统异常【{e}】",
                "resultCode": 500
            }
    return jsonify(res)


@server.route('/updateUserPortrait', methods=['get'])
@swag_from(filepath.UPDATEUSERPORTRAIT)
def update_user_portrait():
    """
    修改用户画像
    """
    data = flask.request.args
    userId = data.get("userId")
    env = data.get("env") if data.get("env") else "test"
    if not userId:
        res = {
            "data": f"用户id不能为空!!",
            "resultCode": 500
        }
        return jsonify(res)
    if userId not in api_config.get("user").get(env):
        res = {
            "data": f"用户【{userId}】非测试用户，不可更改【{env}】环境的用户画像数据！！",
            "resultCode": 500
        }
        return jsonify(res)
    key = f"UP:{userId}"
    # 处理得出需要改变的字段字典
    t_dict = data.copy()
    need_process_data_dict = {i: v for i, v in t_dict.items() if i not in ("env", "userId") and v != ""}
    res_t = car.process_user_portrait(key, env, **need_process_data_dict)
    return jsonify(res_t[1])


@server.route('/test_ps_channel', methods=['post'])
@swag_from(filepath.TESTPSCHANNEL)
def test_ps_channel():
    """
    车位管理系统统一平台测试接口
    """
    data = json.loads(flask.request.data)
    print(data)
    # server_ip = data.get("server_ip") or "192.168.0.202"
    logger.info(data)
    return jsonify(data)


if __name__ == "__main__":
    api_config = my_nacos_client.get_config_yaml(filepath.CONF.get("nacos", "api_data_id"),
                                                 filepath.CONF.get("nacos", "api_group"))
    # 监听服务配置变化
    my_nacos_client.client.add_config_watcher(filepath.CONF.get("nacos", "api_data_id"),
                                              filepath.CONF.get("nacos", "api_group"), config_update)
    server.config['JSON_AS_ASCII'] = True
    server.run(host="0.0.0.0", port=17896, debug=True, threaded=True)
    # kttoken = login("996000386")
    # print(get_onPark("996000386", "川AHJH888", kttoken))
