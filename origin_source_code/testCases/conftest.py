import pytest
import sys
import os
import time
import json
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from common.file_tool import filetool
from testCases.Public import public, mobile
from common import filepath, util, page
from common.configLog import logger
from testCases.Page import login_archery, sqlquery

taskInfo_path = ""


@pytest.fixture(scope="session", autouse=True)
def session_setup():
    # 本地运行的
    logger.info("=================================【【正在进行session级前置处理】】=================================")
    lot_id = filepath.CONF.get('advanced', 'lotId')
    kttoken = public.login(lot_id)
    wx_appId = filepath.CONF.get('car', 'wx_appId')
    server_ip = filepath.CONF.get('advanced', 'ServerIP')
    # 查询场端最近的入场信息id
    vip_car = filepath.CONF.get('car', 'vip_carNo')
    after_car = filepath.CONF.get('car', 'after_carNO')
    special_car = filepath.CONF.get('car', 'special_carNo')
    vip_rights_id = public.get_local_rights_info(vip_car).get("data")[0][2]
    after_rights_id = public.get_local_rights_info(after_car).get("data")[0][2]
    special_rights_id = public.get_local_rights_info(special_car).get("data")[0][2]
    util.save_response_to_json_file(vip_car, vip_rights_id)
    util.save_response_to_json_file(after_car, after_rights_id)
    util.save_response_to_json_file(special_car, special_rights_id)
    # 储存最近的easytesttoken
    token = mobile.login_easytest()
    util.save_response_to_json_file("token", token)
    yield kttoken, lot_id, wx_appId
    logger.info("=================================【【正在进行session级后置处理】】=================================")
    # 删除7天前的log
    filetool.del_folder(diff_day=7)
# @pytest.fixture(scope="session", autouse=True)
# def session_setup(process_easytest):
#     # 服务器运行的
#     logger.info("【【正在进行session级前置处理】】")
#     with open(filepath.FILE_REPORT_PATH, 'w') as td:
#         td.write('0.00%')
#     logger.info('重置通过率为0.00%')
#     lot_id, task_id = process_easytest
#     # 正式环境的参数校验
#     # public.check_formal(lot_id)
#     global taskInfo_path
#     taskInfo_path = os.path.join(filepath.TASKINFO_PATH, str(task_id) + ".json")
#     kttoken = public.login(lot_id)
#     # 关闭车位控制
#     entrances.controlPark(kttoken, lot_id, 0)
#     # 设置含‘军’车辆自动放行
#     entrances.startSpecial(kttoken, lot_id, 1)
#     return kttoken, lot_id
#
#
# @pytest.fixture(scope="session")
# def process_easytest():
#     # 服务器运行的
#     try:
#         token = public.easy_login()
#         public.startTaskTest(token)
#         test_info = public.currentTaskRunPlatform(token)
#         task_id = test_info["data"]['taskId']
#         runPlatform = test_info["data"]["runPlatform"]
#         # lot_id = filepath.CONF.get('advanced', 'lotId_CM3') if runPlatform == "1" else filepath.CONF.get('advanced',
#         #                                                                                                  'lotId_X86')
#         plat_form_name = "CM3+" if runPlatform == "1" else "X86"
#         lot_id = filepath.CONF.get('advanced', 'lotId_CM3') if runPlatform == "1" else filepath.CONF.get('advanced',
#                                                                                                      'lotId_CM3')
#         logger.info("运行平台:%s, lot_id:%s" % (plat_form_name, lot_id))
#         return lot_id, task_id
#     except Exception as msg:
#         raise Exception(logger.error(msg))
#
#
# def pytest_terminal_summary(terminalreporter, exitstatus, config):
#     """收集测试结果 """
#     try:
#         # print(terminalreporter.stats)
#         print("total:", terminalreporter._numcollected)
#         print('passed:', len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown']))
#         print('failed:', len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown']))
#         print('error:', len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown']))
#         print('skipped:', len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown']))
#         print('ratio：%.2f' % (len(terminalreporter.stats.get('passed', []))/terminalreporter._numcollected*100)+'%')
#         total = terminalreporter._numcollected
#         passed = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
#         util.process_rotio(total, passed, taskInfo_path)
#         # terminalreporter._sessionstarttime 会话开始时间
#         duration = time.time() - terminalreporter._sessionstarttime
#         print('total times:', duration, 'seconds')
#     except Exception as e:
#         raise Exception(logger.error(e))


if __name__ == "__main__":
    taskInfo_path = os.path.join(filepath.TASKINFO_PATH, str(666) + ".json")
    # task_info = {"total": 2, "passed": 1}
    # with open(taskInfo_path, "a+") as f:
    #     f.write(json.dumps(task_info))
    #     f.write("\n")
    with open(taskInfo_path, "r+") as f:
        a = f.readlines()
    for i in a:
        print(eval(i)['total'])
        print(type(eval(i)['total']))
