# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: login_archery.py
@Description: 登录线上数据库登录界面
@Author: huangjunhao
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
@time:2021/05/18
===================================
"""
from selenium.webdriver.common.by import By

from common import util
from common.configLog import logger
from common.page import Page


class LoginArchery(Page):
    # 定位方式
    # 用户名框
    username_ele = [By.ID, "inputUsername"]
    # 密码框
    password_ele = [By.ID, "inputPassword"]
    # 登录按钮
    login_but_ele = [By.ID, "btnLogin"]

    @util.catch_exception
    def login(self, username, password):
        # 等待用户名框元素出现
        self.wait(self.username_ele)
        # 输入用户名
        self.find(self.username_ele).send_keys(username)
        # 输入密码
        self.find(self.password_ele).send_keys(password)
        # 点击登录按钮
        self.find(self.login_but_ele).click()
        logger.info("进行了线上数据库网站的登录操作")


if __name__ == '__main__':
    from selenium import webdriver
    from testCases.Page.sqlquery import SqlQuery
    # driver = webdriver.Chrome()
    # # 设置元素识别超时时间
    # driver.implicitly_wait(30)
    # # 设置页面加载超时时间
    # driver.set_page_load_timeout(30)
    # # # 设置异步脚本加载超时时间
    # # driver.set_script_timeout(30)
    # # 将浏览器最大化
    # driver.maximize_window()
    driver = Page().get_driver()
    page_obj = LoginArchery(driver)
    page_obj.open_url("https://archery.keytop.cn:8100/login/")
    page_obj.login("huangjunhao", "huangjunhao,.")
    page_obj_2 = SqlQuery(driver)
    page_obj_2.check_login_success("黄俊豪")
    page_obj_2.select_example("速停车只读-成都研发使用-阿里云")
    result = page_obj_2.get_sql_result("SELECT privilege_status FROM superpark.mc_parking_lot_postpaid_config WHERE lot_id = '592011611';")