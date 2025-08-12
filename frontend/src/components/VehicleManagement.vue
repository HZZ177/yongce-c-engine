<template>
  <el-card class="vehicle-management" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-content">
          <h3 class="card-title">车辆管理</h3>
          <p class="card-subtitle">管理车辆的入场、出场和查询操作</p>
        </div>
      </div>
    </template>
    
    <el-form :model="form" label-width="120px" size="default">
      <!-- 车牌号输入 -->
      <el-form-item label="车牌号" required>
        <el-input 
          v-model="form.carNo" 
          placeholder="请输入车牌号，如：川A12345"
          style="width: 300px"
        />
      </el-form-item>
      
      <!-- 车辆颜色 -->
      <el-form-item label="车辆颜色">
        <el-select v-model="form.carColor" placeholder="请选择车辆颜色" style="width: 200px">
          <el-option label="白色" :value="1" />
          <el-option label="黑色" :value="2" />
          <el-option label="蓝色" :value="3" />
          <el-option label="黄色" :value="4" />
          <el-option label="绿色" :value="5" />
        </el-select>
      </el-form-item>
      
      <!-- 识别度 -->
      <el-form-item label="识别度">
        <el-input 
          v-model="form.recognition" 
          placeholder="请输入识别度，如：1000"
          style="width: 200px"
        />
      </el-form-item>
      
      <!-- 序列号 -->
      <el-form-item label="序列号">
        <el-input 
          v-model="form.iSerial" 
          placeholder="请输入序列号"
          style="width: 200px"
        />
      </el-form-item>
      
      <!-- 入场模式 -->
      <el-form-item label="入场模式">
        <el-radio-group v-model="form.inOpenType">
          <el-radio :label="0">压地感</el-radio>
          <el-radio :label="1">相机直接开闸放行</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <!-- 出场模式 -->
      <el-form-item label="出场模式">
        <el-radio-group v-model="form.outOpenType">
          <el-radio :label="0">压地感</el-radio>
          <el-radio :label="1">相机直接开闸放行</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <!-- 操作按钮 -->
      <el-form-item>
        <div class="action-buttons">
          <el-button 
            type="primary" 
            @click="handleCarIn" 
            :loading="loading.carIn"
            size="default"
            class="action-button"
          >
            <svg v-if="!loading.carIn" class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            车辆入场
          </el-button>
          <el-button 
            type="warning" 
            @click="handleCarOut" 
            :loading="loading.carOut"
            size="default"
            class="action-button"
          >
            <svg v-if="!loading.carOut" class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
            车辆出场
          </el-button>
          <el-button 
            type="info" 
            @click="handleQueryOnPark" 
            :loading="loading.query"
            size="default"
            class="action-button"
          >
            <svg v-if="!loading.query" class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            查询在场
          </el-button>
        </div>
      </el-form-item>
    </el-form>
    
    <!-- 查询结果 -->
    <div v-if="queryResult" class="query-result">
      <div class="result-header">
        <h4 class="result-title">查询结果</h4>
      </div>
      <div class="result-content">
        <div class="result-item">
          <span class="result-label">车牌号</span>
          <span class="result-value">{{ queryResult.carNo }}</span>
        </div>
        <div class="result-item">
          <span class="result-label">在场状态</span>
          <div class="status-indicator" :class="queryResult.isOnPark ? 'online' : 'offline'">
            <div class="status-dot"></div>
            <span class="status-text">{{ queryResult.isOnPark ? '在场' : '不在场' }}</span>
          </div>
        </div>
        <div class="result-item" v-if="queryResult.comeTime">
          <span class="result-label">入场时间</span>
          <span class="result-value">{{ queryResult.comeTime }}</span>
        </div>
        <div class="result-item" v-if="queryResult.duration">
          <span class="result-label">停车时长</span>
          <span class="result-value">{{ queryResult.duration }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useEnvironmentStore } from '@/stores/environment'
import { useHistoryStore } from '@/stores/history'
import { vehicleApi } from '@/api/closeApp'

const envStore = useEnvironmentStore()
const historyStore = useHistoryStore()

// 表单数据
const form = reactive({
  carNo: '',
  carColor: 3,
  recognition: 1000,
  iSerial: undefined as number | undefined,
  inOpenType: 1, // 入场模式：1-相机直接开闸放行
  outOpenType: 0 // 出场模式：0-压地感
})

// 加载状态
const loading = reactive({
  carIn: false,
  carOut: false,
  query: false
})

// 查询结果
const queryResult = ref<any>(null)

// 车辆入场
const handleCarIn = async () => {
  if (!form.carNo) {
    ElMessage.warning('请输入车牌号')
    return
  }
  
  loading.carIn = true
  const startTime = Date.now()
  
  try {
    const params = {
      car_no: form.carNo,
      i_open_type: form.inOpenType, // 使用用户选择的入场模式
      server_ip: envStore.serverIp,
      lot_id: envStore.currentLotId,
      car_color: form.carColor,
      recognition: form.recognition,
      i_serial: form.iSerial
    }
    
    const result = await vehicleApi.carIn(params)
    const duration = Date.now() - startTime
    
    if (result.resultCode === 200) {
      ElMessage.success('车辆入场成功')
      
      // 记录操作历史
      historyStore.addHistory({
        operation: `车辆入场(${form.inOpenType === 0 ? '压地感' : '相机直接开闸放行'})`,
        params: { carNo: form.carNo, ...params },
        result: 'success',
        message: typeof result.data === 'string' ? result.data : JSON.stringify(result.data),
        duration
      })
    } else {
      throw new Error(typeof result.data === 'string' ? result.data : '入场失败')
    }
  } catch (error: any) {
    const duration = Date.now() - startTime
    const errorMsg = error.response?.data?.detail || error.message || '入场失败'
    
    ElMessage.error(errorMsg)
    
    // 记录操作历史
    historyStore.addHistory({
      operation: `车辆入场(${form.inOpenType === 0 ? '压地感' : '相机直接开闸放行'})`,
      params: { carNo: form.carNo },
      result: 'error',
      message: errorMsg,
      duration
    })
  } finally {
    loading.carIn = false
  }
}

// 车辆出场
const handleCarOut = async () => {
  if (!form.carNo) {
    ElMessage.warning('请输入车牌号')
    return
  }
  
  loading.carOut = true
  const startTime = Date.now()
  
  try {
    const params = {
      car_no: form.carNo,
      i_open_type: form.outOpenType, // 使用用户选择的出场模式
      server_ip: envStore.serverIp,
      lot_id: envStore.currentLotId,
      car_color: form.carColor,
      recognition: form.recognition,
      i_serial: form.iSerial
    }
    
    const result = await vehicleApi.carOut(params)
    const duration = Date.now() - startTime
    
    if (result.resultCode === 200) {
      ElMessage.success('车辆出场成功')
      
      // 记录操作历史
      historyStore.addHistory({
        operation: `车辆出场(${form.outOpenType === 0 ? '压地感' : '相机直接开闸放行'})`,
        params: { carNo: form.carNo, ...params },
        result: 'success',
        message: typeof result.data === 'string' ? result.data : JSON.stringify(result.data),
        duration
      })
    } else {
      throw new Error(typeof result.data === 'string' ? result.data : '出场失败')
    }
  } catch (error: any) {
    const duration = Date.now() - startTime
    const errorMsg = error.response?.data?.detail || error.message || '出场失败'
    
    ElMessage.error(errorMsg)
    
    // 记录操作历史
    historyStore.addHistory({
      operation: `车辆出场(${form.outOpenType === 0 ? '压地感' : '相机直接开闸放行'})`,
      params: { carNo: form.carNo },
      result: 'error',
      message: errorMsg,
      duration
    })
  } finally {
    loading.carOut = false
  }
}

// 查询在场车辆
const handleQueryOnPark = async () => {
  if (!form.carNo) {
    ElMessage.warning('请输入车牌号')
    return
  }
  
  loading.query = true
  const startTime = Date.now()
  
  try {
    const params = {
      lot_id: envStore.currentLotId,
      car_no: form.carNo,
      start_time: '',
      end_time: ''
    }
    
    const result = await vehicleApi.carOnPark(params)
    const duration = Date.now() - startTime
    
    if (result.resultCode === 200) {
      const data = result.data
      const vos = data.vos || []
      
      queryResult.value = {
        carNo: form.carNo,
        isOnPark: vos.length > 0,
        comeTime: vos[0]?.comeTime || '',
        duration: vos[0]?.duration || ''
      }
      
      ElMessage.success('查询成功')
      
      // 记录操作历史
      historyStore.addHistory({
        operation: '查询在场车辆',
        params: { carNo: form.carNo, ...params },
        result: 'success',
        message: `查询到${vos.length}条记录`,
        duration
      })
    } else {
      throw new Error(typeof result.data === 'string' ? result.data : '查询失败')
    }
  } catch (error: any) {
    const duration = Date.now() - startTime
    const errorMsg = error.response?.data?.detail || error.message || '查询失败'
    
    ElMessage.error(errorMsg)
    
    // 记录操作历史
    historyStore.addHistory({
      operation: '查询在场车辆',
      params: { carNo: form.carNo },
      result: 'error',
      message: errorMsg,
      duration
    })
  } finally {
    loading.query = false
  }
}
</script>

<style scoped>
.vehicle-management {
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: center;
  align-items: center;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  text-align: center;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.card-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.button-icon {
  width: 1rem;
  height: 1rem;
}

.query-result {
  margin-top: 1.5rem;
  padding: 1.25rem;
  background-color: #f9fafb;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
}

.result-header {
  margin-bottom: 1rem;
}

.result-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.result-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.result-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.result-value {
  font-size: 0.875rem;
  color: #111827;
  font-weight: 500;
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
  background-color: #6b7280;
}

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.status-indicator.online .status-text {
  color: #065f46;
}

.status-indicator.offline .status-text {
  color: #6b7280;
}

/* 模式选择样式优化 */
.el-radio-group {
  display: flex;
  gap: 1rem;
}

.el-radio {
  margin-right: 0;
}

.el-radio__label {
  font-size: 0.875rem;
}
</style> 