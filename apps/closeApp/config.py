import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import logger


class Config:
    def __init__(self):
        config_path = Path(__file__).parent / "config.yml"
        with open(config_path, "r", encoding="utf-8") as f:
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

if __name__ == "__main__":
    config = Config()
    print(config.is_supported_lot_id("280030477"))