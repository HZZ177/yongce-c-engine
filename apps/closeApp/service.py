from .config import Config
from .protocol import DeviceProtocol, PaymentProtocol, BusinessProtocol
from .schema import DeviceOnOffRequest, DeviceOnOffResponse, BaseResponse, PaymentResponse, PaymentRequest, \
    RefundRequest, RefundResponse, CarInOutResponse, CarInOutRequest
import random
from datetime import datetime, timedelta
import traceback
import logging
import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class DeviceService:
    def __init__(self):
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
                failed_devices.append(device_ip)

        if len(success_devices) == len(request.device_list):
            return DeviceOnOffResponse(
                data=f"所有设备上线成功: {', '.join(success_devices)}",
                resultCode=200
            )
        else:
            return DeviceOnOffResponse(
                data=f"部分设备上线失败。成功: {', '.join(success_devices)}; 失败: {', '.join(failed_devices)}",
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
                data=f"部分设备下线失败。成功: {', '.join(success_devices)}; 失败: {', '.join(failed_devices)}",
                resultCode=500
            )

class CarService:
    def __init__(self, device_service: DeviceService):
        self.device_service = device_service
        self.config = Config()
        self.car_in_out_config = {"fail_count": 5, "wait_time": 10}

    async def car_in(self, request: CarInOutRequest) -> CarInOutResponse:
        """车辆入场"""
        try:
            if not request.server_ip:
                return CarInOutResponse(data="服务器IP不能为空", resultCode=500)

            # 获取设备协议，使用指定IP
            device_ip = "192.168.24.115"  # 使用本地 IP
            
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
                i_open_type=0,  # 入场
                i_cap_time=datetime.now()
            ):
                # 关闭连接
                device_protocol.device_off()
                return CarInOutResponse(
                    data=f"【{request.car_no}】入场成功",
                    resultCode=200
                )
            else:
                # 关闭连接
                device_protocol.device_off()
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

    async def car_out(self, request: CarInOutRequest) -> CarInOutResponse:
        """车辆出场"""
        try:
            if not request.server_ip:
                return CarInOutResponse(data="服务器IP不能为空", resultCode=500)

            # 获取设备协议，使用指定IP
            device_ip = "192.168.24.116"  # 使用本地 IP
            
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
                i_open_type=1,  # 出场
                i_cap_time=datetime.now()
            ):
                # 关闭连接
                device_protocol.device_off()
                return CarInOutResponse(
                    data=f"【{request.car_no}】出场成功",
                    resultCode=200
                )
            else:
                # 关闭连接
                device_protocol.device_off()
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

    async def get_on_park(self, lot_id: str, car_no: str, kt_token: str, start_time: str = "", end_time: str = "") -> dict:
        """
        查询在场车辆
        :param lot_id: 车场ID
        :param car_no: 车牌号
        :param kt_token: 统一平台token
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 在场车辆信息
        """
        if not self.config.is_supported_lot_id(lot_id):
            raise HTTPException(status_code=400, detail=f"暂不支持车场【{lot_id}】")

        now = datetime.now()
        zero_today = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
        last_today = zero_today + timedelta(hours=23, minutes=59, seconds=59)
        start_time = zero_today.strftime("%Y-%m-%d %H:%M:%S")
        end_time = last_today.strftime("%Y-%m-%d %H:%M:%S")

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

        url = self.config.get_car_come_domain()

        try:
            async with httpx.AsyncClient(timeout=self.config.get_api_timeout()) as client:
                response = await client.post(url=url, headers=headers, json=data)
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail="查询在场接口出错！")
                return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"查询在场车辆失败: {str(e)}")

class PaymentService:
    def __init__(self, device_service: DeviceService):
        self.device_service = device_service

    async def pay_order(self, request: PaymentRequest) -> PaymentResponse:
        """支付订单"""
        try:
            if not request.server_ip:
                return PaymentResponse(data="服务器IP不能为空", resultCode=500)

            # 获取设备协议
            device_ip = "192.168.0.86"  # 默认设备IP
            protocol = PaymentProtocol(
                server_ip=request.server_ip,
                server_port=5001,
                client_ip=device_ip
            )

            # 发送支付信息
            if protocol.pay_order(
                order_no=request.order_no or f"ORDER_{random.randint(100000, 999999)}",
                pay_money=request.pay_money or 1000,  # 默认支付金额
                car_no=request.car_no
            ):
                return PaymentResponse(
                    data=f"【{request.car_no}】支付成功",
                    resultCode=200
                )
            else:
                return PaymentResponse(
                    data=f"【{request.car_no}】支付失败",
                    resultCode=500
                )
        except Exception as e:
            logger.error(f"支付订单失败: {traceback.format_exc()}")
            return PaymentResponse(
                data=f"【{request.car_no}】支付失败: {str(e)}",
                resultCode=500
            )

    async def refund_order(self, request: RefundRequest) -> RefundResponse:
        """退款订单"""
        try:
            if not request.server_ip:
                return RefundResponse(data="服务器IP不能为空", resultCode=500)

            # 获取设备协议
            device_ip = "192.168.0.86"  # 默认设备IP
            protocol = PaymentProtocol(
                server_ip=request.server_ip,
                server_port=5001,
                client_ip=device_ip
            )

            # 发送退款信息
            if protocol.refund_order(
                order_no=request.order_no,
                refund_money=request.refund_money,
                car_no=request.car_no
            ):
                return RefundResponse(
                    data=f"【{request.car_no}】退款成功",
                    resultCode=200
                )
            else:
                return RefundResponse(
                    data=f"【{request.car_no}】退款失败",
                    resultCode=500
                )
        except Exception as e:
            logger.error(f"退款订单失败: {traceback.format_exc()}")
            return RefundResponse(
                data=f"【{request.car_no}】退款失败: {str(e)}",
                resultCode=500
            )
