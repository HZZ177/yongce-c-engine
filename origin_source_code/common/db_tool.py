"""
@File    : db_tool.py
@Time    : 2020-11-17 10:20
@Author  : huangjunhao
@Software: PyCharm
备注：数据库处理类
"""
import pymysql
# from sshtunnel import SSHTunnelForwarder
# from common import config as conf
from common import filepath
from common.configLog import logger


class DbTool:
    def __init__(self, db_conf=None):
        # self.ssh_conf = filepath.CONF.get("db_ssh")   # 如配置文件中有ssh跳板机设置时，需要打开
        if not db_conf:
            self.db_conf = dict(filepath.CONF.items('db'))
            self.db_conf["port"] = int(self.db_conf.get("port"))
        else:
            self.db_conf = db_conf

    def get_data_by_sql(self, sql, ssh_tag=0, postgres_tag=0):
        """
        :param sql: 查询语句
        :param ssh_tag: 是否需要跳板机进行数据库连接 0/1 (默认不连跳板机)
        :return: 查询结果
        """
        # if ssh_tag:
        #     server = SSHTunnelForwarder(**conf.SSH_config)
        #     server.start()
        #     conf.mysql_config['port'] = server.local_bind_port
        # # 有跳板机配置
        if postgres_tag:
            # 更改键名 db为database
            self.db_conf.update({"database": self.db_conf.pop("db")})
            # conn = psycopg2.connect(**self.db_conf)

        else:
            conn = pymysql.connect(**self.db_conf)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()
        except BaseException as e:
            conn.rollback()
            raise (f"执行出错原因为{e}")
        finally:
            conn.close()
            # if ssh_tag:
            #     server.close()

    def control_db_by_sql(self, sql, ssh_tag=0):
        # if ssh_tag:
        #     server = SSHTunnelForwarder(**conf.SSH_config)
        #     server.start()
        #     conf.mysql_config['port'] = server.local_bind_port
        # 有跳板机配置
        conn = pymysql.connect(**self.db_conf)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                # 提交到数据库执行
                conn.commit()
                # print("提交执行！")
        except BaseException as e:
            conn.rollback()
            # print("提交回滚！")
            # print(f"报错：{e}")
            raise Exception(logger.error(f"{e}"))
        finally:
            conn.close()
            # if ssh_tag:
            #     server.close()

    def get_first_data(self, sql, ssh_tag=0, postgres_tag=0):
        """
            :param sql: 查询语句
            :param ssh_tag: 是否需要跳板机进行数据库连接 0/1 (默认不连跳板机)
            :return: 查询结果
            """
        return self.get_data_by_sql(sql, ssh_tag, postgres_tag)[0][0]

    def delete_register(self):
        sql_1 = f"DELETE FROM t_ecif_account WHERE account='13982196547';DELETE FROM t_ecif_user WHERE phone='13982196547';DELETE FROM t_ecif_company WHERE NAME LIKE '%13982196547%';"
        self.control_db_by_sql(sql_1)
        # sql_2 = f"DELETE FROM t_ecif_user WHERE phone='13982196547';"
        # control_db_by_sql(sql_2, 1)
        # print("清理测试数据2成功！")
        # sql_3 = f"DELETE FROM t_ecif_company WHERE NAME LIKE '%13982196547%';"
        # control_db_by_sql(sql_3, 1)
        # print("清理测试数据3成功！")


db_obj = DbTool()

if __name__ == '__main__':
    # DbTool().delete_register()
    # pass
    # from configparser import ConfigParser
    # from common import filepath
    # CONF = ConfigParser()
    # CONF.read(filepath.SETTING, encoding="utf-8")
    # dict(CONF.items("db"))['port']
    sql_1 = f"SELECT isCancel FROM t_592011611_credible_user WHERE carNo = '川AHJH888';"
    sql = f"SELECT id FROM st_592011611_income_daily_collect_report;"
    # print(DbTool().get_first_data(sql=sql))
    # print(type(DbTool().get_data_by_sql(sql=sql_1)[0][0]))
