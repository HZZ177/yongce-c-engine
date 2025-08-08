import time
import asyncio

from fastapi import APIRouter, HTTPException, Query

from core.logger import logger
from .enum import LotIdEnum, ServerIpEnum
from .schema import (
    DeviceOnOffRequest,
    DeviceOnOffResponse,
    CarInOutRequest,
    CarInOutResponse, PaymentResponse
)
from .service import DeviceService, CarService, PaymentService
from typing import List, Optional


close_dsp_router = APIRouter()

device_service = DeviceService()
car_service = CarService(device_service)
pay_service = PaymentService()

@close_dsp_router.get("/deviceOn", description="设备上线接口", summary="设备上线接口", response_model=DeviceOnOffResponse)
async def device_on(
    device_list: str = Query(..., description="设备IP列表，多个IP用英文逗号分隔"),
    server_ip: ServerIpEnum = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236")
):
    """设备上线接口"""
    # 将逗号分隔的字符串转换为列表
    device_ip_list = [ip.strip() for ip in device_list.split(",") if ip.strip()]

    # 构造请求对象
    request = DeviceOnOffRequest(
        server_ip=server_ip,
        device_list=device_ip_list,
        device_type="1"
    )
    return await device_service.device_on(request)

@close_dsp_router.get("/deviceOff", description="设备下线接口", summary="设备下线接口", response_model=DeviceOnOffResponse)
async def device_off(
    device_list: str = Query(..., description="设备IP列表，多个IP用英文逗号分隔"),
    server_ip: ServerIpEnum = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236")
):
    """设备下线接口"""
    # 将逗号分隔的字符串转换为列表
    device_ip_list = [ip.strip() for ip in device_list.split(",") if ip.strip()]
    
    # 构造请求对象
    request = DeviceOnOffRequest(
        server_ip=server_ip,
        device_list=device_ip_list,
        device_type="1"
    )
    return await device_service.device_off(request)

@close_dsp_router.get("/carIn", description="车辆入场接口", summary="车辆入场接口", response_model=CarInOutResponse)
async def car_in(
    car_no: str = Query(..., description="车牌号"),
    server_ip: ServerIpEnum = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236"),
    lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
    car_color: int = Query(default=3, description="车辆颜色(1:白 2:黑 3:蓝 4:黄 5:绿)"),
    recognition: int = Query(default=1000, description="识别度"),
    i_serial: Optional[int] = Query(default=None, description="序列号")
):
    """车辆入场接口"""
    # 构造请求对象
    request = CarInOutRequest(
        server_ip=server_ip,
        car_no=car_no,
        lot_id=lot_id,
        car_color=car_color,
        recognition=recognition,
        i_serial=i_serial
    )
    # 入车
    res = await car_service.car_in(request)

    # 查询在场车验证，重试三次防止有入车延时
    retry = 3

    for attempt in range(retry):
        car_on_park = await car_service.get_on_park(lot_id=lot_id, car_no=car_no)
        if car_on_park["data"]["vos"]:  # 直接判断列表是否为空
            return res
        
        if attempt < retry - 1:  # 最后一次不需要等待
            await asyncio.sleep(0.5)

    logger.error(f"车辆入场失败！重试{retry}次后，车辆仍未入场")
    raise HTTPException(status_code=500, detail=f"车辆入场失败！重试{retry}次后，车辆仍未入场")


@close_dsp_router.get("/carOut", description="车辆出场接口", summary="车辆出场接口", response_model=CarInOutResponse)
async def car_out(
    car_no: str = Query(..., description="车牌号"),
    server_ip: ServerIpEnum = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236"),
    lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
    car_color: int = Query(default=3, description="车辆颜色(1:白 2:黑 3:蓝 4:黄 5:绿)"),
    recognition: int = Query(default=1000, description="识别度"),
    i_serial: Optional[int] = Query(default=None, description="序列号"),
    i_open_type: int = Query(default=0, description="出场方式，不填默认压地感(0:压地感 1:相机直接开闸放行)")
):
    """车辆出场接口"""
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
            return res

        if attempt < retry - 1:  # 最后一次不需要等待
            await asyncio.sleep(0.5)

    logger.error(f"车辆出场失败！重试{retry}次后，车辆仍然在场")
    raise HTTPException(status_code=500, detail=f"车辆出场失败！重试{retry}次后，车辆仍然在场")

@close_dsp_router.get("/carOnPark", description="查询在场车辆接口", summary="查询在场车辆接口")
async def get_on_park(
    lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
    car_no: str = Query(..., description="车牌号"),
    start_time: str = Query(default="", description="开始时间，非必填，不填默认当天00:00:00"),
    end_time: str = Query(default="", description="结束时间，非必填，不填默认当天23:59:59")
):
    """
    查询在场车辆
    :param lot_id: 车场ID
    :param car_no: 车牌号
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return: 在场车辆信息
    """
    return await car_service.get_on_park(
        lot_id=lot_id,
        car_no=car_no,
        start_time=start_time,
        end_time=end_time
    )

@close_dsp_router.get("/payOrder", description="模拟支付订单接口", summary="模拟支付订单接口")
async def pay_order(
    car_no: str = Query(..., description="车牌号"),
    lot_id: LotIdEnum = Query(..., description="车场ID，测试环境280025535，灰度280030477")
):
    """模拟支付订单接口"""
    return await pay_service.pay_order(lot_id, car_no)


# @close_dsp_router.get("/refundOrder", description="模拟退款订单接口", summary="模拟退款订单接口")
# async def refund_order(
#     car_no: str = Query(..., description="车牌号"),
#     lot_id: str = Query(default="280025535", description="车场ID，测试环境280025535，灰度280030477")
# ):
#     """模拟退款订单接口"""
#     return await pay_service.refund_order(car_no,lot_id)
