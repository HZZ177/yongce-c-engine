# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: entrances.py
@Description: 文件路径管理
@Author: huangjunhao
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
@time:2021/04/29
===================================
"""

from common import util,dspClient,filepath
from common.configLog import logger


# @util.catch_exception
# def getSock(serverip, port, clientip):
#     sock = dspClient.DspClient(server_ip=serverip, server_port=port, client_ip=clientip)
#     return sock


@util.catch_exception
def on_Line(clientip, server_ip="192.168.0.202", over_msg='Z'):
    """
    设备上线
    parameter:
        clientip: 设备ip
        over_msg: 结束指令
    return:
        sock: dspclient对象
    """
    logger.info("【%s设备正在上线】" % clientip)
    serverip = server_ip
    port = int(filepath.CONF.get('advanced', 'ServerPort'))
    device = dspClient.DspClient(server_ip=serverip, server_port=port, client_ip=clientip)
    device.connect()
    # device.find_over(over_msg)
    return device


@util.catch_exception
def off_Line(client_ip, device):
    """
    设备下线
    parameter:
        client_ip: 设备ip
        device: dspclient对象
    return:
    """
    logger.info("【%s设备正在下线】" % client_ip)
    device.close()

