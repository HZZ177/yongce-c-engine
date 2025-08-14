import asyncio
import json
import time
import requests
from typing import List, Dict
from apps.closeApp.config import Config
from apps.closeApp.protocol import DeviceProtocol, PaymentProtocol, BusinessProtocol
from apps.closeApp.schema import DeviceOnOffRequest, DeviceOnOffResponse, BaseResponse, PaymentResponse, PaymentRequest, \
    RefundRequest, RefundResponse, CarInOutResponse, CarInOutRequest
import random
from datetime import datetime
import traceback
from core.logger import logger
from fastapi import HTTPException


class BaseService:
    def __init__(self):
        self.config = Config()

    async def get_kt_token(self, lot_id):
        """获取统一平台登录token"""
        api_url = "/unity/service/open/app/login"
        url = ""
        if lot_id in self.config.get_test_support_lot_ids():
            url = self.config.get_kt_unity_login_domain().get("test") + api_url
        elif lot_id in self.config.get_prod_support_lot_ids():
            url = self.config.get_kt_unity_login_domain().get("prod") + api_url
        # 统一平台登录
        try:
            headers = {"content-type": "application/json", "kt-lotcodes": lot_id}
            data = {"code": "", "expireDay": 0, "loginWay": "", "mobileCode": "0592", "phone": "19182295006"}
            res = requests.post(url=url, headers=headers, data=json.dumps(data))
            if res.status_code != 200:
                logger.error(f"统一平台登录失败: {res.text}")
                raise HTTPException(status_code=500, detail=f"统一平台登录失败: {res.text}")
            else:
                kt_token = res.json()['data']['ktToken']
                logger.debug(f"统一平台登录成功，获取token: {kt_token}")
                return kt_token
        except Exception as e:
            logger.error(f"统一平台登录失败: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"统一平台登录失败: {str(e)}")

    async def get_on_park(
            self,
            lot_id: str,
            car_no: str,
            start_time: str = datetime.now().strftime("%Y-%m-%d 00:00:00"),
            end_time: str = datetime.now().strftime("%Y-%m-%d 23:59:59")
    ) -> dict:
        """
        查询在场车辆
        :param lot_id: 车场ID
        :param car_no: 车牌号
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 在场车辆信息
        """
        if not self.config.is_supported_lot_id(lot_id):
            raise HTTPException(status_code=400, detail=f"暂不支持车场【{lot_id}】")

        kt_token = await self.get_kt_token(lot_id)

        data = {
            "lotCode": lot_id,
            "downloadId": "",
            "pageSize": 10,
            "currentPage": 1,
            "carNo": car_no,
            "comeTimeStart": start_time,
            "totalCount": "0,",
            "comeTimeEnd": end_time
        }

        headers = {
            "content-type": "application/json",
            "kt-token": kt_token,
            "kt-lotcodes": lot_id
        }

        if lot_id in self.config.get_test_support_lot_ids():
            url = self.config.get_car_come_domain().get("test")
        elif lot_id in self.config.get_prod_support_lot_ids():
            url = self.config.get_car_come_domain().get("prod")
        else:
            raise HTTPException(status_code=400, detail=f"暂不支持车场【{lot_id}】")

        try:
            response = requests.post(url=url, headers=headers, json=data, timeout=5)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="查询在场接口出错！")
            return response.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"查询在场车辆失败: {str(e)}")



class DeviceService(BaseService):
    def __init__(self):
        super().__init__()
        self.devices = {}  # 存储设备实例

    async def device_on(self, request: DeviceOnOffRequest) -> DeviceOnOffResponse:
        """设备上线"""
        if not request.device_list:
            return DeviceOnOffResponse(data="设备列表为空", resultCode=500)

        success_devices = []
        failed_devices = []

        for device_ip in request.device_list:
            try:
                protocol = DeviceProtocol(
                    server_ip=request.server_ip,
                    server_port=5001,  # 默认端口
                    client_ip=device_ip
                )

                if protocol.device_on(request.device_type):
                    self.devices[device_ip] = protocol
                    success_devices.append(device_ip)
                else:
                    failed_devices.append(device_ip)
            except Exception as e:
                logger.error(f"设备上线失败: {device_ip}，错误信息: {str(e)}")
                failed_devices.append(device_ip)

        if len(success_devices) == len(request.device_list):
            return DeviceOnOffResponse(
                data=f"所有设备上线成功: {', '.join(success_devices)}",
                resultCode=200
            )
        else:
            return DeviceOnOffResponse(
                data=f"部分设备上线失败！ 成功: {', '.join(success_devices)};  失败: {', '.join(failed_devices)}",
                resultCode=500
            )

    async def device_off(self, request: DeviceOnOffRequest) -> DeviceOnOffResponse:
        """设备下线"""
        if not request.device_list:
            return DeviceOnOffResponse(data="设备列表为空", resultCode=500)

        success_devices = []
        failed_devices = []

        for device_ip in request.device_list:
            try:
                if device_ip in self.devices:
                    protocol = self.devices[device_ip]
                    if protocol.device_off():
                        del self.devices[device_ip]
                        success_devices.append(device_ip)
                    else:
                        failed_devices.append(device_ip)
                else:
                    failed_devices.append(device_ip)
            except Exception as e:
                failed_devices.append(device_ip)

        if len(success_devices) == len(request.device_list):
            return DeviceOnOffResponse(
                data=f"所有设备下线成功: {', '.join(success_devices)}",
                resultCode=200
            )
        else:
            return DeviceOnOffResponse(
                data=f"部分设备下线失败！ 成功: {', '.join(success_devices)};  失败: {', '.join(failed_devices)}",
                resultCode=500
            )

    async def get_all_node_status(self, lot_id, cloud_kt_token):
        """查询通道设备状态"""
        if lot_id in self.config.get_test_support_lot_ids():
            url = self.config.get_test_cloud_channel_query_url()
        elif lot_id in self.config.get_prod_support_lot_ids():
            url = self.config.get_prod_cloud_channel_query_url()
        else:
            raise HTTPException(status_code=400, detail=f"暂不支持车场【{lot_id}】")

        headers = {
            "content-type": "application/json",
            "kt-token": cloud_kt_token
        }
        data = {
            "nodeType": "-1"
        }
        try:
            node_status = requests.post(url=url, headers=headers, json=data)
            if node_status.json().get("code") != 2000:
                raise Exception(f"查询通道设备状态失败！响应：{node_status.text}")
            device_data = node_status.json().get("data")
            return device_data
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"查询通道设备状态失败: {str(e)}")

    async def change_node_status(self, cloud_kt_token, lot_id, node_ids, status):
        """修改通道状态"""
        if lot_id in self.config.get_test_support_lot_ids():
            url = self.config.get_test_cloud_channel_change_url()
        elif lot_id in self.config.get_prod_support_lot_ids():
            url = self.config.get_prod_cloud_channel_change_url()
        else:
            raise HTTPException(status_code=400, detail=f"暂不支持车场【{lot_id}】")

        headers = {
            "content-type": "application/json",
            "kt-token": cloud_kt_token
        }
        data = {
            "nodeIds": node_ids,
            "nodeType": "-1",
            "status": status
        }
        try:
            change_res = requests.post(url=url, headers=headers, json=data)
            res_json = change_res.json()
            if res_json.get("code") != 2000:
                raise Exception(f"修改通道状态失败，响应: {change_res.text}")
            return res_json
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"查询通道设备状态失败: {str(e)}")

    async def get_device_status(self, device_ips: List[str], ttl_seconds: int = 12) -> List[Dict]:
        """查询设备真实在线状态
        
        Args:
            device_ips: 设备IP列表
            ttl_seconds: 心跳超时时间（秒），默认12秒
            
        Returns:
            设备状态列表，每个元素包含 {ip, online, updatedAt}
        """
        import time
        current_time = time.time()
        device_status_list = []
        
        for device_ip in device_ips:
            device_ip = device_ip.strip()
            if not device_ip:
                continue
                
            # 检查设备是否在已连接列表中
            if device_ip in self.devices:
                protocol = self.devices[device_ip]
                connected = protocol.is_connected()
                
                # 检查心跳是否在TTL范围内
                if connected and protocol.last_heartbeat_at:
                    time_since_heartbeat = current_time - protocol.last_heartbeat_at
                    alive = time_since_heartbeat <= ttl_seconds
                    updated_at = protocol.last_heartbeat_at
                else:
                    alive = False
                    updated_at = 0
            else:
                # 设备未连接
                connected = False
                alive = False
                updated_at = 0
            
            device_status_list.append({
                'ip': device_ip,
                'online': alive,
                'updatedAt': updated_at
            })
            
        return device_status_list


class CarService(BaseService):
    def __init__(self, device_service: DeviceService):
        super().__init__()
        self.device_service = device_service


    async def car_in(self, request: CarInOutRequest) -> CarInOutResponse:
        """车辆入场"""
        try:
            if not request.server_ip:
                logger.error("服务器IP不能为空")
                return CarInOutResponse(data="服务器IP不能为空", resultCode=500)

            # 获取设备协议，使用指定IP
            if request.lot_id in self.config.get_test_support_lot_ids():
                device_ip = self.config.get_test_device_ip().get("in_device")
            elif request.lot_id in self.config.get_prod_support_lot_ids():
                device_ip = self.config.get_prod_device_ip().get("in_device")
            else:
                logger.error(f"不支持的停车场: {request.lot_id}")
                return CarInOutResponse(data="不支持的停车场", resultCode=500)

            if not device_ip:
                logger.error("设备IP不能为空")
                raise Exception("设备IP不能为空")

            # 先使用DeviceProtocol进行设备上线
            device_protocol = DeviceProtocol(
                server_ip=request.server_ip or self.config.get_server_ip(),
                server_port=self.config.get_server_port(),
                client_ip=device_ip
            )

            # 进行设备上线
            if not device_protocol.device_on():
                return CarInOutResponse(data=f"设备 {device_ip} 上线失败", resultCode=500)

            # 发送车辆入场信息
            business_protocol = BusinessProtocol(
                server_ip=request.server_ip or self.config.get_server_ip(),
                server_port=self.config.get_server_port(),
                client_ip=device_ip
            )

            # 重用已建立的连接
            business_protocol.sock = device_protocol.sock

            if business_protocol.send_img(
                    i_serial=str(request.i_serial or random.randint(0, 999999999)),
                    i_plate_no=request.car_no,
                    i_car_style=0,
                    i_is_etc=0,
                    i_etc_no="",
                    i_recog_enable=request.recognition,
                    i_color=request.car_color,
                    i_data_type=0,
                    i_open_type=request.i_open_type,  # 入车默认1：相机直接放行
                    i_cap_time=datetime.now()
            ):
                return CarInOutResponse(
                    data=f"【{request.car_no}】入场成功",
                    resultCode=200
                )
            else:
                return CarInOutResponse(
                    data=f"【{request.car_no}】入场失败",
                    resultCode=500
                )
        except Exception as e:
            logger.error(f"车辆入场失败: {traceback.format_exc()}")
            return CarInOutResponse(
                data=f"【{request.car_no}】入场失败: {str(e)}",
                resultCode=500
            )
        finally:
            # 关闭连接
            device_protocol.device_off()

    async def car_out(self, request: CarInOutRequest) -> CarInOutResponse:
        """车辆出场"""
        try:
            if not request.server_ip:
                return CarInOutResponse(data="服务器IP不能为空", resultCode=500)

            # 获取设备协议，使用指定IP
            if request.lot_id in self.config.get_test_support_lot_ids():
                device_ip = self.config.get_test_device_ip().get("out_device")
            elif request.lot_id in self.config.get_prod_support_lot_ids():
                device_ip = self.config.get_prod_device_ip().get("out_device")
            else:
                logger.error(f"不支持的停车场: {request.lot_id}")
                return CarInOutResponse(data="不支持的停车场", resultCode=500)
            if not device_ip:
                logger.error("设备IP不能为空")
                raise Exception("设备IP不能为空")

            # 先使用DeviceProtocol进行设备上线
            device_protocol = DeviceProtocol(
                server_ip=request.server_ip or self.config.get_server_ip(),
                server_port=self.config.get_server_port(),
                client_ip=device_ip
            )

            # 进行设备上线
            if not device_protocol.device_on():
                return CarInOutResponse(data=f"设备 {device_ip} 上线失败", resultCode=500)

            # 发送车辆出场信息
            business_protocol = BusinessProtocol(
                server_ip=request.server_ip or self.config.get_server_ip(),
                server_port=self.config.get_server_port(),
                client_ip=device_ip
            )

            # 重用已建立的连接
            business_protocol.sock = device_protocol.sock

            if business_protocol.send_img(
                    i_serial=str(request.i_serial or random.randint(0, 999999999)),
                    i_plate_no=request.car_no,
                    i_car_style=0,
                    i_is_etc=0,
                    i_etc_no="",
                    i_recog_enable=request.recognition,
                    i_color=request.car_color,
                    i_data_type=0,
                    i_open_type=request.i_open_type, # 出车方式(0:压地感 1:相机直接放行)
                    i_cap_time=datetime.now()
            ):
                return CarInOutResponse(
                    data=f"【{request.car_no}】出场成功",
                    resultCode=200
                )
            else:
                return CarInOutResponse(
                    data=f"【{request.car_no}】出场失败",
                    resultCode=500
                )
        except Exception as e:
            logger.error(f"车辆出场失败: {traceback.format_exc()}")
            return CarInOutResponse(
                data=f"【{request.car_no}】出场失败: {str(e)}",
                resultCode=500
            )
        finally:
            # 关闭连接
            device_protocol.device_off()




class PaymentService(BaseService):
    def __init__(self):
        super().__init__()

    async def get_park_pay_info(self, kt_token, lot_id, car_no, out_time=0):
        """
        获取车场支付订单信息
        :param kt_token:
        :param lot_id:
        :param car_no:
        :param out_time:
        :return:
        """
        logger.info(f"开始查询车场支付订单信息: {lot_id} - {car_no}")
        if lot_id in self.config.get_test_support_lot_ids():
            base_url = self.config.get_yongce_pro_domain().get("test")
        elif lot_id in self.config.get_prod_support_lot_ids():
            base_url = self.config.get_yongce_pro_domain().get("prod")
        else:
            raise HTTPException(status_code=400, detail=f"暂不支持车场【{lot_id}】")

        url = base_url + "nkc/fee-simulate/query-fee"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "kt-lotcodes": lot_id,
            "kt-token": kt_token
        }
        data = {
            "lotCode": lot_id,
            "platNum": car_no,
            "now": out_time,
            "freeMoney": "",
            "freeTime": "",
            "cardNo": ""
        }

        res = requests.post(url=url, headers=headers, data=data, timeout=5)
        if res.status_code != 200:
            logger.error(f"查询车场支付订单接口错误！错误返回为{res.text}")
            raise HTTPException(status_code=500, detail=f"查询车场支付订单接口错误！错误返回为{res.text}")
        else:
            res_dic = res.json()

        if res_dic["resultCode"] == 510 and "没有找到车辆信息" in res_dic["resultMsg"]:
            logger.info("没有该车辆的支付订单信息！")
            return "没有该车辆的支付订单信息！"
        elif res_dic["resultCode"] == 200:
            order_no = res_dic["data"]["orderNo"]
            pay_money = res_dic["data"]["payMoney"]
            logger.info(f"查询车辆【{car_no}】支付订单信息成功，订单号为【{order_no}】, 支付金额为【{pay_money}】")
            return {"orderNo": order_no, "payMoney": pay_money}
        else:
            raise Exception(f"查询车场支付订单接口错误！错误返回为{res_dic}")


    async def pay_order(self, lot_id, car_no, pay_time="") -> PaymentResponse:
        """支付订单"""
        logger.info(f"开始支付车场订单")
        if lot_id in self.config.get_test_support_lot_ids():
            base_url = self.config.get_yongce_pro_domain().get("test")
        elif lot_id in self.config.get_prod_support_lot_ids():
            base_url = self.config.get_yongce_pro_domain().get("prod")
        else:
            raise HTTPException(status_code=400, detail=f"暂不支持车场【{lot_id}】")

        car_no = car_no
        lot_id = lot_id
        # 获取token
        kt_token = await self.get_kt_token(lot_id)
        # 查询订单信息
        order_info = await self.get_park_pay_info(kt_token, lot_id, car_no)
        if order_info != "没有该车辆的支付订单信息！":
            url = base_url + "nkc/fee-simulate/notice"
            headers = {
                "content-type": "application/json",
                "kt-lotcodes": lot_id,
                "kt-token": kt_token
            }
            data = {
                "lotCode": lot_id,
                "orderNo": order_info["orderNo"],
                "carPlateNum": car_no,
                "paidMoney": order_info["payMoney"],
                "payTime": pay_time,
                "cardNo": "",
                "freeMoney": 0,
                "freeTime": 0,
                "merchantOrderNo": "",
                "payChannel": "",
                "payMethod": "",
                "paySource": "2000",
                "reqId": "",
                "totalMoney": 0
            }

            pay_res = requests.post(url=url, headers=headers, data=json.dumps(data), timeout=5)
            if pay_res.status_code == 200:
                res = {
                    "data": f"【{car_no}】的订单【{order_info['orderNo']}】支付普通停车费【{order_info['payMoney']}】成功！",
                    "resultCode": 200
                }
            else:
                res = {
                    "data": f"【{car_no}】的订单【{order_info['orderNo']}】支付失败！",
                    "resultCode": 500
                }
        else:
            res = {
                "data": f"未查询到【{car_no}】的普通支付订单！！",
                "resultCode": 500
            }
        return PaymentResponse(**res)

    async def refund_order(self, lot_id, car_no, pay_time="") -> RefundResponse:
        """退款订单"""
        pass


if __name__ == '__main__':
    device_service = DeviceService()
    car_service = CarService(device_service)
    pay_service = PaymentService()

    kt_token = asyncio.run(car_service.get_kt_token("280025535"))
    res = asyncio.run(pay_service.get_park_pay_info(kt_token, "280025535", "川DHSY01"))
    print(res)
    res = asyncio.run(pay_service.pay_order("280025535", "川DHSY01"))
    print(res)