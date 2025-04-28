# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: sqlquery.py
@Description: 线上数据库查询界面
@Author: huangjunhao
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
@time:2021/05/19
===================================
"""
import time

from selenium.webdriver.common.by import By

from common import util
from common.configLog import logger
from common.page import Page


class SqlQuery(Page):
    # 定位方式
    # 检查登录成功的欢迎标语
    welcome_ele = [By.XPATH, "//a[contains(text(),'你好')]"]
    # 实例选择框
    instance_name_ele = [By.CSS_SELECTOR, "button[data-id='instance_name']"]
    # 数据库选择框
    db_name_ele = [By.CSS_SELECTOR, "button[data-id='db_name']"]
    # 实例搜索框
    search_instance_name_ele = [By.CSS_SELECTOR, "input[placeholder = '搜索您所在组的实例']"]  # 搜索您要查询的数据库、搜索您要查询的表
    # 数据库搜索框
    search_db_name_ele = [By.CSS_SELECTOR, "input[placeholder = '搜索您要查询的数据库']"]
    # 选择实例、数据库、表结构
    select_options_ele = [By.XPATH, "//span[contains(text(),'%s') and @class='text']"]
    # sql表单
    sql_form_ele = [By.ID, "form-sqlquery"]
    # sql输入框
    # sql_input_ele = [By.CLASS_NAME, "ace_text-input"]
    sql_input_ele = [By.CSS_SELECTOR, "#sql_content_editor>textarea"]
    # sql查询but
    query_but_ele = [By.ID, "btn-sqlquery"]
    # 执行结果
    result_ele = [By.CSS_SELECTOR, "table#query_result1 td"]

    @util.catch_exception
    def check_login_success(self, username):
        # 得到欢迎文本
        welcome_tag = self.find(self.welcome_ele).text
        assert username in welcome_tag.replace(" ", "")
        logger.info("登录成功！")

    @util.catch_exception
    def select_example(self, example, db="superpark"):
        # 点击选择实例框
        self.find(self.instance_name_ele).click()
        # 输入搜索实例名
        self.find(self.search_instance_name_ele).send_keys(example)
        # 选择实例名
        select_options_ele = self.select_options_ele.copy()
        select_options_ele[1] = select_options_ele[1] % example
        self.find(select_options_ele).click()
        logger.info(f"选择实例【{example}】成功！")
        # 点击选择数据库
        self.find(self.db_name_ele).click()
        # 输入搜索数据库名
        self.find(self.search_db_name_ele).send_keys(db)
        # 选择数据库名
        select_options_ele = self.select_options_ele.copy()
        select_options_ele[1] = select_options_ele[1] % db
        self.find(select_options_ele).click()
        logger.info(f"选择数据库【{db}】成功！")

    @util.catch_exception
    def get_sql_result(self, sql):
        self.find(self.sql_form_ele).click()
        time.sleep(1)
        # 清除内容
        self.find(self.sql_input_ele).clear()
        # 输入sql
        self.find(self.sql_input_ele).send_keys(sql)
        # 点击sql查询按钮
        self.find(self.query_but_ele).click()
        # 得到查询结果
        time.sleep(1)
        result_elements = self.find(self.result_ele, 1)
        result = [[result.text for result in result_elements]]
        if result[0][0] == "没有找到匹配的记录":
            result = []
        logger.info(f"运行sql【{sql}】，得到查询结果【{result}】！")
        return result