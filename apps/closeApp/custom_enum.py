from enum import Enum


class LotIdEnum(str, Enum):
    """车场ID枚举"""
    TEST_LOT_ID = "280025535"
    PROD_LOT_ID = "280030477"


class ServerIpEnum(str, Enum):
    """服务器IP枚举"""
    TEST_SERVER_IP = "192.168.0.183"
    PROD_SERVER_IP = "192.168.0.236"
