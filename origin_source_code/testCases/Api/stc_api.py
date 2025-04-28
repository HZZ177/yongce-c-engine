# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: stc_api.py
@Description: 速停车测试使用接口
@Author: huangjunhao
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
@time:2022/04/06
===================================
"""
import json
import time

from common import filepath
from common.configLog import logger
from common.processYaml import Yaml
from common.request import request
from testCases.Public.public import get_user_info_by_mms


def get_user_token(user_id, env):
    """
    :return: 模拟登录得到用户的token
    """
    read_data = Yaml(filepath.USERTOKEN, 5)
    url = "https://ts.keytop.cn/pp-server/atss/login" if env == "test" \
        else "https://cloud.keytop.cn/pp-server/atss/login"
    method = read_data.method
    headers = read_data.headers
    query_datas = read_data.allData
    for query_data in query_datas:
        if query_data[0]['id'] == 1:
            sec = query_data[1]['ps']
            request_data = query_data[2]["request_data"]
            request_data["expireTimes"] = int(time.time()) + 60 * 60 * 24 * 7
            request_data["ppUserId"] = user_id
            request_data["ttpUserId"] = get_user_info_by_mms(user_id, env)["wxAuthInfos"][0]["wxOpenId"]
            res = request.request(method=method, url=url, data=json.dumps(request_data), headers=headers, timeout=10)
            result_dic = res.json()
            if result_dic["code"] != 2000:
                raise Exception(logger.error("用户登录接口出错！"))
            else:
                logger.info(f"✔ 查询用户【{user_id}】token成功！")
            return result_dic["data"]["accessToken"]


if __name__ == '__main__':
    print(get_user_token("204350188868616197", "https://ts.keytop.cn/pp-server/atss/login"))
    # print(get_user_token("211003011592360633", "pro"))