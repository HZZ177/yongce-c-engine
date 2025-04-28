# -*-coding:utf-8-*-
"""
@Time:2022-7-15 10:54:18
@Author:for chenqilin
@File:check_tablesnew.py
@Software:PyCharmˉ
"""
import datetime

from common import filepath
from common.db_tool import DbTool
from common.getCloudDataByFormal import GetCloudData, username, password, login_url, authenticate_url, get_url
from common.processYaml import Yaml


# 【停车卡】

def compare_colmns(db_path, csrftoken, sessionid):
    # 对比结果
    diff_result = ""
    read_data = Yaml(db_path, 0)
    db_data = read_data.allDb
    table_schema = db_data[0][2]["table_schema"]

    sql_table = f"select TABLE_NAME from information_schema.TABLES where TABLE_SCHEMA  = '{table_schema}' "

    # 取正式表
    cloud = GetCloudData(username, password, login_url, authenticate_url, get_url)
    cloud.cookies = {"csrftoken": csrftoken,
                     "sessionid": sessionid}
    pro_table_list = []
    pro_table_list += [table[0] for table in
                       cloud.get_data_by_sql(platform=db_data[0][1]["proExample"], database=db_data[0][1]["proDb"],
                                             sql=sql_table, limit_num=0)["data"]["rows"]]

    # 取测试表
    db_obj = DbTool(db_data[0][0])
    test_table_list = []
    test_table_list += [table[0] for table in db_obj.get_data_by_sql(sql=sql_table)]

    # 数据对比
    extra_table = []  # 多余的表存起来

    if len(pro_table_list) > len(test_table_list):
        # print(f"正式环境多了这些表：{set(pro_table_list) - set(test_table_list)}")
        diff_result += f"{'*' * 50}\n"
        diff_result += f"正式环境多了这些表：{set(pro_table_list) - set(test_table_list)}\n"

    if len(pro_table_list) < len(test_table_list):
        # print(f"测试环境多了这些表：{set(test_table_list) - set(pro_table_list)}")
        diff_result += f"{'*' * 50}\n"
        diff_result += f"测试环境多了这些表：{set(test_table_list) - set(pro_table_list)}\n"

    table_list = pro_table_list if len(pro_table_list) < len(test_table_list) else test_table_list

    sql_columns = f"select TABLE_NAME ,COLUMN_NAME ,ORDINAL_POSITION ,COLUMN_DEFAULT ,IS_NULLABLE ,COLUMN_TYPE ," \
                  f"COLUMN_KEY ,EXTRA ,COLUMN_COMMENT  from information_schema.COLUMNS " \
                  f"where TABLE_SCHEMA  = '{table_schema}' and TABLE_NAME in {tuple(table_list)}"
    # sql_columns = f"select TABLE_NAME ,COLUMN_NAME ,ORDINAL_POSITION ,COLUMN_DEFAULT ,IS_NULLABLE ,COLUMN_TYPE ,COLUMN_KEY ,EXTRA ,COLUMN_COMMENT  from information_schema.COLUMNS where TABLE_SCHEMA  = 'city_parking_card' and TABLE_NAME = 'cpc_order'"

    # 取测试的表详情
    test_columns_tuple = db_obj.get_data_by_sql(sql=sql_columns)
    test_columns_dict = {}
    pro_columns_dict = {}

    for colnum in test_columns_tuple:
        # test_columns_dict[str(colnum[0]) + '+' + str(colnum[1])] = list(colnum[2:])
        if str(colnum[0]) not in test_columns_dict.keys():
            test_columns_dict[str(colnum[0])] = {}
        test_columns_dict[str(colnum[0])][str(colnum[1])] = list(colnum[2:])

    # 取正式的表详情
    pro_columns_list = cloud.get_data_by_sql(platform=db_data[0][1]["proExample"], database=db_data[0][1]["proDb"],
                                             sql=sql_columns, limit_num=0)["data"]["rows"]

    for colnum in pro_columns_list:
        # pro_columns_dict[str(colnum[0]) + '+' + str(colnum[1])] = list(colnum[2:])
        if str(colnum[0]) not in pro_columns_dict.keys():
            pro_columns_dict[str(colnum[0])] = {}
        pro_columns_dict[str(colnum[0])][str(colnum[1])] = list(colnum[2:])
    # print(test_columns_dict)
    # print(pro_columns_dict)
    main_columns_dict = pro_columns_dict if len(pro_table_list) < len(test_table_list) else test_columns_dict
    another_columns_dict = test_columns_dict if len(pro_table_list) < len(test_table_list) else pro_columns_dict
    # 对比详细字段
    special_col = {"create_time": 1, "update_time": 0}
    for key in main_columns_dict.keys():
        # table_name = key.split('+')[0]
        table_name = key
        for col_name, col_value in another_columns_dict[table_name].items():
            # 比对字段缺失
            main_col_name = main_columns_dict[table_name].get(col_name)
            if not main_col_name:
                if len(pro_table_list) < len(test_table_list):
                    # print('*' * 50)
                    # print(f"测试环境表{table_name}缺少字段{col_name}")
                    diff_result += f"{'*' * 50}\n"
                    diff_result += f"正式环境表{table_name}缺少字段{col_name}\n"
                else:
                    # print(f"正式环境表{table_name}缺少字段{col_name}")
                    diff_result += f"测试环境表{table_name}缺少字段{col_name}\n"
                continue
            # 比对特殊字段位置
            # 正式环境字段值
            pro_col_info = pro_columns_dict[table_name][col_name][:6]
            pro_col_remark = pro_columns_dict[table_name][col_name][6]
            # 测试环境字段值
            test_col_info = test_columns_dict[table_name][col_name][:6]
            test_col_remark = test_columns_dict[table_name][col_name][6]
            if col_name in special_col.keys():
                pro_col_location = pro_col_info[0]
                pro_col_len = len(pro_columns_dict[table_name])
                test_col_location = test_col_info[0]
                test_col_len = len(test_columns_dict[table_name])
                if test_col_location != test_col_len - special_col[col_name] or pro_col_location != pro_col_len - special_col[col_name]:
                    diff_result += f"{'*' * 50}\n"
                    diff_result += f"表名:{table_name}\n"
                    diff_result += f"字段名:{col_name}\n"
                    diff_result += f"字段顺序错误！\n"
                    diff_result += f"【正式环境】【{col_name}】字段顺序当前为【{pro_col_location}】，实际应为【{pro_col_len - special_col[col_name]}】\n"
                    diff_result += f"【测试环境】【{col_name}】字段顺序当前为【{test_col_location}】，实际应为【{test_col_len - special_col[col_name]}】\n"
            test_col_info.pop(0)
            pro_col_info.pop(0)
            if pro_col_info != test_col_info or pro_col_remark.replace(' ', '') != test_col_remark.replace(' ', ''):
                diff_result += f"{'*' * 50}\n"
                diff_result += f"表名:{table_name}\n"
                diff_result += f"字段名:{col_name}\n"
                diff_result += f"【正式环境】字段详情:[默认值={pro_col_info[0]},IS_NULLABLE={pro_col_info[1]},字段类型={pro_col_info[2]},索引={pro_col_info[3]},EXTRA={pro_col_info[4]},备注={pro_col_remark}]\n"
                diff_result += f"【测试环境】字段详情:[默认值={test_col_info[0]},IS_NULLABLE={test_col_info[1]},字段类型={test_col_info[2]},索引={test_col_info[3]},EXTRA={test_col_info[4]},备注={test_col_remark}]\n"
                diff_result += f"{'*' * 50}\n"

    return diff_result
                # elif pro_columns_dict[key] != test_columns_dict[key]:
        #     print(pro_columns_dict)
        #     print('*' * 50)
        #     print(f"表名:{table_name}")
        #     print(f"字段名:{colnum_name}")
        #     print(
        #         f"【正式环境】字段详情:[字段的排序={pro_columns_dict[key][0]},默认值={pro_columns_dict[key][1]},IS_NULLABLE={pro_columns_dict[key][2]},字段类型={pro_columns_dict[key][3]},索引={pro_columns_dict[key][4]},EXTRA={pro_columns_dict[key][5]},备注={pro_columns_dict[key][6]}]")
        #     print(
        #         f"【测试环境】字段详情:[字段的排序={test_columns_dict[key][0]},默认值={test_columns_dict[key][1]},IS_NULLABLE={test_columns_dict[key][2]},字段类型={test_columns_dict[key][3]},索引={test_columns_dict[key][4]},EXTRA={test_columns_dict[key][5]},备注={test_columns_dict[key][6]}]")
        # elif pro_columns_dict[key][0] != test_columns_dict[key][0]:
        #     print("字段的排序建议SQL：")
        #     # print(f"ALTER TABLE {table_name} MODIFY {colnum_name} 数据类型  AFTER 字段名2;")
        # elif pro_columns_dict[key][1] != test_columns_dict[key][1]:
        #     print("字段的默认值不一致，建议SQL：")
        #     print(f"alter table {table_name} alter `{colnum_name}` set default '5';")
        # else:
        #     pass
# IS_NULLABLE、备注、索引


def check_tables(project, csrftoken, sessionid):
    if project == "cpc":
        diff_result = compare_colmns(filepath.CITYPARKINGCARD, csrftoken, sessionid)
        with open(filepath.CHECKREPORT, "w", encoding="utf-8") as f:
            f.write(f"本次检测完成时间为【{str(datetime.datetime.now())}】\n")
            f.write(diff_result)


if __name__ == '__main__':
    # compare_colmns(filepath.CITYPARKINGCARD)
    check_tables('cpc', "aHnku5SDFXepbxbcKidILgWgZt7aPHuBeWLPQu20eZ7jXwJZ2zBFN41zrT1Y1oBO", "tv5naxdmlmtkad6eaf9679rx27k68li9")
    # check_tables("cpc")



