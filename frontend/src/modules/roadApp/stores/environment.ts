import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Environment, RoadEnvironmentConfig } from '../types'
import { roadConfigApi } from '../api/roadApp'

export const useRoadEnvironmentStore = defineStore('roadEnvironment', () => {
  // 状态
  const currentEnv = ref<Environment>('test')
  const currentLotId = ref<string>('')

  // 配置相关状态
  const config = ref<RoadEnvironmentConfig>({
    test: [],
    prod: []
  })
  const configLoaded = ref(false)
  const configLoading = ref(false)

  // 计算属性
  const availableLots = computed(() => {
    return config.value[currentEnv.value] || []
  })

  const currentLot = computed(() => {
    return availableLots.value.find(lot => lot.id === currentLotId.value)
  })

  // 方法
  const setEnvironment = (env: Environment) => {
    currentEnv.value = env
    localStorage.setItem('yongce-road-current-env', env)

    // 自动切换到该环境下的第一个车场
    const lots = config.value[env] || []
    if (lots.length > 0) {
      setCurrentLotId(lots[0].id)
    } else {
      // 如果没有车场，重置选择
      currentLotId.value = ''
    }
  }

  const setCurrentLotId = (lotId: string) => {
    currentLotId.value = lotId
    localStorage.setItem('yongce-road-current-lot-id', lotId)
  }



  const getCurrentLotName = () => {
    const lot = currentLot.value
    return lot ? `${lot.name} (${lot.id})` : '未选择车场'
  }



  const loadConfig = async () => {
    configLoading.value = true
    try {
      // 调用路侧后端API获取配置
      const result = await roadConfigApi.getConfig()

      if (result.resultCode === 200 && result.data) {
        // 转换后端配置格式为前端需要的格式
        const backendConfig = result.data
        const frontendConfig: RoadEnvironmentConfig = {
          test: backendConfig.parking_lots?.test || [],
          prod: backendConfig.parking_lots?.prod || []
        }

        config.value = frontendConfig
        configLoaded.value = true

        console.log('路侧配置加载成功:', frontendConfig)

        // 检查当前选择的车场是否在当前环境中存在，如果不存在则自动选择第一个
        const currentLotExists = availableLots.value.some(lot => lot.id === currentLotId.value)
        if ((!currentLotId.value || !currentLotExists) && availableLots.value.length > 0) {
          setCurrentLotId(availableLots.value[0].id)
        }
      } else {
        throw new Error(result.resultMsg || '获取路侧配置失败')
      }
    } catch (error) {
      console.error('加载路侧配置失败:', error)

      // 如果API调用失败，使用默认配置
      config.value = {
        test: [],
        prod: []
      }
      configLoaded.value = true
    } finally {
      configLoading.value = false
    }
  }

  const initializeFromStorage = () => {
    // 从localStorage恢复状态
    const savedEnv = localStorage.getItem('yongce-road-current-env') as Environment
    if (savedEnv && ['test', 'prod'].includes(savedEnv)) {
      currentEnv.value = savedEnv
    }

    const savedLotId = localStorage.getItem('yongce-road-current-lot-id')
    if (savedLotId) {
      currentLotId.value = savedLotId
    }


  }



  // 初始化
  initializeFromStorage()

  return {
    // 状态
    currentEnv,
    currentLotId,
    config,
    configLoaded,
    configLoading,

    // 计算属性
    availableLots,
    currentLot,

    // 方法
    setEnvironment,
    setCurrentLotId,
    getCurrentLotName,
    loadConfig,
    initializeFromStorage
  }
})
