import asyncio
import hashlib
import json
import requests
from typing import List, Dict
from apps.closeApp.config import Config
from apps.closeApp.protocol import BusinessProtocol
from apps.closeApp.schema import DeviceOnOffRequest, DeviceOnOffResponse, PaymentResponse, \
    RefundResponse, CarInOutResponse, CarInOutRequest
import random
from datetime import datetime
import traceback
from core.logger import logger
from fastapi import HTTPException

from fastapi import WebSocket

from apps.closeApp.device_manager import device_manager
from apps.closeApp.ssh_manager import SSHManager


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

    async def yongce_pro_admin_login(self, lot_id):
        """永策PRO平台后台登录"""
        phone = "18202823092"
        password = "as..101026"
        img_code = "9078"
        img_code_key = "096b514fxxxxxxxxxxxxx"
        if lot_id in self.config.get_test_support_lot_ids():
            top_group_id = self.config.get_yongce_pro_config().get("top_group_id").get("test")
            base_url = self.config.get_yongce_pro_config().get("domain").get("test")
        elif lot_id in self.config.get_prod_support_lot_ids():
            top_group_id = self.config.get_yongce_pro_config().get("top_group_id").get("prod")
            base_url = self.config.get_yongce_pro_config().get("domain").get("prod")
        else:
            raise HTTPException(status_code=400, detail=f"暂不支持车场【{lot_id}】")

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
        response = requests.post(url=url, headers=headers, json=login_data)
        result_dic = response.json()
        if result_dic["resultCode"] == 200:
            logger.info("永策PRO平台登录成功！")
            return result_dic
        else:
            raise Exception(f"永策PRO平台登录失败！错误为【{result_dic}】!")

    async def get_yongce_pro_admin_token(self, lot_id):
        """获取永策PRO平台后台登录token"""
        login_res = await self.yongce_pro_admin_login(lot_id)
        token = login_res.get("data").get("token")
        return token


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
        :param start_time: 开始时间（可选，默认当天00:00:00）
        :param end_time: 结束时间（可选，默认当天23:59:59）
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

    async def get_channel_qr_pic(self, lot_id):
        """获取车场通道二维码图片"""
        if not self.config.is_supported_lot_id(lot_id):
            raise HTTPException(status_code=400, detail=f"暂不支持车场【{lot_id}】")

        yongce_pro_token = await self.get_yongce_pro_admin_token(lot_id)
        headers = {
            "content-type": "application/json",
            "Token": yongce_pro_token
        }
        data = {
            "lotCode": lot_id,
            "pageNumber": 1,
            "pageSize": 20
        }

        if lot_id in self.config.get_test_support_lot_ids():
            base_url = self.config.get_yongce_pro_config().get("domain").get("test")
        elif lot_id in self.config.get_prod_support_lot_ids():
            base_url = self.config.get_yongce_pro_config().get("domain").get("prod")
        else:
            raise HTTPException(status_code=400, detail=f"暂不支持车场【{lot_id}】")
        url = base_url + "/admin-vehicle-owner/lotSpace/nodeCode/list"
        try:
            response = requests.post(url=url, headers=headers, json=data, timeout=5)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"获取车场通道二维码图片失败！返回信息{response.text}")
            return response.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"获取车场通道二维码图片失败: {str(e)}")




class DeviceService(BaseService):
    def __init__(self):
        super().__init__()
        # self.devices = {}  # 由 device_manager 统一管理

    async def device_on(self, request: DeviceOnOffRequest) -> DeviceOnOffResponse:
        """设备上线（重构后）"""
        if not request.device_list:
            return DeviceOnOffResponse(data="设备列表为空", resultCode=500)

        success_devices = []
        failed_devices = []

        for device_ip in request.device_list:
            # 通过设备IP反向查找车场和设备类型
            lot_info = self.config.get_lot_info_by_device_ip(device_ip)
            if not lot_info:
                logger.warning(f"无法在配置中找到设备IP {device_ip} 对应的车场信息")
                failed_devices.append(device_ip)
                continue

            lot_id = lot_info['lot_id']
            device_type = lot_info['device_type']

            # 使用 device_manager 获取设备
            loop = asyncio.get_running_loop()
            protocol = await loop.run_in_executor(None, device_manager.get_device, lot_id, device_type)

            if protocol and protocol.is_connected():
                success_devices.append(device_ip)
            else:
                failed_devices.append(device_ip)

        if not failed_devices:
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
        """设备下线（重构后）"""
        if not request.device_list:
            return DeviceOnOffResponse(data="设备列表为空", resultCode=500)

        success_devices = []
        failed_devices = []

        for device_ip in request.device_list:
            lot_info = self.config.get_lot_info_by_device_ip(device_ip)
            if not lot_info:
                logger.warning(f"无法在配置中找到设备IP {device_ip} 对应的车场信息")
                failed_devices.append(device_ip)
                continue

            lot_id = lot_info['lot_id']
            device_type = lot_info['device_type']
            device_key = device_manager._get_device_key(lot_id, device_type)

            if device_key in device_manager.devices:
                protocol = device_manager.devices[device_key]
                if protocol.device_off():
                    del device_manager.devices[device_key]
                    success_devices.append(device_ip)
                else:
                    failed_devices.append(device_ip)
            else:
                # 如果设备本就不在线，也算作“下线成功”
                success_devices.append(device_ip)

        if not failed_devices:
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
        """查询设备真实在线状态（重构后）"""
        import time
        current_time = time.time()

        # Create a dictionary for quick lookup of statuses
        status_dict = {ip: {'ip': ip, 'online': False, 'updatedAt': 0} for ip in device_ips}

        # Iterate through the devices managed by the device_manager
        for protocol in device_manager.devices.values():
            device_ip = protocol.client_ip
            if device_ip in status_dict:
                connected = protocol.is_connected()

                if connected and protocol.last_heartbeat_at:
                    time_since_heartbeat = current_time - protocol.last_heartbeat_at
                    alive = time_since_heartbeat <= ttl_seconds
                    updated_at = protocol.last_heartbeat_at
                else:
                    alive = False
                    updated_at = 0

                status_dict[device_ip]['online'] = alive
                status_dict[device_ip]['updatedAt'] = updated_at

        return list(status_dict.values())


class CarService(BaseService):
    def __init__(self):
        super().__init__()
        # self.device_service is no longer needed, using device_manager singleton directly


    async def car_in(self, request: CarInOutRequest) -> CarInOutResponse:
        """车辆入场（重构后）"""
        try:
            # 1. 通过 device_manager 获取设备协议
            loop = asyncio.get_running_loop()
            device_protocol = await loop.run_in_executor(None, device_manager.get_device, request.lot_id, "in")

            if not device_protocol or not device_protocol.is_connected():
                logger.error(f"无法获取或连接到入场设备: lot_id={request.lot_id}")
                return CarInOutResponse(data=f"设备上线失败", resultCode=500)

            # 2. 发送车辆入场信息
            business_protocol = BusinessProtocol(
                server_ip=device_protocol.server_ip,
                server_port=device_protocol.server_port,
                client_ip=device_protocol.client_ip
            )

            # 3. 重用已建立的连接与锁
            business_protocol.sock = device_protocol.sock
            business_protocol.send_lock = device_protocol.send_lock

            if business_protocol.send_img(
                    i_serial=str(request.i_serial or random.randint(0, 999999999)),
                    i_plate_no=request.car_no,
                    i_car_style=0,
                    i_is_etc=0,
                    i_etc_no="",
                    i_recog_enable=request.recognition,
                    i_color=request.car_color,
                    i_data_type=0,
                    i_open_type=request.i_open_type,
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
            logger.error(f"车辆入场失败: {e}")
            raise Exception(e)

    async def car_out(self, request: CarInOutRequest) -> CarInOutResponse:
        """车辆出场（重构后）"""
        try:
            # 1. 通过 device_manager 获取设备协议
            loop = asyncio.get_running_loop()
            device_protocol = await loop.run_in_executor(None, device_manager.get_device, request.lot_id, "out")

            if not device_protocol or not device_protocol.is_connected():
                logger.error(f"无法获取或连接到出场设备: lot_id={request.lot_id}")
                return CarInOutResponse(data=f"设备上线失败", resultCode=500)

            # 2. 发送车辆出场信息
            business_protocol = BusinessProtocol(
                server_ip=device_protocol.server_ip,
                server_port=device_protocol.server_port,
                client_ip=device_protocol.client_ip
            )

            # 3. 重用已建立的连接与锁
            business_protocol.sock = device_protocol.sock
            business_protocol.send_lock = device_protocol.send_lock

            if business_protocol.send_img(
                    i_serial=str(request.i_serial or random.randint(0, 999999999)),
                    i_plate_no=request.car_no,
                    i_car_style=0,
                    i_is_etc=0,
                    i_etc_no="",
                    i_recog_enable=request.recognition,
                    i_color=request.car_color,
                    i_data_type=0,
                    i_open_type=request.i_open_type,
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
            logger.error(f"车辆出场失败: {e}")
            raise Exception(e)


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


class LogMonitorService(BaseService):
    """提供日志监控相关服务"""

    def __init__(self):
        super().__init__()

    def list_log_files(self, lot_id: str) -> List[str]:
        """获取指定车场服务器上的日志文件列表"""
        log_config = self.config.get_log_monitor_config(lot_id)
        if not log_config or not log_config.get('enabled'):
            raise HTTPException(status_code=404, detail="该车场未启用日志监控功能")

        server_ip = self.config.get_parking_lot_by_id(lot_id).get('server_ip')
        if not server_ip:
            raise HTTPException(status_code=404, detail="未找到该车场的服务器IP")

        ssh_manager = SSHManager(
            hostname=server_ip,
            port=log_config.get('ssh_port', 22),
            username=log_config['ssh_user'],
            password=log_config['ssh_password']
        )

        try:
            ssh_manager.connect()
            command = f"ls -1 {log_config['log_directory']}"
            output, error, exit_status = ssh_manager.execute_command(command)
            if exit_status != 0:
                raise HTTPException(status_code=500, detail=f"获取日志文件列表失败: {error}")

            files = [f for f in output.strip().split('\n') if f]  # 过滤掉空行
            files.sort(reverse=True)  # 按名称倒序排序
            return files
        except Exception as e:
            logger.error(f"[LogMonitor] 获取日志文件列表失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            ssh_manager.disconnect()

    async def stream_log_file(self, lot_id: str, filename: str, websocket: WebSocket):
        """通过WebSocket实时流式传输日志文件内容"""
        log_config = self.config.get_log_monitor_config(lot_id)
        if not log_config or not log_config.get('enabled'):
            await websocket.close(code=1008, reason="该车场未启用日志监控功能")
            return

        server_ip = self.config.get_parking_lot_by_id(lot_id).get('server_ip')
        if not server_ip:
            await websocket.close(code=1008, reason="未找到该车场的服务器IP")
            return

        ssh_manager = SSHManager(
            hostname=server_ip,
            port=log_config.get('ssh_port', 22),
            username=log_config['ssh_user'],
            password=log_config['ssh_password']
        )

        channel = None
        try:
            await websocket.accept()
            logger.info(f"[日志监控] WebSocket已接受 {lot_id} - {filename}")
            ssh_manager.connect()
            logger.info(f"[日志监控] 已为日志流建立SSH连接")

            log_file_path = f"{log_config['log_directory']}/{filename}"
            command = f"tail -f {log_file_path}"
            logger.info(f"[日志监控] 正在执行命令: {command}")
            channel = ssh_manager.get_streaming_channel(command)

            buffer = ""
            while not channel.exit_status_ready():
                # Check for client-side close messages
                try:
                    message = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                    if message == 'close':
                        logger.info("[日志监控] 收到来自客户端的'close'消息")
                        break
                except asyncio.TimeoutError:
                    pass  # No message from client, continue

                if channel.recv_ready():
                    data = channel.recv(1024).decode('utf-8', errors='ignore')
                    buffer += data
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line_to_send = line + '\n'
                        logger.debug(f"[日志监控] 正在发送行: {line_to_send.strip()}")
                        await websocket.send_text(line_to_send)

                await asyncio.sleep(0.1)

            # Send any remaining data in the buffer before closing
            if buffer:
                logger.debug(f"[日志监控] 正在发送剩余缓冲区: {buffer.strip()}")
                await websocket.send_text(buffer)

            logger.info("[日志监控] 已退出读取循环")

        except Exception as e:
            logger.error(f"[LogMonitor] 日志流传输异常: {e}")
            await websocket.close(code=1011, reason=f"日志流传输异常: {str(e)}")
        finally:
            if channel:
                channel.close()
            ssh_manager.disconnect()
            logger.info(f"[日志监控] 清理完成，WebSocket连接已关闭")


if __name__ == '__main__':
    base_service = BaseService()
    device_service = DeviceService()
    car_service = CarService()  # Updated initialization
    pay_service = PaymentService()

    res = asyncio.run(base_service.get_channel_qr_pic("280025535"))
    # res = asyncio.run(base_service.yongce_pro_admin_login("280025535"))
    print(res)