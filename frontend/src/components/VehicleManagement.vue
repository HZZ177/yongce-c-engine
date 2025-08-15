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
    
    <div class="vehicle-form-container">
      <!-- 车牌号和车辆颜色 -->
      <div class="form-row">
        <div class="form-item-container">
          <label class="form-label">车牌号</label>
          <div class="form-input-container">
            <el-input 
              v-model="form.carNo" 
              placeholder="不填视为无牌车"
              style="width: 100%"
            />
          </div>
        </div>
        
        <div class="form-item-container">
          <label class="form-label">车辆颜色</label>
          <div class="form-input-container">
            <el-select v-model="form.carColor" placeholder="请选择车辆颜色" style="width: 100%">
              <el-option label="白色" :value="1" />
              <el-option label="黑色" :value="2" />
              <el-option label="蓝色" :value="3" />
              <el-option label="黄色" :value="4" />
              <el-option label="绿色" :value="5" />
            </el-select>
          </div>
        </div>
      </div>
      
      <!-- 识别度和序列号 -->
      <div class="form-row">
        <div class="form-item-container">
          <label class="form-label">识别度</label>
          <div class="form-input-container">
            <el-input 
              v-model="form.recognition" 
              placeholder="请输入识别度，如：1000"
              style="width: 100%"
            />
          </div>
        </div>
        
        <div class="form-item-container">
          <label class="form-label">序列号</label>
          <div class="form-input-container">
            <el-input 
              v-model="form.iSerial" 
              placeholder="请输入序列号"
              style="width: 100%"
            />
          </div>
        </div>
      </div>
      
      <!-- 入场模式 -->
      <div class="form-item-container">
        <label class="form-label">入场模式</label>
        <div class="form-input-container">
          <el-radio-group v-model="form.inOpenType">
            <el-radio :label="0">压地感</el-radio>
            <el-radio :label="1">相机直接开闸放行</el-radio>
          </el-radio-group>
        </div>
      </div>
      
      <!-- 出场模式 -->
      <div class="form-item-container">
        <label class="form-label">出场模式</label>
        <div class="form-input-container">
          <el-radio-group v-model="form.outOpenType">
            <el-radio :label="0">压地感</el-radio>
            <el-radio :label="1">相机直接开闸放行</el-radio>
          </el-radio-group>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="form-buttons-container">
        <div class="action-buttons">
          <el-button 
            type="primary" 
            @click="handleCarIn" 
            :loading="loading.carIn"
            size="default"
            class="action-button"
          >
            车辆入场
          </el-button>
          <el-button 
            type="success" 
            @click="handleCarOut" 
            :loading="loading.carOut"
            size="default"
            class="action-button"
          >
            车辆出场
          </el-button>
          <el-button 
            type="info" 
            @click="handleQueryOnPark" 
            :loading="loading.query"
            size="default"
            class="action-button"
          >
            查询在场(当天)
          </el-button>
        </div>
      </div>
    </div>
    
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
  recognition: 900,
  iSerial: '' as string,
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
  // 车辆入场不需要车牌号必填，不填视为无牌车
  
  loading.carIn = true
  const startTime = Date.now()
  
  try {
    const params: any = {
      car_no: form.carNo,
      i_open_type: form.inOpenType, // 使用用户选择的入场模式
      server_ip: envStore.serverIp,
      lot_id: envStore.currentLotId,
      car_color: form.carColor,
      recognition: form.recognition
    }
    
    // 只有当序列号有有效值时才包含该字段
    if (form.iSerial && form.iSerial.trim() !== '' && !isNaN(Number(form.iSerial))) {
      params.i_serial = form.iSerial
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
      throw new Error(result.resultMsg || '入场失败')
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
    
    // 车辆入场后自动查询在场状态（无论成功失败）
    await performQueryOnPark(form.carNo, true)
  }
}

// 车辆出场
const handleCarOut = async () => {
  // 车辆出场不需要车牌号必填，不填视为无牌车
  
  loading.carOut = true
  const startTime = Date.now()
  
  try {
    const params: any = {
      car_no: form.carNo,
      i_open_type: form.outOpenType, // 使用用户选择的出场模式
      server_ip: envStore.serverIp,
      lot_id: envStore.currentLotId,
      car_color: form.carColor,
      recognition: form.recognition
    }
    
    // 只有当序列号有有效值时才包含该字段
    if (form.iSerial && form.iSerial.trim() !== '' && !isNaN(Number(form.iSerial))) {
      params.i_serial = form.iSerial
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
      throw new Error(result.resultMsg || '出场失败')
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
  
  await performQueryOnPark(form.carNo, false)
}

// 执行查询在场车辆（支持自动查询模式）
const performQueryOnPark = async (carNo: string, autoQuery: boolean = false) => {
  if (!carNo) {
    // 无牌车跳过查询，销毁查询结果窗口
    queryResult.value = null
    return
  }
  
  if (!autoQuery) {
    loading.query = true
  }
  
  const startTime = Date.now()
  
  try {
    const params = {
      lot_id: envStore.currentLotId,
      car_no: carNo,
      start_time: '',
      end_time: ''
    }
    
    const result = await vehicleApi.carOnPark(params)
    const duration = Date.now() - startTime
    
    if (result.resultCode === 200) {
      const data = result.data
      // 处理嵌套的数据结构：result.data.data.vos
      const vos = data.data?.vos || data.vos || []
      
      queryResult.value = {
        carNo: carNo,
        isOnPark: vos.length > 0,
        comeTime: vos[0]?.comeTime || '',
        duration: vos[0]?.strandedTime || '' // 使用正确的字段名 strandedTime
      }
      
      if (!autoQuery) {
        ElMessage.success('查询成功')
      }
      
      // 记录操作历史
      historyStore.addHistory({
        operation: '查询在场车辆',
        params: { carNo: carNo, ...params },
        result: 'success',
        message: `查询到${vos.length}条记录`,
        duration
      })
    } else {
      throw new Error(result.resultMsg || '查询失败')
    }
  } catch (error: any) {
    const duration = Date.now() - startTime
    const errorMsg = error.response?.data?.detail || error.message || '查询失败'
    
    if (!autoQuery) {
      ElMessage.error(errorMsg)
    }
    
    // 记录操作历史
    historyStore.addHistory({
      operation: '查询在场车辆',
      params: { carNo: carNo },
      result: 'error',
      message: errorMsg,
      duration
    })
  } finally {
    if (!autoQuery) {
      loading.query = false
    }
  }
}
</script>

<style scoped>
.vehicle-management {
  margin-bottom: 1.5rem;
  min-height: 500px; /* 最低高度为500px */
}

.vehicle-form-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
}

.form-row {
  display: flex;
  gap: 1rem;
  width: 100%;
  max-width: 600px;
  align-items: flex-start; /* 确保行内元素顶部对齐 */
}

.form-item-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.form-label {
  font-size: 0.875rem;
  color: #606266;
  font-weight: 500;
  margin: 0;
  white-space: nowrap; /* 防止文字换行 */
  min-width: 4rem; /* 统一标签最小宽度 */
  text-align: right; /* 标签右对齐 */
}

.required {
  color: #f56c6c;
  margin-left: 0.25rem;
  font-size: 0.75rem;
}

.form-input-container {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.form-buttons-container {
  display: flex;
  justify-content: center;
  width: 100%;
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