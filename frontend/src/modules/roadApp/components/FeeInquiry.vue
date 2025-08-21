<template>
  <el-card class="fee-inquiry" :class="{ 'has-results': !!queryResult }" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-content">
          <h3 class="card-title">路侧车场管理</h3>
          <p class="card-subtitle">管理路侧车场的车辆信息和在场情况</p>
        </div>

      </div>
    </template>
    
    <div class="fee-form-container">
      <div class="fee-params">
      <!-- 输入参数 -->
      <div class="form-row">
        <div class="form-item-container">
          <label class="form-label">车牌号</label>
          <div class="form-input-container">
            <el-input
              v-model="form.carNo"
              placeholder="请输入车牌号"
              style="width: 100%"
            />
          </div>
        </div>

        <div class="form-item-container">
          <label class="form-label">车辆类型</label>
          <div class="form-input-container">
            <el-select
              v-model="form.carType"
              placeholder="请选择车辆类型"
              style="width: 100%"
              clearable
            >
              <el-option
                v-for="type in CAR_TYPE_OPTIONS"
                :key="type.value"
                :label="type.label"
                :value="type.value"
              />
            </el-select>
          </div>
        </div>
      </div>

      <div class="form-item-container">
        <label class="form-label">路段</label>
        <div class="form-input-container">
          <el-select
            v-model="form.roadCode"
            placeholder="请选择路段"
            style="width: 100%"
            @change="handleRoadChange"
            :loading="loading.roads"
            clearable
          >
            <el-option
              v-for="road in roadList"
              :key="road.roadCode"
              :label="road.roadName"
              :value="road.roadCode"
            />
          </el-select>
        </div>
      </div>

      <div class="form-item-container">
        <label class="form-label">车位</label>
        <div class="form-input-container">
          <el-select
            v-model="form.parkspaceCode"
            placeholder="请选择车位"
            style="width: 100%"
            :loading="loading.parkspaces"
            :disabled="!form.roadCode"
            clearable
          >
            <el-option
              v-for="parkspace in parkspaceList"
              :key="parkspace.parkspaceCode"
              :label="parkspace.parkspaceCode"
              :value="parkspace.parkspaceCode"
            />
          </el-select>
        </div>
      </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="form-buttons-container">
        <div class="action-buttons">
          <el-button
            type="primary"
            @click="handlePresentCarInfoQuery"
            :loading="loading.query"
            size="default"
            class="action-button"
            :disabled="!envStore.currentLotId"
          >
            查询在场车信息
          </el-button>
        </div>
      </div>


    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoadEnvironmentStore } from '../stores/environment'
import { useRoadHistoryStore } from '../stores/history'
import { roadVehicleApi } from '../api/roadApp'
import { ResponseHandler } from '@/modules/shared/utils'
import {
  CAR_TYPE_OPTIONS
} from '../types'
import type {
  RoadPresentCarInfoRequest,
  RoadInfo,
  ParkspaceInfo
} from '../types'

// 定义事件
const emit = defineEmits<{
  queryResult: [result: any]
}>()

const envStore = useRoadEnvironmentStore()
const historyStore = useRoadHistoryStore()

// 表单数据
const form = reactive({
  carNo: '',
  carType: null as number | null,
  parkspaceCode: '',
  roadCode: ''
})

// 加载状态
const loading = reactive({
  query: false,
  roads: false,
  parkspaces: false
})

// 查询结果
const queryResult = ref<any>(null)

// 路段和车位数据
const roadList = ref<RoadInfo[]>([])
const parkspaceList = ref<ParkspaceInfo[]>([])

// 加载路段列表
const loadRoadList = async () => {
  if (!envStore.currentLotId) return

  loading.roads = true
  const startTime = Date.now()
  // 进入加载前先清空旧数据，避免显示上一个环境/车场的数据
  roadList.value = []

  try {
    const params = { lot_id: envStore.currentLotId }
    const result = await roadVehicleApi.roadList(envStore.currentLotId)
    const handleResult = ResponseHandler.handleResponse(result, '', '加载路段列表失败', false)

    // 记录操作历史
    historyStore.addHistory({
      operation: '加载路段列表',
      params,
      result: handleResult.historyResult,
      message: handleResult.historyMessage,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })

    if (handleResult.success && Array.isArray(result.data)) {
      roadList.value = result.data

      // 不再自动设置默认路段，让用户手动选择
    } else {
      // 如果响应失败，显示错误消息
      ElMessage.error(handleResult.toastMessage)
    }
  } catch (error: any) {
    // 网络错误或其他异常的处理
    const errorResult = ResponseHandler.handleError(error, '加载路段列表失败')
    // 请求失败时确保清空数据
    roadList.value = []

    // 记录网络错误历史
    historyStore.addHistory({
      operation: '加载路段列表',
      params: { lot_id: envStore.currentLotId },
      result: errorResult.historyResult,
      message: errorResult.message,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })

    console.error('加载路段列表失败:', error)
  } finally {
    loading.roads = false
  }
}

// 加载车位列表
const loadParkspaceList = async (roadCode: string) => {
  if (!roadCode || !envStore.currentLotId) return

  loading.parkspaces = true
  const startTime = Date.now()
  // 加载前先清空旧数据，避免显示上一个路段/车场的车位
  parkspaceList.value = []

  try {
    const params = { road_code: roadCode, lot_id: envStore.currentLotId }
    const result = await roadVehicleApi.parkspacePage(roadCode, envStore.currentLotId)
    const handleResult = ResponseHandler.handleResponse(result, '', '加载车位列表失败', false)

    // 记录操作历史
    historyStore.addHistory({
      operation: '加载车位列表',
      params,
      result: handleResult.historyResult,
      message: handleResult.historyMessage,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })

    if (handleResult.success && Array.isArray(result.data)) {
      parkspaceList.value = result.data

      // 不再自动设置默认车位，让用户手动选择
    } else {
      // 如果响应失败，显示错误消息
      ElMessage.error(handleResult.toastMessage)
    }
  } catch (error: any) {
    // 网络错误或其他异常的处理
    const errorResult = ResponseHandler.handleError(error, '加载车位列表失败')
    // 请求失败时确保清空数据
    parkspaceList.value = []

    // 记录网络错误历史
    historyStore.addHistory({
      operation: '加载车位列表',
      params: { road_code: roadCode, lot_id: envStore.currentLotId },
      result: errorResult.historyResult,
      message: errorResult.message,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })

    console.error('加载车位列表失败:', error)
  } finally {
    loading.parkspaces = false
  }
}



// 路段变化处理
const handleRoadChange = (roadCode: string) => {
  form.parkspaceCode = '' // 清空车位选择
  parkspaceList.value = [] // 清空车位列表

  if (roadCode) {
    loadParkspaceList(roadCode)
  }
}

// 监听环境和车场变化
watch(() => envStore.currentLotId, (newLotId) => {
  if (newLotId) {
    // 重置表单中的路段和车位
    form.roadCode = ''
    form.parkspaceCode = ''
    // 清空下拉数据，避免残留上一个环境/车场的数据
    roadList.value = []
    parkspaceList.value = []
    // 清空本组件的查询结果，收起底部提示箭头
    queryResult.value = null

    // 加载新的路段列表
    loadRoadList()
  }
}, { immediate: true })

// 查询在场车信息
const handlePresentCarInfoQuery = async () => {
  if (!envStore.currentLotId) {
    ElMessage.warning('请先选择路侧车场')
    return
  }

  loading.query = true
  const startTime = Date.now()

  try {
    const params: RoadPresentCarInfoRequest = {
      car_no: (form.carNo || '').trim(),
      lot_id: envStore.currentLotId,
      car_type: form.carType?.toString() || '',
      parkspace_code: (form.parkspaceCode || '').trim(),
      plate_color: '', // 不传递颜色字段，使用空字符串
      road_code: (form.roadCode || '').trim()
    }

    const result = await roadVehicleApi.presentCarInfo(params)

    // 使用统一的响应处理
    const handleResult = ResponseHandler.handleResponse(
      result,
      '查询在场车信息成功',
      '查询在场车信息失败'
    )

    if (handleResult.success) {
      queryResult.value = result
      // 向父组件发送查询结果
      emit('queryResult', result)
    } else {
      queryResult.value = null
      // 查询失败时清空结果
      emit('queryResult', null)
    }

    // 记录操作历史
    historyStore.addHistory({
      operation: '查询在场车信息',
      params,
      result: handleResult.historyResult,
      message: handleResult.historyMessage,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })

  } catch (error: any) {
    // 网络错误或其他异常的处理
    const errorResult = ResponseHandler.handleError(error, '查询在场车信息失败')
    queryResult.value = null

    // 记录网络错误历史
    historyStore.addHistory({
      operation: '查询在场车信息',
      params: {
        car_no: form.carNo,
        lot_id: envStore.currentLotId,
        car_type: form.carType?.toString() || '',
        parkspace_code: form.parkspaceCode,
        road_code: form.roadCode
      },
      result: errorResult.historyResult,
      message: errorResult.message,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })
  } finally {
    loading.query = false
  }
}


</script>

<style scoped>
.fee-inquiry {
  margin-bottom: 1.5rem;
  position: relative;
  overflow: visible;
}

.card-header {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.header-content {
  text-align: center;
}

.card-title {
  margin: 0 0 0.25rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.card-subtitle {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}



/* 有查询结果时的卡片样式 */
.fee-inquiry.has-results {
  border-bottom: 2px solid #3b82f6;
  position: relative;
}

.fee-inquiry.has-results::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 12px solid transparent; /* 原 8px -> 12px */
  border-right: 12px solid transparent; /* 原 8px -> 12px */
  border-bottom: 12px solid #3b82f6; /* 原 8px -> 12px */
}

.fee-form-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 参数区容器：用于在等高卡片中垂直居中显示参数区域 */
.fee-params {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  flex: 1;
  justify-content: center; /* 垂直居中参数区域 */
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-item-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-input-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-buttons-container {
  margin-top: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.action-button {
  min-width: 120px;
}



.result-header {
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.result-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.result-value {
  font-size: 0.875rem;
  color: #1f2937;
}

.vehicle-list {
  margin-top: 1rem;
}

.vehicle-item {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background-color: white;
  border-radius: 0.375rem;
  border: 1px solid #d1d5db;
}

.vehicle-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.vehicle-no {
  font-weight: 600;
  color: #1f2937;
}

.vehicle-detail {
  font-size: 0.875rem;
  color: #6b7280;
}

.vehicle-time {
  font-size: 0.875rem;
  color: #9ca3af;
}

.result-info {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 0.375rem;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  overflow-x: auto;
}

.result-summary {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
}

.no-data {
  text-align: center;
  padding: 3rem 1rem;
  color: #9ca3af;
}

.no-data-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-data-text {
  font-size: 1rem;
  color: #6b7280;
}



@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
  }


}
</style>
