// 环境类型
export type Environment = 'test' | 'prod'

// API响应格式
export interface ApiResponse<T = any> {
  data: T
  resultCode: number
  resultMsg?: string
}
