from fastapi import APIRouter, HTTPException
from .schema import (
    DeviceOnOffSchema,
    CarInOutSchema,
    DeviceOnOffRequest,
    DeviceOnOffResponse,
    CarInOutRequest,
    OnParkSchema,
    CarInOutResponse
)
from .service import DeviceService, CarService, PaymentService


close_dsp_router = APIRouter()

device_service = DeviceService()
car_server = CarService(device_service)


@close_dsp_router.post("/deviceOn", response_model=DeviceOnOffResponse)
async def device_on(request: DeviceOnOffRequest):
    """设备上线接口"""
    return await device_service.device_on(request)

@close_dsp_router.post("/deviceOff", response_model=DeviceOnOffResponse)
async def device_off(request: DeviceOnOffRequest):
    """设备下线接口"""
    return await device_service.device_off(request)

@close_dsp_router.post("/carIn", response_model=CarInOutResponse)
async def car_in(request: CarInOutRequest):
    """车辆入场接口"""
    car_service = CarService(device_service)
    return await car_service.car_in(request)

@close_dsp_router.post("/carOut", response_model=CarInOutResponse)
async def car_out(request: CarInOutRequest):
    """车辆出场接口"""
    car_service = CarService(device_service)
    return await car_service.car_out(request)

@close_dsp_router.post("/carOnPark")
async def get_on_park(request: OnParkSchema):
    """
    查询在场车辆
    :param request: 请求参数
    :return: 在场车辆信息
    """
    car_service = CarService(device_service)
    return await car_service.get_on_park(
        lot_id=request.lotId,
        car_no=request.carNo,
        kt_token=request.ktToken,
        start_time=request.StartTime,
        end_time=request.EndTime
    )