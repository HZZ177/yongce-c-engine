"""
@File    : file_tool.py
@Time    : 2020-11-17 15:37
@Author  : huangjunhao
@Software: PyCharm
备注：处理文件（日志、截图等）类
"""

import os
import shutil

from dateutil import rrule
from dateutil.parser import parse
import datetime

from common import filepath, util
from common.configLog import logger


class FileTool:
    # 定时清理过期file

    @staticmethod
    @util.catch_exception
    def del_file(file_path=filepath.LOG_PATH, diff_day=1, file_type='.log'):
        """
        删除日志文件格式为（20210301101112用例测试日志.log）
        :param file_path: 文件的储存路径，默认为config中配置路径
        :param file_type: 需要删除的文件类型，默认为删除.log文件
        :param diff_day: 日期差值，默认清理除今天以外的所有文件
        """
        logger.info(f"执行文件清理!文件类型为{file_type}，天数为{diff_day}")
        for root, dirs, files in os.walk(file_path):
            for filename in files:
                # 判断是否为指定文件类型
                if filename[-4:] == file_type:
                    # 计算日期差值
                    day_count = rrule.rrule(rrule.DAILY, dtstart=parse(filename[:8]),
                                            until=datetime.date.today()).count() \
                                - 1
                    # 判断是否属于需要清理的时间范围
                    if day_count >= diff_day and os.path.exists(os.path.join(file_path, filename)):
                        logger.info(f"需删除文件为{filename}")
                        os.remove(os.path.join(file_path, filename))

    @staticmethod
    @util.catch_exception
    def del_folder(file_path=filepath.LOG_PATH, diff_day=1):
        """
        删除过期的日志文件夹 格式为（2021-06-16）
        :param file_path: 文件的储存路径，默认为config中配置路径
        :param diff_day: 日期差值，默认清理除今天以外的所有文件
        """
        logger.info(f"执行文件夹清理!，天数为{diff_day}")
        for root, dirs, files in os.walk(file_path):
            for dir in dirs:
                # 计算日期差值
                day_count = rrule.rrule(rrule.DAILY, dtstart=parse(dir),
                                        until=datetime.date.today()).count() \
                            - 1
                # 判断是否属于需要清理的时间范围
                if day_count >= diff_day and os.path.exists(os.path.join(file_path, dir)):
                    logger.info(f"需删除文件夹为{dir}")
                    shutil.rmtree(os.path.join(file_path, dir))


filetool = FileTool()

if __name__ == '__main__':
    FileTool().del_folder()