"""
@File    : page.py
@Time    : 2020-9-4 15:31
@Author  : huangjunhao
@Software: PyCharm
备注：page类
"""
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from common import util, filepath
from common.configLog import logger


class Page:
    def __init__(self, driver=None):
        self.driver = driver

    def get_driver(self):
        try:
            options = Options()
            # options = webdriver.ChromeOptions()
            # options.headless = True
            options.add_argument("--headless")  # => 为Chrome配置无头模式
            # options.add_argument('--no-sandbox')
            # options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=options)
            # self.driver = webdriver.Chrome()
            # 设置元素识别超时时间
            self.driver.implicitly_wait(30)
            # 设置页面加载超时时间
            self.driver.set_page_load_timeout(30)
            # # 设置异步脚本加载超时时间
            # driver.set_script_timeout(30)
            # 将浏览器最大化
            self.driver.maximize_window()
        except Exception as e:
            raise Exception(f"无头错误{e}")
        return self.driver

    @util.catch_exception
    def wait(self, locator, timeout=10, tag_num=0):
        time_count = 0
        logger.info(f"进行等待操作，等待对象为{locator}")
        while True:
            if time_count == timeout:
                raise Exception("超时！未找到元素对象!")
            try:
                if self.find(locator, tag_num):
                    break
            except BaseException:
                time.sleep(1)
                time_count += 1
                logger.info(f"等待了{time_count}s")

    @util.catch_exception
    def select(self, locator, option):
        pass

    @util.catch_exception
    def re_clcik(self, click_ele, assert_locator, retry_num=int(filepath.CONF.get("retry", "num")), tag_num=0):
        """
        有些元素需要重复点击才能生效时，调用此函数
        :param click_ele: 点击对象
        :param assert_locator: 点击后的检测对象
        :param retry_num: 重试次数，默认3次，在配置文件中可配置
        :param tag_num: 查找对象tag
        """
        count = 0
        while count < retry_num:
            click_ele.click()
            if self.find(assert_locator, tag_num):
                logger.info(f"点击成功")
                break
            time.sleep(1)
            count += 1
            logger.info(f"重试click方法，第{count}次")
        if count == 3:
            raise Exception(logger.info(f"元素{click_ele},点击{retry_num},仍未点击成功!"))

    @util.catch_exception
    def find(self, locator, tag_num=0):
        """

        :param tag_num: 查找tag，0为单对象，1为多对象
        :param locator:元素定位方法
        :return: 元素对象
        """
        logger.info(f"进行元素查找操作，等待对象为{locator}")
        if tag_num == 0:
            return self.driver.find_element(*locator)
        elif tag_num == 1:
            return self.driver.find_elements(*locator)

    @util.catch_exception
    def open_url(self, url):
        """

        :param url:打开被测网站
        """
        self.driver.get(url)
        logger.info(f"打开被测网站{url}")


if __name__ == '__main__':
    pass