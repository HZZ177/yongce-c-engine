// 环境类型
export type Environment = 'test' | 'prod'

// 车场配置
export interface LotConfig {
  id: string
  name: string
  serverIp: string
  inDeviceIp: string
  outDeviceIp: string
}

// 环境配置
export interface EnvironmentConfig {
  currentEnv: Environment
  currentLotId: string
  serverIp: string
  deviceStatus: {
    inDevice: boolean
    outDevice: boolean
  }
}

// 设备管理
export interface DeviceInfo {
  ip: string
  status: boolean
  type: 'in' | 'out'
}

// 车辆信息
export interface VehicleInfo {
  carNo: string
  carColor: number
  recognition: number
  iSerial?: string
  iOpenType: number
}

// 支付信息
export interface PaymentInfo {
  orderNo: string
  payMoney: number
  carNo: string
  lotId: string
}

// 操作历史
export interface OperationHistory {
  id: string
  timestamp: string
  operation: string
  params: any
  result: 'success' | 'error'
  message: string
  duration?: number
}

// API响应格式
export interface ApiResponse<T = any> {
  data: T
  resultCode: number
  resultMsg?: string
}

// 设备上下线请求
export interface DeviceOnOffRequest {
  device_list: string
  server_ip: string
}

// 车辆进出场请求
export interface CarInOutRequest {
  car_no: string
  i_open_type: number
  server_ip: string
  lot_id: string
  car_color: number
  recognition: number
  i_serial?: string
}

// 查询在场车辆请求
export interface CarOnParkRequest {
  lot_id: string
  car_no: string
  start_time?: string
  end_time?: string
}

// 支付订单请求
export interface PayOrderRequest {
  car_no: string
  lot_id: string
}

// 节点长抬状态请求
export interface NodeStatusRequest {
  lot_id: string
  cloud_kt_token: string
}

export interface NodeStatusItem {
  nodeName: string
  nodeType: number
  nodeId: number
  status: '0' | '1'
  onTime?: string
  onUser?: string
  offTime?: string
  offUser?: string
}

export interface NodeStatusResponse {
  code: number
  message: string
  data: NodeStatusItem[]
}

// 节点长抬状态变更请求
export interface ChangeNodeStatusRequest {
  cloud_kt_token: string
  lot_id: string
  node_ids: string
  status: number
}

// 通道二维码信息
export interface ChannelQrCode {
  nodeId: number
  shortCode: string
  nodeType: number
  nodeName: string
  nodeCodeUrl: string
  nodeQrCode: string
  linkUrl: string
}

// 获取通道二维码图片响应
export interface GetChannelQrPicResponse {
  success: boolean
  code: string
  msg: string
  requestId: string | null
  data: {
    records: ChannelQrCode[]
    pageSize: number
    pageNumber: number
    totalCount: number
    totalPage: number
    recordSize: number
  }
} 