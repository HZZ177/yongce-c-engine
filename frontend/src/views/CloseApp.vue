<template>
  <div class="close-app">
    <!-- 顶部配置栏 - 融合环境配置和设备管理 -->
    <div class="top-config-bar">
      <div class="config-section">
        <!-- 第一行：标题和服务器IP -->
        <div class="config-header">
          <div class="section-title">环境配置</div>
          <div class="server-ip">
            <span class="ip-label">服务器IP:</span>
            <span class="ip-value">{{ envStore.serverIp }}</span>
          </div>
        </div>
        
        <!-- 第二行：环境按钮和车场选择 -->
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
              <span class="env-name">生产环境</span>
            </button>
          </div>
          
          <div class="lot-select">
            <el-select 
              v-model="currentLotId" 
              placeholder="请选择车场"
              @change="handleLotChange"
              style="width: 200px"
              :loading="envStore.configLoading"
              :disabled="envStore.configLoading || availableLots.length === 0"
              size="small"
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
        <!-- 第一行：标题和批量按钮 -->
        <div class="device-header">
          <div class="section-title">设备管理</div>
          <div class="device-actions">
            <el-button type="primary" @click="handleBatchOn" :loading="deviceLoading" size="small">
              <svg class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12h14"/>
              </svg>
              批量上线
            </el-button>
            <el-button type="danger" @click="handleBatchOff" :loading="deviceLoading" size="small">
              <svg class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
              批量下线
            </el-button>
          </div>
        </div>
        
        <!-- 第二行：设备状态 -->
        <div class="device-status">
          <div v-for="device in deviceList" :key="device.ip" class="device-item">
            <span class="device-ip">{{ device.ip }}</span>
            <div class="status-indicator" :class="device.status ? 'online' : 'offline'">
              <div class="status-dot"></div>
              <span class="status-text">{{ device.status ? '在线' : '离线' }}</span>
            </div>
            <el-button 
              :type="device.status ? 'danger' : 'primary'"
              size="small"
              @click="handleDeviceToggle(device)"
              :loading="device.loading"
            >
              {{ device.status ? '下线' : '上线' }}
            </el-button>
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
        <VehicleManagement />
          </el-col>
          <el-col :span="12">
        <PaymentManagement />
      </el-col>
        </el-row>
      
        <!-- 操作历史 - 移到最下方 -->
        <OperationHistory />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useEnvironmentStore } from '@/stores/environment'
import { useHistoryStore } from '@/stores/history'
import { deviceApi } from '@/api/closeApp'
import VehicleManagement from '@/components/VehicleManagement.vue'
import PaymentManagement from '@/components/PaymentManagement.vue'
import OperationHistory from '@/components/OperationHistory.vue'

const envStore = useEnvironmentStore()
const historyStore = useHistoryStore()
const deviceLoading = ref(false)

// 组件挂载时加载配置
onMounted(async () => {
  if (!envStore.configLoaded) {
    await envStore.loadConfig()
  }
})

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
      loading: false
    },
    {
      ip: currentLot.outDeviceIp,
      type: 'out' as const,
      status: envStore.deviceStatus.outDevice,
      loading: false
    }
  ].filter(device => device.ip)
})

// 环境切换
const handleEnvSwitch = async (env: 'test' | 'prod', event: Event) => {
  event.preventDefault()
  envStore.setEnvironment(env)
}

// 车场切换
const handleLotChange = (lotId: string) => {
  envStore.setLotId(lotId)
}

// 设备操作
const handleDeviceToggle = async (device: any) => {
  if (!device.ip) {
    ElMessage.warning('设备IP不能为空')
    return
  }
  
  device.loading = true
  try {
    const operation = device.status ? 'off' : 'on'
    const result = device.status 
      ? await deviceApi.deviceOff({ device_list: device.ip, server_ip: envStore.serverIp })
      : await deviceApi.deviceOn({ device_list: device.ip, server_ip: envStore.serverIp })
    
    if (result.resultCode === 200) {
      // 更新设备状态
      if (device.type === 'in') {
        envStore.updateDeviceStatus('inDevice', !device.status)
      } else {
        envStore.updateDeviceStatus('outDevice', !device.status)
      }
      
      ElMessage.success(`设备${device.status ? '下线' : '上线'}成功`)
      
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
    device.loading = false
  }
}

// 批量操作
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
}

.config-header {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  margin-bottom: 8px;
  position: relative;
}

.config-header .section-title {
  margin-bottom: 0;
}

.server-ip {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  margin-left: 120px;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 10px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-size: 12px;
}

.ip-label {
  color: #6b7280;
  font-weight: 500;
}

.ip-value {
  color: #374151;
  font-weight: 600;
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
  margin-left: 140px;
  display: flex;
  gap: 8px;
}

.section-title {
  font-size: 14px;
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
  padding: 6px 8px;
  background: #ffffff;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  flex: 1;
  justify-content: center;
}

.device-ip {
  font-size: 12px;
  color: #374151;
  min-width: 120px;
  text-align: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
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
  font-size: 11px;
  font-weight: 500;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .top-config-bar {
    flex-direction: column;
    gap: 20px;
  }
}
</style> 