<template>
  <div class="close-app">
    <!-- 顶部配置栏 - 融合环境配置和设备管理 -->
    <div class="top-config-bar">
      <div class="config-section">
        <!-- 第一行：标题 -->
        <div class="config-header">
          <div class="section-title">环境配置</div>
          <div class="config-actions">
            <el-button
              type="primary"
              size="small"
              @click="showParkingLotEditor"
              :disabled="!envStore.configLoaded"
            >
              <el-icon><Edit /></el-icon>
              环境编辑
            </el-button>
          </div>
        </div>
        
        <!-- 第二行：环境按钮 -->
        <div class="config-row">
          <div class="env-switch">
            <button 
              class="env-button" 
              :class="{ active: currentEnv === 'test' }"
              @click="handleEnvSwitch('test', $event)"
            >
              <div class="env-icon test-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 12l2 2 4-4"/>
                  <path d="M21 12c-1 0-2-1-2-2s1-2 2-2 2 1 2 2-1 2-2 2z"/>
                  <path d="M3 12c1 0 2-1 2-2s-1-2-2-2-2 1-2 2 1 2 2 2z"/>
                </svg>
              </div>
              <span class="env-name">测试环境</span>
            </button>
            <button 
              class="env-button" 
              :class="{ active: currentEnv === 'prod' }"
              @click="handleEnvSwitch('prod', $event)"
            >
              <div class="env-icon prod-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </div>
              <span class="env-name">灰度环境</span>
            </button>
          </div>
        </div>
        
        <!-- 第三行：服务器IP和车场选择 -->
        <div class="config-row">
          <div class="server-ip">
            <span class="ip-label">服务器IP:</span>
            <span class="ip-value">{{ envStore.serverIp }}</span>
          </div>
          
          <div class="lot-select">
            <el-select 
              v-model="currentLotId" 
              placeholder="请选择车场"
              @change="handleLotChange"
              style="width: 200px"
              :loading="envStore.configLoading"
              :disabled="envStore.configLoading || availableLots.length === 0"
              size="default"
            >
              <el-option
                v-for="lot in availableLots"
                :key="lot.id"
                :label="`${lot.name} (${lot.id})`"
                :value="lot.id"
              />
            </el-select>
          </div>
        </div>
      </div>
      
      <!-- 分割线 -->
      <div class="divider"></div>
      
      <div class="device-section">
        <!-- 第一行：标题和设置云助手token按钮 -->
        <div class="device-header">
          <div class="section-title">设备管理</div>
          <div class="device-actions">
            <el-button type="primary" size="small" @click="handleSetCloudToken">
              设置云助手Token
            </el-button>
            <StandardTooltip
              content="需要在运维中心手动代理登录到对应车场的云助手获取一下"
            />
            <el-button 
              type="success" 
              size="small" 
              @click="handleRefreshNodeStatus"
              :loading="envStore.nodeStatusLoading"
              :disabled="!envStore.cloudKtToken || !envStore.currentLotId"
            >
              刷新长抬状态
            </el-button>
            <StandardTooltip
              content="该功能依赖设备保持在线状态才能查到准确的状态或成功更改状态<br>否则会固定返回关闭<br>因此刷新时会自动上线所有设备"
              :raw-content="true"
            />
          </div>
        </div>
        
        <!-- 第二行：设备状态 -->
        <div class="device-status">
          <div v-for="device in deviceList" :key="device.ip" class="device-item">
            <div class="device-type-status">
              <span class="device-type">{{ device.type === 'in' ? '入口' : '出口' }}</span>
              <div class="status-indicator" :class="device.status ? 'online' : 'offline'">
                <div class="status-dot"></div>
                <span class="status-text">{{ device.status ? '在线' : '离线' }}</span>
              </div>
            </div>
            <div class="device-info">
              <div class="device-name">
                <StandardTooltip
                  content="名称必须和车场配置的通道名称保持一致，需要通过名称查询/变更通道状态"
                />
                <span>{{ getChannelName(device) }}</span>
                <el-button link type="primary" size="small" @click="handleEditChannelName(device)">编辑</el-button>
              </div>
              <span class="device-ip">{{ device.ip }}</span>
            </div>
            <!-- 按钮容器 -->
            <div class="device-buttons">
              <el-button 
                :type="device.status ? 'danger' : 'primary'"
                size="small"
                @click="handleDeviceToggle(device)"
                :loading="device.loading"
              >
                {{ device.status ? '下线' : '上线' }}
              </el-button>
              <!-- 查看二维码按钮 -->
              <el-button 
                type="info"
                size="small"
                @click="handleViewQrCode(device)"
                :disabled="!envStore.currentLotId"
              >
                通道码
              </el-button>
            </div>
            <!-- 长抬状态开关 -->
            <div class="long-lift-status">
              <span class="status-label">通道长抬</span>
              <el-tooltip
                v-if="!device.status"
                content="设备离线，需先连接设备"
                placement="top"
                effect="light"
              >
                <div class="switch-wrapper">
                  <el-switch
                    :model-value="getLongLiftStatus(device)"
                    :active-value="'1'"
                    :inactive-value="'0'"
                    :disabled="!envStore.cloudKtToken || !envStore.currentLotId || deviceLoadingStates[device.ip] || !device.status"
                    size="default"
                    @change="handleLongLiftStatusChange(device, $event)"
                  />
                </div>
              </el-tooltip>
              <el-switch
                v-else
                :model-value="getLongLiftStatus(device)"
                :active-value="'1'"
                :inactive-value="'0'"
                :disabled="!envStore.cloudKtToken || !envStore.currentLotId || deviceLoadingStates[device.ip]"
                size="default"
                @change="handleLongLiftStatusChange(device, $event)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 功能区域 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <!-- 车辆管理和支付管理 - 同一行平分宽度 -->
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="12">
        <VehicleManagement @toggle-log-monitor="toggleLogMonitor" :is-log-monitor-visible="showLogMonitor" />
          </el-col>
          <el-col :span="12">
        <PaymentManagement />
      </el-col>
        </el-row>

        <!-- 日志监控卡片 -->
        <!-- 日志监控卡片 -->
        <el-row v-if="showLogMonitor" style="margin-bottom: 20px;">
          <el-col :span="24">
            <LogMonitor :lot-id="envStore.currentLotId" @close="toggleLogMonitor" />
          </el-col>
        </el-row>

        <!-- 操作历史 - 移到最下方 -->
        <OperationHistory />
      </el-col>
    </el-row>
    
    <!-- 二维码弹窗 -->
    <QrCodeDialog
      v-model="qrCodeDialogVisible"
      :channel-name="currentQrCodeDevice ? getChannelName(currentQrCodeDevice) : ''"
      :channel-type="currentQrCodeDevice?.type || 'in'"
      :lot-id="envStore.currentLotId"
    />

    <!-- 车场编辑器 -->
    <ParkingLotEditor
      v-model="parkingLotEditorVisible"
      :current-env="envStore.currentEnv"
      @refresh="handleParkingLotRefresh"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'
import { useEnvironmentStore } from '../stores/environment'
import { useHistoryStore } from '../stores/history'
import { deviceApi, nodeApi } from '../api/closeApp'
import VehicleManagement from '../components/VehicleManagement.vue'
import PaymentManagement from '../components/PaymentManagement.vue'
import OperationHistory from '../components/OperationHistory.vue'
import StandardTooltip from '@/modules/shared/components/StandardTooltip.vue'
import QrCodeDialog from '../components/QrCodeDialog.vue'
import ParkingLotEditor from '../components/ParkingLotEditor.vue'
import LogMonitor from '@/components/LogMonitor.vue' // Use alias for root src path

const envStore = useEnvironmentStore()
const historyStore = useHistoryStore()
const deviceLoading = ref(false)

// 设备加载状态管理
const deviceLoadingStates = ref<Record<string, boolean>>({})

// 二维码弹窗状态
const qrCodeDialogVisible = ref(false)
const currentQrCodeDevice = ref<any>(null)

// 车场编辑器状态
const parkingLotEditorVisible = ref(false)

// 日志监控卡片可见性
const showLogMonitor = ref(false)

const toggleLogMonitor = () => {
  showLogMonitor.value = !showLogMonitor.value
}

// 组件挂载时加载配置
onMounted(async () => {
  // 清理旧的localStorage数据（迁移到后端配置）
  localStorage.removeItem('yongce-channel-names')

  if (!envStore.configLoaded) {
    await envStore.loadConfig()
  }
  // 启动设备状态轮询
  envStore.startDeviceStatusPolling()
  // 预加载二维码数据
  if (envStore.currentLotId) {
    await envStore.preloadQrCodeData()
  }
})

// 组件卸载时停止轮询
onUnmounted(() => {
  envStore.stopDeviceStatusPolling()
})

// 通道名称相关
const getChannelName = (device: any): string => {
  return envStore.getChannelName(device.ip, device.type)
}

const handleEditChannelName = async (device: any) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入通道名称', '编辑通道名称', {
      inputValue: getChannelName(device),
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })

    const success = await envStore.setChannelName(device.ip, value)
    if (success) {
      ElMessage.success('通道名称更新成功')
    } else {
      ElMessage.error('通道名称更新失败')
    }
  } catch {
    // 用户取消
  }
}

// 获取长抬状态
const getLongLiftStatus = (device: any): string => {
  const channelName = getChannelName(device)
  const node = envStore.nodeStatus.find(item => item.nodeName === channelName)
  return node ? node.status : '0'
}

// 处理长抬状态变更
const handleLongLiftStatusChange = async (device: any, newStatus: string) => {
  if (!envStore.cloudKtToken || !envStore.currentLotId) {
    ElMessage.warning('请先设置云助手Token并选择车场')
    return
  }
  
  const channelName = getChannelName(device)
  const node = envStore.nodeStatus.find(item => item.nodeName === channelName)
  
  if (!node) {
    ElMessage.warning('未在缓存中找到对应的通道节点信息，可能是名称与车场配置不对应或token失效，请检查')
    return
  }
  
  deviceLoadingStates.value[device.ip] = true
  const startTime = Date.now()
  
  try {
    const result = await nodeApi.changeNodeStatus({
      cloud_kt_token: envStore.cloudKtToken,
      lot_id: envStore.currentLotId,
      node_ids: node.nodeId.toString(),
      status: parseInt(newStatus)
    })
    
    if (result.resultCode === 200) {
      ElMessage.success(`通道长抬状态${newStatus === '1' ? '开启' : '关闭'}成功`)
      
      // 刷新节点状态以获取最新数据
      await envStore.fetchNodeStatus()
      
      // 记录操作历史
      const duration = Date.now() - startTime
      historyStore.addHistory({
        operation: '变更通道长抬状态',
        params: {
          channelName: channelName,
          nodeId: node.nodeId,
          oldStatus: node.status,
          newStatus: newStatus,
          lotId: envStore.currentLotId
        },
        result: 'success',
        message: typeof result.data === 'string' ? result.data : JSON.stringify(result.data),
        duration
      })
    } else {
      throw new Error(typeof result.data === 'string' ? result.data : '状态变更失败')
    }
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || error.message || '状态变更失败'
    ElMessage.error(errorMsg)
    
    // 记录操作历史
    const duration = Date.now() - startTime
    historyStore.addHistory({
      operation: '变更通道长抬状态',
      params: {
        channelName: channelName,
        nodeId: node.nodeId,
        oldStatus: node.status,
        newStatus: newStatus,
        lotId: envStore.currentLotId
      },
      result: 'error',
      message: errorMsg,
      duration
    })
  } finally {
    deviceLoadingStates.value[device.ip] = false
  }
}

// 查看二维码
const handleViewQrCode = (device: any) => {
  if (!envStore.currentLotId) {
    ElMessage.warning('请先选择车场')
    return
  }
  
  currentQrCodeDevice.value = device
  qrCodeDialogVisible.value = true
}

// 设置云助手Token
const handleSetCloudToken = async () => {
  try {
    const { value } = await ElMessageBox.prompt('请输入云助手Token（cloud_kt_token）', '设置云助手Token', {
      inputValue: envStore.cloudKtToken,
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入cloud_kt_token'
    })
    envStore.setCloudKtToken(value)
    ElMessage.success('云助手Token已保存')
    // 立即刷新一次节点状态
    await envStore.fetchNodeStatus()
  } catch {
    // 用户取消
  }
}

// 刷新长抬状态
const handleRefreshNodeStatus = async () => {
  if (!envStore.cloudKtToken || !envStore.currentLotId) {
    ElMessage.warning('请先设置云助手Token并选择车场')
    return
  }
  
  const startTime = Date.now()
  
  try {
    // 确保设备状态轮询已启动
    if (!envStore.deviceStatusPolling) {
      envStore.startDeviceStatusPolling()
    }
    
    // 第一步：先执行所有设备的上线接口
    const devices = deviceList.value
    if (devices.length === 0) {
      ElMessage.warning('没有可操作的设备')
      return
    }
    
    const deviceIps = devices.map((d: any) => d.ip).join(',')
    
    // 调用设备上线接口
    const deviceOnResult = await deviceApi.deviceOn({ 
      device_list: deviceIps, 
      server_ip: envStore.serverIp 
    })
    
    if (deviceOnResult.resultCode !== 200) {
      throw new Error(typeof deviceOnResult.data === 'string' ? deviceOnResult.data : '设备上线失败')
    }
    
    // 不再强制更新设备状态为在线，而是等待轮询结果
    ElMessage.info('设备上线操作已执行，正在同步设备状态...')
    
    // 记录设备上线操作历史
    historyStore.addHistory({
      operation: '批量设备上线',
      params: { 
        deviceIps: deviceIps, 
        serverIp: envStore.serverIp,
        operation: 'on'
      },
      result: 'success',
      message: typeof deviceOnResult.data === 'string' ? deviceOnResult.data : JSON.stringify(deviceOnResult.data),
      duration: 0
    })
    
    // 等待一小段时间让设备状态同步
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 第二步：设备上线成功后，再调用查询状态的接口
    const result = await envStore.refreshNodeStatus()
    
    // 检查接口返回结果
    if (result && result.success) {
      ElMessage.success('长抬状态刷新成功')
      
      // 记录刷新长抬状态操作历史
      const duration = Date.now() - startTime
      let message = '接口调用成功'
      if (result.data && Array.isArray(result.data)) {
        // 直接转换为JSON字符串，显示原始内容
        message = JSON.stringify(result.data)
      } else if (result.data) {
        message = typeof result.data === 'string' ? result.data : JSON.stringify(result.data)
      }
      
      historyStore.addHistory({
        operation: '刷新长抬状态',
        params: { 
          lotId: envStore.currentLotId, 
          cloudKtToken: envStore.cloudKtToken,
          deviceIps: deviceIps,
          deviceOnResult: typeof deviceOnResult.data === 'string' ? deviceOnResult.data : JSON.stringify(deviceOnResult.data)
        },
        result: 'success',
        message: message,
        duration
      })
    } else {
      // 接口调用失败
      let errorMsg = '查询通道状态失败'
      
      // 从 result.data 中提取错误信息
      if (result?.data) {
        if (typeof result.data === 'string') {
          errorMsg = result.data
        } else if (result.data.message) {
          errorMsg = result.data.message
        } else if (result.data.error) {
          errorMsg = result.data.error
        } else {
          errorMsg = JSON.stringify(result.data)
        }
      }
      
      ElMessage.error(errorMsg)
      
      // 记录失败的操作历史
      const duration = Date.now() - startTime
      historyStore.addHistory({
        operation: '刷新长抬状态',
        params: { 
          lotId: envStore.currentLotId, 
          cloudKtToken: envStore.cloudKtToken,
          deviceIps: deviceIps,
          deviceOnResult: typeof deviceOnResult.data === 'string' ? deviceOnResult.data : JSON.stringify(deviceOnResult.data)
        },
        result: 'error',
        message: errorMsg,
        duration
      })
    }
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || error.message || '刷新失败'
    ElMessage.error(errorMsg)
    
    // 记录操作历史
    const duration = Date.now() - startTime
    let message = errorMsg
    if (error.response?.data) {
      message = error.response.data.data || error.response.data.message || errorMsg
    }
    
    // 判断是哪个操作失败，记录相应的操作历史
    if (error.message && error.message.includes('设备上线失败')) {
      // 设备上线失败
      historyStore.addHistory({
        operation: '批量设备上线',
        params: { 
          deviceIps: deviceList.value.map((d: any) => d.ip).join(','), 
          serverIp: envStore.serverIp,
          operation: 'on'
        },
        result: 'error',
        message: errorMsg,
        duration: 0
      })
    } else {
      // 刷新长抬状态失败
      historyStore.addHistory({
        operation: '刷新长抬状态',
        params: { 
          lotId: envStore.currentLotId, 
          cloudKtToken: envStore.cloudKtToken,
          error: errorMsg
        },
        result: 'error',
        message: message,
        duration
      })
    }
  }
}

// 环境相关
const currentEnv = computed(() => envStore.currentEnv)
const currentLotId = computed({
  get: () => envStore.currentLotId,
  set: (value: string) => envStore.setLotId(value)
})
const availableLots = computed(() => envStore.availableLots)

// 设备相关
const deviceList = computed(() => {
  const currentLot = envStore.currentLotConfig
  if (!currentLot) return []
  
  return [
    {
      ip: currentLot.inDeviceIp,
      type: 'in' as const,
      status: envStore.deviceStatus.inDevice,
      loading: deviceLoadingStates.value[currentLot.inDeviceIp] || false
    },
    {
      ip: currentLot.outDeviceIp,
      type: 'out' as const,
      status: envStore.deviceStatus.outDevice,
      loading: deviceLoadingStates.value[currentLot.outDeviceIp] || false
    }
  ].filter(device => device.ip)
})

// 环境切换
const handleEnvSwitch = async (env: 'test' | 'prod', event: Event) => {
  event.preventDefault()
  showLogMonitor.value = false // 关闭日志监控
  envStore.setEnvironment(env)
  // 环境切换后预加载通道码缓存
  await envStore.preloadQrCodeData()
}

// 车场切换
const handleLotChange = async (lotId: string) => {
  showLogMonitor.value = false // 关闭日志监控
  envStore.setLotId(lotId)
  // 车场切换后预加载二维码数据
  await envStore.preloadQrCodeData()
}

// 设备操作
const handleDeviceToggle = async (device: any) => {
  if (!device.ip) {
    ElMessage.warning('设备IP不能为空')
    return
  }
  
  deviceLoadingStates.value[device.ip] = true
  try {
    const operation = device.status ? 'off' : 'on'
    const result = device.status 
      ? await deviceApi.deviceOff({ device_list: device.ip, server_ip: envStore.serverIp })
      : await deviceApi.deviceOn({ device_list: device.ip, server_ip: envStore.serverIp })
    
    if (result.resultCode === 200) {
      // 不再直接更新设备状态，而是立即触发一次状态查询以获取真实状态
      const currentLot = envStore.currentLotConfig
      if (currentLot) {
        const ips = []
        if (currentLot.inDeviceIp) ips.push(currentLot.inDeviceIp)
        if (currentLot.outDeviceIp) ips.push(currentLot.outDeviceIp)
        
        if (ips.length > 0) {
          // 立即查询一次设备状态，加速状态收敛
          await envStore.fetchDeviceStatus(ips)
        }
      }
      
      ElMessage.success(`设备${device.status ? '下线' : '上线'}操作已执行，正在同步状态...`)
      
      // 记录操作历史
      historyStore.addHistory({
        operation: `设备${device.status ? '下线' : '上线'}`,
        params: { deviceIp: device.ip, operation },
        result: 'success',
        message: typeof result.data === 'string' ? result.data : JSON.stringify(result.data),
        duration: 0
      })
    } else {
      throw new Error(typeof result.data === 'string' ? result.data : '操作失败')
    }
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || error.message || '操作失败'
    ElMessage.error(errorMsg)
    
    // 记录操作历史
    historyStore.addHistory({
      operation: `设备${device.status ? '下线' : '上线'}`,
      params: { deviceIp: device.ip, operation: device.status ? 'off' : 'on' },
      result: 'error',
      message: errorMsg,
      duration: 0
    })
  } finally {
    deviceLoadingStates.value[device.ip] = false
  }
}

// 批量操作（已隐藏按钮，但逻辑保留以备后续使用）
const handleBatchOn = async () => {
  await handleBatchOperation('on', '上线')
}

const handleBatchOff = async () => {
  await handleBatchOperation('off', '下线')
}

const handleBatchOperation = async (operation: 'on' | 'off', operationName: string) => {
  const devices = deviceList.value
  if (devices.length === 0) {
    ElMessage.warning('没有可操作的设备')
    return
  }
  
  deviceLoading.value = true
  const startTime = Date.now()
  
  try {
    const deviceIps = devices.map((d: any) => d.ip).join(',')
    const result = operation === 'on'
      ? await deviceApi.deviceOn({ device_list: deviceIps, server_ip: envStore.serverIp })
      : await deviceApi.deviceOff({ device_list: deviceIps, server_ip: envStore.serverIp })
    
    if (result.resultCode === 200) {
      // 更新所有设备状态
      devices.forEach((device: any) => {
        if (device.type === 'in') {
          envStore.updateDeviceStatus('inDevice', operation === 'on')
        } else {
          envStore.updateDeviceStatus('outDevice', operation === 'on')
        }
      })
      
      const duration = Date.now() - startTime
      ElMessage.success(`批量${operationName}成功`)
      
      // 记录操作历史
      historyStore.addHistory({
        operation: `批量设备${operationName}`,
        params: { deviceIps, operation },
        result: 'success',
        message: typeof result.data === 'string' ? result.data : JSON.stringify(result.data),
        duration
      })
    } else {
      throw new Error(typeof result.data === 'string' ? result.data : '操作失败')
    }
  } catch (error: any) {
    const duration = Date.now() - startTime
    const errorMsg = error.response?.data?.detail || error.message || '操作失败'
    
    ElMessage.error(errorMsg)
    
    // 记录操作历史
    historyStore.addHistory({
      operation: `批量设备${operationName}`,
      params: { deviceIps: devices.map((d: any) => d.ip).join(','), operation },
      result: 'error',
      message: errorMsg,
      duration
    })
  } finally {
    deviceLoading.value = false
  }
}

// 车场编辑器相关方法
const showParkingLotEditor = () => {
  parkingLotEditorVisible.value = true
}

const handleParkingLotRefresh = async () => {
  console.log('开始刷新主界面配置数据...')
  console.log('刷新前的设备IP:', envStore.currentLotConfig?.inDeviceIp, envStore.currentLotConfig?.outDeviceIp)

  // 强制重新加载配置
  await envStore.loadConfig(true)

  console.log('刷新后的设备IP:', envStore.currentLotConfig?.inDeviceIp, envStore.currentLotConfig?.outDeviceIp)
  ElMessage.success('车场配置已刷新')
}
</script>

<style scoped>
.close-app {
  padding: 20px;
}

/* 顶部配置栏样式 */
.top-config-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
}

.config-section,
.device-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  align-items: center;
}

.config-row {
  display: flex;
  gap: 15px;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.config-header {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  margin-bottom: 12px;
  position: relative;
}

.config-header .section-title {
  margin-bottom: 0;
}

.config-actions {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  margin-left: 145px;
  display: flex;
  gap: 8px;
}

.server-ip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 10px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-size: 12px;
  min-width: 160px;
  justify-content: center;
}

.ip-label {
  color: #6b7280;
  font-weight: 500;
}

.ip-value {
  color: #374151;
  font-weight: 600;
}

.lot-select {
  display: flex;
  justify-content: center;
}

.device-header {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  position: relative;
}

.device-header .section-title {
  margin-bottom: 0;
}

.device-actions {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  margin-left: 220px;
  display: flex;
  gap: 8px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 3px;
  text-align: center;
}

/* 环境切换按钮样式 */
.env-switch {
  display: flex;
  gap: 10px;
}

.env-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
}

.env-button:hover {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.env-button.active {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
}

.env-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.env-icon svg {
  width: 12px;
  height: 12px;
}

.test-icon {
  background-color: #d1fae5;
  color: #065f46;
}

.prod-icon {
  background-color: #fef3c7;
  color: #92400e;
}

.env-button.active .test-icon {
  background-color: #10b981;
  color: white;
}

.env-button.active .prod-icon {
  background-color: #f59e0b;
  color: white;
}

.env-name {
  font-size: 12px;
  font-weight: 500;
}

/* 设备管理样式 */
.device-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.help-icon {
  color: #909399;
  font-size: 12px;
  cursor: help;
  transition: color 0.2s ease;
}

.help-icon:hover {
  color: #606266;
}

.device-name .help-icon {
  font-size: 11px;
  color: #6b7280;
}

.device-status {
  display: flex;
  flex-direction: row;
  gap: 8px;
}

.device-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 8px;
  background: #ffffff;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  flex: 1;
  justify-content: center;
  min-height: 80px;
}

.device-type-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 60px;
}

.device-type {
  font-size: 11px;
  color: #6b7280;
  font-weight: 500;
  min-width: 35px;
  text-align: center;
  padding: 4px 6px;
  background: #f3f4f6;
  border-radius: 3px;
}

.device-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 160px;
  gap: 8px;
}

.device-name {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 4px;
  background: #f8fafc;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
  min-width: 140px;
  justify-content: space-between;
}

.device-name span {
  color: #1f2937;
  font-weight: 500;
}

.device-name .el-button {
  padding: 2px 6px;
  font-size: 11px;
  height: auto;
  line-height: 1.2;
  border: none;
  background: transparent;
  color: #3b82f6;
  transition: all 0.2s ease;
}

.device-name .el-button:hover {
  background: #eff6ff;
  color: #1d4ed8;
  border-radius: 3px;
}

.device-ip {
  font-size: 12px;
  color: #374151;
  min-width: 140px;
  text-align: center;
  background: #ffffff;
  padding: 3px 8px;
  border-radius: 3px;
  border: 1px solid #e5e7eb;
  font-family: 'Courier New', monospace;
  font-weight: 500;
}

.device-buttons {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
  justify-content: center;
  min-width: 80px;
  width: 80px;
  padding: 0;
}

.device-buttons .el-button {
  width: 100%;
  min-width: 70px;
  margin: 0;
  padding: 8px 15px;
  box-sizing: border-box;
}

.long-lift-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  min-width: 80px;
}

.status-label {
  font-size: 11px;
  color: #6b7280;
  font-weight: 500;
}

.status-indicator {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 4px;
  min-width: 50px;
  justify-content: center;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-indicator.online .status-dot {
  background-color: #10b981;
}

.status-indicator.offline .status-dot {
  background-color: #ef4444;
}

.status-text {
  font-size: 10px;
  font-weight: 500;
  text-align: center;
}

.status-indicator.online .status-text {
  color: #065f46;
}

.status-indicator.offline .status-text {
  color: #991b1b;
}

.button-icon {
  width: 12px;
  height: 12px;
  margin-right: 4px;
}

/* 分割线样式 */
.divider {
  width: 1px;
  background-color: #e5e7eb;
  margin: 0 20px;
  align-self: stretch;
}

/* 开关包装器样式 */
.switch-wrapper {
  display: inline-block;
}

/* 离线状态下的开关样式 */
.switch-wrapper .el-switch.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .top-config-bar {
    flex-direction: column;
    gap: 20px;
  }
}
</style> 