import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { OperationHistory } from '@/types'

export const useHistoryStore = defineStore('history', () => {
  // 操作历史列表
  const historyList = ref<OperationHistory[]>([])

  // 添加操作历史
  const addHistory = (operation: Omit<OperationHistory, 'id' | 'timestamp'>) => {
    const history: OperationHistory = {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleString('zh-CN'),
      ...operation
    }
    
    historyList.value.unshift(history)
    
    // 只保留最近100条记录
    if (historyList.value.length > 100) {
      historyList.value = historyList.value.slice(0, 100)
    }
  }

  // 清空历史记录
  const clearHistory = () => {
    historyList.value = []
  }

  // 删除指定历史记录
  const removeHistory = (id: string) => {
    const index = historyList.value.findIndex(item => item.id === id)
    if (index > -1) {
      historyList.value.splice(index, 1)
    }
  }

  return {
    historyList,
    addHistory,
    clearHistory,
    removeHistory
  }
}) 