from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional

from apps.roadApp.custom_enum import RoadLotIdEnum


class RoadCarInOutRequest(BaseModel):
    """路侧车辆入场/出场请求"""
    lot_id: str = Field(..., description="车场ID，测试环境4799，灰度280030147")
    road_code: str = Field(..., description="路段编号")
    park_space_code: str = Field(..., description="车位编号")
    car_no: str = Field("", description="车牌号")
    car_type: int = Field(default=1, description="车辆类型 0小型车 1中型车 2大型车 3新能源车 4特殊车辆 5非机动车 6摩托车 7三轮车 8新能源货车")
    plate_color: str = Field(default="蓝", description="车牌颜色，中文")
    in_time: str = Field(default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description="入场时间，非必填，不填默认当前时间")
    source: int = Field(default=0, description="车辆来源，不填默认pos机 0:POS机 1:地磁 2:相机 3:web端 4:视频桩 5:移动端 6:巡逻车")


class RoadPresentCarInfoRequest(BaseModel):
    """路侧在场车辆查询请求"""
    car_no: str = Field("", description="车牌号")
    lot_id: RoadLotIdEnum = Field(..., description="车场ID，测试环境4799，灰度280030147")
    road_code: str = Field(default="", description="路段编号")
    parkspace_code: str = Field(default="", description="车位编号")
    plate_color: str = Field(default="", description="车辆颜色(1:白 2:黑 3:蓝 4:黄 5:绿)")
    car_type: str = Field(default="", description="车辆类型")
