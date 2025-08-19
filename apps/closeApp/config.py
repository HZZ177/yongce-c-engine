import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from core.logger import logger


class Config:
    def __init__(self):
        self.config_path = Path(__file__).parent / "config.yml"
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def get_server_config(self) -> Dict[str, Any]:
        """获取设备相关配置"""
        return self.config.get("device", {})

    def get_parking_config(self) -> Dict[str, Any]:
        """获取车场相关配置"""
        return self.config.get("parking", {})

    def get_server_ip(self) -> str:
        """获取服务器IP"""
        return self.get_server_config().get("server_ip", "192.168.0.183")

    def get_server_port(self) -> int:
        """获取服务器端口"""
        return self.get_server_config().get("server_port", 5001)

    def get_test_device_ip(self) -> dict:
        """获取测试环境设备IPw，包含进出口设备"""
        return self.config.get("device", {}).get("test", {})

    def get_prod_device_ip(self) -> dict:
        """获取生产环境设备IP，包含进出口设备"""
        return self.config.get("device", {}).get("prod", {})

    def get_test_support_lot_ids(self) -> List[str]:
        """获取测试环境支持的车场ID列表"""
        return self.config.get("support_parking_ips", {}).get("test", [])

    def get_prod_support_lot_ids(self) -> List[str]:
        """获取生产环境支持的车场ID列表"""
        return self.config.get("support_parking_ips", {}).get("prod", [])

    def get_default_lot_id(self) -> str:
        """获取默认车场ID"""
        return self.get_parking_config().get("default_lot_id", "280025535")

    def get_car_come_domain(self) -> dict:
        """获取车辆入场接口域名"""
        return self.config.get("car_come_domain", {})

    def is_supported_lot_id(self, lot_id: str) -> bool:
        """检查车场ID是否支持"""
        allowed_lot_ids = self.get_test_support_lot_ids() + self.get_prod_support_lot_ids()
        return lot_id in allowed_lot_ids

    def get_kt_unity_login_domain(self) -> dict:
        """获取统一平台登录域名"""
        return self.config.get("unity_login_domain", {})

    def get_yongce_pro_domain(self) -> dict:
        """获取永策平台域名"""
        return self.config.get("yongce_pro_domain", {})

    def get_test_cloud_channel_query_url(self) -> str:
        """获取测试环境云助手通道查询接口"""
        return self.config.get("cloud_channel_query_url", {}).get("test", "")

    def get_prod_cloud_channel_query_url(self) -> str:
        """获取正式环境云助手通道查询接口"""
        return self.config.get("cloud_channel_query_url", {}).get("prod", "")

    def get_test_cloud_channel_change_url(self) -> str:
        """获取测试环境云助手通道变更接口"""
        return self.config.get("cloud_channel_change_url", {}).get("test", "")

    def get_prod_cloud_channel_change_url(self) -> str:
        """获取正式环境云助手通道变更接口"""
        return self.config.get("cloud_channel_change_url", {}).get("prod", "")

    def get_yongce_pro_config(self) -> dict:
        """获取永策后台测试环境相关配置"""
        return self.config.get("yongce_pro", {})

    # ==================== 新增：车场配置管理方法 ====================

    def get_parking_lots(self, env: str = None) -> Union[Dict[str, List[Dict]], List[Dict]]:
        """获取车场配置列表

        Args:
            env: 环境名称，如果为None则返回所有环境的配置

        Returns:
            如果指定env，返回该环境的车场列表；否则返回所有环境的配置字典
        """
        parking_lots = self.config.get("parking_lots", {})
        if env:
            return parking_lots.get(env, [])
        return parking_lots

    def get_parking_lot_by_id(self, lot_id: str) -> Optional[Dict]:
        """根据车场ID获取车场配置"""
        for env_lots in self.config.get("parking_lots", {}).values():
            for lot in env_lots:
                if lot.get("id") == lot_id:
                    return lot
        return None

    def get_parking_lot_name(self, lot_id: str) -> str:
        """获取车场名称"""
        lot = self.get_parking_lot_by_id(lot_id)
        return lot.get("name", f"车场{lot_id}") if lot else f"车场{lot_id}"

    def get_parking_lot_env(self, lot_id: str) -> Optional[str]:
        """获取车场所属环境"""
        for env, env_lots in self.config.get("parking_lots", {}).items():
            for lot in env_lots:
                if lot.get("id") == lot_id:
                    return env
        return None

    def get_default_channel_name(self, device_ip: str) -> Optional[str]:
        """获取设备IP对应的默认通道名称"""
        for env_lots in self.config.get("parking_lots", {}).values():
            for lot in env_lots:
                channel_names = lot.get("channel_names", {})
                if device_ip in channel_names:
                    return channel_names[device_ip]
        return None

    def get_lot_channel_names(self, lot_id: str) -> Dict[str, str]:
        """获取指定车场的所有通道名称配置"""
        lot = self.get_parking_lot_by_id(lot_id)
        if lot:
            return lot.get("channel_names", {})
        return {}

    def set_channel_name(self, lot_id: str, device_ip: str, channel_name: str) -> bool:
        """设置指定车场设备的通道名称

        采用文件优先的方式：先重新加载配置文件，修改后保存，再重载到内存
        这样确保与直接修改配置文件的方式保持一致
        """
        try:
            # 1. 重新加载最新的配置文件，确保获取最新数据
            self._load_config()

            # 2. 在配置数据中查找并修改通道名称
            config_modified = False
            for env_lots in self.config.get("parking_lots", {}).values():
                for lot in env_lots:
                    if lot.get("id") == lot_id:
                        if "channel_names" not in lot:
                            lot["channel_names"] = {}
                        lot["channel_names"][device_ip] = channel_name
                        config_modified = True
                        break
                if config_modified:
                    break

            if not config_modified:
                logger.error(f"未找到车场ID: {lot_id}")
                return False

            # 3. 保存修改后的配置到文件
            if not self.save_config():
                logger.error("保存配置文件失败")
                return False

            # 4. 重新加载配置到内存，确保内存与文件一致
            self.reload_config()
            logger.info(f"通道名称设置成功: 车场{lot_id}, 设备{device_ip} -> {channel_name}")
            return True

        except Exception as e:
            logger.error(f"设置通道名称时发生错误: {e}")
            # 发生错误时重新加载配置，确保内存状态正确
            try:
                self.reload_config()
            except Exception as reload_error:
                logger.error(f"重载配置失败: {reload_error}")
            return False

    def add_parking_lot(self, env: str, lot_config: Dict[str, Any]) -> bool:
        """添加车场配置

        采用文件优先的方式：先重新加载配置文件，修改后保存，再重载到内存

        Args:
            env: 环境名称 (test/prod)
            lot_config: 车场配置字典，必须包含id字段

        Returns:
            是否添加成功
        """
        try:
            if not lot_config.get("id"):
                logger.error("车场配置必须包含id字段")
                return False

            # 1. 重新加载最新的配置文件，确保获取最新数据
            self._load_config()

            # 2. 检查是否已存在
            if self.get_parking_lot_by_id(lot_config["id"]):
                logger.error(f"车场ID {lot_config['id']} 已存在")
                return False

            # 3. 确保parking_lots结构存在
            if "parking_lots" not in self.config:
                self.config["parking_lots"] = {}
            if env not in self.config["parking_lots"]:
                self.config["parking_lots"][env] = []

            # 4. 添加车场配置
            self.config["parking_lots"][env].append(lot_config)

            # 5. 更新向后兼容的配置
            self._update_legacy_config()

            # 6. 保存修改后的配置到文件
            if not self.save_config():
                logger.error("保存配置文件失败")
                return False

            # 7. 重新加载配置到内存，确保内存与文件一致
            self.reload_config()
            logger.info(f"车场配置添加成功: {lot_config.get('name', lot_config['id'])}")
            return True

        except Exception as e:
            logger.error(f"添加车场配置时发生错误: {e}")
            # 发生错误时重新加载配置，确保内存状态正确
            try:
                self.reload_config()
            except Exception as reload_error:
                logger.error(f"重载配置失败: {reload_error}")
            return False

    def update_parking_lot(self, lot_id: str, updates: Dict[str, Any]) -> bool:
        """更新车场配置

        采用文件优先的方式：先重新加载配置文件，修改后保存，再重载到内存

        Args:
            lot_id: 车场ID
            updates: 要更新的字段字典

        Returns:
            是否更新成功
        """
        try:
            # 1. 重新加载最新的配置文件，确保获取最新数据
            self._load_config()

            # 2. 在配置数据中查找并更新车场配置
            config_modified = False
            for env_lots in self.config.get("parking_lots", {}).values():
                for lot in env_lots:
                    if lot.get("id") == lot_id:
                        lot.update(updates)
                        config_modified = True
                        break
                if config_modified:
                    break

            if not config_modified:
                logger.error(f"未找到车场ID: {lot_id}")
                return False

            # 3. 更新向后兼容的配置
            self._update_legacy_config()

            # 4. 保存修改后的配置到文件
            if not self.save_config():
                logger.error("保存配置文件失败")
                return False

            # 5. 重新加载配置到内存，确保内存与文件一致
            self.reload_config()
            logger.info(f"车场配置更新成功: {lot_id}")
            return True

        except Exception as e:
            logger.error(f"更新车场配置时发生错误: {e}")
            # 发生错误时重新加载配置，确保内存状态正确
            try:
                self.reload_config()
            except Exception as reload_error:
                logger.error(f"重载配置失败: {reload_error}")
            return False

    def remove_parking_lot(self, lot_id: str) -> bool:
        """删除车场配置

        采用文件优先的方式：先重新加载配置文件，修改后保存，再重载到内存

        Args:
            lot_id: 车场ID

        Returns:
            是否删除成功
        """
        try:
            # 1. 重新加载最新的配置文件，确保获取最新数据
            self._load_config()

            # 2. 在配置数据中查找并删除车场配置
            config_modified = False
            for env_name, env_lots in self.config.get("parking_lots", {}).items():
                for i, lot in enumerate(env_lots):
                    if lot.get("id") == lot_id:
                        env_lots.pop(i)
                        config_modified = True
                        break
                if config_modified:
                    break

            if not config_modified:
                logger.error(f"未找到车场ID: {lot_id}")
                return False

            # 3. 更新向后兼容的配置
            self._update_legacy_config()

            # 4. 保存修改后的配置到文件
            if not self.save_config():
                logger.error("保存配置文件失败")
                return False

            # 5. 重新加载配置到内存，确保内存与文件一致
            self.reload_config()
            logger.info(f"车场配置删除成功: {lot_id}")
            return True

        except Exception as e:
            logger.error(f"删除车场配置时发生错误: {e}")
            # 发生错误时重新加载配置，确保内存状态正确
            try:
                self.reload_config()
            except Exception as reload_error:
                logger.error(f"重载配置失败: {reload_error}")
            return False

    def _update_legacy_config(self):
        """更新向后兼容的配置结构"""
        parking_lots = self.config.get("parking_lots", {})

        # 更新support_parking_ips
        support_parking_ips = {}
        support_server_ips = {}
        device_config = {}

        for env, lots in parking_lots.items():
            support_parking_ips[env] = [lot["id"] for lot in lots]
            support_server_ips[env] = [lot.get("server_ip", "") for lot in lots]

            # 设备配置使用第一个车场的设备信息
            if lots and lots[0].get("devices"):
                device_config[env] = lots[0]["devices"]

        self.config["support_parking_ips"] = support_parking_ips
        self.config["support_server_ips"] = support_server_ips
        if device_config:
            self.config["device"] = device_config

    def save_config(self) -> bool:
        """保存配置到文件

        Returns:
            是否保存成功
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
            logger.info("配置文件保存成功")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False

    def reload_config(self):
        """重新加载配置文件"""
        self._load_config()


if __name__ == "__main__":
    config = Config()
    print(config.is_supported_lot_id("280030477"))