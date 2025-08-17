import time
import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from core.logger import logger
from .custom_enum import LotIdEnum, ServerIpEnum
from .schema import (
    DeviceOnOffRequest,
    CarInOutRequest
)
from .service import DeviceService, CarService, PaymentService, BaseService
from .config import Config
from .util import success_response, error_response
from typing import List, Optional

def convert_pydantic_model(obj):
    """将pydantic模型转换为字典，如果不是pydantic模型则直接返回"""
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    return obj

close_dsp_router = APIRouter()

base_service = BaseService()
device_service = DeviceService()
car_service = CarService(device_service)
pay_service = PaymentService()
config = Config()

@close_dsp_router.get("/deviceOn", description="设备上线接口", summary="设备上线接口")
async def device_on(
    device_list: str = Query(..., description="设备IP列表，多个IP用英文逗号分隔"),
    server_ip: ServerIpEnum = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236")
):
    """设备上线接口"""
    try:
        # 将逗号分隔的字符串转换为列表
        device_ip_list = [ip.strip() for ip in device_list.split(",") if ip.strip()]

        # 构造请求对象
        request = DeviceOnOffRequest(
            server_ip=server_ip,
            device_list=device_ip_list,
            device_type="1"
        )
        result = await device_service.device_on(request)
        return success_response(data=convert_pydantic_model(result))
    except Exception as e:
        logger.error(f"设备上线失败: {e}")
        return error_response(message=str(e))

@close_dsp_router.get("/deviceOff", description="设备下线接口", summary="设备下线接口")
async def device_off(
    device_list: str = Query(..., description="设备IP列表，多个IP用英文逗号分隔"),
    server_ip: ServerIpEnum = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236")
):
    """设备下线接口"""
    try:
        # 将逗号分隔的字符串转换为列表
        device_ip_list = [ip.strip() for ip in device_list.split(",") if ip.strip()]
        
        # 构造请求对象
        request = DeviceOnOffRequest(
            server_ip=server_ip,
            device_list=device_ip_list,
            device_type="1"
        )
        result = await device_service.device_off(request)
        return success_response(data=convert_pydantic_model(result))
    except Exception as e:
        logger.error(f"设备下线失败: {e}")
        return error_response(message=str(e))

@close_dsp_router.get("/carIn", description="车辆入场接口", summary="车辆入场接口")
async def car_in(
    car_no: str = Query("", description="车牌号"),
    i_open_type: int = Query(default=1, description="入场方式，不填默认相机直接放行(0:压地感 1:相机直接开闸放行)"),
    server_ip: ServerIpEnum = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236"),
    lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
    car_color: int = Query(default=3, description="车辆颜色(1:白 2:黑 3:蓝 4:黄 5:绿)"),
    recognition: int = Query(default=900, description="识别度"),
    i_serial: Optional[int] = Query(default=None, description="序列号")
):
    """车辆入场接口"""
    try:
        # 构造请求对象
        request = CarInOutRequest(
            server_ip=server_ip,
            car_no=car_no,
            lot_id=lot_id,
            car_color=car_color,
            recognition=recognition,
            i_serial=i_serial,
            i_open_type=i_open_type
        )
        # 入车
        res = await car_service.car_in(request)

        # 查询在场车验证，重试三次防止有入车延时
        retry = 3

        for attempt in range(retry):
            car_on_park = await car_service.get_on_park(lot_id=lot_id, car_no=car_no)
            if car_on_park["data"]["vos"]:  # 直接判断列表是否为空
                return success_response(data=convert_pydantic_model(res))
            
            if attempt < retry - 1:  # 最后一次不需要等待
                await asyncio.sleep(1)
                logger.info(f"执行入车后，在场车未查到车牌号{car_no}，尝试进行第{attempt + 2}次查询")

        logger.error(f"车辆入场失败！重试{retry}次后，车辆仍未入场")
        return error_response(message=f"车辆入场失败！重试{retry}次后，车辆仍未入场")
    except Exception as e:
        logger.error(f"车辆入场失败: {e}")
        return error_response(message=str(e))


@close_dsp_router.get("/carOut", description="车辆出场接口", summary="车辆出场接口")
async def car_out(
    car_no: str = Query("", description="车牌号"),
    i_open_type: int = Query(default=0, description="出场方式，不填默认压地感(0:压地感 1:相机直接开闸放行)"),
    server_ip: ServerIpEnum = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236"),
    lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
    car_color: int = Query(default=3, description="车辆颜色(1:白 2:黑 3:蓝 4:黄 5:绿)"),
    recognition: int = Query(default=900, description="识别度"),
    i_serial: Optional[int] = Query(default=None, description="序列号")
):
    """车辆出场接口"""
    try:
        # 构造请求对象
        request = CarInOutRequest(
            server_ip=server_ip,
            car_no=car_no,
            lot_id=lot_id,
            car_color=car_color,
            recognition=recognition,
            i_serial=i_serial,
            i_open_type = i_open_type
        )

        # 出车
        res = await car_service.car_out(request)

        # 查询在场车验证，重试三次防止有出车延时
        retry = 3

        for attempt in range(retry):
            car_on_park = await car_service.get_on_park(lot_id=lot_id, car_no=car_no)
            if not car_on_park["data"]["vos"]:  # 直接判断列表是否为空
                return success_response(data=convert_pydantic_model(res))

            if attempt < retry - 1:  # 最后一次不需要等待
                await asyncio.sleep(1)
                logger.info(f"执行出车后，在场车仍能查到车牌号{car_no}，尝试进行第{attempt + 2}次查询")

        logger.error(f"车辆出场失败！重试{retry}次后，车辆仍然在场")
        return error_response(message=f"车辆出场失败！重试{retry}次后，车辆仍然在场")
    except Exception as e:
        logger.error(f"车辆出场失败: {e}")
        return error_response(message=str(e))

@close_dsp_router.get("/carOnPark", description="查询在场车辆接口", summary="查询在场车辆接口")
async def get_on_park(
    lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
    car_no: str = Query(..., description="车牌号"),
    start_time: str = Query(default=datetime.now().strftime("%Y-%m-%d 00:00:00"), description="开始时间，非必填，不填默认当天00:00:00"),
    end_time: str = Query(default=datetime.now().strftime("%Y-%m-%d 23:59:59"), description="结束时间，非必填，不填默认当天23:59:59")
):
    """
    查询在场车辆
    :param lot_id: 车场ID
    :param car_no: 车牌号
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return: 在场车辆信息
    """
    try:
        result = await car_service.get_on_park(
            lot_id=lot_id,
            car_no=car_no,
            start_time=start_time,
            end_time=end_time
        )
        return success_response(data=result)
    except Exception as e:
        logger.error(f"查询在场车辆失败: {e}")
        return error_response(message=str(e))

@close_dsp_router.get("/payInfo", description="模拟获取支付信息接口", summary="模拟获取支付信息接口")
async def get_pay_info(
    car_no: str = Query(..., description="车牌号"),
    lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477")
):
    """获取支付订单信息接口"""
    kt_token = await pay_service.get_kt_token(lot_id)
    res = await pay_service.get_park_pay_info(kt_token, lot_id, car_no)
    return success_response(data=res)

@close_dsp_router.get("/payOrder", description="模拟支付订单接口", summary="模拟支付订单接口")
async def pay_order(
    car_no: str = Query(..., description="车牌号"),
    lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477")
):
    """模拟支付订单接口"""
    try:
        result = await pay_service.pay_order(lot_id, car_no)
        return success_response(data=convert_pydantic_model(result))
    except Exception as e:
        logger.error(f"支付订单失败: {e}")
        return error_response(message=str(e))



# @close_dsp_router.get("/refundOrder", description="模拟退款订单接口", summary="模拟退款订单接口")
# async def refund_order(
#     car_no: str = Query(..., description="车牌号"),
#     lot_id: str = Query(default="280025535", description="车场ID，测试环境280025535，灰度280030477")
# ):
#     """模拟退款订单接口"""
#     pass

@close_dsp_router.get("/config", description="获取配置信息接口", summary="获取配置信息接口")
async def get_config():
    """获取配置信息接口"""
    try:
        return success_response(data=config.config)
    except Exception as e:
        logger.error(f"获取配置信息失败: {e}")
        return error_response(message="获取配置信息失败")


@close_dsp_router.get("/nodeStatus", description="查询通道状态接口", summary="查询通道状态接口")
async def node_status(
    lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
    cloud_kt_token: str = Query(..., description="云助手token，需要自己代理到云助手获取一下")
):
    """查询通道状态接口"""
    try:
        all_status_list = await device_service.get_all_node_status(lot_id, cloud_kt_token)
        return success_response(data=convert_pydantic_model(all_status_list))
    except Exception as e:
        logger.error(f"查询通道状态失败: {e}")
        return error_response(message=f"查询通道状态失败：{e}")


@close_dsp_router.get("/changeNodeStatus", description="通道长抬状态变更接口", summary="通道长抬状态变更接口")
async def change_node_status(
        cloud_kt_token: str = Query(..., description="云助手token，需要自己代理到云助手获取一下"),
        lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
        node_ids: str = Query(..., description="通道ID列表"),
        status: int = Query(..., description="通道状态 0:关闭长抬，1:打开长抬"),
):
    """通道长抬状态变更接口"""
    try:
        res = await device_service.change_node_status(cloud_kt_token, lot_id, node_ids, status)
        return success_response(data=convert_pydantic_model(res))
    except Exception as e:
        logger.error(f"通道长抬状态变更失败: {e}")
        return error_response(message="通道长抬状态变更失败")


@close_dsp_router.get("/deviceStatus", description="查询设备真实在线状态接口", summary="查询设备真实在线状态接口")
async def get_device_status(
    device_ips: str = Query(..., description="设备IP列表，多个IP用英文逗号分隔"),
    ttl_seconds: int = Query(default=12, description="心跳超时时间（秒），默认12秒")
):
    """查询设备真实在线状态接口"""
    try:
        # 将逗号分隔的字符串转换为列表
        device_ip_list = [ip.strip() for ip in device_ips.split(",") if ip.strip()]
        
        if not device_ip_list:
            return error_response(message="设备IP列表为空")
        
        result = await device_service.get_device_status(device_ip_list, ttl_seconds)
        return success_response(data=result)
    except Exception as e:
        logger.error(f"查询设备状态失败: {e}")
        return error_response(message=f"查询设备状态失败: {str(e)}")


@close_dsp_router.get("/getChannelQrPic", description="获取通道二维码图片接口", summary="获取通道二维码图片接口")
async def get_channel_qr_pic(
    lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477")
):
    """获取通道二维码图片接口"""
    try:
        result = await base_service.get_channel_qr_pic(lot_id)
        return success_response(data=result)
    except Exception as e:
        logger.error(f"获取通道二维码图片失败: {e}")
        return error_response(message=f"获取通道二维码图片失败: {str(e)}")