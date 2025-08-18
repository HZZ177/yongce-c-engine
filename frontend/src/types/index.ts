// 重新导出共享类型
export type { Environment, ApiResponse } from '@/modules/shared/types'

// 重新导出封闭车场类型
export type {
  LotConfig,
  EnvironmentConfig,
  DeviceInfo,
  VehicleInfo,
  PaymentInfo,
  OperationHistory,
  DeviceOnOffRequest,
  CarInOutRequest,
  CarOnParkRequest,
  PayOrderRequest,
  NodeStatusRequest,
  NodeStatusItem,
  NodeStatusResponse,
  ChangeNodeStatusRequest,
  ChannelQrCode,
  GetChannelQrPicResponse
} from '@/modules/closeApp/types'