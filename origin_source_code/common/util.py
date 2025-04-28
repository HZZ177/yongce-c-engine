import json
import os
import re
import socket
import time
import random
import traceback
from functools import wraps
from common.configLog import logger
from common import filepath, encryption
import json
from jsonpath_rw import parse


def checkResultCode(resJson, is_log=True):
    """
    检测接口响应结果
    parameter:
        resJson: 接口返回json数据
        is_log: 不需要打印日志传False
    return:
        检测失败抛异常
    """
    if 'resultCode' in resJson:
        code = resJson['resultCode']
        if code != 200:
            raise Exception(logger.error("接口响应参数: %s" % resJson))
    elif "code" in resJson:
        code = resJson["code"]
        if code == '102':
            logger.info(resJson['msg'])
        elif code != "200":
            raise Exception(logger.error("接口响应参数: %s" % resJson))
    # elif "resCode" in resJson:
    #     code = resJson["resCode"]
    #     if code != "0":
    #         raise Exception(logger.error("接口响应参数: %s" % resJson))
    if is_log:
        logger.info("接口响应参数: %s" % resJson)


def get_parameter(Data, lot_id="", kttoken=""):
    """
    获取接口请求数据 data
    parameter:
        Data: 测试数据
        lot_id: 车场id
        kttoken: kttoken
    return:
        url: 接口地址
        headers: 请求头
        allData: 全部data数据
    """
    url = Data.url
    headers = Data.headers
    headers['Content-Type'] = "application/json;charset=UTF-8"
    if kttoken:
        headers['kt-token'] = kttoken
    if lot_id:
        headers['kt-lotcodes'] = lot_id
    allData = Data.allData
    return url, headers, allData


def get_query_parame(Data, lot_id="", kttoken=""):
    """
    获取接口请求数据 query
    parameter:
        Data: 测试数据
        lot_id: 车场id
        kttoken: kttoken
    return:
        url: 接口地址
        headers: 请求头
        allQuery: 全部query数据
    """
    url = Data.url
    headers = Data.headers
    headers['Content-Type'] = "application/json;charset=UTF-8"
    if kttoken:
        headers['kt-token'] = kttoken
    if lot_id:
        headers['kt-lotcodes'] = lot_id
    allQuery = Data.allQuery
    return url, headers, allQuery


def process_query(query):
    """
    处理query数据
    parameter:
        query: query数据
    return:
        query_str: 处理完数据 -> ?key1=value1&key2=value2
    """
    query_str = "&".join([str(key) + "=" + str(values) for key, values in query.items()])
    query_str = "?" + query_str
    return query_str


def process_rotio(total, passed, taskInfo_path):
    """
    处理通过率
    parameter:
        total: 执行用例总数
        passed: 通过用例数量
        taskInfo_path: 测试信息路径
    return:
    """
    task_info = {"total": total, "passed": passed}
    with open(taskInfo_path, "a+") as f:
        f.write(json.dumps(task_info))
        f.write("\n")
    with open(taskInfo_path, "r") as f:
        all_info = f.readlines()
    all_total = 0
    all_passed = 0
    for info in all_info:
        all_total += eval(info)['total']
        all_passed += eval(info)['passed']
    ratio = all_passed / all_total
    with open(filepath.FILE_REPORT_PATH, 'w') as td:
        td.write('%.2f%%' % (ratio * 100))


# def access_data(data, lotCode, reqid):
#     """
#     加密数据 6.x接口
#     parameter:
#         data: 需要加密数据
#         lotCode: 车场id
#         reqid: reqid
#     return:
#         base_data: 请求数据
#         auth: 认证数据
#     """
#     now_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
#     accessKey = filepath.CONF.get('access', 'accessKey')
#     accessToken = filepath.CONF.get('access', 'accessToken')
#     base_data = {
#         "accessKey": accessKey,
#         "lotCode": lotCode,
#         "ts": now_time,
#         "sign": "",
#         "data": data,
#         "reqId": reqid,
#     }
#     sign = encryption.get_sign(data, accessToken)
#     base_data["sign"] = sign
#     auth = encryption.aes_encrypt(accessKey, "{}:{}".format(accessToken, now_time))
#     return base_data, auth


def access_data_sha256(data, lotCode, reqid):
    """
    加密数据 6.x接口 sha256
    parameter:
        data: 需要加密数据
        lotCode: 车场id
        reqid: reqid
    return:
        base_data: 请求数据
        auth: 认证数据
    """
    now_time = int(time.time()*1000)
    accessKey = filepath.CONF.get('access', 'accessKey')
    accessToken = filepath.CONF.get('access', 'accessToken')
    base_data = {
        "accessKey": accessKey,
        "lotCode": lotCode,
        "ts": now_time,
        "sign": "",
        "data": data,
        "reqId": reqid,
    }
    sign = encryption.get_sign_sha256(data, accessToken)
    base_data["sign"] = sign
    API_TOKEN = encryption.sha256Encode(accessToken + str(now_time))
    return base_data, API_TOKEN


def access_data_new(data, lotCode, reqid):
    """
    加密数据 6.x对内接口
    parameter:
        data: 需要加密数据
        lotCode: 车场id
        reqid: reqid
    return:
        base_data: 请求数据
        auth: 认证数据
    """
    now_time = str(int(time.time() * 1000))
    appId = filepath.CONF.get('access', 'appId')
    appSecret = filepath.CONF.get('access', 'appSecret')
    data["appId"] = appId
    data["ts"] = now_time
    key = encryption.get_key(data, appSecret)
    data["key"] = key
    #auth = encryption.aes_encrypt(appSecret, "{}:{}".format(appSecret, now_time))
    return data


def generate_car(is_special=False):
    """
    随机生成车牌
    parameter:
        is_special: 生成特殊车牌传True，默认为False
    return:
        car_no: 随机生成的车牌
    """
    province = '京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽赣粤青藏川宁琼'
    letter = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    numbers = '0123456789'
    car_no = ""
    car_no += province[random.randint(1, len(province)-1)]
    car_no += letter[random.randint(1, len(letter)-1)]
    for i in range(4):
        car_no += numbers[random.randint(1, len(numbers)-1)]
    end_str = "军" if is_special else numbers[random.randint(1, len(numbers)-1)]
    car_no += end_str
    logger.info("随机生成车牌：%s" % car_no)
    return car_no


def check_recv(recv_list, need_in=True):
    """
    检测dsp返回数据是否开闸，收到R指令
    parameter:
        recv_list: 接受消息列表
        need_in: 车辆需要入场为True,不需要为False
    return:
    """
    temp = False
    for msg in recv_list:
        if '收到R指令' in msg:
            logger.info("dsp收到R指令，开闸")
            temp = True
    if not temp:
        logger.info("dsp没有收到R指令，没有开闸")
    if need_in == temp:
        logger.info("✔ 校验成功")
    else:
        raise Exception(logger.error('校验失败'))


# def check_dsp():
#     """
#     检测dsp是否挂住导致整个程序堵塞，若挂住测重启dspserver
#     只能以守护线程方式运行
#     """
#     end_time = time.time() + 60
#     while time.time() < end_time:
#         if RUN_TEMP:
#             with RUN_LOCK:
#                 RUN_TEMP.clear()
#                 return
#     logger.error("dspclient已经挂住,正在通过正在重启DspServer更正")
#     public.restartDspServer()
#
#
# def check_run(func):
#     """
#     开启线程确保程序不会挂住
#     """
#     def warpper(*args, **kwargs):
#         threading.Thread(target=check_dsp, daemon=True).start()
#         res = func(*args, **kwargs)
#         with RUN_LOCK:
#             RUN_TEMP.append(func.__name__)
#             return res
#     return warpper


def catch_exception(func):
    """捕获异常写入日志"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            raise Exception(logger.error(traceback.format_exc()))
    return wrapper


@catch_exception
def retry_fun(func):
    """失败重试，setting文件中配置，默认3次"""
    def wrapper(*args, **kwargs):
        temp = True  # 打印日志标记
        if kwargs.get('no_log'):
            temp = False
            kwargs.pop('no_log')
        num = int(filepath.CONF.get("retry", "num"))
        i = 1
        while i < num + 1:
            try:
                if temp:
                    logger.info("第%s次，进行%s" % (i, func.__name__))
                res = func(*args, **kwargs)
                return res
            except Exception as msg:
                logger.error(msg)
                i += 1
                time.sleep(1)
        logger.error(f"请求失败{num}次！请求函数:%s" % func.__name__)

    return wrapper


@catch_exception
def get_json_data_by_path(v, data):
    """
    处理响应数据，主要是从响应数据中获取依赖需要的数据
    :param v: 依赖的字段，如 test_id:data.uuid 表示依赖其他用例的参数是uuid, 然后uuid的层级是data.uuid
    :param data: 对应依赖用例的响应体
    :return: 从依赖用例的响应体中提取出的对应依赖字段的数据
    """
    json_exe = parse(v)
    if not isinstance(data, dict):
        data = json.loads(data)
    try:
        result = [match.value for match in json_exe.find(data)][0]
        return result
    except TypeError:
        raise ValueError(logger.error('未能获取有效参数或给予的JSON路径不对，请检查参数设置！'))


@catch_exception
def format_request_data_extend(request_data, key_data=""):
    '''
    根据需要处理用例中的依赖项，这里主要处理 session
    当然通过在用例中利用模板 ${} 来自定义参数，也可以实现其他更复杂的依赖
    :param request_data:
    :return:
    '''
    params_re = re.compile(r'\$([jstcnsk]+)\{(.+?)\}')
    if request_data:
        # 通过正则表达式找到参数中所有的 ${} 格式的待处理依赖
        custom_params = re.findall(params_re, request_data)
        for p in custom_params:
            k, v = p
            if k == 't':
                if v == 'session':
                    pass
                    # value = get_session()
                else:
                    pass
            # elif k == 's':
            #     # 如果是$s{}参数形式，表示SQL语句，则直接到数据库中执行该语句
            #     v = v.split(',')
            #     value = DbTool.get_first_data(*v)
            # elif k == 'j':
            #     # 如果是$j{}参数形式, 则需要从依赖用例的响应中获取实际数据
            #     try:
            #         case_id, value = v.split(':', 1)
            #         print(case_id, value)
            #         value = self.get_json_data_by_path(value, self.get_data_from_json_file(case_id))
            #     except Exception:
            #         raise ValueError('未能从指定用例的响应中取回依赖数据，请检查参数设置或用例的执行顺序！')
            elif k == 'k':
                # 如果是$k{}参数形式, 则需要替换关键字
                value = key_data
            # elif k == 'cs':
            #     # 如果是$cs{}参数形式，表示构造随机字符串
            #     v = int(v)
            #     value = creat.creat_str(v)
            # elif k == 'cn':
            #     # 如果是$cn{}参数形式，表示构造随机字符串
            #     v = int(v)
            #     value = creat.creat_number(v)
            # elif k == 'csn':
            #     # 如果是$csn{}参数形式，表示构造随机字符串
            #     v = int(v)
            #     value = creat.creat_str_number(v)
            # 将找到的依赖项逐一处理，使用正则表达式中的sub方法，sub(替换后的内容, 需要替换的字符串, 替换次数)
            request_data = params_re.sub(str(value), request_data, 1)
        return request_data


def save_response_to_json_file(id, res):
    '''
    将云端数据库查出的billid的结果存入json文件，以便后续用例判断是否授权成功
    存储时，以用例车牌为key，查出的billid为value
    :param id: 车牌
    :param res: 云端查出的billid
    :return:
    '''
    new_data = {id: res}
    # 如果 json 文件不存在，则创建
    if not os.path.exists(filepath.BILLID):
        with open(filepath.BILLID, 'w'):
            pass
    with open(filepath.BILLID, 'r') as j:
        try:
            comment = json.load(j)
        except json.decoder.JSONDecodeError:
            comment = new_data
        if comment:
            comment.update(new_data)
    with open(filepath.BILLID, 'w') as j:
        json.dump(comment, j, ensure_ascii=False, indent=4)
    with open(filepath.BILLID, "r") as j:
        comment = json.load(j)
        logger.info(f"存储code成功json文件信息为{comment}")


def get_data_from_json_file(key):
    '''
    从 json 文件中读取数据
    以用例ID为key，读取该用例执行后的Response，用作其他用例的依赖
    :param key:
    :return:
    '''
    with open(filepath.BILLID) as j:
        comment = json.load(j)
        return comment.get(key)


def get_host_ip():
    """

    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


if __name__ == "__main__":
    # print(generate_car())
    from testCases.Public import car
    # key = filepath.CONF.get("car", "wx_appId")
    # key = filepath.CONF.get("car", "wx_appId")
    # from common.processYaml import Yaml
    # read_data = Yaml(filepath.PARK, 1)
    # headers = read_data.headers
    # app_id = filepath.CONF.get("postpay", "app-id")
    # secret_key = filepath.CONF.get("postpay", "secret-key")
    # headers["app-id"] = app_id
    # headers["secret-key"] = secret_key
    # print(headers)
    # print(format_request_data_extend("$k{mc-app-id}", app_id))
    # print(format_request_data_extend("$k{mc-key}", secret_key))
    # save_response_to_json_file("川AV8888", "B6d4RSedZMorEU1CkbIIXE")
    # print("川AV8888".encode("GBK"))
    # print(get_data_from_json_file("川AV8888"))
    js = {
    "test_01": {
        "args": {},
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
            "Content-Length": "16",
            "Content-Type": "application/json",
            "Host": "172.18.0.8",
            "User-Agent": "python-requests/2.24.0"
        },
        "origin": "172.18.0.1",
        "url": "http://172.18.0.8/get"
    },
    "test_02": {
        "args": {},
        "data": "{\"custtel\": 132456789}",
        "files": {},
        "form": {},
        "headers": {
            "Accept": "*/* 1",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
            "Content-Length": "22",
            "Content-Type": "application/json",
            "Host": "172.18.0.9",
            "User-Agent": "python-requests/2.24.0"
        },
        "json": {
            "custtel": 132456789
        },
        "origin": "172.18.0.1",
        "url": "http://172.18.0.8/post"
    }
}
    v = "$..Content-headers[?(@.Host=='172.18.0.9')]"
    json_exe = parse(v)
    for i in json_exe.find(js):
        print(i.value)
    # print([i.context.value["Content-Length"] for i in json_exe.find(js) if i.value == "172.18.0.9"])