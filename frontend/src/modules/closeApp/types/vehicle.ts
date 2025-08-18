// 车辆管理相关类型

// 车辆信息
export interface VehicleInfo {
  carNo: string
  carColor: number
  recognition: number
  iSerial?: string
  iOpenType: number
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
