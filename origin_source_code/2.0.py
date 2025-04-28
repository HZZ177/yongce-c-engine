# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: test.py
@Description: 文件路径管理
@Author: huangjunhao
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
@time:2021/04/29
===================================
"""
import datetime
import os
import random
import re
import sqlite3
import traceback
from time import sleep
import flask
import json
from flask import jsonify
import requests

from common.configLog import logger
from common.dspClient import DspClient
from common.util import get_host_ip
from testCases.Public import car, park, public
from testCases.Public.public import login
import random
from flask import Flask, jsonify, request
from flasgger import Swagger
import socket
server = flask.Flask(__name__)
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


def get_onPark(lotId, carNo, ktToken, StartTime="", EndTime=""):
    now = datetime.datetime.now()
    zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
    StartTime = zeroToday.strftime("%Y-%m-%d %H:%M:%S")
    EndTime = lastToday.strftime("%Y-%m-%d %H:%M:%S")
    data_dic = {"lotCode": lotId,
                "downloadId": "",
                "pageSize": 10,
                "plateType": 0,
                "currentPage": 1,
                "carNo": carNo,
                "comeTimeStart": StartTime,
                # "comeTimeStart": "2021/08/02 00:00:00",
                "totalCount": "0,",
                "comeTimeEnd": EndTime
                # "comeTimeEnd": "2021/08/02 23:59:59"
                }
    headers = {"content-type": "application/json", "kt-token": ktToken, "kt-lotcodes": lotId}
    if lotId == "996000386":
        url = "https://s2-test.keytop.cn/nkc/carCome/findCarComePage"
    elif lotId == "9078":
        url = "http://ipark.keytop.cn/nkc/carCome/findCarComePage"
    res = requests.post(url=url, headers=headers,data=json.dumps(data_dic))
    if res.status_code != 200:
        raise Exception("查询在场接口出错！")
    return res.json()


@server.route('/get_wx_token', methods=['post'])
def get_wx_token():
    """
        得到与微信公众号交互使用的token
        得到微信token，测试：wxed9d3e6dc4a3704f，正式：wx88f62889b30261ac
        ---
        tags:
          - 获得微信token API
        parameters:
          - name: wx_id
            in: body
            type: string
            required: true
            description: wx_id
            schema:
              id: get_token
              properties:
                wx_id:
                  type: string
                  default: "xxxx"
        responses:
          500:
            description: Not find wx_id
          200:
            description: 返回正确的wx_id对应的token
            schema:
              id: awesome
              properties:
                token:
                  type: string
                  description: wx_id对应的token
                  default: ""
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
def device_On():
    """
        设备上线
        ---
        tags:
         -  出入车 API
        parameters:
          - name: param
            in: body
            type: string
            required: true
            schema:
              id: device_schema
              properties:
                  clientIps:
                      type: array
                      description: 设备ip数组
                      example: ["192.168.0.144","192.168.0.145"]
                  server_ip:
                      type: string
                      description: 服务器ip，默认192.168.0.202
                      example: "192.168.0.202"

        responses:
          500:
            description: clientIps is []
          200:
            description: 所有设备上线成功!!
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
def device_Off():
    """
        设备下线
        ---
        tags:
         -  出入车 API
        parameters:
          - name: param
            in: body
            type: string
            required: true
            schema:
              id: device_schema
              properties:
                  clientIps:
                      type: array
                      description: 设备ip数组
                      example: ["192.168.0.144","192.168.0.145"]
                  server_ip:
                      type: string
                      description: 服务器ip，默认192.168.0.202
                      example: "192.168.0.202"

        responses:
          500:
            description: clientIps is []
          200:
            description: 所有设备下线成功!!
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
def car_In():
    """
        入车
        进行入车操作
        ---
        tags:
          - 出入车 API
        parameters:
          - name: car_no
            in: query
            type: string
            required: true
            description: 车牌号
          - name: server_ip
            in: query
            type: string
            required: false
            description: 车场ip,默认192.168.0.202,正式环境ip为192.168.0.114
          - name: lot_id
            in: query
            type: string
            required: false
            description: 车场id,默认996000386,正式环境9078
        responses:
          500:
            description: Not find car_no
          200:
            description: 返回正确的入车状态
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

        if lot_id == "996000386" and server_ip == "192.168.0.202":
            ktToken = login(lot_id)
            device_ip = "192.168.0.144"
        else:

            url = "https://park.keytop.cn/unity/service/open/login/password"
            headers = {"content-type": "application/json", "kt-lotcodes": lot_id}
            data = {"loginName": 15281967090, "password": 123456}
            ktToken = requests.post(url=url, headers=headers, data=json.dumps(data)).json()['data']['ktToken']
            device_ip = "192.168.0.148"

        dsp_obj_in = DspClient(server_ip, 5001, device_ip, client_port=0)
        dsp_obj_in.connect()
        i_serial = random.randint(0, 999999999)
        dsp_obj_in.send_img(str(i_serial), car_no, 0, 0, "", 1000, 3, 0, 0, i_cap_time=datetime.datetime.now())
        time = 0
        while time < 10:
            mms_result_dic = get_onPark(lot_id, car_no, ktToken)
            if mms_result_dic["data"]["vos"] == []:
                sleep(1)
                time += 1
                continue
            elif mms_result_dic["data"]["vos"][0]["carNo"] == car_no:
                res = {
                    "data": f"【{car_no}】入场成功",
                    "resultCode": 200
                }

                break
            else:
                sleep(1)
                time += 1
                continue
        if time >= 10:
            res = {
                "data": f"【{car_no}】入场失败, timeout=10s",
                "resultCode": 500
            }
        dsp_obj_in.close()
    return jsonify(res)


@server.route('/car_Out', methods=['get'])
def car_Out():
    """
            出车
            进行出车操作
            ---
            tags:
              - 出入车 API
            parameters:
              - name: car_no
                in: query
                type: string
                required: true
                description: 车牌号
              - name: server_ip
                in: query
                type: string
                required: false
                description: 车场ip,默认192.168.0.202,正式环境ip为192.168.0.114
              - name: lot_id
                in: query
                type: string
                required: false
                description: 车场id,默认996000386,正式环境9078
            responses:
              500:
                description: Not find car_no
              200:
                description: 返回正确的出车状态
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
    if not server_ip or not car_no:
        res = {
            "data": "Not find car_no",
            "resultCode": 500
        }
    else:
        if lot_id == "996000386" and server_ip == "192.168.0.202":
            ktToken = login(lot_id)
            device_ip = "192.168.0.145"
        else:
            url = "https://park.keytop.cn/unity/service/open/login/password"
            headers = {"content-type": "application/json", "kt-lotcodes": lot_id}
            data = {"loginName": 15281967090, "password": 123456}
            ktToken = requests.post(url=url, headers=headers, data=json.dumps(data)).json()['data']['ktToken']
            device_ip = "192.168.0.147"
        dsp_obj_out = DspClient(server_ip, 5001, device_ip, client_port=0)
        dsp_obj_out.connect()
        i_serial = random.randint(0, 999999999)
        dsp_obj_out.send_img(str(i_serial), car_no, 0, 0, "", 1000, 3, 0, 0, i_cap_time=datetime.datetime.now())
        time = 0
        while time < 10:
            mms_result_dic = get_onPark(lot_id, car_no, ktToken)
            if mms_result_dic["data"]["vos"] == []:
                res = {
                    "data": f"【{car_no}】出场成功",
                    "resultCode": 200
                }
                break

            else:
                sleep(1)
                time += 1
                continue
        if time >= 10:
            res = {
                "data": f"【{car_no}】出场失败, timeout=10s",
                "resultCode": 500
            }
        dsp_obj_out.close()
    return jsonify(res)


@server.route('/PayOrder', methods=['get'])
def Pay_Order():
    """
        支付
        进行模拟缴费操作
        ---
        tags:
          - 出入车 API
        parameters:
          - name: car_no
            in: query
            type: string
            required: true
            description: 车牌号
          - name: server_ip
            in: query
            type: string
            required: false
            description: 车场ip,默认192.168.0.202,正式环境ip为192.168.0.114
          - name: lot_id
            in: query
            type: string
            required: false
            description: 车场id,默认996000386,正式环境9078
        responses:
          500:
            description: Not find car_no
          200:
            description: 返回正确的支付状态
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
        if lot_id == "996000386" and server_ip == "192.168.0.202":
            ktToken = login(lot_id)
            # 模拟缴费
            order_info = park.get_park_pay_info(ktToken, lot_id, car_no)
            if order_info:
                if park.pay_order(ktToken, lot_id, order_info["orderNo"], order_info["payMoney"], car_no):
                    res = {
                        "data": f"【{car_no}】的订单【{order_info['orderNo']}】支付成功！",
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
            url = "https://park.keytop.cn/unity/service/open/login/password"
            headers = {"content-type": "application/json", "kt-lotcodes": lot_id}
            data = {"loginName": 15281967090, "password": 123456}
            ktToken = requests.post(url=url, headers=headers, data=json.dumps(data)).json()['data']['ktToken']
            # 模拟缴费
            order_info = park.get_park_pay_info_pro(ktToken, lot_id, car_no)
            if order_info:
                if park.pay_order_pro(ktToken, lot_id, order_info["orderNo"], order_info["payMoney"], car_no):
                    res = {
                        "data": f"【{car_no}】的订单【{order_info['orderNo']}】支付成功！",
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
    return jsonify(res)


if __name__ == "__main__":
    server.config['JSON_AS_ASCII'] = True
    server.run(host="0.0.0.0", port='17896', debug=True)
    # kttoken = login("996000386")
    # print(get_onPark("996000386", "川AHJH888", kttoken))
