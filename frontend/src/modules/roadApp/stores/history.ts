import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RoadOperationHistory, Environment } from '../types'

// 生成唯一ID
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

export const useRoadHistoryStore = defineStore('roadHistory', () => {
  const history = ref<RoadOperationHistory[]>([])

  const addHistory = (operation: Omit<RoadOperationHistory, 'id' | 'timestamp'>) => {
    const newRecord: RoadOperationHistory = {
      id: generateId(),
      timestamp: new Date().toLocaleString('zh-CN'),
      ...operation
    }
    
    history.value.unshift(newRecord)
    
    // 限制历史记录数量，保留最近100条
    if (history.value.length > 100) {
      history.value = history.value.slice(0, 100)
    }
  }

  const clearHistory = () => {
    history.value = []
  }

  const removeHistoryItem = (id: string) => {
    const index = history.value.findIndex(item => item.id === id)
    if (index > -1) {
      history.value.splice(index, 1)
    }
  }

  const getHistoryByOperation = (operationType: string) => {
    return history.value.filter(item => item.operation === operationType)
  }

  const getHistoryByEnv = (env: Environment) => {
    return history.value.filter(item => item.env === env)
  }

  const getHistoryByLot = (lotId: string) => {
    return history.value.filter(item => item.lotId === lotId)
  }

  return {
    history,
    addHistory,
    clearHistory,
    removeHistoryItem,
    getHistoryByOperation,
    getHistoryByEnv,
    getHistoryByLot
  }
})
