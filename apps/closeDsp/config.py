import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

class Config:
    def __init__(self):
        config_path = Path(__file__).parent / "config.yml"
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def get_device_config(self) -> Dict[str, Any]:
        """获取设备相关配置"""
        return self.config.get("device", {})

    def get_parking_config(self) -> Dict[str, Any]:
        """获取车场相关配置"""
        return self.config.get("parking", {})

    def get_api_config(self) -> Dict[str, Any]:
        """获取接口相关配置"""
        return self.config.get("api", {})

    def get_server_ip(self) -> str:
        """获取服务器IP"""
        return self.get_device_config().get("server_ip", "192.168.0.202")

    def get_server_port(self) -> int:
        """获取服务器端口"""
        return self.get_device_config().get("server_port", 8080)

    def get_device_type(self) -> str:
        """获取设备类型"""
        return self.get_device_config().get("device_type", "1")

    def get_test_support_lot_ids(self) -> List[str]:
        """获取测试环境支持的车场ID列表"""
        return self.get_parking_config().get("test_support_lot_ids", [])

    def get_prod_support_lot_ids(self) -> List[str]:
        """获取生产环境支持的车场ID列表"""
        return self.get_parking_config().get("prod_support_lot_ids", [])

    def get_default_lot_id(self) -> str:
        """获取默认车场ID"""
        return self.get_parking_config().get("default_lot_id", "996000386")

    def get_api_timeout(self) -> int:
        """获取接口超时时间"""
        return self.get_api_config().get("timeout", 30)

    def get_car_come_domain(self, is_test: bool = True) -> str:
        """获取车辆入场接口域名"""
        env = "test" if is_test else "prod"
        return self.get_api_config().get("car_come_domain", {}).get(env, "")

    def is_supported_lot_id(self, lot_id: str, is_test: bool = True) -> bool:
        """检查车场ID是否支持"""
        if is_test:
            return lot_id in self.get_test_support_lot_ids()
        return lot_id in self.get_prod_support_lot_ids() 