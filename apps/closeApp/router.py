from fastapi import APIRouter, HTTPException, Query
from .schema import (
    DeviceOnOffRequest,
    DeviceOnOffResponse,
    CarInOutRequest,
    CarInOutResponse
)
from .service import DeviceService, CarService, PaymentService
from typing import List, Optional


close_dsp_router = APIRouter()

device_service = DeviceService()
car_server = CarService(device_service)


@close_dsp_router.get("/deviceOn", description="设备上线接口", summary="设备上线接口", response_model=DeviceOnOffResponse)
async def device_on(
    device_list: str = Query(..., description="设备IP列表，多个IP用逗号分隔"),
    server_ip: str = Query(default="192.168.0.202", description="服务器IP"),
    device_type: str = Query(default="1", description="设备类型")
):
    """设备上线接口"""
    # 将逗号分隔的字符串转换为列表
    device_ip_list = [ip.strip() for ip in device_list.split(",") if ip.strip()]
    
    # 构造请求对象
    request = DeviceOnOffRequest(
        server_ip=server_ip,
        device_list=device_ip_list,
        device_type=device_type
    )
    return await device_service.device_on(request)

@close_dsp_router.get("/deviceOff", description="设备下线接口", summary="设备下线接口", response_model=DeviceOnOffResponse)
async def device_off(
    device_list: str = Query(..., description="设备IP列表，多个IP用逗号分隔"),
    server_ip: str = Query(default="192.168.0.202", description="服务器IP"),
    device_type: str = Query(default="1", description="设备类型")
):
    """设备下线接口"""
    # 将逗号分隔的字符串转换为列表
    device_ip_list = [ip.strip() for ip in device_list.split(",") if ip.strip()]
    
    # 构造请求对象
    request = DeviceOnOffRequest(
        server_ip=server_ip,
        device_list=device_ip_list,
        device_type=device_type
    )
    return await device_service.device_off(request)

@close_dsp_router.get("/carIn", description="车辆入场接口", summary="车辆入场接口", response_model=CarInOutResponse)
async def car_in(
    car_no: str = Query(..., description="车牌号"),
    server_ip: str = Query(default="192.168.0.202", description="服务器IP"),
    lot_id: str = Query(default="996000386", description="车场ID"),
    car_color: int = Query(default=3, description="车辆颜色"),
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
    car_service = CarService(device_service)
    return await car_service.car_in(request)

@close_dsp_router.get("/carOut", description="车辆出场接口", summary="车辆出场接口", response_model=CarInOutResponse)
async def car_out(
    car_no: str = Query(..., description="车牌号"),
    server_ip: str = Query(default="192.168.0.202", description="服务器IP"),
    lot_id: str = Query(default="996000386", description="车场ID"),
    car_color: int = Query(default=3, description="车辆颜色"),
    recognition: int = Query(default=1000, description="识别度"),
    i_serial: Optional[int] = Query(default=None, description="序列号")
):
    """车辆出场接口"""
    # 构造请求对象
    request = CarInOutRequest(
        server_ip=server_ip,
        car_no=car_no,
        lot_id=lot_id,
        car_color=car_color,
        recognition=recognition,
        i_serial=i_serial
    )
    return await car_server.car_out(request)

@close_dsp_router.get("/carOnPark", description="查询在场车辆接口", summary="查询在场车辆接口")
async def get_on_park(
    lotId: str = Query(..., description="车场ID"),
    carNo: str = Query(..., description="车牌号"),
    ktToken: str = Query(..., description="统一平台token"),
    StartTime: str = Query(default="", description="开始时间"),
    EndTime: str = Query(default="", description="结束时间")
):
    """
    查询在场车辆
    :param lotId: 车场ID
    :param carNo: 车牌号
    :param ktToken: 统一平台token
    :param StartTime: 开始时间
    :param EndTime: 结束时间
    :return: 在场车辆信息
    """
    car_service = CarService(device_service)
    return await car_service.get_on_park(
        lot_id=lotId,
        car_no=carNo,
        kt_token=ktToken,
        start_time=StartTime,
        end_time=EndTime
    )