#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/11/9 下午7:21
# @Author  : Heshouyi
# @File    : file_path.py
# @Software: PyCharm
# @description:

import os

'''项目目录'''
# 项目根目录，指向yongce-c-engine
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

'''一级目录'''
apps_path = os.path.abspath(os.path.join(project_path, 'apps'))     # app根目录
core_path = os.path.abspath(os.path.join(project_path, 'core'))     # core目录
log_path = os.path.abspath(os.path.join(project_path, 'logs'))      # 日志目录
static_path = os.path.abspath(os.path.join(project_path, 'static'))     # 静态资源目录

'''二级目录'''
close_dsp_path = os.path.abspath(os.path.join(apps_path, 'closeDsp'))


if __name__ == '__main__':
    print(project_path)
