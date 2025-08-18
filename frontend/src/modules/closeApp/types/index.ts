// 统一导出所有封闭车场相关类型

// 重新导出共享类型
export type { Environment, ApiResponse } from '@/modules/shared/types'

// 重新导出环境配置相关类型
export type {
  LotConfig,
  EnvironmentConfig,
  OperationHistory
} from './environment'

// 重新导出设备管理相关类型
export type {
  DeviceInfo,
  DeviceOnOffRequest,
  NodeStatusRequest,
  NodeStatusItem,
  NodeStatusResponse,
  ChangeNodeStatusRequest,
  ChannelQrCode,
  GetChannelQrPicResponse
} from './device'

// 重新导出车辆管理相关类型
export type {
  VehicleInfo,
  CarInOutRequest,
  CarOnParkRequest
} from './vehicle'

// 重新导出支付管理相关类型
export type {
  PaymentInfo,
  PayOrderRequest
} from './payment'
