import yaml
from pathlib import Path
from typing import Dict, List, Optional

from core.logger import logger


class RoadConfig:
    """路侧车场配置管理类 - 简化版本，只管理API接口和车场基本信息"""

    def __init__(self):
        self.config_path = Path(__file__).parent / "config.yml"
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def get_test_support_lot_ids(self):
        """测试环境支持的车场ID列表"""
        test_lots = self.get_parking_lots().get("test")
        if test_lots:
            return [lot["id"] for lot in test_lots]
        else:
            return  []

    def get_prod_support_lot_ids(self):
        """正式环境支持的车场ID列表"""
        test_lots = self.get_parking_lots().get("prod")
        if test_lots:
            return [lot["id"] for lot in test_lots]
        else:
            return  []

    def get_road_swagger_base_url(self, env: str) -> str:
        """获取路侧Swagger基础URL"""
        return self.config.get("road_api_endpoints", {}).get("swagger_base_url", {}).get(env, "")

    def get_api_endpoint(self, endpoint_name: str) -> str:
        """获取路侧具体API接口路径（通用，不分环境）"""
        return self.config.get("road_api_endpoints", {}).get(endpoint_name, "")

    def get_yongce_pro_domain(self) -> dict:
        """获取永策Pro域名"""
        return self.config.get("yongce_pro_endpoints", {}).get("domain", {})

    def get_yongce_pro_top_group_id(self) -> dict:
        """获取永策Pro的top_group_id"""
        return self.config.get("yongce_pro_endpoints", {}).get("top_group_id", {})

    def get_yongce_pro_endpoint(self, endpoint_name: str) -> str:
        """获取永策具体API接口路径（通用，不分环境）"""
        return self.config.get("yongce_pro_endpoints", {}).get(endpoint_name, "")

    def get_parking_lots(self, env: str = None) -> Dict:
        """获取车场配置列表"""
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

    def get_parking_road_lot_id(self, lot_id: str) -> str:
        """获取车场路侧的车场id"""
        lot = self.get_parking_lot_by_id(lot_id)
        return lot.get("road_lot_id", "") if lot else f""

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            logger.info("路侧车场配置文件保存成功")
        except Exception as e:
            logger.error(f"路侧车场配置文件保存失败: {e}")
            raise

    def add_parking_lot(self, env: str, lot_config: Dict) -> bool:
        """添加路侧车场配置"""
        try:
            if not lot_config.get("id"):
                logger.error("路侧车场配置必须包含id字段")
                return False

            # 重新加载最新的配置文件
            self._load_config()

            # 检查车场ID是否已存在
            if self.get_parking_lot_by_id(lot_config["id"]):
                logger.error(f"路侧车场ID {lot_config['id']} 已存在")
                return False

            # 确保环境存在
            if "parking_lots" not in self.config:
                self.config["parking_lots"] = {}
            if env not in self.config["parking_lots"]:
                self.config["parking_lots"][env] = []

            # 添加车场配置
            self.config["parking_lots"][env].append(lot_config)

            # 保存配置文件
            self.save_config()

            # 重新加载配置到内存
            self._load_config()

            logger.info(f"路侧车场配置添加成功: {lot_config['id']}")
            return True

        except Exception as e:
            logger.error(f"添加路侧车场配置失败: {e}")
            return False

    def update_parking_lot(self, lot_id: str, updates: Dict) -> bool:
        """更新路侧车场配置"""
        try:
            # 重新加载最新的配置文件
            self._load_config()

            # 查找并更新车场配置
            for env_lots in self.config.get("parking_lots", {}).values():
                for lot in env_lots:
                    if lot.get("id") == lot_id:
                        lot.update(updates)

                        # 保存配置文件
                        self.save_config()

                        # 重新加载配置到内存
                        self._load_config()

                        logger.info(f"路侧车场配置更新成功: {lot_id}")
                        return True

            logger.error(f"路侧车场不存在: {lot_id}")
            return False

        except Exception as e:
            logger.error(f"更新路侧车场配置失败: {e}")
            return False

    def remove_parking_lot(self, lot_id: str) -> bool:
        """删除路侧车场配置"""
        try:
            # 重新加载最新的配置文件
            self._load_config()

            # 查找并删除车场配置
            for env, env_lots in self.config.get("parking_lots", {}).items():
                for i, lot in enumerate(env_lots):
                    if lot.get("id") == lot_id:
                        env_lots.pop(i)

                        # 保存配置文件
                        self.save_config()

                        # 重新加载配置到内存
                        self._load_config()

                        logger.info(f"路侧车场配置删除成功: {lot_id}")
                        return True

            logger.error(f"路侧车场不存在: {lot_id}")
            return False

        except Exception as e:
            logger.error(f"删除路侧车场配置失败: {e}")
            return False

if __name__ == "__main__":
    config = RoadConfig()
    print(config.get_yongce_pro_domain())