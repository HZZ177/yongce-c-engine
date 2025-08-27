// 从共享类型导入基础类型
import type { ApiResponse } from '@/modules/shared/types'

// 设备管理相关类型
export interface DeviceInfo {
  ip: string
  status: boolean
  type: 'in' | 'out'
}

// 设备上下线请求
export interface DeviceOnOffRequest {
  device_list: string
  server_ip: string
}

// 节点长抬状态请求
export interface NodeStatusRequest {
  lot_id: string
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

// 场内码信息
export interface CloseParkCodeRecord {
  lotCode: string
  lotName: string
  lotType: number
  lotTypeName: string
  parkingSpaceNum: number
  closeParkCode: string
}

// 获取场内码响应
export interface GetCloseParkCodeResponse {
  success: boolean
  code: string
  msg: string
  requestId: string | null
  data: {
    records: CloseParkCodeRecord[]
    pageSize: number
    pageNumber: number
    totalCount: number
    totalPage: number
    recordSize: number
  }
}
