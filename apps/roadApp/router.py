import asyncio
from datetime import datetime

from fastapi import APIRouter, Query

from core.logger import logger
from .custom_enum import RoadLotIdEnum
from .schema import (
    RoadCarInOutRequest,
    RoadPresentCarInfoRequest
)
from .service import RoadService
from .config import RoadConfig
from core.util import success_response, error_response
from typing import Optional

def convert_pydantic_model(obj):
    """将pydantic模型转换为字典，如果不是pydantic模型则直接返回"""
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    return obj

road_dsp_router = APIRouter()

road_service = RoadService()
config = RoadConfig()



@road_dsp_router.get("/carIn", description="路侧车辆入场接口", summary="路侧车辆入场接口")
async def car_in(
    lot_id: RoadLotIdEnum = Query(..., description="车场ID，测试环境4799，灰度280030147"),
    road_code: str = Query("", description="路段id"),
    park_space_code: str = Query("", description="车位编号"),
    car_no: str = Query("", description="车牌号"),
    car_type: int = Query(default=0, description="车辆类型 0:小型车 1:中型车 2:大型车 3:新能源车 4:特殊车辆 5:非机动车 6:摩托车 7:三轮车 8:新能源货车"),
    plate_color: str = Query(default="蓝", description="车牌颜色，中文"),
    in_time: str = Query(default=None, description="入场时间，非必填，不填默认当前时间"),
    source: int = Query(default=0, description="车辆来源，不填默认pos机 0:POS机 1:地磁 2:相机 3:web端 4:视频桩 5:移动端 6:巡逻车"),
):
    """路侧车辆入场接口"""
    try:
        request = RoadCarInOutRequest(
            lot_id=lot_id,
            road_code=road_code,
            park_space_code=park_space_code,
            car_no=car_no,
            car_type=car_type,
            plate_color=plate_color,
            in_time=in_time,
            source=source
        )
        res = await road_service.car_in(request)
        return success_response(data=res)
    except Exception as e:
        logger.error(f"车辆【{car_no}】入场失败: {e}")
        return error_response(data=f"车辆入场失败，报错信息：{e}")


@road_dsp_router.get("/carOut", description="路侧车辆出场接口", summary="路侧车辆出场接口")
async def car_out(
    lot_id: RoadLotIdEnum = Query(..., description="车场ID，测试环境4799，灰度280030147"),
    road_code: str = Query("", description="路段id"),
    park_space_code: str = Query("", description="车位编号"),
    car_no: str = Query("", description="车牌号"),
    car_type: int = Query(default=0, description="车辆类型 0:小型车 1:中型车 2:大型车 3:新能源车 4:特殊车辆 5:非机动车 6:摩托车 7:三轮车 8:新能源货车"),
    plate_color: str = Query(default="蓝", description="车牌颜色，中文"),
    in_time: str = Query(default=None, description="入场时间，非必填，不填默认当前时间"),
    source: int = Query(default=0, description="车辆来源，不填默认pos机 0:POS机 1:地磁 2:相机 3:web端 4:视频桩 5:移动端 6:巡逻车"),
):
    """路侧车辆出场接口"""
    try:
        request = RoadCarInOutRequest(
            lot_id=lot_id,
            road_code=road_code,
            park_space_code=park_space_code,
            car_no=car_no,
            car_type=car_type,
            plate_color=plate_color,
            in_time=in_time,
            source=source
        )
        res = await road_service.car_out(request)
        return success_response(data=res)
    except Exception as e:
        logger.error(f"车辆【{car_no}】出场失败: {e}")
        return error_response(data=f"车辆出场失败，报错信息：{e}")


@road_dsp_router.get("/carOutSettle", description="路侧车辆POS机离场接口(触发无感)", summary="路侧车辆POS机离场接口(触发无感)")
async def car_out_settle(
        lot_id: RoadLotIdEnum = Query(..., description="车场ID，测试环境4799，灰度280030147"),
        road_code: str = Query("", description="路段id"),
        park_space_code: str = Query("", description="车位编号"),
        car_no: str = Query("", description="车牌号"),
        plate_color: str = Query(default="蓝", description="车牌颜色，中文")
):
    try:
        request = RoadCarInOutRequest(
            lot_id=lot_id,
            road_code=road_code,
            park_space_code=park_space_code,
            car_no=car_no,
            plate_color=plate_color
        )
        res = await road_service.car_outsettle(request)
        return success_response(data=res)
    except Exception as e:
        logger.error(f"车辆【{car_no}】POS机离场失败: {e}")
        return error_response(data=f"车POS机离场失败，报错信息：{e}")


@road_dsp_router.get("/presentCarInfo", description="路侧在场车辆查询接口", summary="路侧在场车辆查询接口")
async def get_present_car_info(
    car_no: str = Query("", description="车牌号"),
    lot_id: RoadLotIdEnum = Query(..., description="车场ID，测试环境4799，灰度280030147"),
    car_type: str = Query("", description="车辆类型"),
    parkspace_code: str = Query("", description="车位编号"),
    plate_color: str = Query(default="", description="车辆颜色(1:白 2:黑 3:蓝 4:黄 5:绿)"),
    road_code: str = Query("", description="路段编号"),
):
    """路侧在场车辆查询接口"""
    try:
        data = RoadPresentCarInfoRequest(
            car_no=car_no,
            lot_id=lot_id,
            road_code=road_code,
            parkspace_code=parkspace_code,
            plate_color=plate_color,
            car_type=car_type
        )
        response = await road_service.road_present_car_info(data)
        return success_response(data=response)
    except Exception as e:
        return error_response(data=f"查询路侧在场车失败，报错信息：{e}")

@road_dsp_router.get("/config", description="获取路侧配置信息接口", summary="获取路侧配置信息接口")
async def get_config():
    """获取路侧配置信息接口"""
    try:
        # 获取配置信息
        parking_lots = config.get_parking_lots()
        road_api_endpoints = config.config.get("road_api_endpoints", {})

        config_data = {
            "parking_lots": parking_lots,
            "api_endpoints": road_api_endpoints
        }
        return success_response(data=config_data)
    except Exception as e:
        logger.error(f"获取路侧配置信息失败: {e}")
        return error_response(message="获取路侧配置信息失败")

@road_dsp_router.post("/config/parking-lot", description="添加路侧车场配置", summary="添加路侧车场配置")
async def add_parking_lot(
    env: str = Query(..., description="环境名称 (test/prod)"),
    lot_config: dict = None
):
    """添加路侧车场配置"""
    try:
        if not lot_config:
            return error_response(message="路侧车场配置不能为空")

        success = config.add_parking_lot(env, lot_config)
        if success:
            return success_response(message="路侧车场配置添加成功")
        else:
            return error_response(message="路侧车场配置添加失败")
    except Exception as e:
        logger.error(f"添加路侧车场配置失败: {e}")
        return error_response(message="添加路侧车场配置失败")

@road_dsp_router.put("/config/parking-lot/{lot_id}", description="更新路侧车场配置", summary="更新路侧车场配置")
async def update_parking_lot(
    lot_id: str,
    updates: dict
):
    """更新路侧车场配置"""
    try:
        success = config.update_parking_lot(lot_id, updates)
        if success:
            return success_response(message="路侧车场配置更新成功")
        else:
            return error_response(message="路侧车场配置更新失败，车场不存在")
    except Exception as e:
        logger.error(f"更新路侧车场配置失败: {e}")
        return error_response(message="更新路侧车场配置失败")

@road_dsp_router.delete("/config/parking-lot/{lot_id}", description="删除路侧车场配置", summary="删除路侧车场配置")
async def delete_parking_lot(lot_id: str):
    """删除路侧车场配置"""
    try:
        success = config.remove_parking_lot(lot_id)
        if success:
            return success_response(message="路侧车场配置删除成功")
        else:
            return error_response(message="路侧车场配置删除失败，车场不存在")
    except Exception as e:
        logger.error(f"删除路侧车场配置失败: {e}")
        return error_response(message="删除路侧车场配置失败")

@road_dsp_router.get("/config/parking-lot/{lot_id}", description="获取路侧车场配置", summary="获取路侧车场配置")
async def get_parking_lot(lot_id: str):
    """获取单个路侧车场配置"""
    try:
        lot_config = config.get_parking_lot_by_id(lot_id)
        if lot_config:
            return success_response(data=lot_config)
        else:
            return error_response(message="路侧车场不存在")
    except Exception as e:
        logger.error(f"获取路侧车场配置失败: {e}")
        return error_response(message="获取路侧车场配置失败")

@road_dsp_router.get("/roadPage", description="获取路侧车场路段列表", summary="获取路侧车场路段列表")
async def get_road_page(
    lot_id: RoadLotIdEnum = Query(..., description="车场ID，测试环境4799，灰度280030147")
):
    """获取路侧车场路段列表"""
    try:
        res = await road_service.get_road_page(lot_id)
        data = res.get("data")
        return success_response(data=data)
    except Exception as e:
        logger.error(f"获取路侧车场路段列表失败: {e}")
        return error_response(data=f"获取路侧车场路段列表失败，报错{e}")

@road_dsp_router.get("/parkspacePage", description="分页查询路侧车位", summary="分页查询路侧车位")
async def query_park_space_page(
    lot_id: RoadLotIdEnum = Query(..., description="车场ID，测试环境4799，灰度280030147"),
    road_code: str = Query(..., description="车位ID"),
    page_num: int = Query(1, description="页码，默认第一页"),
    page_size: int = Query(20, description="每页数量，默认20")
):
    """获取路侧车场路段列表"""
    try:
        res = await road_service.query_park_space_page(lot_id, road_code, page_num, page_size)
        data = res.get("data").get("records")
        return success_response(data=data)
    except Exception as e:
        logger.error(f"获取路侧车场路段列表失败: {e}")
        return error_response(data=f"获取路侧车场路段列表失败，报错{e}")
