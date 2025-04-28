# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: order.py
@Description: 订单相关处理
@Author: huangjunhao
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
@time:2021/05/08
===================================
"""
import datetime
import time

import allure

from common import filepath, util
from common.configLog import logger
from common.db_tool import DbTool
from common.getCloudDataByFormal import cloud
from common.processYaml import Yaml


@util.catch_exception
@util.retry_fun
@allure.step("删除【{carNo}】的临时账单")
def del_Bill(carNo):
    """

    删除6.x车场临时账单
    :param carNo:
    """
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.OWEBILL, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                table_name = query_data[2].get("tableName")
                del_sql = f"delete from {table_name} WHERE CAR_PLATE_NUM='{carNo}'and TURN_ARREAR_ORDER='N';"
                db_obj.control_db_by_sql(del_sql)
                logger.info(f"清除【{carNo}】的6.x车场临时账单记录成功")
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        pass


@util.catch_exception
@util.retry_fun
@allure.step("修改【{user_id}】的支付账单状态")
def update_bus_order(user_id):
    """

    修改busorder状态
    :param user_id:
    """
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.ONPARK, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                update_sql = f"update bus_order set TRADE_STATE = '00' where USER_ID ='{user_id}' and TRADE_STATE !='00' " \
                          f"and ORDER_CATEGORY='01';"
                db_obj.control_db_by_sql(update_sql)
                logger.info(f"修改用户【{user_id}】的账单支付记录成功")
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        pass


@util.catch_exception
@util.retry_fun
@allure.step("提前【{carNo}】的临时账单时间")
def update_Bill(carNo, min=4):
    """

    更改6.x车场临时账单生成时间
    :param min: 向前移动分钟数，默认为4
    :param carNo:
    """
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        str_time = (datetime.datetime.now()-datetime.timedelta(minutes=min)).strftime("%Y-%m-%d %H:%M:%S")
        # time = datetime.datetime.now()-datetime.timedelta(minutes=min)
        # print(time)
        read_data = Yaml(filepath.OWEBILL, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                table_name = query_data[2].get("tableName")
                update_sql = f"UPDATE {table_name} SET CREATE_TIME = '{str_time}' WHERE CAR_PLATE_NUM='{carNo}'and TURN_ARREAR_ORDER='N';"
                db_obj.control_db_by_sql(update_sql)
                logger.info(f"提前【{carNo}】的6.x车场临时账单记录时间至【{str_time}】成功")
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        pass


@util.catch_exception
@util.retry_fun
@allure.step("删除【{user_id}】的支付账单")
def del_order(user_id):
    """

    删除账单
    :param carNo:
    """
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 测试环境检查
    if server_ip == filepath.CONF.get('advanced', 'test_ServerIP'):
        read_data = Yaml(filepath.OWEORDER, 0)
        db_data = read_data.allDb
        query_datas = read_data.allQuery
        db_obj = DbTool(db_data[0][0])
        for query_data in query_datas:
            if query_data[0]['id'] == 1:
                table_name = query_data[2].get("tableName")
                del_sql = f"delete from {table_name} where PP_USER_ID='{user_id}';"
                db_obj.control_db_by_sql(del_sql)
                logger.info(f"清除用户【{user_id}】的后付费欠费订单记录成功")
    elif server_ip == filepath.CONF.get('advanced', 'pro_ServerIP'):
        pass


if __name__ == '__main__':
    # from common.request import request
    # import json
    # car_No = filepath.CONF.get('car', 'vip_carNo')
    # user_id = filepath.CONF.get('car', 'vip_user')
    # lot_id = filepath.CONF.get("advanced", "lotId")
    # # del_Bill(car_No)
    # # del_order(user_id)
    # # update_bus_order(user_id)
    # url = "http://117.173.153.41:60004/privilege-strategy/getPrivilegeStrategy"
    # data = {
    #     "carPlateNum": "川AHJH888",
    #     "lotId": "592011611"
    # }
    # headers = {
    #     "Content-Type": "application/json;charset=UTF-8"
    # }
    # res = request.get(url=url, params=data, headers=headers)
    # result_dic = res.json()
    # print(result_dic)

    print(check_user_order("206936381951627288"))