import yaml
from common.configLog import logger
import os
from common import filepath


class Yaml:
    def __init__(self, filename, mode):
        """
        filename 文件名
        mode 模式：1 统一平台地址 2 收费系统6.0管理后台地址
        """
        self.filename = filename
        self.mode = mode

    def read_yaml(self):
        """获取yaml中数据"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    file_data = f.read()
                data = yaml.load(file_data, Loader=yaml.FullLoader)
                return data
            except Exception as msg:
                raise Exception(logger.error(msg))
        else:
            raise FileNotFoundError(logger.error("没有找到文件:%s" % self.filename))

    def _get_domain(self):
        """获取域名"""
        try:
            api_unity = filepath.CONF.get("domain", "api_unity")
            api_web = filepath.CONF.get("domain", "api_web")
            api_internally = filepath.CONF.get("domain", "api_internally")
            api_postpay = filepath.CONF.get("domain", "api_postpay")
            api_bi = filepath.CONF.get("domain", "api_bi")
            api_easy = filepath.CONF.get("domain", "api_easytest")
            if self.mode == 1:
                domian = api_unity
            elif self.mode == 2:
                domian = api_web
            elif self.mode == 3:
                domian = api_internally
            elif self.mode == 4:
                domian = self.read_yaml()["host"]
            elif self.mode == 5:
                domian = api_postpay
            elif self.mode == 6:
                domian = api_bi
            elif self.mode == 7:
                domian = api_easy
            elif self.mode == 0:
                domian = ""
            else:
                raise Exception(logger.error("mode参数输入错误"))
            return domian
        except Exception as msg:
            raise Exception(logger.error(msg))

    @property
    def url(self):
        """
        获取api
        return url:str
        """
        domian = self._get_domain()
        try:
            data = self.read_yaml()["api"]
            return "".join((domian, data))
        except KeyError as msg:
            raise KeyError(logger.error("KeyError:{%s}" % msg))

    @property
    def method(self):
        """
        获取method
        return url:str

        """
        try:
            data = self.read_yaml()["method"]
            return data
        except KeyError as msg:
            raise KeyError(logger.error("KeyError:{%s}" % msg))

    @property
    def headers(self):
        """
        获取headers
        return dict
        """
        try:
            headers = self.read_yaml()['headers'] if self.read_yaml()['headers'] else {}
            return headers
        except KeyError as msg:
            raise KeyError(logger.error("KeyError:{%s}" % msg))

    @property
    def allData(self):
        """
        获取data数据
        return list --> [[{ps}, {data}], [{ps}, {data}] ...]
        """
        try:
            allData = self.read_yaml()['data']
            return allData
        except KeyError as msg:
            raise KeyError(logger.error("KeyError:{%s}" % msg))

    @property
    def allQuery(self):
        """
        获取query数据
        return list --> [[{ps}, {query}], [{ps}, {query}] ...]
        """
        try:
            allQuery = self.read_yaml()['query']
            return allQuery
        except KeyError as msg:
            raise KeyError(logger.error("KeyError:{%s}" % msg))

    @property
    def allDb(self):
        """
        获取相关db数据
        :return:
        """
        try:
            allDb = self.read_yaml()['db']
            return allDb
        except KeyError as msg:
            raise KeyError(logger.error("KeyError:{%s}" % msg))


if __name__ == "__main__":
    read_data = Yaml(filepath.USERINFOBYMMS, 4)
    print(read_data.read_yaml())
    # allData = read_data.allData
    # for data in allData:
    #     print(data[0]['id'])
    #     print(data[0]['id'] == 1)
    #     print(data[1]['ps'])
    #     print(data[2])