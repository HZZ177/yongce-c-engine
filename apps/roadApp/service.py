import uuid

import requests

from apps.roadApp.config import RoadConfig
from apps.roadApp.schema import RoadCarInOutRequest
from core.logger import logger


class RoadService:
    """路侧车辆管理服务 - 通过HTTP接口调用实现"""

    def __init__(self):
        self.config = RoadConfig()

    async def car_in(self, request: RoadCarInOutRequest):
        """路侧车辆入场"""
        if request.lot_id in self.config.get_test_support_lot_ids():
            url = self.config.get_swagger_base_url("test") + self.config.get_api_endpoint("car_in")
            road_code = "road005348"    # 暂时写死 - dwb永策路段1
            park_space_code = "GH1"     # 暂时写死 - 车位号
        elif request.lot_id in self.config.get_prod_support_lot_ids():
            url = self.config.get_swagger_base_url("prod") + self.config.get_api_endpoint("car_in")
            road_code = "road005615"  # 暂时写死 - 守一路段
            park_space_code = "1"  # 暂时写死 - 车位号
        else:
            logger.error(f"不支持的lot_id: {request.lot_id}")
            raise Exception(f"不支持的lot_id{request.lot_id}")

        park_code = self.config.get_parking_road_lot_id(request.lot_id)

        header = {
            "Content-Type": "application/json",
        }
        data = {
            "parkCode": park_code,
            "roadCode": road_code,
            "carNo": request.car_no,
            "parkspaceCode": park_space_code,
            "carType": request.car_type,
            "plateColor": request.plate_color,
            "inTime": request.in_time,
            "source": request.source,
            "eventId": str(uuid.uuid4()),
        }
        res = requests.post(url,headers=header, json=data)
        if res.status_code != 200:
            logger.error(f"路侧车辆入场接口调用失败！错误为【{res.text}】")
            raise Exception(f"路侧车辆入场接口调用失败！错误为【{res.text}】")
        else:
            if not res.json().get("success"):
                logger.error(f"路侧车辆入场接口调用失败！错误为【{res.json()}】")
                raise Exception(f"路侧车辆入场接口调用失败！错误为【{res.json()}】")
            logger.info(f"路侧车辆入场接口调用成功！返回结果为【{res.json()}】")
            return res.json()

    async def car_out(self, request: RoadCarInOutRequest):
        """路侧车辆出场"""
        if request.lot_id in self.config.get_test_support_lot_ids():
            url = self.config.get_swagger_base_url("test") + self.config.get_api_endpoint("car_out")
            road_code = "road005348"  # 暂时写死 - dwb永策路段1
            park_space_code = "GH1"  # 暂时写死 - 车位号
        elif request.lot_id in self.config.get_prod_support_lot_ids():
            url = self.config.get_swagger_base_url("prod") + self.config.get_api_endpoint("car_out")
            road_code = "road005615"  # 暂时写死 - 守一路段
            park_space_code = "1"  # 暂时写死 - 车位号
        else:
            logger.error(f"不支持的lot_id: {request.lot_id}")
            raise Exception(f"不支持的lot_id{request.lot_id}")

        park_code = self.config.get_parking_road_lot_id(request.lot_id)

        header = {
            "Content-Type": "application/json",
        }
        data = {
            "parkCode": park_code,
            "roadCode": road_code,
            "carNo": request.car_no,
            "parkspaceCode": park_space_code,
            "carType": request.car_type,
            "plateColor": request.plate_color,
            "inTime": request.in_time,
            "source": request.source,
            "eventId": str(uuid.uuid4()),
        }
        res = requests.post(url, headers=header, json=data)
        if res.status_code != 200:
            logger.error(f"路侧车辆出场接口调用失败！错误为【{res.text}】")
            raise Exception(f"路侧车辆出场接口调用失败！错误为【{res.text}】")
        else:
            if not res.json().get("success"):
                logger.error(f"路侧车辆出场接口调用失败！错误为【{res.json()}】")
                raise Exception(f"路侧车辆出场接口调用失败！错误为【{res.json()}】")
            logger.info(f"路侧车辆出场接口调用成功！返回结果为【{res.json()}】")
            return res.json()

    async def get_on_park(self, lot_id: str, car_no: str, start_time: str = None, end_time: str = None) -> dict:
        """查询路侧在场车辆 - 调用路侧系统HTTP接口"""
        # 占位实现 - 后续填充HTTP接口调用逻辑
        pass

    async def query_fee(self, lot_id: str, car_no: str):
        """路侧查费 - 调用路侧系统HTTP接口"""
        # 占位实现 - 后续填充HTTP接口调用逻辑
        pass
