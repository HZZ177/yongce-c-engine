import asyncio
import threading
from typing import Dict, Optional

from apps.closeApp.config import Config
from apps.closeApp.protocol import DeviceProtocol
from core.logger import logger


class EnvironmentDevice:
    """
    环境与设备配置映射
    - 负责读取现有的 config.yml 并根据车场ID和设备类型组装设备配置
    - 适配现有配置结构，无需修改 config.yml
    """

    def __init__(self):
        self.config = Config()

    def get_device_config(self, lot_id: str, device_type: str) -> Optional[Dict]:
        """
        根据车场ID和设备类型获取设备配置
        Args:
            lot_id: 车场ID
            device_type: 设备类型 ('in' or 'out')
        Returns:
            包含设备IP、服务器IP等信息的配置字典，如果找不到则返回None
        """
        if not self.config.is_supported_lot_id(lot_id):
            logger.warning(f"不支持的车场ID: {lot_id}")
            return None

        device_ip_key = f"{device_type}_device"
        server_ip = None
        device_ip = None

        if lot_id in self.config.get_test_support_lot_ids():
            env_config = self.config.get_parking_lot_by_id(lot_id)
            if env_config:
                server_ip = env_config.get('server_ip')
            device_ip = self.config.get_test_device_ip().get(device_ip_key)

        elif lot_id in self.config.get_prod_support_lot_ids():
            env_config = self.config.get_parking_lot_by_id(lot_id)
            if env_config:
                server_ip = env_config.get('server_ip')
            device_ip = self.config.get_prod_device_ip().get(device_ip_key)

        if not device_ip or not server_ip:
            logger.error(f"无法找到车场 {lot_id} 的设备或服务器IP配置")
            return None

        return {
            "lot_id": lot_id,
            "device_type": device_type,
            "client_ip": device_ip,
            "server_ip": server_ip,
            "server_port": 5001  # 默认端口
        }


class DeviceManager:
    """
    设备管理器 (单例)
    - 负责所有设备实例的创建、生命周期管理和复用
    - 内置设备健康监控和自动重连机制
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 防止重复初始化
        if not hasattr(self, 'initialized'):
            self.devices: Dict[str, DeviceProtocol] = {}
            self.environment_device = EnvironmentDevice()
            self.initialized = True
            logger.info("DeviceManager 初始化完成")

    def _get_device_key(self, lot_id: str, device_type: str) -> str:
        """生成设备唯一标识"""
        env = self.environment_device.config.get_parking_lot_env(lot_id)
        return f"{env}_{lot_id}_{device_type}"

    def _cleanup_device(self, device_key: str) -> None:
        """清理指定的设备连接"""
        if device_key in self.devices:
            protocol = self.devices[device_key]
            try:
                if protocol:
                    logger.info(f"正在清理不健康的设备连接: {device_key}")
                    protocol.device_off()
                del self.devices[device_key]
                logger.info(f"设备连接清理完成: {device_key}")
            except Exception as e:
                logger.error(f"清理设备连接时出错 {device_key}: {e}")
                # 即使清理失败，也要从字典中移除
                if device_key in self.devices:
                    del self.devices[device_key]

    def get_device(self, lot_id: str, device_type: str) -> Optional[DeviceProtocol]:
        """
        获取一个已连接的设备实例
        - 如果设备已存在且健康（连接正常且心跳活跃），则直接返回
        - 如果设备不存在或不健康，则清理旧连接并建立新连接
        """
        device_key = self._get_device_key(lot_id, device_type)

        # 检查设备是否存在且健康
        if device_key in self.devices:
            protocol = self.devices[device_key]
            if protocol and protocol.is_healthy():
                logger.debug(f"复用已存在的健康设备连接: {device_key}")
                return protocol
            else:
                # 设备存在但不健康，需要清理并重新建立连接
                if protocol:
                    if protocol.is_connected() and not protocol.is_heartbeat_active():
                        logger.warning(f"设备 {device_key} 连接存在但心跳已停止，清理并重新连接...")
                    elif not protocol.is_connected():
                        logger.warning(f"设备 {device_key} 连接已断开，清理并重新连接...")
                    else:
                        logger.warning(f"设备 {device_key} 状态异常，清理并重新连接...")
                else:
                    logger.warning(f"设备 {device_key} 协议对象为空，清理并重新连接...")

                # 清理不健康的设备连接
                self._cleanup_device(device_key)

        # 获取设备配置
        device_config = self.environment_device.get_device_config(lot_id, device_type)
        if not device_config:
            logger.error(f"无法获取设备配置: {lot_id} ({device_type})")
            return None

        # 创建并连接新设备
        protocol = DeviceProtocol(
            server_ip=device_config["server_ip"],
            server_port=device_config["server_port"],
            client_ip=device_config["client_ip"]
        )

        if protocol.device_on():
            self.devices[device_key] = protocol
            logger.info(f"设备 {device_key} 上线并连接成功")
            return protocol
        else:
            logger.error(f"设备 {device_key} 上线失败")
            return None

    async def initialize_all_devices(self):
        """在应用启动时初始化所有在配置中定义的设备"""
        logger.info("开始初始化所有已配置的设备...")
        all_lots = self.environment_device.config.get_parking_lots()
        for env, lots in all_lots.items():
            for lot in lots:
                lot_id = lot.get("id")
                if not lot_id:
                    continue
                # 初始化入场和出场设备
                for device_type in ["in", "out"]:
                    logger.debug(f"正在初始化设备: {env}_{lot_id}_{device_type}")
                    # 使用非阻塞方式获取设备，避免启动时卡死
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(None, self.get_device, lot_id, device_type)
        logger.info("所有已配置设备初始化完成")

    def shutdown_all_devices(self):
        """在应用关闭时优雅地关闭所有设备连接"""
        logger.info("开始关闭所有设备连接...")
        device_count = len(self.devices)
        success_count = 0

        for device_key, protocol in self.devices.items():
            try:
                if protocol:
                    if protocol.is_connected():
                        protocol.device_off()
                        logger.info(f"设备 {device_key} 已成功下线")
                        success_count += 1
                    else:
                        logger.debug(f"设备 {device_key} 已处于离线状态")
                        success_count += 1
                else:
                    logger.warning(f"设备 {device_key} 协议对象为空")
            except Exception as e:
                logger.error(f"关闭设备 {device_key} 时出错: {e}")

        self.devices.clear()
        logger.info(f"设备连接关闭完成: 成功 {success_count}/{device_count}")

    def reconcile_devices(self):
        """
        关闭所有当前活动的设备连接，以便在配置更改后重新初始化。
        """
        logger.info("配置已更改，正在协调设备连接...")
        self.shutdown_all_devices()  # 直接复用关闭逻辑
        logger.info("设备连接协调完成，可以重新初始化设备")


# 创建 DeviceManager 的单例实例
device_manager = DeviceManager()


