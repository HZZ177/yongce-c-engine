<template>
  <el-card class="vehicle-management" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-content">
          <h3 class="card-title">路侧车辆管理</h3>
          <p class="card-subtitle">管理路侧车辆的入场、出场和查询操作</p>
        </div>
      </div>
    </template>
    
    <div class="vehicle-form-container">
      <!-- 车牌号和车牌颜色 -->
      <div class="form-row">
        <div class="form-item-container">
          <label class="form-label">车牌号</label>
          <div class="form-input-container">
            <el-input
              v-model="form.carNo"
              placeholder="可以填写 空车牌/未登记 作为车牌"
              style="width: 100%"
            />
          </div>
        </div>

        <div class="form-item-container">
          <label class="form-label">车牌颜色</label>
          <div class="form-input-container">
            <el-select v-model="form.plateColor" placeholder="请选择车牌颜色" style="width: 100%">
              <el-option
                v-for="color in PLATE_COLORS"
                :key="color.value"
                :label="color.label"
                :value="color.value"
              />
            </el-select>
          </div>
        </div>
      </div>

      <!-- 车辆类型和车辆来源 -->
      <div class="form-row">
        <div class="form-item-container">
          <label class="form-label">车辆类型</label>
          <div class="form-input-container">
            <el-select v-model="form.carType" placeholder="请选择车辆类型" style="width: 100%">
              <el-option
                v-for="type in CAR_TYPE_OPTIONS"
                :key="type.value"
                :label="type.label"
                :value="type.value"
              />
            </el-select>
          </div>
        </div>

        <div class="form-item-container">
          <label class="form-label">车辆来源</label>
          <div class="form-input-container">
            <el-select v-model="form.source" placeholder="请选择车辆来源" style="width: 100%">
              <el-option
                v-for="source in VEHICLE_SOURCE_OPTIONS"
                :key="source.value"
                :label="source.label"
                :value="source.value"
              />
            </el-select>
          </div>
        </div>
      </div>

      <!-- 入场时间 -->
      <div class="form-item-container">
        <label class="form-label">入场时间</label>
        <div class="form-input-container">
          <el-date-picker
            v-model="form.inTime"
            type="datetime"
            placeholder="选择入场时间（可选，默认当前时间）"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
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
            :disabled="!envStore.currentLotId"
          >
            车辆入场
          </el-button>
          <el-button
            type="success"
            @click="handleCarOut"
            :loading="loading.carOut"
            size="default"
            class="action-button"
            :disabled="!envStore.currentLotId"
          >
            车辆出场
          </el-button>
          <el-button
            type="info"
            @click="handleQueryOnPark"
            :loading="loading.query"
            size="default"
            class="action-button"
            :disabled="!envStore.currentLotId"
          >
            车辆在场情况查询
          </el-button>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoadEnvironmentStore } from '../stores/environment'
import { useRoadHistoryStore } from '../stores/history'
import { roadVehicleApi } from '../api/roadApp'
import { ResponseHandler } from '@/modules/shared/utils'
import {
  CarType,
  VehicleSource,
  PLATE_COLORS,
  CAR_TYPE_OPTIONS,
  VEHICLE_SOURCE_OPTIONS
} from '../types'
import type {
  RoadCarInOutRequest,
  RoadCarOnParkRequest
} from '../types'

const envStore = useRoadEnvironmentStore()
const historyStore = useRoadHistoryStore()

// 表单数据
const form = reactive({
  carNo: '',
  plateColor: '蓝',
  carType: CarType.SMALL,
  source: VehicleSource.POS,
  inTime: ''
})

// 加载状态
const loading = reactive({
  carIn: false,
  carOut: false,
  query: false
})

// 常量已通过导入可直接在模板中使用

// 路侧车辆入场
const handleCarIn = async () => {
  if (!envStore.currentLotId) {
    ElMessage.warning('请先选择路侧车场')
    return
  }

  loading.carIn = true
  const startTime = Date.now()

  try {
    const params: RoadCarInOutRequest = {
      lot_id: envStore.currentLotId,
      car_no: form.carNo,
      car_type: form.carType,
      plate_color: form.plateColor,
      in_time: form.inTime || new Date().toLocaleString('sv-SE').replace('T', ' '),
      source: form.source
    }

    const result = await roadVehicleApi.carIn(params)

    // 使用统一的响应处理
    const handleResult = ResponseHandler.handleResponse(result, '路侧车辆入场成功', '路侧车辆入场失败')

    // 记录操作历史（无论成功失败都记录一次）
    historyStore.addHistory({
      operation: '路侧车辆入场',
      params,
      result: handleResult.historyResult,
      message: handleResult.historyMessage,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })

    // 如果失败，不需要再抛出异常，因为已经处理过了
  } catch (error: any) {
    // 网络错误或其他异常的处理
    const errorResult = ResponseHandler.handleError(error, '路侧车辆入场失败')

    // 记录网络错误历史
    historyStore.addHistory({
      operation: '路侧车辆入场',
      params: {
        lot_id: envStore.currentLotId,
        car_no: form.carNo,
        car_type: form.carType,
        plate_color: form.plateColor,
        source: form.source
      },
      result: errorResult.historyResult,
      message: errorResult.message,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })
  } finally {
    loading.carIn = false
  }
}

// 路侧车辆出场
const handleCarOut = async () => {
  if (!envStore.currentLotId) {
    ElMessage.warning('请先选择路侧车场')
    return
  }

  loading.carOut = true
  const startTime = Date.now()

  try {
    const params: RoadCarInOutRequest = {
      lot_id: envStore.currentLotId,
      car_no: form.carNo,
      car_type: form.carType,
      plate_color: form.plateColor,
      in_time: form.inTime || new Date().toLocaleString('sv-SE').replace('T', ' '),
      source: form.source
    }

    const result = await roadVehicleApi.carOut(params)

    // 使用统一的响应处理
    const handleResult = ResponseHandler.handleResponse(result, '路侧车辆出场成功', '路侧车辆出场失败')

    // 记录操作历史（无论成功失败都记录一次）
    historyStore.addHistory({
      operation: '路侧车辆出场',
      params,
      result: handleResult.historyResult,
      message: handleResult.historyMessage,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })

    // 如果失败，不需要再抛出异常，因为已经处理过了
  } catch (error: any) {
    // 网络错误或其他异常的处理
    const errorResult = ResponseHandler.handleError(error, '路侧车辆出场失败')

    // 记录网络错误历史
    historyStore.addHistory({
      operation: '路侧车辆出场',
      params: {
        lot_id: envStore.currentLotId,
        car_no: form.carNo,
        car_type: form.carType,
        plate_color: form.plateColor,
        source: form.source
      },
      result: errorResult.historyResult,
      message: errorResult.message,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })
  } finally {
    loading.carOut = false
  }
}

// 查询路侧在场车辆
const handleQueryOnPark = async () => {
  if (!envStore.currentLotId) {
    ElMessage.warning('请先选择路侧车场')
    return
  }

  if (!form.carNo.trim()) {
    ElMessage.warning('请输入车牌号')
    return
  }

  loading.query = true
  const startTime = Date.now()

  try {
    const params: RoadCarOnParkRequest = {
      lot_id: envStore.currentLotId,
      car_no: form.carNo
    }

    const result = await roadVehicleApi.carOnPark(params)

    // 处理查询结果，优先使用业务逻辑消息
    let customSuccessMessage = ''
    if (ResponseHandler.isSuccess(result)) {
      const vehicles = result.data?.vos || []
      customSuccessMessage = vehicles.length > 0
        ? `查询到 ${vehicles.length} 辆路侧在场车辆`
        : '未查询到路侧在场车辆'
    }

    // 使用统一的响应处理，但优先使用自定义消息
    const handleResult = ResponseHandler.handleResponse(
      result,
      customSuccessMessage || '查询路侧在场车辆成功',
      '查询路侧在场车辆失败'
    )

    // 记录操作历史（无论成功失败都记录一次）
    historyStore.addHistory({
      operation: '查询路侧在场车辆',
      params,
      result: handleResult.historyResult,
      message: handleResult.historyMessage,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })

    // 如果失败，不需要再抛出异常，因为已经处理过了
  } catch (error: any) {
    // 网络错误或其他异常的处理
    const errorResult = ResponseHandler.handleError(error, '查询路侧在场车辆失败')

    // 记录网络错误历史
    historyStore.addHistory({
      operation: '查询路侧在场车辆',
      params: { car_no: form.carNo },
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
/* 复用封闭车场的样式 */
.vehicle-management {
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: center;
  align-items: center;
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

.vehicle-form-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
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
