from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DeviceOnOffSchema(BaseModel):
    server_ip: str = Field(default="192.168.0.202", description="服务器IP")
    device_list: List[str] = Field(..., description="设备IP列表")

class CarInOutSchema(BaseModel):
    server_ip: str = Field(default="192.168.0.202", description="服务器IP")
    car_no: str = Field(default="", description="车牌号")
    lot_id: str = Field(default="996000386", description="车场ID")
    car_color: int = Field(default=3, description="车辆颜色")
    recognition: int = Field(default=1000, description="识别度")
    i_serial: Optional[int] = Field(default=None, description="序列号")

class OnParkSchema(BaseModel):
    lotId: str = Field(..., description="车场ID")
    carNo: str = Field(..., description="车牌号")
    ktToken: str = Field(..., description="统一平台token")
    StartTime: str = Field(default="", description="开始时间")
    EndTime: str = Field(default="", description="结束时间")

class CarInOutResponse(BaseModel):
    data: str = Field(..., description="响应数据")
    resultCode: int = Field(..., description="响应码")

class BaseResponse(BaseModel):
    data: str = Field(..., description="响应数据")
    resultCode: int = Field(..., description="响应码")

class DeviceOnOffRequest(BaseModel):
    server_ip: str = Field(default="192.168.0.202", description="服务器IP")
    device_list: List[str] = Field(..., description="设备IP列表")
    device_type: str = Field(default="1", description="设备类型")

class DeviceOnOffResponse(BaseResponse):
    pass

class PaymentRequest(BaseModel):
    server_ip: str = Field(default="192.168.0.202", description="服务器IP")
    car_no: str = Field(..., description="车牌号")
    lot_id: str = Field(default="996000386", description="车场ID")
    order_no: Optional[str] = Field(default=None, description="订单号")
    pay_money: Optional[int] = Field(default=None, description="支付金额")

class RefundRequest(BaseModel):
    server_ip: str = Field(default="192.168.0.202", description="服务器IP")
    car_no: str = Field(..., description="车牌号")
    lot_id: str = Field(default="996000386", description="车场ID")
    order_no: str = Field(..., description="订单号")
    refund_money: int = Field(..., description="退款金额")

class PaymentResponse(BaseResponse):
    pass

class RefundResponse(BaseResponse):
    pass

class CarInOutRequest(BaseModel):
    server_ip: str = Field(default="192.168.0.202", description="服务器IP")
    car_no: str = Field(..., description="车牌号")
    lot_id: str = Field(default="996000386", description="车场ID")
    car_color: int = Field(default=3, description="车辆颜色")
    recognition: int = Field(default=1000, description="识别度")
    i_serial: Optional[int] = Field(default=None, description="序列号")
