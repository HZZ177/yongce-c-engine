import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Environment, EnvironmentConfig, LotConfig } from '../types'
import axios from 'axios'
import { deviceApi, nodeApi } from '../api/closeApp'

export const useEnvironmentStore = defineStore('environment', () => {
  // 获取车场名称的函数 - 从后端配置获取
  const getLotName = (lotId: string, env: Environment, index: number): string => {
    // 从后端配置中查找车场名称
    const lots = lotConfigs.value[env] || []
    const lot = lots.find(l => l.id === lotId)
    if (lot && lot.name) {
      return lot.name
    }
    // 如果没有配置名称，使用默认规则
    return env === 'test' ? `测试车场${index + 1}` : `生产车场${index + 1}`
  }

  // 从本地存储获取初始值，如果没有则使用默认值
  const getStoredEnv = (): Environment => {
    const stored = localStorage.getItem('yongce-current-env')
    return (stored as Environment) || 'test'
  }
  
  const getStoredLotId = (): string => {
    const stored = localStorage.getItem('yongce-current-lot-id')
    return stored || ''
  }
  
  // 通道名称映射（从后端配置获取）
  const channelNameMap = ref<Record<string, string>>({})

  // 获取通道名称（从后端配置获取，兜底为入口通道/出口通道）
  const getChannelName = (deviceIp: string, deviceType: 'in' | 'out'): string => {
    // 从后端配置获取通道名称
    if (channelNameMap.value[deviceIp]) {
      return channelNameMap.value[deviceIp]
    }

    // 兜底名称
    return deviceType === 'in' ? '入口通道' : '出口通道'
  }

  // 设置通道名称（更新后端配置）
  const setChannelName = async (deviceIp: string, name: string): Promise<boolean> => {
    if (!deviceIp || !currentLotId.value) return false

    try {
      const response = await axios.put('/closeApp/config/channel-name', null, {
        params: {
          lot_id: currentLotId.value,
          device_ip: deviceIp,
          channel_name: name
        }
      })

      if (response.data.code === 200) {
        // 更新本地缓存
        channelNameMap.value = { ...channelNameMap.value, [deviceIp]: name }
        // 重新加载配置以确保数据同步
        await loadConfig()
        return true
      }
      return false
    } catch (error) {
      console.error('设置通道名称失败:', error)
      return false
    }
  }

  // 云助手token存储
  const getStoredCloudKtToken = (): string => {
    return localStorage.getItem('yongce-cloud-kt-token') || ''
  }
  const cloudKtToken = ref<string>(getStoredCloudKtToken())
  const setCloudKtToken = (token: string) => {
    cloudKtToken.value = token
    localStorage.setItem('yongce-cloud-kt-token', token)
  }

  // 节点状态数据
  const nodeStatus = ref<any[]>([])
  const nodeStatusLoading = ref(false)
  
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

  // 设备状态轮询相关
  const deviceStatusPolling = ref<NodeJS.Timeout | null>(null)
  const deviceStatusPollingInterval = ref(5000) // 默认5秒轮询一次
  const lastDeviceStatusFetch = ref<Record<string, { online: boolean; updatedAt: number }>>({})

  // 二维码数据缓存
  const qrCodeData = ref<Record<string, any>>({})
  const qrCodeDataLoading = ref(false)
  const qrCodeDataLoaded = ref(false)

  // 计算属性
  const currentLotConfig = computed(() => {
    const lots = lotConfigs.value[currentEnv.value] || []
    return lots.find(lot => lot.id === currentLotId.value) || lots[0] || null
  })

  const serverIp = computed(() => currentLotConfig.value?.serverIp || '')

  const availableLots = computed(() => lotConfigs.value[currentEnv.value] || [])

  // 获取节点状态
  const fetchNodeStatus = async () => {
    if (!currentLotId.value || !cloudKtToken.value) {
      return
    }
    
    nodeStatusLoading.value = true
    try {
      const response = await axios.get('/closeApp/nodeStatus', {
        params: {
          lot_id: currentLotId.value,
          cloud_kt_token: cloudKtToken.value
        }
      })
      
      if (response.data.code === 200) {
        nodeStatus.value = response.data.data || []
        return { success: true, data: response.data }
      } else {
        console.warn('获取节点状态失败:', response.data.message)
        nodeStatus.value = []
        return { success: false, data: response.data }
      }
    } catch (error) {
      console.error('获取节点状态失败:', error)
      nodeStatus.value = []
      return { success: false, error: error }
    } finally {
      nodeStatusLoading.value = false
    }
  }

  // 手动刷新节点状态（供外部调用）
  const refreshNodeStatus = async () => {
    if (!cloudKtToken.value) {
      console.warn('云助手Token未设置，无法获取节点状态')
      return
    }
    if (!currentLotId.value) {
      console.warn('未选择车场，无法获取节点状态')
      return
    }
    return await fetchNodeStatus()
  }

  // 方法
  const setEnvironment = (env: Environment) => {
    currentEnv.value = env
    // 保存到本地存储
    localStorage.setItem('yongce-current-env', env)

    // 重置通道码缓存
    qrCodeData.value = {}
    qrCodeDataLoaded.value = false

    // 自动切换到该环境下的第一个车场
    const lots = lotConfigs.value[env] || []
    if (lots.length > 0) {
      currentLotId.value = lots[0].id
      localStorage.setItem('yongce-current-lot-id', lots[0].id)
      
      // 环境切换完成后立即查询设备状态，避免等待轮询延迟
      const currentLot = lots[0]
      if (currentLot && (currentLot.inDeviceIp || currentLot.outDeviceIp)) {
        const ips = []
        if (currentLot.inDeviceIp) ips.push(currentLot.inDeviceIp)
        if (currentLot.outDeviceIp) ips.push(currentLot.outDeviceIp)
        
        if (ips.length > 0) {
          // 异步调用，不阻塞环境切换流程
          fetchDeviceStatus(ips).catch(error => {
            console.warn('环境切换后设备状态查询失败:', error)
          })
        }
      }
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

    // 重置通道码缓存
    qrCodeData.value = {}
    qrCodeDataLoaded.value = false

    // 切换车场后重新获取节点状态
    if (cloudKtToken.value) {
      fetchNodeStatus()
    }
    
    // 车场切换完成后立即查询设备状态，避免等待轮询延迟
    const currentLot = lotConfigs.value[currentEnv.value]?.find(lot => lot.id === lotId)
    if (currentLot && (currentLot.inDeviceIp || currentLot.outDeviceIp)) {
      const ips = []
      if (currentLot.inDeviceIp) ips.push(currentLot.inDeviceIp)
      if (currentLot.outDeviceIp) ips.push(currentLot.outDeviceIp)
      
      if (ips.length > 0) {
        // 异步调用，不阻塞车场切换流程
        fetchDeviceStatus(ips).catch(error => {
          console.warn('车场切换后设备状态查询失败:', error)
        })
      }
    }
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
  const loadConfig = async (forceReload: boolean = false) => {
    if (!forceReload && (configLoaded.value || configLoading.value)) {
      return
    }
    
    configLoading.value = true
    try {
      const response = await axios.get('/closeApp/config')
      const configData = response.data.data
      
      // 解析配置数据
      const testLots: LotConfig[] = []
      const prodLots: LotConfig[] = []

      // 优先使用新的parking_lots结构
      if (configData.parking_lots) {
        // 处理测试环境配置
        const testParkingLots = configData.parking_lots.test || []
        testParkingLots.forEach((lot: any, index: number) => {
          const lotConfig = {
            id: lot.id,
            name: lot.name || getLotName(lot.id, 'test', index),
            serverIp: lot.server_ip || '',
            inDeviceIp: lot.devices?.in_device || '',
            outDeviceIp: lot.devices?.out_device || '',
            channelNames: lot.channel_names || {}
          }
          testLots.push(lotConfig)

          // 更新通道名称映射
          if (lot.channel_names) {
            Object.assign(channelNameMap.value, lot.channel_names)
          }
        })

        // 处理生产环境配置
        const prodParkingLots = configData.parking_lots.prod || []
        prodParkingLots.forEach((lot: any, index: number) => {
          const lotConfig = {
            id: lot.id,
            name: lot.name || getLotName(lot.id, 'prod', index),
            serverIp: lot.server_ip || '',
            inDeviceIp: lot.devices?.in_device || '',
            outDeviceIp: lot.devices?.out_device || '',
            channelNames: lot.channel_names || {}
          }
          prodLots.push(lotConfig)

          // 更新通道名称映射
          if (lot.channel_names) {
            Object.assign(channelNameMap.value, lot.channel_names)
          }
        })
      } else {
        // 向后兼容：使用旧的配置结构
        const testLotIds = configData.support_parking_ips?.test || []
        const testServerIps = configData.support_server_ips?.test || []
        const testDevices = configData.device?.test || {}

        testLotIds.forEach((lotId: string, index: number) => {
          testLots.push({
            id: lotId,
            name: getLotName(lotId, 'test', index),
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
            name: getLotName(lotId, 'prod', index),
            serverIp: prodServerIps[index] || '',
            inDeviceIp: prodDevices.in_device || '',
            outDeviceIp: prodDevices.out_device || ''
          })
        })
      }
      
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
      
      // 配置加载完成后，如果有token则获取节点状态
      if (cloudKtToken.value && currentLotId.value) {
        await fetchNodeStatus()
      }
      
    } catch (error) {
      console.error('加载配置失败:', error)
      // 配置加载失败，保持空配置状态
      configLoaded.value = true
    } finally {
      configLoading.value = false
    }
  }

  // 获取设备真实在线状态
  const fetchDeviceStatus = async (ips: string[]): Promise<Record<string, { online: boolean; updatedAt: number }>> => {
    if (ips.length === 0) {
      return {}
    }
    
    try {
      const response = await deviceApi.deviceStatus({
        device_ips: ips.join(',')
      })
      
      if (response.resultCode === 200) {
        const statusMap: Record<string, { online: boolean; updatedAt: number }> = {}
        
        // 处理返回的状态数据
        if (Array.isArray(response.data)) {
          response.data.forEach((item: any) => {
            if (item.ip) {
              statusMap[item.ip] = {
                online: item.online || false,
                updatedAt: item.updatedAt || 0
              }
            }
          })
        }
        
        // 更新存储的状态
        lastDeviceStatusFetch.value = statusMap
        
        // 更新现有的deviceStatus以保持兼容性
        const currentLot = currentLotConfig.value
        if (currentLot) {
          if (currentLot.inDeviceIp && statusMap[currentLot.inDeviceIp]) {
            deviceStatus.value.inDevice = statusMap[currentLot.inDeviceIp].online
          }
          if (currentLot.outDeviceIp && statusMap[currentLot.outDeviceIp]) {
            deviceStatus.value.outDevice = statusMap[currentLot.outDeviceIp].online
          }
        }
        
        return statusMap
      } else {
        console.warn('获取设备状态失败:', response.resultMsg)
        return {}
      }
    } catch (error) {
      console.error('获取设备状态失败:', error)
      return {}
    }
  }

  // 启动设备状态轮询
  const startDeviceStatusPolling = () => {
    if (deviceStatusPolling.value) {
      return // 已经在轮询中
    }
    
    const poll = async () => {
      const currentLot = currentLotConfig.value
      if (currentLot && (currentLot.inDeviceIp || currentLot.outDeviceIp)) {
        const ips = []
        if (currentLot.inDeviceIp) ips.push(currentLot.inDeviceIp)
        if (currentLot.outDeviceIp) ips.push(currentLot.outDeviceIp)
        
        if (ips.length > 0) {
          await fetchDeviceStatus(ips)
        }
      }
    }
    
    // 立即执行一次
    poll()
    
    // 设置定时轮询
    deviceStatusPolling.value = setInterval(poll, deviceStatusPollingInterval.value)
  }

  // 停止设备状态轮询
  const stopDeviceStatusPolling = () => {
    if (deviceStatusPolling.value) {
      clearInterval(deviceStatusPolling.value)
      deviceStatusPolling.value = null
    }
  }

  // 设置轮询间隔
  const setDeviceStatusPollingInterval = (interval: number) => {
    deviceStatusPollingInterval.value = Math.max(1000, interval) // 最小1秒
    
    // 如果正在轮询，重启轮询以应用新间隔
    if (deviceStatusPolling.value) {
      stopDeviceStatusPolling()
      startDeviceStatusPolling()
    }
  }

  // 预加载二维码数据
  const preloadQrCodeData = async () => {
    if (!currentLotId.value || qrCodeDataLoading.value) {
      return
    }
    
    qrCodeDataLoading.value = true
    try {
      const response = await axios.get('/closeApp/getChannelQrPic', {
        params: {
          lot_id: currentLotId.value
        }
      })
      
      if (response.data.code === 200 && response.data.data) {
        const responseData = response.data.data
        
        if (responseData.success && responseData.data?.records) {
          // 将二维码数据按通道名称存储
          const qrCodeMap: Record<string, any> = {}
          responseData.data.records.forEach((record: any) => {
            if (record.nodeName && record.nodeQrCode) {
              qrCodeMap[record.nodeName] = record
            }
          })
          
          qrCodeData.value = qrCodeMap
          qrCodeDataLoaded.value = true
          console.log('二维码数据预加载成功:', Object.keys(qrCodeMap))
        }
      }
    } catch (error) {
      console.error('预加载二维码数据失败:', error)
      qrCodeDataLoaded.value = false
    } finally {
      qrCodeDataLoading.value = false
    }
  }

  // 获取指定通道的二维码数据
  const getQrCodeData = (channelName: string) => {
    return qrCodeData.value[channelName] || null
  }

  // 刷新二维码数据
  const refreshQrCodeData = async () => {
    qrCodeDataLoaded.value = false
    await preloadQrCodeData()
  }

  return {
    // 状态
    currentEnv,
    currentLotId,
    deviceStatus,
    channelNameMap,
    cloudKtToken,
    nodeStatus,
    nodeStatusLoading,
    configLoaded,
    configLoading,
    lastDeviceStatusFetch,
    deviceStatusPollingInterval,
    deviceStatusPolling,
    qrCodeData,
    qrCodeDataLoading,
    qrCodeDataLoaded,

    // 计算属性
    currentLotConfig,
    serverIp,
    availableLots,

    // 方法
    setEnvironment,
    setLotId,
    updateDeviceStatus,
    resetDeviceStatus,
    setChannelName,
    getChannelName,
    setCloudKtToken,
    fetchNodeStatus,
    loadConfig,
    refreshNodeStatus,
    fetchDeviceStatus,
    startDeviceStatusPolling,
    stopDeviceStatusPolling,
    setDeviceStatusPollingInterval,
    preloadQrCodeData,
    getQrCodeData,
    refreshQrCodeData
  }
}) 