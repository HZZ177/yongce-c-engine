// 路侧车场环境配置相关类型定义

import type { Environment } from '@/modules/shared/types'

// 路侧车场配置
export interface RoadLotConfig {
  id: string
  road_lot_id: string
  name: string
  description: string
}

// 路侧环境配置
export interface RoadEnvironmentConfig {
  test: RoadLotConfig[]
  prod: RoadLotConfig[]
}

// 路侧操作历史记录
export interface RoadOperationHistory {
  id: string
  timestamp: string
  operation: string
  params: Record<string, any>
  result: 'success' | 'error'
  message: string
  duration: number
  env: Environment
  lotId: string
  lotName: string
}
