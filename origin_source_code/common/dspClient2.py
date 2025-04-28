import socket
import os
import math
import time
import struct
import numpy as np
import traceback
import datetime
import threading
from common.configLog import logger


class DspClient:
    def __init__(self, server_ip, server_port, client_ip, client_port=0):
        self.server_ip = str(server_ip)
        self.server_port = int(server_port)
        self.client_ip = str(client_ip)
        self.client_port = int(client_port)
        self.img_data_list = None
        self.heart_lock = threading.Lock()
        self.recv_lock = threading.Lock()
        self.send_lock = threading.Lock()
        self.write_lock = threading.Lock()
        self.RECV_LIST = []
        self.sock = None

    def connect(self, device_type='1'):
        """
        模拟设备上线
        连接车场,并开启心跳线程和接受线程
        :return:
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.client_ip, self.client_port))
            self.sock.settimeout(3000)
            self.sock.connect((self.server_ip, self.server_port))
            with self.send_lock:
                if str(device_type) == '10':
                    self.sock.send(self.send_com_command('C', bytes([0x0C, 0x04, 0x00, 0x31])))
                else:
                    self.sock.send(self.send_com_command('C', bytes([0x01, 0x04, 0x00])))
                self.sock.send(self.send_com_command('D', bytes(self.client_ip, encoding="utf-8")))
                self.sock.send(self.send_com_command('F', bytes([0x00])))
            threading.Thread(target=self.watch_heart, daemon=True).start()
            threading.Thread(target=self.async_receive_data, daemon=True).start()
        except Exception as ex_img_msg:
            raise Exception(logger.error(traceback.format_exc()))

    def close(self):
        """
        模拟设备下线
        断开车场连接
        :return:
        """
        try:
            self.sock.close()
        except Exception as ex_img_msg:
            raise Exception(logger.error(traceback.format_exc()))

    def send_etcno(self, i_serial, i_is_etc, i_etc_no, i_in_out_type, i_cap_time):
        """
        模拟取卡取票
        卡票信息
        :param ws_key:
        :param server_ip:
        :param dsp_ip:
        :param i_is_etc:
        :param i_etc_no:
        :param i_in_out_type:
        :return:
        """
        try:
            logger.info('模拟取卡取票请求参数：serial:%s, is_etc:%s, etc_no:%s, in_out_type:%s, cap_time:%s' % (
            i_serial, i_is_etc, i_etc_no, i_in_out_type, i_cap_time))
            if not self.sock._closed:
                if len(i_etc_no) > 0:
                    self.send_etc(i_serial, int(i_is_etc), i_etc_no, i_in_out_type, i_cap_time)
                    # time.sleep(5)
            else:
                raise Exception(logger.error("%s设备未连接" % self.client_ip))
        except Exception as ex_img_msg:
            raise Exception(logger.error(traceback.format_exc()))

    def send_etc(self, i_serial, i_is_etc, i_etc_no, i_in_out_type, i_cap_time):
        """
        发送过车消息
        :param i_serial:序列号
        :param i_plate_no:
        :param i_car_style:
        :param i_is_etc:
        :param i_etc_no:
        :param i_recog_enable:
        :return:
        """
        try:
            # 进出口类型
            first_byte = bytes([0x00])
            if i_in_out_type == 1:
                inout_byte = bytes([0x05])
            else:
                inout_byte = bytes([0x06])

            # 取卡取票指令类型 0102
            one_byte = bytes([0x01])
            two_byte = bytes([0x02])

            # 序列号
            if len(i_serial) == 0:
                i_serial = '000000'
            serial_byte = struct.pack('!i', int(i_serial))

            # 取卡取票类型 0:取卡, 1:刷卡, 2:取票；5:验证码；6:远距离卡号(华为)
            isetc_byte = bytes([i_is_etc])

            # 0:未开闸; 1:已开闸；
            isopen_byte = bytes([0x00])

            # 0:非缓存; 1:已缓存；
            iscache_byte = bytes([0x00])

            # 卡票号长度（数值，16进制）
            etcnolen_byte = bytes([len(i_etc_no)])

            # 出车卡/票号（可见字符串）
            etcno_byte = bytes(i_etc_no, encoding="utf8")

            etc_total_bytes = first_byte + inout_byte + one_byte + two_byte + serial_byte + isetc_byte + isopen_byte + iscache_byte + etcnolen_byte + etcno_byte

            totoal_types = self.send_command('Z', 0, 1, 0, etc_total_bytes, i_cap_time)

            logger.info(self.client_ip + ",发送Z指令：" + i_etc_no)
            with self.send_lock:
                self.sock.send(totoal_types)
        except Exception as ex_img_msg:
            raise Exception(traceback.format_exc())

    def send_img(self, i_serial, i_plate_no, i_car_style, i_is_etc, i_etc_no, i_recog_enable, i_color,
                 i_data_type, i_open_type, i_cap_time):
        """
        发送图片
        :param dsp_ip:设备IP
        :param i_serial: 序列号
        :param i_plate_no: 车牌号
        :param i_car_style: 车型
        :param i_is_etc: 是否卡票
        :param i_etc_no: 卡\票号
        :param i_recog_enable: 识别度
        :return:
        """
        try:
            logger.info('''模拟压地感请求参数：serial:%s, plate_no:%s, car_style:%s, is_etc:%s, etc_no:%s, recog:%s, 
                        color:%s, data_type:%s, open_type:%s, i_cap_time:%s''' % (
                i_serial, i_plate_no, i_car_style, i_is_etc, i_etc_no,
                i_recog_enable, i_color, i_data_type, i_open_type, i_cap_time))
            if not self.sock._closed:
                plateno_list = i_plate_no.split(',')
                for plate_no in plateno_list:
                    logger.info("开始发送图片,推送车辆信息,%s" % plate_no)
                    self.send_imgs(i_serial, plate_no, int(i_car_style), int(i_is_etc), i_etc_no,
                                   int(i_recog_enable), i_color, i_data_type, i_open_type, i_cap_time)
            else:
                raise Exception(logger.error("%s设备未连接" % self.client_ip))
        except Exception as ex_img_msg:
            raise Exception(logger.error(traceback.format_exc()))

    def send_z_comcmd(self, i_serial, i_open_type, i_cap_time):
        try:
            if not self.sock._closed:
                open_type_msg = ''
                if i_open_type >= 11:
                    if i_open_type == 11:
                        open_type_msg = '未开闸前后退离开地感'
                    elif i_open_type == 12:
                        open_type_msg = '开闸后后退离开地感'
                    elif i_open_type == 13:
                        open_type_msg = '未开闸时前进离开地感'
                    elif i_open_type == 14:
                        open_type_msg = '已开闸时前进离开地感'
                    elif i_open_type == 15:
                        open_type_msg = '道闸杆被折断'
                    logger.info('''模拟%s请求参数：serial:%s, open_type:%s, i_cap_time:%s''' % (
                        open_type_msg, i_serial, i_open_type, i_cap_time))
                    self.send_z_cmd(i_serial, i_open_type, i_cap_time)
            else:
                raise Exception(logger.error("%s设备未连接" % self.client_ip))
        except Exception as ex_zcmd_msg:
            raise Exception(logger.error(traceback.format_exc()))

    def send_z_cmd(self, i_serial, i_open_type, i_cap_time):
        """

        :param ws_key:
        :param i_serial:
        :param i_open_type:
        :param i_cap_time:
        :return:
        """
        try:
            first_byte = bytes([0x09])
            one_byte = bytes([0x00])
            two_byte = bytes(0)
            if i_open_type == 11:
                two_byte = bytes([0x05])
            elif i_open_type == 12:
                two_byte = bytes([0x06])
            elif i_open_type == 13:
                two_byte = bytes([0x07])
            elif i_open_type == 14:
                two_byte = bytes([0x09])
            elif i_open_type == 15:
                two_byte = bytes([0x08])
            logger.info('z指令：' + str(two_byte))
            # 序列号
            if len(i_serial) == 0:
                i_serial = '000000'
            serial_byte = struct.pack('!i', int(i_serial))
            etc_total_bytes = one_byte + first_byte + one_byte + two_byte + serial_byte
            totoal_types = self.send_command('Z', 0, 1, 0, etc_total_bytes, i_cap_time)

            logger.info("发送Z指令：0009")
            with self.send_lock:
                self.sock.send(totoal_types)
            return True
        except Exception as ex_img_msg:
            raise RuntimeError(logger.error(traceback.format_exc()))

    def send_imgs(self, i_serial, i_plate_no, i_car_style, i_is_etc, i_etc_no, i_recog_enable, i_color, i_data_type,
                  i_open_type, i_cap_time):
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
            img_list = self.send_command_img(i_serial, i_plate_no, i_car_style, i_is_etc, i_etc_no, i_recog_enable,
                                             i_color, i_data_type, i_open_type, i_cap_time)
            logger.info("发送J指令：" + str(img_list[0]))
            self.img_data_list = img_list
            with self.send_lock:
                self.sock.send(img_list[0])

            time.sleep(0.01)
            if self.img_data_list is not None:
                if len(self.img_data_list) > 0:
                    total_len = len(self.img_data_list)
                    ki = 1
                    logger.info("%s,发送J指令第%s包" % (self.client_ip, ki))
                    while ki < total_len:
                        with self.send_lock:
                            self.sock.send(self.img_data_list[ki])
                            time.sleep(0.01)
                            ki = ki + 1
                    self.img_data_list = None
                    logger.info("%s,发送J指令第%s包" % (self.client_ip, ki))

            return True
        except Exception as ex_img_msg:
            raise Exception(logger.error(traceback.format_exc()))

    def send_command_img(self, i_serial, i_plate_no, i_car_style, i_is_etc, i_etc_no, i_recog_enable, i_color,
                         i_data_type, i_open_type, i_cap_time):
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
            img_list = []
            data_bytes = bytes()
            # 时间戳字节
            if i_cap_time is None:
                i_cap_time = datetime.datetime.now()
            time_span = int(time.mktime(time.strptime(i_cap_time.strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')))
            # time_span = int(time.mktime(i_cap_time))
            # 指令类型
            command_name = 'J'

            # 第0个数据包
            park_serial = 0

            # 数据包总数
            img_url = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Files')
            img_name = os.path.join(img_url, '201604091316_02187_蓝皖J84846_Benz') + ".jpg"
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

            # 车牌颜色 1、"白",2、"黑","3、蓝",4、"黄",5、”绿” 1个字节
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
            # if int(i_data_type) == 0:
            #     is_open = bytes([int('000' + i_open_type, 2)])
            # else:
            #     is_open = bytes([])
            # is_open = bytes([int(i_data_type)]) + bytes([int(i_open_type)])
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

    def send_command(self, command_name, time_span, total_park, park_serial, data, i_cap_time=None):
        """
        通用指令
        :return:
        """
        try:
            # 发送指令
            if time_span == 0 and i_cap_time is None:
                i_cap_time = datetime.datetime.now()
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

    def send_com_command(self, command_name, data):
        return self.send_command(command_name, 0, 1, 0, data)

    def escape_send_data(self, data_bytes):
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

    def watch_heart(self):
        """
        心跳监视
        :return:
        """
        while True:
            try:
                with self.heart_lock:
                    if not self.sock._closed:
                        with self.send_lock:
                            self.sock.send(self.send_com_command('F', bytes([0x00])))
                        time.sleep(5)
                    else:
                        return
            except Exception as ex_msg:
                raise RuntimeError(logger.error(traceback.format_exc()))

    def async_receive_data(self):
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
                            return_temp = self.receive_command(total_receve)
                            total_receve = bytes(0)
                            # time.sleep(0.1)
                        else:
                            continue
                    else:
                        return
            except OSError:

                # logger.warning('[WinError 10038] 在一个非套接字上尝试了一个操作。')
                pass
            except Exception as ex_receive_msg:
                logger.error(traceback.format_exc())

    def receive_command(self, receive_bytes):
        """
        接收服务端信息处理
        :param receive_bytes:
        :return:
        """
        try:
            msg_list = self.recive_data_to_tuple(receive_bytes)
            for child in msg_list:
                if child[1] != bytes([0xee]) and child[1] != bytes([0xbb]) and child[1] != bytes([0xfc]):
                    try:
                        command_name = child[1].decode('utf-8')
                    except Exception as msg:
                        logger.warning("%s child:%s" % (msg, str(child)))
                        command_name = str(child[1])
                    if command_name != 'F':
                        logger.info('%s,收到%s指令' % (self.client_ip, command_name))
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
                        logger.info('%s,发送V指令' % self.client_ip)
                    # elif command_name == 'J':
                    #     time.sleep(0.01)
                    #     if self.img_data_list is not None:
                    #         if len(self.img_data_list) > 0:
                    #             total_len = len(self.img_data_list)
                    #             ki = 1
                    #             logger.info("%s,发送J指令第%s包" % (self.client_ip, ki))
                    #             while ki < total_len:
                    #                 with self.send_lock:
                    #                     self.sock.send(self.img_data_list[ki])
                    #                     time.sleep(0.01)
                    #                     ki = ki + 1
                    #             self.img_data_list = None
                    #             logger.info("%s,发送J指令第%s包" % (self.client_ip, ki))
                    elif command_name == 'R':
                        with self.send_lock:
                            self.sock.send(self.send_com_command('R', bytes([0])))
                        logger.info('%s,收到开闸指令,发送R指令应答' % self.client_ip)
                    with self.write_lock:
                        self.RECV_LIST.append(command_name)
        except Exception as cmd_ex:
            raise RuntimeError(logger.error('%s:%s' % (self.client_ip, traceback.format_exc())))

    def recive_data_to_tuple(self, recivedata):
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

    def escape_receive_data(self, data_bytes):
        """
        接收转义
        :param data_bytes: 接收的字节
        :return: 转义后的字节
        """

        k = 0
        new_bytes = bytes()
        while k < len(data_bytes):
            if data_bytes[k] == 0xff:
                if data_bytes[k + 1] == 0xbb:
                    new_bytes = new_bytes + bytes([0xfb])
                elif data_bytes[k + 1] == 0xfc:
                    new_bytes = new_bytes + bytes([0xff])
                elif data_bytes[k + 1] == 0xee:
                    new_bytes = new_bytes + bytes([0xfe])
                else:
                    new_bytes = new_bytes + bytes([data_bytes[k]])
            else:
                new_bytes = new_bytes + bytes([data_bytes[k]])
            k = k + 1
        return new_bytes

    def find_over(self, recv_msg, timeout=5):
        """
        查找结束命令
        :param recv_msg: 需要查找的命令, 字符串或列表
        :param timeout: 超时时间
        :return: 转义后的字节
        """
        if isinstance(recv_msg, str):
            msg_list = [recv_msg]
        elif isinstance(recv_msg, list):
            msg_list = recv_msg
        else:
            raise TypeError("错误的类型")
        try:
            endtime = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
            while datetime.datetime.now() < endtime:
                with self.write_lock:
                    for msg in msg_list:
                        if msg in self.RECV_LIST:
                            logger.info('%s find %s指令' % (self.client_ip, msg))
                            self.RECV_LIST.clear()
                            return
                time.sleep(0.1)
            logger.warning("%s not find %s命令" % (self.client_ip, recv_msg))
        except Exception as ex_msg:
            raise RuntimeError(logger.error(traceback.format_exc()))
