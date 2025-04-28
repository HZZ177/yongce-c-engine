# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: my_nacos.py
@Description: 
@Author: huangjunhao
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
@time:2023/04/13
===================================
"""
import nacos
import yaml

from common import filepath


class MyNaCosClient:
    """
    创建nacos客户端
    """
    def __init__(self, server_addresses=None, name_space=None, *args, **kwargs):
        server_addresses = server_addresses if server_addresses else filepath.CONF.get("nacos", "server_addresses")
        name_space = name_space if name_space else filepath.CONF.get("nacos", "name_space")
        self.client = nacos.NacosClient(server_addresses, namespace=name_space, *args, **kwargs)

    def get_client(self):
        """
        返回nacos客户端
        :return:
        """
        return self.client

    def get_config_yaml(self, data_id, group):
        """
        按照yaml格式解析配置文件，返回字典
        :return:
        """
        server_config = yaml.load(self.client.get_config(data_id, group), Loader=yaml.FullLoader)
        return server_config
