// 路侧查费相关类型定义

// 路侧查费信息
export interface RoadFeeInfo {
  carNo: string
  lotId: string
  fee: number
  duration: number
  startTime?: string
  endTime?: string
}

// 路侧查费请求
export interface RoadFeeInquiryRequest {
  car_no: string
  lot_id: string
}
