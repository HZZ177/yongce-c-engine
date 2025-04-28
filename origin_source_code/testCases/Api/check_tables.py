# -*-coding:utf-8-*-
"""
@Time:2021/11/25 15:31
@Author:for huangjunhao
@File:check_tables.py
@Software:PyCharmˉ
"""
# 【会员】
# 后付费表
import re

# import dictdiffer
import datetime
from common import filepath
from common.configLog import logger
from common.db_tool import DbTool
from common.processYaml import Yaml
from common.getCloudDataByFormal import GetCloudData, username, password, login_url, authenticate_url, get_url
from difflib import Differ

# 【会员】
superpark = ["mc_", "ps_", "user_"]
# ab test 表
ab_test = ["flow_"]
# 会员购物中心 表
member_mall = ["mm_"]
# stcop 表
stc_op = ["stc_op_"]

# 【广告】
# stcop 表
ad_stc_op = ["stc_op_"]
# 广告数据存储库
ad_advertisement = ["ad_"]
# 广告增值组库
user_added_value = ["user_"]

# 【寻车】
# 寻车所有库
find_car_all = [""]


def get_table_info(db_path):
    """
    得到需要查询的项目表信息字典
    @param db_path: 库名yaml文件所在
    """
    read_data = Yaml(db_path, 0)
    db_data = read_data.allDb
    db_obj = DbTool(db_data[0][0])
    if_itera = [("superpark_wx_test", "superpark", superpark), ("superpark_wx_test", "ab_test", ab_test),
                ("member_mall", "member_mall", member_mall), ("stc_op_test", "superpark", stc_op),
                ("advertisement_test", "superpark", ad_advertisement),
                ("user_added_value", "user_added_value", user_added_value),
                ("find_car", "find_car", find_car_all)]
    table_start_list = []
    for test_db, pro_db, table_start_keys in if_itera:
        if db_data[0][0]["db"] == test_db and db_data[0][1]["proDb"] == pro_db:
            table_start_list = table_start_keys
    if not table_start_list:
        raise Exception(f"暂不支持得到库【{db_data[0][0]['db']}】的表信息!")
    # 测试
    test_sql_table = "show tables like '{}%'"
    test_table_list = []
    test_sql_table_info = "show create table {}"
    test_table_info_list = []

    sql_table_list = [test_sql_table.format(table_key) for table_key in table_start_list]
    for sql_table in sql_table_list:
        test_table_list += [table[0] for table in db_obj.get_data_by_sql(sql=sql_table)]
    sql_table_info_list = [test_sql_table_info.format(table_key) for table_key in test_table_list]
    for sql_table_info in sql_table_info_list:
        test_table_info_list += [
            re.sub(r"AUTO_INCREMENT=[0-9]+\s", "", re.sub(r"DEFAULT\sCHARSET=[utf8|utf8mb4]{1,}\s", "", table_info[1])) for
            table_info in db_obj.get_data_by_sql(sql=sql_table_info)]
    test_table_dic = dict(zip(test_table_list, test_table_info_list))
    # print(test_table_dic)

    # 正式
    # 实例化正式环境查询对象
    cloud = GetCloudData(username, password, login_url, authenticate_url, get_url)

    pro_sql_table = "show tables like '{}%'"
    pro_table_list = []
    pro_sql_table_info = "show create table {}"
    pro_table_info_list = []
    pro_sql_table_list = [pro_sql_table.format(table_key) for table_key in table_start_list]
    for sql_table in pro_sql_table_list:
        pro_table_list += [table[0] for table in
                           cloud.get_data_by_sql(platform=db_data[0][1]["proExample"], database=db_data[0][1]["proDb"],
                                                 sql=sql_table, limit_num=0)["data"]["rows"]]
    # print(pro_table_list)
    # print(len(pro_table_list))
    pro_sql_table_info_list = [pro_sql_table_info.format(table_key) for table_key in pro_table_list]
    # print(pro_sql_table_info_list)
    for sql_table_info in pro_sql_table_info_list:
        pro_table_info_list += [
            re.sub(r"AUTO_INCREMENT=[0-9]+\s", "", re.sub(r"DEFAULT\sCHARSET=[utf8|utf8mb4]{1,}\s", "", table_info[1])) for
            table_info in cloud.get_data_by_sql(platform=db_data[0][1]["proExample"], database=db_data[0][1]["proDb"],
                                                sql=sql_table_info, limit_num=0)["data"]["rows"]]
    pro_table_dic = dict(zip(pro_table_list, pro_table_info_list))
    # print(pro_table_dic)
    return [test_table_dic, pro_table_dic]


def check_tables(project):
    """
    检查表结构
    @param project: 项目名 vip/ad 会员/广告
    """
    if project == "vip":
        superpark_tables = get_table_info(filepath.SUPERPARKWXTEST)
        member_tables = get_table_info(filepath.MEMBERMALL)
        ab_test_tables = get_table_info(filepath.DBABTEST)
        stc_op_tables = get_table_info(filepath.STCOPTEST)
        test_tables = superpark_tables[0].copy()
        test_tables.update(member_tables[0])
        test_tables.update(ab_test_tables[0])
        test_tables.update(stc_op_tables[0])
        pro_tables = superpark_tables[1].copy()
        pro_tables.update(member_tables[1])
        pro_tables.update(ab_test_tables[1])
        pro_tables.update(stc_op_tables[1])
    elif project == "ad":
        stc_op_tables = get_table_info(filepath.STCOPTEST)
        ad_test_tables = get_table_info(filepath.ADTEST)
        user_added_value_tables = get_table_info(filepath.USERADDEDVALUE)
        test_tables = stc_op_tables[0].copy()
        test_tables.update(ad_test_tables[0])
        test_tables.update(user_added_value_tables[0])
        pro_tables = stc_op_tables[1].copy()
        pro_tables.update(ad_test_tables[1])
        pro_tables.update(user_added_value_tables[1])
    elif project == "find_car":
        find_car_tables = get_table_info(filepath.FINDCAR)
        test_tables = find_car_tables[0].copy()
        pro_tables = find_car_tables[1].copy()
    else:
        raise Exception(f"暂不支持检查【{project}】项目的表结构！")
    with open(filepath.CHECKREPORT, "w", encoding="utf-8") as f:
        f.write(f"本次检测时间为【{str(datetime.datetime.now())}】\n")
        d = Differ()
        # for diff in list(dictdiffer.diff(test_tables, pro_tables)):
        for diff in list([]):
            if diff[0] == "change":
                diff_table = diff[1]
                diff = d.compare(diff[2][0].splitlines(), diff[2][1].splitlines())
                diff_str = ('\n'.join(list(diff)))
                f.write(f"表【{diff_table}】存在不同\n")
                f.write("======================================================\n")
                f.write(diff_str + "\n")
                f.write("======================================================\n")
            elif diff[0] == "add":
                for add_table in diff[2]:
                    f.write("======================================================\n")
                    f.write(f"表【{add_table[0]}】在测试环境不存在，在正式环境存在\n")
                    f.write("======================================================\n")
            elif diff[0] == "remove":
                for del_table in diff[2]:
                    f.write("======================================================\n")
                    f.write(f"表【{del_table[0]}】在正式环境不存在，在测试环境存在\n")
                    f.write("======================================================\n")


if __name__ == '__main__':
    # pass
    # get_table_info(filepath.USERADDEDVALUE)
    check_tables("ad")
    import os

    # print()
    # name = filepath.CHECKREPORT.split('\\')[-1]  # 切割出文件名称
    # filePath = r"C:\code\ktpostpaid\\"
