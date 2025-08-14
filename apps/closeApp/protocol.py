from typing import Optional
import socket
import threading
import struct
import traceback
from datetime import datetime
from core.logger import logger
import os
import math
import time
import numpy as np


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
        self.write_lock = threading.Lock()
        self.RECV_LIST = []
        self.img_data_list = None

    def connect(self):
        """建立TCP连接"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 使用 0.0.0.0 或 localhost 代替特定的客户端 IP
            try:
                self.sock.bind((self.client_ip, self.client_port))
            except Exception as e:
                logger.error(f"无法绑定{self.client_ip}:{self.client_port}: {str(e)}")
                return False
            self.sock.settimeout(3000)
            logger.debug(f"尝试连接到 {self.server_ip}:{self.server_port}")
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
                     park_serial: int, data: bytes, i_cap_time=None) -> bytes:
        """
        通用指令
        :return:
        """
        try:
            # 发送指令
            if time_span == 0 and i_cap_time is None:
                i_cap_time = datetime.now()
            if time_span == 0:
                time_span = int(
                    time.mktime(time.strptime(i_cap_time.strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')))
            data_len = len(data)

            # 时间戳字节
            time_span_byte = struct.pack('!i', time_span)

            # 指令类型字节
            command_byte = bytes(command_name, encoding="utf8")

            # 数据包总数
            total_packs_byte = struct.pack('!h', total_park)

            # 第几个数据包
            park_serial_byte = struct.pack('!h', park_serial)

            # 数据包信息
            data_len_byte = struct.pack('!h', data_len)

            # 消息体
            data_bytes2 = time_span_byte + command_byte + total_packs_byte + park_serial_byte + data_len_byte

            # 校验码
            try:
                i = 0
                data_int = 0
                data_int_bytes = data_bytes2 + data
                while i < len(data_int_bytes):
                    temp = np.int16([data_int_bytes[i]])
                    if data_int > 0:
                        data_int = np.int16(data_int + temp)
                    else:
                        data_int = np.int16(data_int + temp)
                    i += 1
            except Exception as msg:
                raise RuntimeError(logger.error(traceback.format_exc()))
            data_bytes2 = data_bytes2 + data

            # 校验码字节
            total_length_byte = struct.pack('!h', data_int[0])

            total_bytes = data_bytes2 + total_length_byte
            body_bytes = self.escape_send_data(total_bytes)

            # 完整消息体
            body_send_bytes = bytes([0xfb]) + body_bytes + bytes([0xfe])
            return body_send_bytes
        except Exception as msg:
            raise Exception(logger.error(traceback.format_exc()))

    def send_com_command(self, command_name: str, data: bytes) -> bytes:
        return self.send_command(command_name, 0, 1, 0, data)

    def escape_send_data(self, data_bytes: bytes) -> bytes:
        """
        发送转义
        :param data_bytes: 需要发送的字节
        :return: 转义后的字节
        """
        k = 0
        new_bytes = bytes()
        while k < len(data_bytes):
            if data_bytes[k] == 0xfb:
                new_bytes = new_bytes + bytes([0xff, 0xbb])
            elif data_bytes[k] == 0xff:
                new_bytes = new_bytes + bytes([0xff, 0xfc])
            elif data_bytes[k] == 0xfe:
                new_bytes = new_bytes + bytes([0xff, 0xee])
            else:
                new_bytes = new_bytes + bytes([data_bytes[k]])
            k = k + 1
        return new_bytes

    def escape_receive_data(self, data_bytes: bytes) -> bytes:
        """
        接收转义
        :param data_bytes: 接收的字节
        :return: 转义后的字节
        """
        k = 0
        new_bytes = bytes()
        while k < len(data_bytes):
            if data_bytes[k] == 0xff:
                if k + 1 < len(data_bytes):
                    if data_bytes[k + 1] == 0xbb:
                        new_bytes = new_bytes + bytes([0xfb])
                        k += 2
                        continue
                    elif data_bytes[k + 1] == 0xfc:
                        new_bytes = new_bytes + bytes([0xff])
                        k += 2
                        continue
                    elif data_bytes[k + 1] == 0xee:
                        new_bytes = new_bytes + bytes([0xfe])
                        k += 2
                        continue
            new_bytes = new_bytes + bytes([data_bytes[k]])
            k += 1
        return new_bytes

    def _async_receive_data(self):
        """
        接收服务端消息线程
        :return:
        """
        return_temp = None
        while not return_temp:
            try:
                total_receve = bytes()
                with self.recv_lock:
                    if not self.sock._closed:
                        receive_msg = self.sock.recv(65535)
                        if len(receive_msg) == 0:
                            time.sleep(0.1)
                            continue
                        if len(receive_msg) < 15:
                            total_receve += receive_msg
                            continue
                        else:
                            total_receve = receive_msg
                        if total_receve[len(total_receve) - 1:len(total_receve)] == bytes([0xfe]):
                            return_temp = self._receive_command(total_receve)
                            total_receve = bytes(0)
                        else:
                            continue
                    else:
                        return
            except OSError:
                pass
            except Exception as ex_receive_msg:
                logger.error(traceback.format_exc())

    def _receive_command(self, receive_bytes: bytes):
        """
        接收服务端信息处理
        :param receive_bytes:
        :return:
        """
        try:
            msg_list = self._receive_data_to_tuple(receive_bytes)
            for child in msg_list:
                if child[1] != bytes([0xee]) and child[1] != bytes([0xbb]) and child[1] != bytes([0xfc]):
                    try:
                        command_name = child[1].decode('utf-8')
                    except Exception as msg:
                        logger.warning("%s child:%s" % (msg, str(child)))
                        command_name = str(child[1])
                    if command_name != 'F':
                        logger.debug('%s,收到%s指令' % (self.client_ip, command_name))
                    if command_name == 'C':
                        break
                    elif command_name == 'D':
                        break
                    elif command_name == 'F':
                        break
                    elif command_name == 'V':
                        version_no = 'test'
                        with self.send_lock:
                            self.sock.send(self.send_com_command('V', bytes(version_no, encoding="utf-8")))
                        logger.debug('%s,发送V指令' % self.client_ip)
                    elif command_name == 'R':
                        with self.send_lock:
                            self.sock.send(self.send_com_command('R', bytes([0])))
                        logger.debug('%s,收到开闸指令,发送R指令应答' % self.client_ip)
                    with self.write_lock:
                        self.RECV_LIST.append(command_name)
        except Exception as cmd_ex:
            raise RuntimeError(logger.error('%s:%s' % (self.client_ip, traceback.format_exc())))

    def _receive_data_to_tuple(self, recivedata: bytes):
        """
        接收数据解析
        :param recivedata:
        :return:
        """
        try:
            types_list = recivedata.split(bytes([0xfb]))
            tuple_list = []
            for row in types_list:
                if len(row) > 0:
                    row_new = bytes([0xfb]) + row
                    recevie_body = self.escape_receive_data(row_new)
                    data_length = len(recevie_body) - 15
                    data_type = bytes()
                    if data_length > 0:
                        unpark_tuple = struct.unpack('!i1s4h', recevie_body[1:14])
                        data_type = recevie_body[15: len(recevie_body) - 1]
                    else:
                        unpark_tuple = struct.unpack('!i1s4h', recevie_body[1:14])
                    tuple_to_list = list(unpark_tuple)
                    tuple_to_list.append(data_type)
                    tuple_list.append(tuple_to_list)
            return tuple_list
        except Exception as ex_msg:
            raise RuntimeError(logger.error(traceback.format_exc()))

class DeviceProtocol(BaseProtocol):
    def __init__(self, server_ip: str, server_port: int, client_ip: str, client_port: int = 0):
        super().__init__(server_ip, server_port, client_ip, client_port)
        self.heart_thread = None
        self.recv_thread = None
        self.last_heartbeat_at = None  # 记录最后一次心跳成功的时间戳

    def device_on(self, device_type: str = '1') -> bool:
        """设备上线"""
        try:
            if not self.connect():
                return False

            with self.send_lock:
                # 发送设备类型
                if str(device_type) == '10':
                    self.sock.send(self.send_com_command('C', bytes([0x0C, 0x04, 0x00, 0x31])))
                else:
                    self.sock.send(self.send_com_command('C', bytes([0x01, 0x04, 0x00])))
                
                # 发送设备IP
                self.sock.send(self.send_com_command('D', bytes(self.client_ip, encoding="utf-8")))
                
                # 发送状态
                self.sock.send(self.send_com_command('F', bytes([0x00])))

            # 启动心跳和接收线程
            self.heart_thread = threading.Thread(target=self._watch_heart, daemon=True)
            self.recv_thread = threading.Thread(target=self._async_receive_data, daemon=True)
            self.heart_thread.start()
            self.recv_thread.start()

            logger.debug(f"设备 {self.client_ip} 上线成功")
            return True
        except Exception as e:
            logger.error(f"设备上线失败: {traceback.format_exc()}")
            return False

    def device_off(self) -> bool:
        """设备下线"""
        try:
            if self.sock:
                self.close()
            self.last_heartbeat_at = None  # 清空心跳时间戳
            logger.debug(f"设备 {self.client_ip} 下线成功")
            return True
        except Exception as e:
            logger.error(f"设备下线失败: {traceback.format_exc()}")
            return False

    def is_connected(self) -> bool:
        """检查设备是否仍然连接"""
        return self.sock is not None and not self.sock._closed

    def _watch_heart(self):
        """心跳线程"""
        while True:
            try:
                with self.heart_lock:
                    if self.sock and not self.sock._closed:
                        with self.send_lock:
                            self.sock.send(self.send_com_command('F', bytes([0x00])))
                            # 心跳发送成功，更新时间戳
                            self.last_heartbeat_at = time.time()
                        time.sleep(5)
                    else:
                        # 连接已断开，清空心跳时间戳
                        self.last_heartbeat_at = None
                        return
            except Exception as e:
                logger.error(f"心跳发送失败: {traceback.format_exc()}")
                # 心跳异常，清空时间戳
                self.last_heartbeat_at = None
                break

class BusinessProtocol(BaseProtocol):
    def __init__(self, server_ip: str, server_port: int, client_ip: str, client_port: int = 0):
        super().__init__(server_ip, server_port, client_ip, client_port)

    def send_img(self, i_serial: str, i_plate_no: str, i_car_style: int, i_is_etc: int, 
                i_etc_no: str, i_recog_enable: int, i_color: int, i_data_type: int, 
                i_open_type: int, i_cap_time: datetime) -> bool:
        """发送车辆进出场信息"""
        try:
            logger.debug(f'''模拟压地感请求参数：serial:{i_serial}, plate_no:{i_plate_no}, car_style:{i_car_style}, 
                        is_etc:{i_is_etc}, etc_no:{i_etc_no}, recog:{i_recog_enable}, color:{i_color}, 
                        data_type:{i_data_type}, open_type:{i_open_type}, i_cap_time:{i_cap_time}''')
            
            if not self.sock or self.sock._closed:
                raise Exception(f"{self.client_ip}设备未连接")

            plateno_list = i_plate_no.split(',')
            for plate_no in plateno_list:
                logger.debug(f"开始发送图片,推送车辆信息,{plate_no}")
                self._send_imgs(i_serial, plate_no, int(i_car_style), int(i_is_etc), i_etc_no,
                              int(i_recog_enable), i_color, i_data_type, i_open_type, i_cap_time)
            return True
        except Exception as e:
            logger.error(f"发送车辆信息失败: {traceback.format_exc()}")
            return False

    def _send_imgs(self, i_serial: str, i_plate_no: str, i_car_style: int, i_is_etc: int, 
                  i_etc_no: str, i_recog_enable: int, i_color: int, i_data_type: int, 
                  i_open_type: int, i_cap_time: datetime):
        """
        发送过车消息
        :param i_serial:
        :param i_plate_no:
        :param i_car_style:
        :param i_is_etc:
        :param i_etc_no:
        :param i_recog_enable:
        :return:
        """
        try:
            img_list = self._send_command_img(i_serial, i_plate_no, i_car_style, i_is_etc, i_etc_no, i_recog_enable,
                                             i_color, i_data_type, i_open_type, i_cap_time)
            logger.debug("发送J指令：" + str(img_list[0]))
            self.img_data_list = img_list
            with self.send_lock:
                self.sock.send(img_list[0])

            time.sleep(0.01)
            if self.img_data_list is not None:
                if len(self.img_data_list) > 0:
                    total_len = len(self.img_data_list)
                    ki = 1
                    logger.debug("%s,发送J指令第%s包" % (self.client_ip, ki))
                    while ki < total_len:
                        with self.send_lock:
                            self.sock.send(self.img_data_list[ki])
                            ki = ki + 1
                    self.img_data_list = None
                    logger.debug("%s,发送J指令第%s包" % (self.client_ip, ki))

            return True
        except Exception as ex_img_msg:
            raise Exception(logger.error(traceback.format_exc()))

    def _send_command_img(self, i_serial: str, i_plate_no: str, i_car_style: int, i_is_etc: int, 
                         i_etc_no: str, i_recog_enable: int, i_color: int, i_data_type: int, 
                         i_open_type: int, i_cap_time: datetime):
        """
        J指令数据包封装
        :param i_serial:
        :param i_plate_no:
        :param i_car_style:
        :param i_is_etc:
        :param i_etc_no:
        :param i_recog_enable:
        :return:
        """
        try:
            logger.debug(f"开始封装J指令数据包")
            img_list = []
            data_bytes = bytes()
            # 时间戳字节
            if i_cap_time is None:
                i_cap_time = datetime.now()
            time_span = int(time.mktime(time.strptime(i_cap_time.strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')))
            # 指令类型
            command_name = 'J'

            # 第0个数据包
            park_serial = 0

            # 数据包总数
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            img_url = os.path.join(project_root, 'static')
            img_name = os.path.join(img_url, 'default_car.jpg')
            
            # 确保图像文件存在
            if not os.path.exists(img_name):
                # 如果原始图片不存在，创建一个空图片
                logger.warning(f"图像文件 {img_name} 不存在，使用默认图像数据")
                img_bytes = bytes([0xFF] * 1024 * 10)  # 创建一个较大的图像数据
            else:
                # 读取图片数据
                with open(img_name, 'rb') as f:
                    img_bytes = f.read()
                
            total_packs = int(math.ceil((len(img_bytes) * 1.0) / 1024))

            # 卡号标志 1个字节
            is_etc = bytes([i_is_etc])
            img_data = is_etc

            # 卡号信息 28个字节
            if i_is_etc == 1:
                etc_no = bytes(i_etc_no, encoding="gbk")
                img_data = img_data + etc_no + bytes(28 - len(etc_no))
            else:
                if len(i_serial) > 0:
                    etc_no = bytes(12)
                    img_data = img_data + etc_no
                    img_data = img_data + struct.pack('!i', int(i_serial))
                    img_data = img_data + etc_no
                else:
                    etc_no = bytes(28)
                    img_data = img_data + etc_no

            # 车牌颜色 1、"白",2、"黑","3、蓝",4、"黄",5、"绿" 1个字节
            color = bytes([i_color])
            img_data = img_data + color

            # 车牌号
            plate_bytes = bytes(i_plate_no, encoding="gbk")
            img_data = img_data + plate_bytes
            if len(plate_bytes) < 15:
                plate_new_len = 15 - len(plate_bytes)
                plate_new_bytes = bytes(plate_new_len)[0:plate_new_len]
                img_data = img_data + plate_new_bytes

            # 识别度
            img_data = img_data + struct.pack('!h', int(i_recog_enable))

            # 开闸及缓存
            is_open = bytes([int(i_data_type + i_open_type)])
            img_data = img_data + is_open

            # 投票标记
            is_null = bytes([0])
            img_data = img_data + is_null

            # 车型
            img_data = img_data + bytes([i_car_style])

            # 车长
            car_len = bytes([0])
            img_data = img_data + car_len

            # 车标信息
            img_data = img_data + bytes(10)

            # 总图像数据长度
            img_len = struct.pack('!i', len(img_bytes))
            img_data = img_data + img_len
            first_data = self.send_command(command_name, time_span, total_packs, park_serial, img_data)
            img_list.append(first_data)

            k = 0
            temp_data = bytes(1024)
            while k < total_packs:
                k += 1
                temp_data = img_bytes[(k - 1) * len(temp_data): k * len(temp_data)]
                temp_data_len = len(temp_data)
                temp_data_bytes = self.send_command(command_name, time_span, total_packs, k, temp_data)
                if temp_data_len < len(temp_data):
                    break
                img_list.append(temp_data_bytes)
            return img_list
        except Exception as msg:
            raise RuntimeError(logger.error(traceback.format_exc()))

class PaymentProtocol(BaseProtocol):
    def __init__(self, server_ip: str, server_port: int, client_ip: str, client_port: int = 0):
        super().__init__(server_ip, server_port, client_ip, client_port)

    def pay_order(self, order_no: str, pay_money: int, car_no: str) -> bool:
        """支付订单"""
        try:
            if not self.connect():
                return False
                
            logger.debug(f"支付订单：订单号={order_no}, 金额={pay_money}, 车牌号={car_no}")

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
                
            self.close()
            return True
        except Exception as e:
            logger.error(f"支付订单失败: {traceback.format_exc()}")
            self.close()
            return False

    def refund_order(self, order_no: str, refund_money: int, car_no: str) -> bool:
        """退款订单"""
        try:
            if not self.connect():
                return False
                
            logger.debug(f"退款订单：订单号={order_no}, 金额={refund_money}, 车牌号={car_no}")

            # 组装退款数据
            data = (
                bytes([0x01]) +  # 固定头，退款用01
                bytes(order_no, encoding="utf8") +  # 订单号
                struct.pack('!i', refund_money) +  # 退款金额
                bytes(car_no, encoding="utf8")  # 车牌号
            )

            # 发送退款命令
            command = self.send_command('P', 0, 1, 0, data)
            with self.send_lock:
                self.sock.send(command)
                
            self.close()
            return True
        except Exception as e:
            logger.error(f"退款订单失败: {traceback.format_exc()}")
            self.close()
            return False
