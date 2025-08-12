<template>
  <el-card class="device-management" shadow="hover">
    <!-- 第一行：设备管理标题 -->
    <div class="title-row">
          <h3 class="card-title">设备管理</h3>
    </div>
    
    <!-- 第二行：副标题 -->
    <div class="subtitle-row">
          <p class="card-subtitle">管理停车场设备的连接状态</p>
        </div>
    
    <!-- 第三行：批量操作按钮 -->
    <div class="button-row">
          <el-button type="primary" @click="handleBatchOn" :loading="loading" size="default">
            <svg class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            批量上线
          </el-button>
          <el-button type="danger" @click="handleBatchOff" :loading="loading" size="default">
            <svg class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
            批量下线
          </el-button>
        </div>
    
    <!-- 最下方：设备信息展示区域 -->
    <div class="device-info-section">
    <el-table :data="deviceList" style="width: 100%" v-loading="loading">
      <el-table-column prop="ip" label="设备IP" width="180" />
      <el-table-column prop="type" label="设备类型" width="120">
        <template #default="{ row }">
          <el-tag :type="row.type === 'in' ? 'primary' : 'success'">
            {{ row.type === 'in' ? '入口设备' : '出口设备' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <div class="status-indicator" :class="row.status ? 'online' : 'offline'">
            <div class="status-dot"></div>
            <span class="status-text">{{ row.status ? '在线' : '离线' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button 
            :type="row.status ? 'danger' : 'primary'"
            size="small"
            @click="handleDeviceToggle(row)"
            :loading="row.loading"
            class="action-button"
          >
            <svg v-if="!row.loading" class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path v-if="row.status" d="M18 6L6 18M6 6l12 12"/>
              <path v-else d="M12 5v14M5 12h14"/>
            </svg>
            {{ row.status ? '下线' : '上线' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useEnvironmentStore } from '@/stores/environment'
import { useHistoryStore } from '@/stores/history'
import { deviceApi } from '@/api/closeApp'
import type { DeviceInfo } from '@/types'

const envStore = useEnvironmentStore()
const historyStore = useHistoryStore()

const loading = ref(false)

// 设备列表
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
  ].filter(device => device.ip) // 过滤掉空IP的设备
})

// 单个设备操作
const handleDeviceToggle = async (device: DeviceInfo & { loading: boolean }) => {
  if (!device.ip) {
    ElMessage.warning('设备IP为空，无法操作')
    return
  }
  
  device.loading = true
  const startTime = Date.now()
  
  try {
    const params = {
      device_list: device.ip,
      server_ip: envStore.serverIp
    }
    
    const api = device.status ? deviceApi.deviceOff : deviceApi.deviceOn
    const result = await api(params)
    
    const duration = Date.now() - startTime
    
    if (result.resultCode === 200) {
      // 更新设备状态
      envStore.updateDeviceStatus(
        device.type === 'in' ? 'inDevice' : 'outDevice',
        !device.status
      )
      
      ElMessage.success(`${device.status ? '下线' : '上线'}成功`)
      
      // 记录操作历史
      historyStore.addHistory({
        operation: `设备${device.status ? '下线' : '上线'}`,
        params: { deviceIp: device.ip, deviceType: device.type },
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
      operation: `设备${device.status ? '下线' : '上线'}`,
      params: { deviceIp: device.ip, deviceType: device.type },
      result: 'error',
      message: errorMsg,
      duration
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
  
  loading.value = true
  const startTime = Date.now()
  
  try {
    const deviceIps = devices.map(d => d.ip).join(',')
    const params = {
      device_list: deviceIps,
      server_ip: envStore.serverIp
    }
    
    const api = operation === 'on' ? deviceApi.deviceOn : deviceApi.deviceOff
    const result = await api(params)
    
    const duration = Date.now() - startTime
    
    if (result.resultCode === 200) {
      // 更新所有设备状态
      devices.forEach(device => {
        envStore.updateDeviceStatus(
          device.type === 'in' ? 'inDevice' : 'outDevice',
          operation === 'on'
        )
      })
      
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
      params: { deviceIps: devices.map(d => d.ip).join(','), operation },
      result: 'error',
      message: errorMsg,
      duration
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 初始化时重置设备状态
  envStore.resetDeviceStatus()
})
</script>

<style scoped>
.device-management {
  margin-bottom: 1.5rem;
}

.title-row {
  margin-bottom: 0.25rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.subtitle-row {
  margin-bottom: 1rem;
}

.card-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.button-row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.button-icon {
  width: 1rem;
  height: 1rem;
  margin-right: 0.25rem;
}

.device-info-section {
  /* Add any specific styles for the device info section if needed */
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.status-indicator.online .status-dot {
  background-color: #10b981;
}

.status-indicator.offline .status-dot {
  background-color: #ef4444;
}

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.status-indicator.online .status-text {
  color: #065f46;
}

.status-indicator.offline .status-text {
  color: #991b1b;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.action-button .button-icon {
  width: 0.875rem;
  height: 0.875rem;
  margin-right: 0;
}
</style> 