import datetime
import hashlib
import json

import requests
from requests.adapters import HTTPAdapter

from common import filepath
from common.configLog import logger
import time

from common.processYaml import Yaml


class Requests:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def retry(func):
        """失败重试，默认3次"""
        def wrapper(*args, **kwargs):
            temp = True     # 打印日志标记
            if kwargs.get('no_log'):
                temp = False
                kwargs.pop('no_log')
            num = args[1] if len(args) > 1 else 3
            i = 1
            while i < num+1:
                try:
                    if temp:
                        logger.info("第%s次%s请求,请求参数:%s" % (i, func.__name__, kwargs))
                    res = func(*args, **kwargs)
                    return res
                except Exception as msg:
                    logger.error(msg)
                    i += 1
                    time.sleep(1)
            logger.error("请求失败3次！请求参数:%s" % kwargs)
        return wrapper

    @retry
    def get(self, *args, **kwargs):
        response = requests.get(**kwargs)
        if response.status_code == 200:
            return response
        else:
            raise Exception(logger.error("该请求得到响应：%s ,响应码: %s" % (response, response.status_code)))

    @retry
    def post(self, *args, **kwargs):
        response = requests.post(**kwargs)
        if response.status_code == 200:
            return response
        else:
            raise Exception(logger.error("该请求得到响应：%s ,响应码: %s" % (response, response.status_code)))

    @retry
    def request(self, method, url, **kwargs):
        response = requests.request(method, url, **kwargs)
        if response.status_code == 200:
            return response
        else:
            raise Exception(logger.error("该请求得到响应：%s ,响应码: %s" % (response, response.status_code)))

    def mms_request(self, data):
        url = data.get("url")
        method = data.get("method")
        headers = data.get("headers")
        request_data = data.get("request_data")
        logger.info(f'请求中台接口信息参数：url:{url} headers:{headers} data:{request_data}')
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=2))
        s.mount('https://', HTTPAdapter(max_retries=2))
        timeOut = data.get("timeOut")
        if method == "post" or method == "POST":
            response = s.post(url=url, headers=headers, data=request_data, timeout=timeOut)
        elif method == "get" or method == "GET":
            response = s.get(url=url, headers=headers, params=request_data, timeout=timeOut)
        if response.status_code == 200:
            return response
        else:
            raise Exception(logger.error("该请求得到响应：%s ,响应码: %s" % (response, response.status_code)))

    def queryUrl(self, url, queryDict):
        try:
            query = '?' + '&'.join([str(key)+"="+str(value) for key, value in queryDict.items()])
            new_url = "".join((url, query))
        except Exception as msg:
            logger.error(msg)
        return new_url


request = Requests()


if __name__ == "__main__":
    from testCases.Public.public import process_mms
    r = Requests()
    # res = r.get(4, url='https://www.baidu.com/', timeout=5)
    # print("res: ", res)
    test_dic = {
        "url": "http://mms-test.keytop.cn",
        "sid": "cn.keytop.stc.pp.pp-server./selectUserAuthInfoByUserId",
        "version": "1.0.0",
        "appKey": "6182484814727F1504B6B1E328E576F1",
        "app_id": "cn.keytop.stc.pp.cp-region",
        "data": {
            "ppUserId": "90127049743683904"
        }
    }
    # data = process_mms(filepath.ONPARKBYMMS)
    # data["request_data"]["plateNumber"] = "川AV8888"
    data = process_mms(filepath.OWEBILLBYMMS)
    data["request_data"]["lpn"] = "云X48977"
    print(r.mms_request(data).json())