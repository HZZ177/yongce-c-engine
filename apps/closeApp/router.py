import time
import asyncio
from datetime import datetime

from fastapi import APIRouter, Query, WebSocket

from core.logger import logger

from .schema import (
    DeviceOnOffRequest,
    CarInOutRequest
)
from .service import DeviceService, CarService, PaymentService, BaseService, LogMonitorService
from .device_manager import device_manager
from .config import Config
from core.util import success_response, error_response
from typing import List, Optional

def convert_pydantic_model(obj):
    """将pydantic模型转换为字典，如果不是pydantic模型则直接返回"""
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    return obj

close_dsp_router = APIRouter()

base_service = BaseService()
device_service = DeviceService()
car_service = CarService()
pay_service = PaymentService()
log_monitor_service = LogMonitorService()
config = Config()

@close_dsp_router.get("/deviceOn", description="设备上线接口", summary="设备上线接口")
async def device_on(
    device_list: str = Query(..., description="设备IP列表，多个IP用英文逗号分隔"),
    server_ip: str = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236")
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
        return error_response(message=f"设备上线失败: {e}")

@close_dsp_router.get("/deviceOff", description="设备下线接口", summary="设备下线接口")
async def device_off(
    device_list: str = Query(..., description="设备IP列表，多个IP用英文逗号分隔"),
    server_ip: str = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236")
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
    server_ip: str = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236"),
    lot_id: str = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
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

        # 如果是无牌车，跳过在场验证，直接返回结果
        if car_no == "":
            logger.info("无牌车，跳过在场车验证，直接返回结果")
            return success_response(data=f"无牌车压地感成功，凭据号：{i_serial}")

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
    server_ip: str = Query(..., description="服务器IP，测试环境192.168.0.183，灰度192.168.0.236"),
    lot_id: str = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
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

        # 如果是无牌车，跳过在场验证，直接返回结果
        if car_no == "":
            logger.info("无牌车，跳过在场车验证，直接返回结果")
            return success_response(data=f"无牌车压地感成功，凭据号：{i_serial}")

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
    lot_id: str = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
    car_no: str = Query(..., description="车牌号"),
    start_time: str = Query(default=None, description="开始时间，非必填，不填默认当天00:00:00"),
    end_time: str = Query(default=None, description="结束时间，非必填，不填默认当天23:59:59")
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
    lot_id: str = Query(..., description="车场ID，测试环境280025535，灰度280030477")
):
    """获取支付订单信息接口"""
    kt_token = await pay_service.get_unity_token(lot_id)
    res = await pay_service.get_park_pay_info(kt_token, lot_id, car_no)
    return success_response(data=res)

@close_dsp_router.get("/payOrder", description="模拟支付订单接口", summary="模拟支付订单接口")
async def pay_order(
    car_no: str = Query(..., description="车牌号"),
    lot_id: str = Query(..., description="车场ID，测试环境280025535，灰度280030477")
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


@close_dsp_router.post("/config/reload", description="重新加载配置文件", summary="重新加载配置文件")
async def reload_config():
    """重新加载配置文件接口

    当直接修改配置文件后，可以调用此接口重新加载配置到内存中
    """
    try:
        config.reload_config()
        logger.info("配置文件重新加载成功")
        return success_response(message="配置文件重新加载成功")
    except Exception as e:
        logger.error(f"重新加载配置文件失败: {e}")
        return error_response(message=f"重新加载配置文件失败: {str(e)}")


@close_dsp_router.post("/config/parking-lot", description="添加车场配置", summary="添加车场配置")
async def add_parking_lot(
    env: str = Query(..., description="环境名称 (test/prod)"),
    lot_config: dict = None
):
    """添加车场配置"""
    try:
        if not lot_config:
            return error_response(message="车场配置不能为空")

        success = config.add_parking_lot(env, lot_config)
        if success:
            device_manager.reconcile_devices()
            await device_manager.initialize_all_devices()
            return success_response(message="车场配置添加并重载设备成功")
        else:
            return error_response(message="车场配置添加失败")
    except Exception as e:
        logger.error(f"添加车场配置失败: {e}")
        return error_response(message="添加车场配置失败")


@close_dsp_router.put("/config/parking-lot/{lot_id}", description="更新车场配置", summary="更新车场配置")
async def update_parking_lot(
    lot_id: str,
    updates: dict
):
    """更新车场配置"""
    try:
        success = config.update_parking_lot(lot_id, updates)
        if success:
            device_manager.reconcile_devices()
            await device_manager.initialize_all_devices()
            return success_response(message="车场配置更新并重载设备成功")
        else:
            return error_response(message="车场配置更新失败，车场不存在")
    except Exception as e:
        logger.error(f"更新车场配置失败: {e}")
        return error_response(message="更新车场配置失败")


@close_dsp_router.delete("/config/parking-lot/{lot_id}", description="删除车场配置", summary="删除车场配置")
async def delete_parking_lot(lot_id: str):
    """删除车场配置"""
    try:
        success = config.remove_parking_lot(lot_id)
        if success:
            device_manager.reconcile_devices()
            await device_manager.initialize_all_devices()
            return success_response(message="车场配置删除并重载设备成功")
        else:
            return error_response(message="车场配置删除失败，车场不存在")
    except Exception as e:
        logger.error(f"删除车场配置失败: {e}")
        return error_response(message="删除车场配置失败")


@close_dsp_router.get("/config/parking-lot/{lot_id}", description="获取车场配置", summary="获取车场配置")
async def get_parking_lot(lot_id: str):
    """获取单个车场配置"""
    try:
        lot_config = config.get_parking_lot_by_id(lot_id)
        if lot_config:
            return success_response(data=lot_config)
        else:
            return error_response(message="车场不存在")
    except Exception as e:
        logger.error(f"获取车场配置失败: {e}")
        return error_response(message="获取车场配置失败")


@close_dsp_router.get("/config/channel-names/{lot_id}", description="获取车场通道名称配置", summary="获取车场通道名称配置")
async def get_channel_names(lot_id: str):
    """获取指定车场的通道名称配置"""
    try:
        channel_names = config.get_lot_channel_names(lot_id)
        return success_response(data=channel_names)
    except Exception as e:
        logger.error(f"获取通道名称配置失败: {e}")
        return error_response(message="获取通道名称配置失败")


@close_dsp_router.put("/config/channel-name", description="设置通道名称", summary="设置通道名称")
async def set_channel_name(
    lot_id: str,
    device_ip: str,
    channel_name: str
):
    """设置指定车场设备的通道名称"""
    try:
        success = config.set_channel_name(lot_id, device_ip, channel_name)
        if success:
            # set_channel_name方法已经包含了保存和重载逻辑，无需重复调用
            return success_response(message="通道名称设置成功")
        else:
            return error_response(message="设置失败，车场不存在")
    except Exception as e:
        logger.error(f"设置通道名称失败: {e}")
        return error_response(message="设置通道名称失败")


@close_dsp_router.get("/config/default-channel-name/{device_ip}", description="获取设备默认通道名称", summary="获取设备默认通道名称")
async def get_default_channel_name(device_ip: str):
    """获取设备IP对应的默认通道名称"""
    try:
        channel_name = config.get_default_channel_name(device_ip)
        if channel_name:
            return success_response(data={"device_ip": device_ip, "channel_name": channel_name})
        else:
            return error_response(message="未找到该设备的默认通道名称")
    except Exception as e:
        logger.error(f"获取默认通道名称失败: {e}")
        return error_response(message="获取默认通道名称失败")


@close_dsp_router.get("/nodeStatus", description="查询通道状态接口", summary="查询通道状态接口")
async def node_status(
    lot_id: str = Query(..., description="车场ID，测试环境280025535，灰度280030477")
):
    """查询通道状态接口"""
    try:
        all_status_list = await device_service.get_all_node_status(lot_id)
        return success_response(data=convert_pydantic_model(all_status_list))
    except Exception as e:
        logger.error(f"查询通道状态失败: {e}")
        return error_response(message=f"查询通道状态失败：{e}")


@close_dsp_router.get("/changeNodeStatus", description="通道长抬状态变更接口", summary="通道长抬状态变更接口")
async def change_node_status(
        lot_id: str = Query(..., description="车场ID，测试环境280025535，灰度280030477"),
        node_ids: str = Query(..., description="通道ID列表"),
        status: int = Query(..., description="通道状态 0:关闭长抬，1:打开长抬"),
):
    """通道长抬状态变更接口"""
    try:
        res = await device_service.change_node_status(lot_id, node_ids, status)
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
    lot_id: str = Query(..., description="车场ID，测试环境280025535，灰度280030477")
):
    """获取通道二维码图片接口"""
    try:
        result = await base_service.get_channel_qr_pic(lot_id)
        return success_response(data=result)
    except Exception as e:
        logger.error(f"获取通道二维码图片失败: {e}")
        return error_response(data=f"获取通道二维码图片失败: {e}")


@close_dsp_router.get("/getCloseParkCode", description="获取封闭车场-场内码", summary="获取封闭车场-场内码")
async def get_channel_qr_pic(
    lot_id: str = Query(..., description="车场ID，测试环境280025535，灰度280030477")
):
    """获取封闭车场的场内码"""
    try:
        result = await base_service.get_close_park_code(lot_id)
        return success_response(data=result)
    except Exception as e:
        logger.error(f"获取封闭场内码失败: {e}")
        return error_response(data=f"获取封闭场内码失败: {e}")


# ==================== 日志监控相关接口 ====================

@close_dsp_router.get("/log-files", description="获取日志文件列表", summary="获取日志文件列表")
async def list_log_files(
    lot_id: str = Query(..., description="车场ID")
):
    """获取指定服务器上的日志文件列表"""
    try:
        files = log_monitor_service.list_log_files(lot_id)
        return success_response(data=files)
    except Exception as e:
        logger.error(f"获取日志文件列表失败: {e}")
        return error_response(message=f"获取日志文件列表失败: {str(e)}")

@close_dsp_router.websocket("/ws/log-monitor")
async def websocket_log_monitor(
    websocket: WebSocket,
    lot_id: str = Query(..., description="车场ID"),
    filename: str = Query(..., description="要监控的日志文件名"),
    lines: int = Query(10, description="查看日志的尾部行数")
):
    """通过WebSocket实时监控日志文件"""
    await log_monitor_service.stream_log_file(lot_id, filename, websocket, lines)

