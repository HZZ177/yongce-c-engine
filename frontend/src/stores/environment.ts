import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Environment, EnvironmentConfig, LotConfig } from '@/types'
import axios from 'axios'

export const useEnvironmentStore = defineStore('environment', () => {
  // 从本地存储获取初始值，如果没有则使用默认值
  const getStoredEnv = (): Environment => {
    const stored = localStorage.getItem('yongce-current-env')
    return (stored as Environment) || 'test'
  }
  
  const getStoredLotId = (): string => {
    const stored = localStorage.getItem('yongce-current-lot-id')
    return stored || ''
  }
  
  // 环境配置
  const currentEnv = ref<Environment>(getStoredEnv())
  const currentLotId = ref<string>(getStoredLotId())
  
  // 车场配置映射 - 从后端API动态获取
  const lotConfigs = ref<Record<Environment, LotConfig[]>>({
    test: [],
    prod: []
  })

  // 配置加载状态
  const configLoaded = ref(false)
  const configLoading = ref(false)

  // 设备状态
  const deviceStatus = ref({
    inDevice: false,
    outDevice: false
  })

  // 计算属性
  const currentLotConfig = computed(() => {
    const lots = lotConfigs.value[currentEnv.value] || []
    return lots.find(lot => lot.id === currentLotId.value) || lots[0] || null
  })

  const serverIp = computed(() => currentLotConfig.value?.serverIp || '')

  const availableLots = computed(() => lotConfigs.value[currentEnv.value] || [])

  // 方法
  const setEnvironment = (env: Environment) => {
    currentEnv.value = env
    // 保存到本地存储
    localStorage.setItem('yongce-current-env', env)
    // 自动切换到该环境下的第一个车场
    const lots = lotConfigs.value[env] || []
    if (lots.length > 0) {
      currentLotId.value = lots[0].id
      localStorage.setItem('yongce-current-lot-id', lots[0].id)
    } else {
      // 如果没有可用车场，清空当前选择
      currentLotId.value = ''
      localStorage.removeItem('yongce-current-lot-id')
    }
  }

  const setLotId = (lotId: string) => {
    currentLotId.value = lotId
    // 保存到本地存储
    localStorage.setItem('yongce-current-lot-id', lotId)
  }

  const updateDeviceStatus = (type: 'inDevice' | 'outDevice', status: boolean) => {
    deviceStatus.value[type] = status
  }

  const resetDeviceStatus = () => {
    deviceStatus.value = {
      inDevice: false,
      outDevice: false
    }
  }

  // 从后端API加载配置
  const loadConfig = async () => {
    if (configLoaded.value || configLoading.value) {
      return
    }
    
    configLoading.value = true
    try {
      const response = await axios.get('/closeApp/config')
      const configData = response.data.data
      
      // 解析配置数据
      const testLots: LotConfig[] = []
      const prodLots: LotConfig[] = []
      
      // 处理测试环境配置
      const testLotIds = configData.support_parking_ips?.test || []
      const testServerIps = configData.support_server_ips?.test || []
      const testDevices = configData.device?.test || {}
      
      testLotIds.forEach((lotId: string, index: number) => {
        testLots.push({
          id: lotId,
          name: `测试车场${index + 1}`,
          serverIp: testServerIps[index] || '',
          inDeviceIp: testDevices.in_device || '',
          outDeviceIp: testDevices.out_device || ''
        })
      })
      
      // 处理生产环境配置
      const prodLotIds = configData.support_parking_ips?.prod || []
      const prodServerIps = configData.support_server_ips?.prod || []
      const prodDevices = configData.device?.prod || {}
      
      prodLotIds.forEach((lotId: string, index: number) => {
        prodLots.push({
          id: lotId,
          name: `生产车场${index + 1}`,
          serverIp: prodServerIps[index] || '',
          inDeviceIp: prodDevices.in_device || '',
          outDeviceIp: prodDevices.out_device || ''
        })
      })
      
      lotConfigs.value = {
        test: testLots,
        prod: prodLots
      }
      
      configLoaded.value = true
      
      // 如果当前选择的车场不在新配置中，自动切换到第一个可用车场
      const currentLots = lotConfigs.value[currentEnv.value] || []
      if (currentLots.length > 0) {
        if (!currentLotId.value || !currentLots.find(lot => lot.id === currentLotId.value)) {
          currentLotId.value = currentLots[0].id
          localStorage.setItem('yongce-current-lot-id', currentLots[0].id)
        }
      } else {
        // 如果没有可用车场，清空当前选择
        currentLotId.value = ''
        localStorage.removeItem('yongce-current-lot-id')
      }
      
    } catch (error) {
      console.error('加载配置失败:', error)
      // 配置加载失败，保持空配置状态
      configLoaded.value = true
    } finally {
      configLoading.value = false
    }
  }

  return {
    // 状态
    currentEnv,
    currentLotId,
    deviceStatus,
    configLoaded,
    configLoading,
    
    // 计算属性
    currentLotConfig,
    serverIp,
    availableLots,
    
    // 方法
    setEnvironment,
    setLotId,
    updateDeviceStatus,
    resetDeviceStatus,
    loadConfig
  }
}) 