// 统一导出所有路侧车场相关类型

// 重新导出共享类型
export type { Environment, ApiResponse } from '@/modules/shared/types'

// 重新导出环境配置相关类型
export type {
  RoadLotConfig,
  RoadEnvironmentConfig,
  RoadOperationHistory
} from './environment'



// 重新导出车辆管理相关类型和枚举
export type {
  RoadVehicleInfo,
  RoadCarInOutRequest,
  RoadCarOnParkRequest,
  RoadPresentCarInfoRequest,
  RoadInfo,
  ParkspaceInfo
} from './vehicle'

export {
  CarType,
  VehicleSource,
  PLATE_COLORS,
  PLATE_COLOR_CODES,
  CAR_TYPE_OPTIONS,
  VEHICLE_SOURCE_OPTIONS
} from './vehicle'

// 重新导出查费相关类型
export type {
  RoadFeeInfo,
  RoadFeeInquiryRequest
} from './fee'
