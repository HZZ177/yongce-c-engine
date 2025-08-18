// 从共享类型导入基础类型
import type { Environment } from '@/modules/shared/types'

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
