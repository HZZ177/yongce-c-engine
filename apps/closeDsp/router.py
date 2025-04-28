from fastapi import APIRouter, Query, Body, HTTPException
import datetime
import json
import requests
from urllib.parse import urljoin
from common import filepath
from core.logger import logger
from common.dspClient import DspClient
from common.my_nacos import MyNaCosClient
from common.util import get_host_ip
from common.cp_console import query_order, get_cookie_test, refund
from testCases.Api import check_tables_new
from testCases.Api.stc_api import get_user_token
from testCases.Public import car, park, public
from testCases.Public.public import login
import random
from .schema import DeviceOnOffSchema, CarInOutSchema, DeviceOnOffRequest, DeviceOnOffResponse, CarInOutRequest, OnParkSchema
from .service import CloseDspService, DeviceService
from .protocol import DeviceOnOffResponse, CarInOutResponse
from .service import CarService
from .service import PaymentService

close_dsp_router = APIRouter()
service = CloseDspService()
device_service = DeviceService()

@close_dsp_router.post("/deviceOn", response_model=DeviceOnOffResponse)
async def device_on(params: DeviceOnOffSchema):
    """
    设备上线api
    """
    try:
        return await service.device_on(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@close_dsp_router.post("/deviceOff", response_model=DeviceOnOffResponse)
async def device_off(params: DeviceOnOffSchema):
    """
    设备下线api
    """
    try:
        return await service.device_off(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@close_dsp_router.get("/carIn", response_model=CarInOutResponse)
async def car_in(params: CarInOutSchema):
    """
    入车api
    """
    try:
        return await service.car_in(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@close_dsp_router.get("/carOut", response_model=CarInOutResponse)
async def car_out(params: CarInOutSchema):
    """
    出车api
    """
    try:
        return await service.car_out(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@close_dsp_router.post("/device/on", response_model=DeviceOnOffResponse)
async def device_on_new(request: DeviceOnOffRequest):
    """设备上线接口"""
    return await device_service.device_on(request)

@close_dsp_router.post("/device/off", response_model=DeviceOnOffResponse)
async def device_off_new(request: DeviceOnOffRequest):
    """设备下线接口"""
    return await device_service.device_off(request)

@close_dsp_router.get("/car/in", response_model=CarInOutResponse)
async def car_in(request: CarInOutRequest):
    """车辆入场接口"""
    car_service = CarService(device_service)
    return await car_service.car_in(request)

@close_dsp_router.get("/car/out", response_model=CarInOutResponse)
async def car_out(request: CarInOutRequest):
    """车辆出场接口"""
    car_service = CarService(device_service)
    return await car_service.car_out(request)

@close_dsp_router.post("/car/onPark")
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