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
          <div class="query-group">
            <el-button
              type="info"
              @click="handleQueryOnPark"
              :loading="loading.query"
              size="default"
              class="action-button"
            >
              查询在场(不选日期默认当天)
            </el-button>
            <div class="date-picker-wrapper">
              <el-button
                ref="dateIconButtonRef"
                type="text"
                size="small"
                class="date-icon-button"
                :class="{ 'has-date': hasCustomDate }"
                :title="hasCustomDate ? '已选择日期范围' : '选择日期范围'"
                @click="showDateRangePicker"
              >
                <div class="date-icon-container">
                  <el-icon class="date-icon">
                    <Calendar />
                  </el-icon>
                  <el-icon v-if="hasCustomDate" class="check-icon">
                    <Check />
                  </el-icon>
                </div>
              </el-button>

              <!-- 日期范围选择下拉面板 -->
              <div
                ref="dateRangePanelRef"
                v-show="showDateRangePanel"
                class="date-range-panel"
                @click.stop
              >
                <div class="date-range-panel-content">
                  <div class="date-picker-container">
                    <el-date-picker
                      v-model="tempDateRange"
                      type="datetimerange"
                      range-separator="至"
                      start-placeholder="开始日期时间"
                      end-placeholder="结束日期时间"
                      format="YYYY-MM-DD HH:mm:ss"
                      value-format="YYYY-MM-DD HH:mm:ss"
                      style="width: 100%"
                      locale="zh-cn"
                      :default-time="[
                        new Date(2000, 1, 1, 0, 0, 0),
                        new Date(2000, 1, 1, 23, 59, 59)
                      ]"
                    />
                  </div>
                  <div class="panel-footer">
                    <el-button size="small" @click="clearDateRange">清除</el-button>
                    <el-button size="small" type="primary" @click="confirmDateRange">确定</el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <el-button
            type="warning"
            @click="showLogMonitorDialog = true"
            size="default"
            class="action-button"
          >
            日志监控
          </el-button>
        </div>
      </div>
    </div>



    <!-- 日志监控弹窗 -->
    <el-dialog
      v-model="showLogMonitorDialog"
      title="实时日志监控"
      width="70%"
      :destroy-on-close="true"
    >
      <LogMonitor :lot-id="envStore.currentLotId" v-if="showLogMonitorDialog" />
    </el-dialog>

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
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import LogMonitor from './LogMonitor.vue'
import { ElMessage } from 'element-plus'
import { useEnvironmentStore } from '@/stores/environment'
import { useHistoryStore } from '@/stores/history'
import { vehicleApi } from '@/api/closeApp'
import { Calendar, Check } from '@element-plus/icons-vue'

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

// 日期选择相关状态
const dateRange = ref<[Date, Date] | null>(null)
const tempDateRange = ref<[Date, Date] | null>(null)
const hasCustomDate = ref(false)
const showDateRangePanel = ref(false)

// 模板引用
const dateIconButtonRef = ref()
const dateRangePanelRef = ref()

// 日志监控相关状态
const showLogMonitorDialog = ref(false)

// 车辆入场
const handleCarIn = async () => {
  // 车辆入场不需要车牌号必填，不填视为无牌车
  
  loading.carIn = true
  const startTime = Date.now()
  const isUnlicensed = !form.carNo || form.carNo.trim() === ''
  
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
      ElMessage.success(isUnlicensed ? '发送成功' : '车辆入场成功')
      
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
    
    ElMessage.error(isUnlicensed ? '发送失败' : errorMsg)
    
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
  const isUnlicensed = !form.carNo || form.carNo.trim() === ''
  
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
      ElMessage.success(isUnlicensed ? '发送成功' : '车辆出场成功')
      
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
    
    ElMessage.error(isUnlicensed ? '发送失败' : errorMsg)
    
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

// 显示日期范围选择器
const showDateRangePicker = () => {
  tempDateRange.value = dateRange.value ? [...dateRange.value] : null
  showDateRangePanel.value = true
}

// 确认日期范围选择
const confirmDateRange = () => {
  if (tempDateRange.value && tempDateRange.value.length === 2) {
    dateRange.value = tempDateRange.value
    hasCustomDate.value = true
    showDateRangePanel.value = false
    ElMessage.success('日期范围已设置')
  } else {
    ElMessage.warning('请选择日期范围')
  }
}

// 清除日期范围
const clearDateRange = () => {
  tempDateRange.value = null
  dateRange.value = null
  hasCustomDate.value = false
  showDateRangePanel.value = false
  ElMessage.info('日期范围已清除')
}

// 点击外部关闭面板
const handleClickOutside = (event: Event) => {
  if (!showDateRangePanel.value) return

  const target = event.target as Element
  const panel = dateRangePanelRef.value?.$el || dateRangePanelRef.value
  const button = dateIconButtonRef.value?.$el || dateIconButtonRef.value

  // 检查是否点击了面板内部或按钮
  if (panel && panel.contains(target)) return
  if (button && button.contains(target)) return

  // 检查是否点击了 Element Plus 日期选择器的弹出层
  const datePickerPopups = document.querySelectorAll('.el-picker__popper, .el-popper, .el-date-picker__time-header')
  for (const popup of datePickerPopups) {
    if (popup && popup.contains(target)) return
  }

  // 如果都不是，则关闭面板
  showDateRangePanel.value = false
}

// 组件挂载时添加事件监听
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

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
    const params: any = {
      lot_id: envStore.currentLotId,
      car_no: carNo
    }
    
    // 如果选择了自定义日期范围，添加时间参数
    if (hasCustomDate.value && dateRange.value && dateRange.value.length === 2) {
      const [startDate, endDate] = dateRange.value
      params.start_time = startDate
      params.end_time = endDate
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
  align-items: center;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

/* 查询按钮和日期按钮的组合样式 */
.query-group {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.date-picker-wrapper {
  position: relative;
  display: inline-flex;
}

.date-icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  background-color: #f0f2f5;
  border: 1px solid #d1d5db;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 0.25rem;
  padding: 0;
}

.date-icon-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.date-icon {
  width: 1.25rem !important;
  height: 1.25rem !important;
  font-size: 1.25rem !important;
}

.check-icon {
  position: absolute;
  bottom: -0.125rem;
  right: -0.125rem;
  width: 0.75rem;
  height: 0.75rem;
  color: #10b981;
  background-color: #fff;
  border-radius: 50%;
  padding: 0.125rem;
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

/* 日期选择相关样式 */
.date-icon-button:hover {
  background-color: #e0e3e7;
  border-color: #9ca3af;
}

.date-icon-button.has-date {
  background-color: #f0f9ff;
  border-color: #0ea5e9;
}

.date-icon-button.has-date:hover {
  background-color: #e0f2fe;
  border-color: #0284c7;
}

/* 日期范围下拉面板样式 */
.date-range-panel {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 1000;
  margin-top: 0.5rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  min-width: 400px;
}

.date-range-panel-content {
  padding: 1.25rem;
}

.date-picker-container {
  margin-bottom: 1rem;
}

.panel-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #f3f4f6;
}


</style> 