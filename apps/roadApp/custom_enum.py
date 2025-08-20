from enum import Enum


class RoadLotIdEnum(str, Enum):
    """路侧车场ID枚举"""
    TEST_LOT_ID = "4799"  # 路侧测试环境车场ID
    PROD_LOT_ID = "280030147"  # 路侧灰度环境车场ID
