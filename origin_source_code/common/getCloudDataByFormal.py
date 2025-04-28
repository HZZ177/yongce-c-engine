from common.request import request
from common.configLog import logger
import requests
from common import util


# 收费系统分区与库对应字典
PLATFORM = {
    "收费系统主库1-华为云": ('cloud_system', 'nkc-job', 'park1', 'park2', 'park3', 'park4', 'park5', 'park6', 'parkmanager'),
    "收费系统主库2-华为云": ('park7', 'park8', 'park9', 'park10', 'park11'),
    "收费系统主库3-华为云": ('park12', 'park13', 'park14', 'park15', 'park16'),
    "收费系统主库4-华为云": ('park17', 'park18', 'park19', 'park20', 'park21'),
    "收费系统主库5-华为云": ('park22', 'park23', 'park24', 'park25', 'park26'),
    "收费系统主库6-华为云": ('park27', 'park28', 'park29', 'park30', 'park31'),
}
# 正式环境查询实例化所需参数
login_url = "https://archery.keytop.cn:8100/login/"
username = "chenqilin"
password = "chenqilin"
authenticate_url = "https://archery.keytop.cn:8100/authenticate/"
get_url = "https://archery.keytop.cn:8100/query/"


class GetCloudData:

    def __init__(self, username, password, login_url, authenticate_url, get_url):
        self.client = requests.session()
        self.login_url = login_url
        self.authenticate_url = authenticate_url
        self.get_url = get_url
        # 登录
        self.cookies = self.authenticate(username, password)

    def get_csrf_token(self):
        """
        获取csrftoken
        :return:
        """
        self.client.get(self.login_url)
        # csrf_token = self.client.cookies['csrftoken']
        csrf_token = ""
        return csrf_token

    def get_headers(self, csrf_token, session_id=''):
        """
        获取请求头
        :param csrf_token:
        :param session_id:
        :return:
        """
        headers = {'x-csrftoken': csrf_token}
        if session_id:
            headers['cookie'] = 'csrftoken=%s; sessionid=%s' % (csrf_token, session_id)
        else:
            headers['cookie'] = 'csrftoken=%s' % csrf_token
        return headers

    def get_platform(self, database):
        """
        获取分区
        :param database:
        :return:
        """
        for platform, databases in PLATFORM.items():
            if database in databases:
                return platform
        logger.warning('没有找到%s所对应的平台' % database)

    def authenticate(self, username, password):
        """
        登录获取cookies信息
        :param username:
        :param password:
        :return:
        """
        csrf_token = self.get_csrf_token()
        headers = self.get_headers(csrf_token)
        data = {
            "username": (None, username),
            "password": (None, password)
        }
        self.client.post(url=self.authenticate_url, headers=headers, data=data)
        cookies = self.client.cookies
        return cookies

    def get_data(self, platform, basedata, sql, limit_num):
        """
        获取请求数据
        :param platform: 分区
        :param basedata: 库
        :param sql: sql
        :return:
        """
        base_data = {'instance_name': (None, platform),
                     'db_name': (None, basedata),
                     'schema_name': (None, ''),
                     'tb_name': (None, ''),
                     'sql_content': (None, sql),
                     'limit_num': (None, limit_num)}
        return base_data

    def get_info(self, lot_id):
        """
        获取车场所在库
        :param lot_id: 车场id
        :return:
        """
        sql = """select d.dbname from t_lotpark p left join t_database d on d.id=p.databaseId where lotCode='%s' limit 100;""" % lot_id
        data = self.get_data('收费系统主库1-华为云', 'parkmanager', sql)
        headers = self.get_headers(self.cookies['csrftoken'], self.cookies['sessionid'])
        res = request.post(url=self.get_url, headers=headers, data=data, timeout=5)
        util.checkResultCode(res.json())
        database = res.json().get("data").get("rows")[0][0]
        return database

    def select(self, lot_id, sql):
        """
        查询收费系统云端数据
        :param lot_id:
        :param sql:
        :return:
        """
        database = self.get_info(lot_id)
        platform = self.get_platform(database)
        headers = self.get_headers(self.cookies['csrftoken'], self.cookies['sessionid'])
        data = self.get_data(platform, database, sql)
        res = request.post(url=self.get_url, headers=headers, data=data, timeout=5)
        util.checkResultCode(res.json())
        return res.json()

    def get_data_by_sql(self, platform, database, sql, limit_num=100):
        database = database
        platform = platform
        headers = self.get_headers(self.cookies['csrftoken'], self.cookies['sessionid'])
        print(headers)
        data = self.get_data(platform, database, sql, limit_num)
        res = request.post(url=self.get_url, headers=headers, data=data, timeout=5)
        util.checkResultCode(res.json())
        return res.json()


cloud = GetCloudData(username, password, login_url, authenticate_url, get_url)
if __name__ == "__main__":

    sql = "SELECT city_id FROM superpark.mc_parking_lot WHERE lot_id = '592011611';"
    # data = cloud.get_data(platform="速停车只读-成都研发使用-阿里云", basedata=None, sql=sql)
    res_dic = cloud.get_data_by_sql(platform="速停车只读-成都研发使用-阿里云", database="superpark", sql=sql)
    # headers = cloud.get_headers(cloud.cookies['csrftoken'], cloud.cookies['sessionid'])
    print(res_dic)
    # lot_id = "371015398"
    # sql = 'select externStatus from t_769013706_carcome;'
    # cloud.select(lot_id, sql)