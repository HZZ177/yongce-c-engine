// 路侧设备管理相关类型定义

// 路侧设备信息
export interface RoadDeviceInfo {
  ip: string
  type: 'in' | 'out'
  status: boolean
  loading?: boolean
  channelName?: string
}

// 路侧设备上线/下线请求
export interface RoadDeviceOnOffRequest {
  device_list: string
  server_ip: string
}

// 路侧节点状态请求
export interface RoadNodeStatusRequest {
  lot_id: string
  cloud_kt_token: string
}

// 路侧节点状态项
export interface RoadNodeStatusItem {
  nodeId: string
  nodeName: string
  status: number // 0: 关闭长抬, 1: 打开长抬
  deviceIp: string
}

// 路侧节点状态响应
export interface RoadNodeStatusResponse {
  resultCode: number
  resultMsg: string
  data: RoadNodeStatusItem[]
}

// 路侧变更节点状态请求
export interface RoadChangeNodeStatusRequest {
  cloud_kt_token: string
  lot_id: string
  node_ids: string
  status: number
}

// 路侧通道二维码
export interface RoadChannelQrCode {
  nodeCode: string
  nodeName: string
  qrCodeUrl: string
}

// 路侧获取通道二维码响应
export interface RoadGetChannelQrPicResponse {
  list: RoadChannelQrCode[]
}
