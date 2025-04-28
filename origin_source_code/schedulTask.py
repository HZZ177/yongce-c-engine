import datetime
import json
import time

import requests
import schedule as schedule
import redis
from common.file_tool import filetool
find_car_url = "https://find-car-admin-test.keytop.cn/find_car_admin/user/selectPageList"


def get_find_car_token():
    db_data = {
        "host": "120.55.20.180",
        "port": 6379,
        "password": "Keytop123",
        "db": "14"
    }
    redis_obj = redis.Redis(**db_data, decode_responses=True)
    user_token = [user_info.split("find_car:userToken:")[1] for user_info in redis_obj.keys("find_car:userToken:*") if "黄俊豪" in redis_obj.get(user_info)]
    return user_token[0]


def refresh_redis_token():
    manage_token = get_find_car_token()
    if not manage_token:
        raise Exception("寻车管理平台token获取失败！")
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "accesstoken": manage_token,
        "Accept": "application/json"
    }
    data = {
        "mail": "",
        "tel": "",
        "name": ""}
    res = requests.post(url=find_car_url, data=json.dumps(data), headers=headers, timeout=10)
    print(res.text)
    return res.status_code


def task():
    code = refresh_redis_token()
    if code == 200:
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"寻车管理平台刷新成功, 本次刷新时间为{now_time}")
    else:
        raise Exception("寻车管理平台token刷新失败")


if __name__ == '__main__':
    # refresh_redis_token()
    schedule.every(30).minutes.do(task)
    # schedule.every().saturday.at("13:15").do(clean_log)
    while True:
        schedule.run_pending()
        time.sleep(1)