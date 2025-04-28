# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
===================================
@FileName: filepath.py
@Description: 文件路径管理
@Author: wurun
@Software: PyCharm
@Version: 1.0
@Update:
@Copyright: 
===================================
"""

import os
import time
from configparser import ConfigParser

'''项目目录'''
PRO_PATH = os.path.dirname(os.path.realpath(__file__))  # 获取项目目录

'''一级目录'''
RESULT_PATH = os.path.join(PRO_PATH, 'result')  # 测试报告/日志存放目录
TEST_CASE_PATH = os.path.join(PRO_PATH, '../testCases')  # 测试用例存放目录
TEST_DATA_PATH = os.path.join(PRO_PATH, '../testDatas')  # 测试文件存放目录
LOG_PATH = os.path.join(PRO_PATH, '../logs')  # 日志文件存放目录
REPORT_PATH = os.path.join(PRO_PATH, '../reports')  # 测试报告存放目录
TASKINFO_PATH = os.path.join(PRO_PATH, '../taskInfo')  # 测试任务信息存放目录

FILES = os.path.join(PRO_PATH, '../Files')  # 测试所需第三方文件存放目录

'''二级目录'''
DSP_PATH = os.path.join(TEST_DATA_PATH, 'dsp')      # dsp参数目录
CONFIG_PATH = os.path.join(TEST_DATA_PATH, 'config')    # 配置参数目录
LOGIN_PATH = os.path.join(TEST_DATA_PATH, 'login')      # 登录参数目录
DEVICE_PATH = os.path.join(TEST_DATA_PATH, 'devices')      # 添加设备目录

EASYTEST_PATH = os.path.join(TEST_DATA_PATH, 'mobile')      # easyTest操作目录
CHARGE_PATH = os.path.join(TEST_DATA_PATH, 'charge')      # 收费操作目录
LOTSETTING_PATH = os.path.join(TEST_DATA_PATH, 'lotSetting')      # 车场配置操作目录

RIGHTS_PATH = os.path.join(TEST_DATA_PATH, 'rights')   # 授权信息检验目录
PARK_PATH = os.path.join(TEST_DATA_PATH, 'park')  # 车场配置信息检验目录
CAR_PATH = os.path.join(TEST_DATA_PATH, 'car')      # 车辆信息校验目录
API_PATH = os.path.join(TEST_DATA_PATH, 'api')      # 接口信息目录
DB_PATH = os.path.join(TEST_DATA_PATH, 'db')      # 数据库信息目录

FILE_REPORT_PATH = os.path.join(REPORT_PATH, 'testRatio.txt')  # 测试报告存放目录


'''三级目录'''
USERTOKEN = os.path.join(CAR_PATH, 'UserToken.yaml')  # 用户token
# USERTOKEN = os.path.join(CAR_PATH, 'UserTokenMysql.yaml')  # 用户token
CLOUDRIGHTS = os.path.join(RIGHTS_PATH, 'CloudRights.yaml')  # 云端授权信息检验
LOCALRIGHTS = os.path.join(RIGHTS_PATH, 'LocalRights.yaml')  # 场端授权信息检验
CARCOMES = os.path.join(RIGHTS_PATH, 'CarComes.yaml')  # 入场记录信息
PARK = os.path.join(PARK_PATH, 'Park.yaml')  # 车场配置信息校验
PARKLIST = os.path.join(PARK_PATH, 'ParkList.yaml')  # 车场列表信息
EDITPARK = os.path.join(PARK_PATH, 'EditPark.yaml')  # 编辑车场信息
GETPARKPAYINFO = os.path.join(PARK_PATH, 'park_payinfo.yaml')  # 得到订单信息
GETPARKPAYINFO_PRO = os.path.join(PARK_PATH, 'park_payinfo_pro.yaml')  # 得到订单信息
NOTICE_PRO = os.path.join(PARK_PATH, 'notice_pro.yaml')  # 得到支付完成信息
NOTICE = os.path.join(PARK_PATH, 'notice.yaml')  # 得到支付完成信息
OWEBILL = os.path.join(CAR_PATH, 'OweBill.yaml')  # 车辆临时欠费信息校验
OWEORDER = os.path.join(CAR_PATH, 'OweOrder.yaml')  # 车辆欠费订单信息校验
VIPINFOBYDB = os.path.join(CAR_PATH, 'VipInfoByDB.yaml')  # 得到车辆会员信息
VIPINFOBYDBV2 = os.path.join(CAR_PATH, 'VipInfoByDBV2.yaml')  # 得到车辆新会员表信息
GETSENDPLANCONFIGID = os.path.join(CAR_PATH, 'GetSendPlanConfigId.yaml')  # 得优惠卷配置id
GETSENDPLANCONFIG = os.path.join(CAR_PATH, 'GetSendPlanConfig.yaml')  # 得优惠卷配置
GETSENDPLAN = os.path.join(CAR_PATH, 'GetSendPlan.yaml')  # 得优惠卷发放计划
VIPUSER = os.path.join(CAR_PATH, 'VipUser.yaml')  # 车辆会员信息校验
OPENVIP = os.path.join(CAR_PATH, "OpenVip.yaml")  # 车辆开通老会员
OPENVIPV2 = os.path.join(CAR_PATH, "OpenVipV2.yaml")  # 车辆开通新会员
CLOSEVIP = os.path.join(CAR_PATH, "CloseVip.yaml")  # 车辆关闭会员
MODIFYLPN = os.path.join(CAR_PATH, "ModifyLpn.yaml")  # 修改会员的优惠券可用车牌
OPENVIPINFOBYDB = os.path.join(CAR_PATH, "OpenVipInfoByDB.yaml")  # 车辆开通会员的订单信息
GETCREDITSCOREBYDB = os.path.join(CAR_PATH, "GetCreditScoreByDB.yaml")  # 会员的信用分据库信息
GETCREDITSCORE = os.path.join(CAR_PATH, "GetCreditScore.yaml")  # 会员的信用分接口信息
CHANGEPOSTPAIDSTATUS = os.path.join(CAR_PATH, "ChangePostpaidStatus.yaml")  # 更改后付费状态
GETPOSTPAIDINFOBYBD = os.path.join(CAR_PATH, "GetPostpaidInfoByDB.yaml")  # 得到后付费数据库基本信息
GETPOSTPAIDCHANGEINFO = os.path.join(CAR_PATH, "GetPostpaidChangeInfo.yaml")  # 得到后付费变更记录的数据库基本信息
SETPOSTPAIDFAILURE = os.path.join(CAR_PATH, "SetPostpaidFailure.yaml")  # 将后付费状态置为失效
SETPOSTPAIDUSERTOOLD = os.path.join(CAR_PATH, "SetPostpaidUserToOld.yaml")  # 将后付费用户置为旧用户
POSTPAIDPARKLIST = os.path.join(CAR_PATH, "PostpaidParkList.yaml")  # 后付费车场列表
FINDPARKINGLOTS = os.path.join(CAR_PATH, "FindParkingLots.yaml")  # 寻找车场列表
BANNERPARKINGLOTS = os.path.join(CAR_PATH, "BannerParkingLots.yaml")  # banner车场列表
ONPARK = os.path.join(CAR_PATH, 'OnPark.yaml')  # 车辆在场信息校验
DISABLELOT = os.path.join(CAR_PATH, 'DisabledLot.yaml')  # 车辆禁用场端信息校验
EDITDISABLELOT = os.path.join(CAR_PATH, 'EditDisabledLot.yaml')  # 增加/删除车辆禁用车场信息
EDITPOSTCITY = os.path.join(CAR_PATH, 'EditPostCity.yaml')  # 修改后付费用户可用城市信息
EDITUSERCITY = os.path.join(CAR_PATH, 'EditUserCity.yaml')  # 修改后用户默认城市信息
ADDWHITELIST = os.path.join(CAR_PATH, 'AddWhiteList.yaml')  # 增加用户白名单
QUERYWHITELIST = os.path.join(CAR_PATH, 'QueryWhiteList.yaml')  # 查询用户白名单列表
DELWHITELIST = os.path.join(CAR_PATH, 'DelWhiteList.yaml')  # 删除用户白名单列表
PRIVACYCAR = os.path.join(CAR_PATH, 'PrivacyCar.yaml')  # 车辆隐私车牌信息校验
BINDCARNO = os.path.join(CAR_PATH, 'BindCarNo.yaml')  # 绑定车辆默认车牌
PAYMENTBLACKLIST = os.path.join(CAR_PATH, 'PaymentBlackList.yaml')  # 车辆信用付黑名单信息校验
ADDPAYMENTBLACKLIST = os.path.join(CAR_PATH, 'AddPaymentBlackList.yaml')  # 增加车辆信用付黑名单信息
DELPAYMENTBLACKLIST = os.path.join(CAR_PATH, 'DellPaymentBlackList.yaml')  # 删除车辆信用付黑名单信息
BIBLACK = os.path.join(CAR_PATH, 'BIBlack.yaml')  # 特权放行车辆BI黑名单信息接口校验
INSERTBIBLACK = os.path.join(CAR_PATH, 'InsertBIBlack.yaml')  # 插入BI黑名单信息
REMOVEBIBLACK = os.path.join(CAR_PATH, 'RemoveBIBlack.yaml')  # 插入BI黑名单信息
BICARDATA = os.path.join(CAR_PATH, 'BiCarData.yaml')  # 特权放行车辆BI特权放行_v2信息接口校验
BICARDATA_V1 = os.path.join(CAR_PATH, 'BiCarDataV1.yaml')  # 特权放行车辆BI特权放行_v1信息接口校验
CARCITY = os.path.join(CAR_PATH, 'CarCity.yaml')  # 车辆城市校验
AFTERBINDING = os.path.join(CAR_PATH, 'AfterBinding.yaml')  # 后付费车辆绑定车牌校验
ABTEST = os.path.join(CAR_PATH, 'ABTest.yaml')  # 用户AB测试白名单校验
GETWXTOKEN = os.path.join(CAR_PATH, 'GetWxToken.yaml')  # 得到微信原始token
USERWX = os.path.join(CAR_PATH, 'UserWx.yaml')  # 得到用户的微信相关信息
POSTSETTING = os.path.join(CAR_PATH, 'PostSetting.yaml')  # 得到用户的后付费设置相关信息
ADDPOSTLPN = os.path.join(CAR_PATH, 'AddPostLpn.yaml')  # 增加后付费车辆
REMOVEPOSTLPN = os.path.join(CAR_PATH, 'RemovePostLpn.yaml')  # 移除后付费车辆
USERINFO = os.path.join(CAR_PATH, 'UserInfo.yaml')  # 得到用户相关信息
USERINFOBYMMS = os.path.join(CAR_PATH, 'UserInfoByMms.yaml')  # 通过中台接口得到用户相关信息
ONPARKBYMMS = os.path.join(CAR_PATH, 'OnParkByMms.yaml')  # 通过中台接口得到车辆在场相关信息
DELONPARKBYMMS = os.path.join(CAR_PATH, 'DelOnParkByMms.yaml')  # 通过中台接口删除车辆在场相关信息
ADDONPARKBYMMS = os.path.join(CAR_PATH, 'AddOnParkByMms.yaml')  # 通过中台接口增加车辆在场相关信息
OWEBILLBYMMS = os.path.join(CAR_PATH, 'OweBillByMms.yaml')  # 通过中台接口得到车辆6.X车场临时账单相关信息
ONRIGHTSBYMMS = os.path.join(CAR_PATH, "OnRightsByMms.yaml")  # 通过中台接口查询用户能否被后付费授权
GETPIKADATA = os.path.join(CAR_PATH, "GetPikaData.yaml")  # 得到pika数据
UPDATEPIKADATA = os.path.join(CAR_PATH, "UpdatePikaData.yaml")  # 修改pika数据

REDSPSERVER = os.path.join(DSP_PATH, 'restartDspServer.yaml')    # 重启dspserver参数
LOGIN = os.path.join(LOGIN_PATH, 'login.yaml')      # 登录参数
# SETTING = os.path.join(CONFIG_PATH, 'setting.conf')     # 配置参数,本地
SETTING = os.path.join(CONFIG_PATH, 'test_setting.conf')     # 配置参数，测试
# SETTING = os.path.join(CONFIG_PATH, 'pro_setting.conf')     # 配置参数，正式
BILLID = os.path.join(CONFIG_PATH, 'billId.json')     # 云端billid json文件
CHANNELSEND = os.path.join(DSP_PATH, 'ChannelSend.yaml')    # 直接通过通道调用云端接口

EASYLOGIN = os.path.join(EASYTEST_PATH, 'login.yaml')      # easyTest登录参数
POSTCASERUNNING = os.path.join(EASYTEST_PATH, 'postCaseRunning.yaml')  # 提交用例执行状态
POSTCAROUT = os.path.join(EASYTEST_PATH, 'PostCarOut.yaml')  # 提交出场记录
GETCARPAY = os.path.join(EASYTEST_PATH, 'getCarPay.yaml')  # 得到支付结果
POSTCARPAY = os.path.join(EASYTEST_PATH, 'postCarPay.yaml')  # 提交支付记录
POSTPAIDAUTH = os.path.join(EASYTEST_PATH, "PostPaidAuth.yaml")  # 提交场端授权记录
GETCARINNOTICE = os.path.join(EASYTEST_PATH, "getCarInNotice.yaml")  # 得到入场通知结果
POSTCARINNOTICE = os.path.join(EASYTEST_PATH, "postCarInNotice.yaml")  # 提交入场通知结果
POSTVIPPAYMENTURL = os.path.join(EASYTEST_PATH, "PostVIPPaymentUrl.yaml")  # 提交支付链接
POSTVIPPAYMENTRES = os.path.join(EASYTEST_PATH, "PostVIPPaymentRes.yaml")  # 提交开通结果
GETVIPPAYMENTRES = os.path.join(EASYTEST_PATH, "getVIPPaymentRes.yaml")  # 得到开通结果

GETWXTOKENAPI = os.path.join(API_PATH, "get_wx_token.yaml")  # 微信token
DEVICEONAPI = os.path.join(API_PATH, "device_On.yaml")  # 设备上线
DEVICEOFFAPI = os.path.join(API_PATH, "device_Off.yaml")  # 设备下线
CARINAPI = os.path.join(API_PATH, "car_In.yaml")  # 进行入车
CAROUTAPI = os.path.join(API_PATH, "car_Out.yaml")  # 进行出车
PAYORDERAPI = os.path.join(API_PATH, "Pay_Order.yaml")  # 进行支付
REFUNDAPI = os.path.join(API_PATH, "refund.yaml")  # 进行退费
CHECKDBTABLES = os.path.join(API_PATH, "checkDbTables.yaml")  # 检查库表
GETUSERTOKEN = os.path.join(API_PATH, "getUserToken.yaml")  # 得到用户accessToken
UPDATEUSERPORTRAIT = os.path.join(API_PATH, "update_user_portrait.yaml")  # 修改biopen用户画像
TESTPSCHANNEL = os.path.join(API_PATH, "test_ps_channel.yaml")  # 测试 test_ps_channel


MEMBERMALL = os.path.join(DB_PATH, "memberMall.yaml")  # 检查库表 member_mall
STCOPTEST = os.path.join(DB_PATH, "stcopTest.yaml")  # 检查库表 stc_op_test
DBABTEST = os.path.join(DB_PATH, "superParkWxTest.yaml")  # 检查库表 ab_test
SUPERPARKWXTEST = os.path.join(DB_PATH, "superParkWxTestPostpaid.yaml")  # 检查库表 superpark_wx_test
ADTEST = os.path.join(DB_PATH, "adTest.yaml")  # 检查库表 advertisement_test
USERADDEDVALUE = os.path.join(DB_PATH, "userAddedValue.yaml")  # 检查库表 user_added_value
FINDCAR = os.path.join(DB_PATH, "findCarRDS.yaml")  # 检查库表 find_car
CHECKREPORT = os.path.join(REPORT_PATH, "check_report.txt")  # 检查报告地址
STCUSERTOKEN = os.path.join(DB_PATH, 'UserTokenMysql.yaml')  # 用户token

CITYPARKINGCARD = os.path.join(DB_PATH, "cityParkingCard.yaml")  # 检查库表 superpark_wx_test





'''四级目录'''


'''失败用例'''


def fetch_path(dir_path):
    """
       生成目录路径
       * @ param path: 目录路径
       * @ return 若目录不存在，则生成
    """
    path = os.path.join(PRO_PATH, dir_path)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def fetch_path_with_d(dir_path, suffix):
    """
       生成文件路径
       * @ param dir_path: 路径
       * @ param suffix: 文件名后缀
       * @ return 路径+当前日期+当前时间+后缀
    """
    day = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    now = time.strftime('%H_%M_%S', time.localtime(time.time()))
    file_path = os.path.join(fetch_path(dir_path), day)
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    file_name = os.path.join(file_path, now + suffix)
    return file_name


def del_file(path):
    """
        删除文件
        * @ param path: 需要清除文件夹的路径
    """
    for i in os.listdir(path):
        path_file = os.path.join(path, i)  # 取文件绝对路径
        if os.path.isfile(path_file):
            os.remove(path_file)
        else:
            del_file(path_file)


CONF = ConfigParser()
CONF.read(SETTING, encoding="utf-8")

if __name__ == '__main__':
    # print(CONF_PATH.split("\\")[-1])
    # print(XML_REPORT_PATH)
    del_file(os.path.join(PRO_PATH, '.coverage'))