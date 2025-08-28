// 路侧车辆管理相关类型定义

// 车辆类型枚举
export enum CarType {
  SMALL = 0,      // 小型车
  MEDIUM = 1,     // 中型车
  LARGE = 2,      // 大型车
  NEW_ENERGY = 3, // 新能源车
  SPECIAL = 4,    // 特殊车辆
  NON_MOTOR = 5,  // 非机动车
  MOTORCYCLE = 6, // 摩托车
  TRICYCLE = 7,   // 三轮车
  NEW_ENERGY_TRUCK = 8 // 新能源货车
}

// 车辆来源枚举
export enum VehicleSource {
  POS = 0,        // POS机
  MAGNETIC = 1,   // 地磁
  CAMERA = 2,     // 相机
  WEB = 3,        // web端
  VIDEO_PILE = 4, // 视频桩
  MOBILE = 5,     // 移动端
  PATROL = 6      // 巡逻车
}

// 车牌颜色选项
export const PLATE_COLORS = [
  { label: '蓝色', value: '蓝' },
  { label: '黄色', value: '黄' },
  { label: '绿色', value: '绿' }
] as const

// 车牌颜色编码选项（用于查询在场车信息接口）
export const PLATE_COLOR_CODES = [
  { label: '白色', value: '1' },
  { label: '黑色', value: '2' },
  { label: '蓝色', value: '3' },
  { label: '黄色', value: '4' },
  { label: '绿色', value: '5' }
] as const

// 车辆类型选项
export const CAR_TYPE_OPTIONS = [
  { label: '小型车', value: CarType.SMALL },
  { label: '中型车', value: CarType.MEDIUM },
  { label: '大型车', value: CarType.LARGE },
  { label: '新能源车', value: CarType.NEW_ENERGY },
  { label: '特殊车辆', value: CarType.SPECIAL },
  { label: '非机动车', value: CarType.NON_MOTOR },
  { label: '摩托车', value: CarType.MOTORCYCLE },
  { label: '三轮车', value: CarType.TRICYCLE },
  { label: '新能源货车', value: CarType.NEW_ENERGY_TRUCK }
] as const

// 车辆来源选项
export const VEHICLE_SOURCE_OPTIONS = [
  { label: 'POS机', value: VehicleSource.POS },
  { label: '地磁', value: VehicleSource.MAGNETIC },
  { label: '相机', value: VehicleSource.CAMERA },
  { label: 'web端', value: VehicleSource.WEB },
  { label: '视频桩', value: VehicleSource.VIDEO_PILE },
  { label: '移动端', value: VehicleSource.MOBILE },
  { label: '巡逻车', value: VehicleSource.PATROL }
] as const

// 路侧车辆信息
export interface RoadVehicleInfo {
  carNo: string
  carType: CarType
  plateColor: string
  source: VehicleSource
  inTime?: string
}

// 路侧车辆入场/出场请求（匹配后端接口参数）
export interface RoadCarInOutRequest {
  lot_id: string
  car_no: string
  car_type: CarType
  plate_color: string
  in_time?: string
  source: VehicleSource
  road_code?: string
  park_space_code?: string
}

// 路侧在场车辆查询请求
export interface RoadCarOnParkRequest {
  lot_id: string
  car_no: string
  start_time?: string
  end_time?: string
}

// 路侧在场车信息查询请求（新接口）
export interface RoadPresentCarInfoRequest {
  car_no: string
  lot_id: string
  car_type: string
  parkspace_code: string
  plate_color: string
  road_code: string
}

// 路段信息
export interface RoadInfo {
  id: string;
  roadCode: string;
  roadName: string;
  parkspaceNum: number;
  idleParkspaceNum?: number | null;
  parkCode: string;
  parkName: string;
  longitude?: string | null;
  latitude?: string | null;
  isDelete?: number;
  createTime: string;
  updateTime: string;
  createBy?: string;
  updateBy?: string;
  feeRuleName?: string;
}

// 车位信息
export interface ParkspaceInfo {
  id: string
  parkspaceCode: string
  parkspaceType: number
  parkName: string
  roadCode: string
  roadName: string
  longitude?: string
  latitude?: string
  status: number
  createTime: string
  updateTime: string
  parkspacePlate?: string // 车位上的车牌信息，格式：无车 或 有车(川DHSY00)
}
