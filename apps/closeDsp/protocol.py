from typing import Optional
from pydantic import BaseModel, Field
import socket
import threading
import struct
import traceback
from datetime import datetime


class BaseProtocol:
    def __init__(self, server_ip: str, server_port: int, client_ip: str, client_port: int = 0):
        self.server_ip = str(server_ip)
        self.server_port = int(server_port)
        self.client_ip = str(client_ip)
        self.client_port = int(client_port)
        self.sock = None
        self.heart_lock = threading.Lock()
        self.recv_lock = threading.Lock()
        self.send_lock = threading.Lock()
        self.RECV_LIST = []

    def connect(self):
        """建立TCP连接"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.client_ip, self.client_port))
            self.sock.settimeout(3000)
            self.sock.connect((self.server_ip, self.server_port))
            return True
        except Exception as e:
            logger.error(f"连接失败: {traceback.format_exc()}")
            return False

    def close(self):
        """关闭连接"""
        try:
            if self.sock:
                self.sock.close()
            return True
        except Exception as e:
            logger.error(f"关闭连接失败: {traceback.format_exc()}")
            return False

    def send_command(self, command_name: str, time_span: int, total_park: int, 
                    park_serial: int, data: bytes, i_cap_time: Optional[datetime] = None) -> bytes:
        """发送命令"""
        try:
            # 命令头
            command_header = bytes([0x7E])
            
            # 命令类型
            command_type = bytes(command_name, encoding='utf-8')
            
            # 时间戳
            if i_cap_time:
                timestamp = int(i_cap_time.timestamp())
            else:
                timestamp = int(datetime.now().timestamp())
            time_bytes = struct.pack('!I', timestamp)
            
            # 数据长度
            data_len = len(data)
            len_bytes = struct.pack('!H', data_len)
            
            # 组装命令
            command = command_header + command_type + time_bytes + len_bytes + data
            
            # 计算校验和
            checksum = sum(command[1:]) & 0xFF
            command += bytes([checksum])
            
            return command
        except Exception as e:
            logger.error(f"命令组装失败: {traceback.format_exc()}")
            raise

class DeviceProtocol(BaseProtocol):
    def __init__(self, server_ip: str, server_port: int, client_ip: str, client_port: int = 0):
        super().__init__(server_ip, server_port, client_ip, client_port)
        self.heart_thread = None
        self.recv_thread = None

    def device_on(self, device_type: str = '1') -> bool:
        """设备上线"""
        try:
            if not self.connect():
                return False

            with self.send_lock:
                # 发送设备类型
                if str(device_type) == '10':
                    self.sock.send(self.send_command('C', 0, 1, 0, bytes([0x0C, 0x04, 0x00, 0x31])))
                else:
                    self.sock.send(self.send_command('C', 0, 1, 0, bytes([0x01, 0x04, 0x00])))
                
                # 发送设备IP
                self.sock.send(self.send_command('D', 0, 1, 0, bytes(self.client_ip, encoding="utf-8")))
                
                # 发送状态
                self.sock.send(self.send_command('F', 0, 1, 0, bytes([0x00])))

            # 启动心跳和接收线程
            self.heart_thread = threading.Thread(target=self._watch_heart, daemon=True)
            self.recv_thread = threading.Thread(target=self._async_receive_data, daemon=True)
            self.heart_thread.start()
            self.recv_thread.start()

            logger.info(f"设备 {self.client_ip} 上线成功")
            return True
        except Exception as e:
            logger.error(f"设备上线失败: {traceback.format_exc()}")
            return False

    def device_off(self) -> bool:
        """设备下线"""
        try:
            if self.sock:
                self.close()
            logger.info(f"设备 {self.client_ip} 下线成功")
            return True
        except Exception as e:
            logger.error(f"设备下线失败: {traceback.format_exc()}")
            return False

    def _watch_heart(self):
        """心跳线程"""
        while True:
            try:
                with self.heart_lock:
                    if self.sock:
                        self.sock.send(self.send_command('H', 0, 1, 0, bytes([0x00])))
                threading.Event().wait(30)  # 每30秒发送一次心跳
            except Exception as e:
                logger.error(f"心跳发送失败: {traceback.format_exc()}")
                break

    def _async_receive_data(self):
        """接收数据线程"""
        while True:
            try:
                if self.sock:
                    data = self.sock.recv(1024)
                    if data:
                        self.RECV_LIST.append(data)
            except Exception as e:
                logger.error(f"数据接收失败: {traceback.format_exc()}")
                break

class BusinessProtocol(BaseProtocol):
    def __init__(self, server_ip: str, server_port: int, client_ip: str, client_port: int = 0):
        super().__init__(server_ip, server_port, client_ip, client_port)

    def send_img(self, i_serial: str, i_plate_no: str, i_car_style: int, i_is_etc: int, 
                i_etc_no: str, i_recog_enable: int, i_color: int, i_data_type: int, 
                i_open_type: int, i_cap_time: datetime) -> bool:
        """发送车辆进出场信息"""
        try:
            logger.info(f'''模拟压地感请求参数：serial:{i_serial}, plate_no:{i_plate_no}, car_style:{i_car_style}, 
                        is_etc:{i_is_etc}, etc_no:{i_etc_no}, recog:{i_recog_enable}, color:{i_color}, 
                        data_type:{i_data_type}, open_type:{i_open_type}, i_cap_time:{i_cap_time}''')
            
            if not self.sock or self.sock._closed:
                raise Exception(f"{self.client_ip}设备未连接")

            plateno_list = i_plate_no.split(',')
            for plate_no in plateno_list:
                logger.info(f"开始发送图片,推送车辆信息,{plate_no}")
                self._send_imgs(i_serial, plate_no, int(i_car_style), int(i_is_etc), i_etc_no,
                              int(i_recog_enable), i_color, i_data_type, i_open_type, i_cap_time)
            return True
        except Exception as e:
            logger.error(f"发送车辆信息失败: {traceback.format_exc()}")
            return False

    def _send_imgs(self, i_serial: str, i_plate_no: str, i_car_style: int, i_is_etc: int, 
                  i_etc_no: str, i_recog_enable: int, i_color: int, i_data_type: int, 
                  i_open_type: int, i_cap_time: datetime):
        """发送单条车辆信息"""
        try:
            # 进出口类型
            first_byte = bytes([0x00])
            if i_open_type == 0:  # 入场
                inout_byte = bytes([0x05])
            else:  # 出场
                inout_byte = bytes([0x06])

            # 序列号
            if len(i_serial) == 0:
                i_serial = '000000'
            serial_byte = struct.pack('!i', int(i_serial))

            # 车牌号
            plate_no_bytes = bytes(i_plate_no, encoding="utf8")

            # 车型
            car_style_byte = bytes([i_car_style])

            # 是否ETC
            isetc_byte = bytes([i_is_etc])

            # 识别度
            recog_byte = struct.pack('!i', i_recog_enable)

            # 车辆颜色
            color_byte = bytes([i_color])

            # 数据类型
            data_type_byte = bytes([i_data_type])

            # 组装数据
            data = (first_byte + inout_byte + serial_byte + plate_no_bytes + car_style_byte + 
                   isetc_byte + recog_byte + color_byte + data_type_byte)

            # 发送命令
            command = self.send_command('I', 0, 1, 0, data, i_cap_time)
            with self.send_lock:
                self.sock.send(command)
        except Exception as e:
            logger.error(f"发送车辆信息失败: {traceback.format_exc()}")
            raise

class PaymentProtocol(BaseProtocol):
    def __init__(self, server_ip: str, server_port: int, client_ip: str, client_port: int = 0):
        super().__init__(server_ip, server_port, client_ip, client_port)

    def pay_order(self, order_no: str, pay_money: int, car_no: str) -> bool:
        """支付订单"""
        try:
            if not self.sock or self.sock._closed:
                raise Exception(f"{self.client_ip}设备未连接")

            # 组装支付数据
            data = (
                bytes([0x00]) +  # 固定头
                bytes(order_no, encoding="utf8") +  # 订单号
                struct.pack('!i', pay_money) +  # 支付金额
                bytes(car_no, encoding="utf8")  # 车牌号
            )

            # 发送支付命令
            command = self.send_command('P', 0, 1, 0, data)
            with self.send_lock:
                self.sock.send(command)
            return True
        except Exception as e:
            logger.error(f"支付订单失败: {traceback.format_exc()}")
            return False

    def refund_order(self, order_no: str, refund_money: int, car_no: str) -> bool:
        """退款订单"""
        try:
            if not self.sock or self.sock._closed:
                raise Exception(f"{self.client_ip}设备未连接")

            # 组装退款数据
            data = (
                bytes([0x00]) +  # 固定头
                bytes(order_no, encoding="utf8") +  # 订单号
                struct.pack('!i', refund_money) +  # 退款金额
                bytes(car_no, encoding="utf8")  # 车牌号
            )

            # 发送退款命令
            command = self.send_command('R', 0, 1, 0, data)
            with self.send_lock:
                self.sock.send(command)
            return True
        except Exception as e:
            logger.error(f"退款订单失败: {traceback.format_exc()}")
            return False
