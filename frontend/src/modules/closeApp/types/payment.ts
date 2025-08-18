// 支付管理相关类型

// 支付信息
export interface PaymentInfo {
  orderNo: string
  payMoney: number
  carNo: string
  lotId: string
}

// 支付订单请求
export interface PayOrderRequest {
  car_no: string
  lot_id: string
}
