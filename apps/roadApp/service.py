import hashlib
import uuid

from apps.roadApp.config import RoadConfig
from core.requests import RequestClient
from apps.roadApp.schema import RoadCarInOutRequest, RoadPresentCarInfoRequest
from core.logger import logger


class RoadService:
    """路侧车辆管理服务 - 通过HTTP接口调用实现"""

    def __init__(self):
        self.config = RoadConfig()
        self.http_client = RequestClient()

    async def car_in(self, request: RoadCarInOutRequest):
        """路侧车辆入场"""
        if request.lot_id in self.config.get_test_support_lot_ids():
            url = self.config.get_road_swagger_base_url("test") + self.config.get_api_endpoint("car_in")
        elif request.lot_id in self.config.get_prod_support_lot_ids():
            url = self.config.get_road_swagger_base_url("prod") + self.config.get_api_endpoint("car_in")
        else:
            logger.error(f"不支持的lot_id: {request.lot_id}")
            raise Exception(f"不支持的lot_id{request.lot_id}")

        park_code = self.config.get_parking_road_lot_id(request.lot_id)

        header = {
            "Content-Type": "application/json",
        }
        data = {
            "parkCode": park_code,
            "roadCode": request.road_code,
            "carNo": request.car_no,
            "parkspaceCode": request.park_space_code,
            "carType": request.car_type,
            "plateColor": request.plate_color,
            "inTime": request.in_time,
            "source": request.source,
            "eventId": str(uuid.uuid4()),
        }
        res = self.http_client.post(url,headers=header, json=data)
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
            url = self.config.get_road_swagger_base_url("test") + self.config.get_api_endpoint("car_out")
        elif request.lot_id in self.config.get_prod_support_lot_ids():
            url = self.config.get_road_swagger_base_url("prod") + self.config.get_api_endpoint("car_out")
        else:
            logger.error(f"不支持的lot_id: {request.lot_id}")
            raise Exception(f"不支持的lot_id{request.lot_id}")

        park_code = self.config.get_parking_road_lot_id(request.lot_id)

        header = {
            "Content-Type": "application/json",
        }
        data = {
            "parkCode": park_code,
            "roadCode": request.road_code,
            "carNo": request.car_no,
            "parkspaceCode": request.park_space_code,
            "carType": request.car_type,
            "plateColor": request.plate_color,
            "inTime": request.in_time,
            "source": request.source,
            "eventId": str(uuid.uuid4()),
        }
        res = self.http_client.post(url, headers=header, json=data)
        if res.status_code != 200:
            logger.error(f"路侧车辆出场接口调用失败！错误为【{res.text}】")
            raise Exception(f"路侧车辆出场接口调用失败！错误为【{res.text}】")
        else:
            if not res.json().get("success"):
                logger.error(f"路侧车辆出场接口调用失败！错误为【{res.json()}】")
                raise Exception(f"路侧车辆出场接口调用失败！错误为【{res.json()}】")
            logger.info(f"路侧车辆出场接口调用成功！返回结果为【{res.json()}】")
            return res.json()

    async def road_present_car_info(self, request: RoadPresentCarInfoRequest):
        """查询路侧在场车辆"""
        if request.lot_id in self.config.get_test_support_lot_ids():
            url = self.config.get_road_swagger_base_url("test") + self.config.get_api_endpoint("present_car_info")
        elif request.lot_id in self.config.get_prod_support_lot_ids():
            url = self.config.get_road_swagger_base_url("prod") + self.config.get_api_endpoint("present_car_info")
        else:
            logger.error(f"不支持的lot_id: {request.lot_id}")
            raise Exception(f"不支持的lot_id{request.lot_id}")

        park_code = self.config.get_parking_road_lot_id(request.lot_id)

        header = {
            "Content-Type": "application/json",
        }
        data = {
            "carNo": request.car_no,
            "parkCode": park_code,
            "roadCode": request.road_code,
            "parkspaceCode": request.parkspace_code,
            "plateColor": request.plate_color,
            "carType": request.car_type,
        }

        res = self.http_client.post(url, headers=header, json=data)

        if res.status_code != 200:
            logger.error(f"路侧查询在场车调用失败！错误为【{res.text}】")
            raise Exception(f"路侧查询在场车调用失败！错误为【{res.text}】")
        else:
            if not res.json().get("success"):
                logger.error(f"路侧查询在场车调用失败！错误为【{res.json()}】")
                raise Exception(f"路侧查询在场车调用失败！错误为【{res.json()}】")
            logger.info(f"路侧查询在场车调用成功！返回结果为【{res.json()}】")
            return res.json()

    async def yongce_pro_admin_login(self, lot_id):
        """永策PRO平台后台登录"""
        phone = "18202823092"
        password = "as..101026"
        img_code = "9078"
        img_code_key = "096b514fxxxxxxxxxxxxx"
        if lot_id in self.config.get_test_support_lot_ids():
            base_url = self.config.get_yongce_pro_domain().get("test")
            top_group_id = self.config.get_yongce_pro_top_group_id().get("test")
        elif lot_id in self.config.get_prod_support_lot_ids():
            base_url = self.config.get_yongce_pro_domain().get("prod")
            top_group_id = self.config.get_yongce_pro_top_group_id().get("prod")
        else:
            raise Exception(f"暂不支持车场【{lot_id}】")

        url = base_url + "/user-center/api/login/login"
        h = hashlib.md5()
        h.update(password.encode(encoding='utf-8'))

        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json",
            "topGroupId": top_group_id,
        }

        login_data = {
            "phone": phone,
            "password": h.hexdigest(),
            "loginMethod": 1,
            "topGroupId": top_group_id,
            "code": img_code,
            "codeKey": img_code_key
        }
        response = self.http_client.post(url=url, headers=headers, json=login_data)
        result_json = response.json()
        if result_json["resultCode"] == 200:
            logger.info("永策PRO平台登录成功！")
            return result_json
        else:
            raise Exception(f"永策PRO平台登录失败！错误为【{result_json}】!")

    async def get_yongce_pro_admin_token(self, lot_id):
        """获取永策PRO平台后台登录token"""
        login_res = await self.yongce_pro_admin_login(lot_id)
        token = login_res.get("data").get("token")
        return token

    async def get_road_list(self, lot_id):
        """获取车场路段列表"""
        token = await self.get_yongce_pro_admin_token(lot_id)
        if lot_id in self.config.get_test_support_lot_ids():
            base_url = self.config.get_yongce_pro_domain().get("test")
        elif lot_id in self.config.get_prod_support_lot_ids():
            base_url = self.config.get_yongce_pro_domain().get("prod")
        else:
            raise Exception(f"暂不支持车场【{lot_id}】")

        url = base_url + self.config.get_yongce_pro_endpoint("road_list")
        headers = {
            "Content-Type": "application/json",
            "token": token
        }

        data = {
            "lotId": lot_id,
            "roadName": ""
        }
        res = self.http_client.post(url=url, json=data, headers=headers, timeout=10)
        if res.status_code != 200:
            raise Exception(f"请求失败，返回：{res.text}")
        result_json = res.json()
        if result_json["resultCode"] == 200:
            logger.info("获取路段列表成功！")
            return result_json
        else:
            raise Exception(f"获取路段列表失败！返回为【{result_json}】!")

    async def query_park_space_page(self, lot_id, road_code, page_num, page_size):
        """获取车场路段列表"""
        token = await self.get_yongce_pro_admin_token(lot_id)
        if lot_id in self.config.get_test_support_lot_ids():
            base_url = self.config.get_yongce_pro_domain().get("test")
        elif lot_id in self.config.get_prod_support_lot_ids():
            base_url = self.config.get_yongce_pro_domain().get("prod")
        else:
            raise Exception(f"暂不支持车场【{lot_id}】")

        url = base_url + self.config.get_yongce_pro_endpoint("parkspace_page")
        headers = {
            "Content-Type": "application/json",
            "token": token
        }

        data = {
            "stcId": lot_id,
            "roadCode": road_code,
            "pageNum": page_num,
            "pageSize": page_size,
        }
        res = self.http_client.post(url=url, json=data, headers=headers, timeout=10)
        if res.status_code != 200:
            raise Exception(f"请求失败，返回：{res.text}")
        result_json = res.json()
        if result_json["resultCode"] == 200:
            logger.info("分页查询车位成功！")
            return result_json
        else:
            raise Exception(f"分页查询车位失败！返回为【{result_json}】!")


