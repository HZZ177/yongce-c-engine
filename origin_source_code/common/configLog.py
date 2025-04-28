# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: configLog.py
@Description: 日志配置类
@Author: wurun
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright:
===================================
"""

import logging
from common import filepath
import os
import warnings


class Logger:
    def __init__(self):
        """指定保存日志的文件路径，日志级别"""
        warnings.simplefilter("ignore", ResourceWarning)
        # 创建一个logger
        module_path = self.get_module()
        self.logger = logging.getLogger(module_path)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        # 创建一个handler,用于写入日志文件
        log_name = filepath.fetch_path_with_d(filepath.LOG_PATH, '.log')
        fh = logging.FileHandler(log_name, encoding='utf-8')
        fh.setLevel(logging.INFO)
        # 在创建一个handler,用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # 定义handler的输出格式
        # formatter = logging.Formatter('%(levelname)s -- %(asctime)s - %(name)s - %(message)s')
        formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(pathname)s - '
                                      '%(funcName)s:%(lineno)d => %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def get_module(self):
        """
        获取当前文件模块路径
        """
        project_path = filepath.PRO_PATH
        file_path = os.path.abspath(__file__)
        module_path = file_path.split(project_path)[1].split(".")[0][1:].replace("\\", ".")
        return module_path

    def get_log(self):
        return self.logger


logger = Logger().get_log()


if __name__ == "__main__":
    log = Logger()

