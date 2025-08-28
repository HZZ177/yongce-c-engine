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

      <!-- 路段和车位 -->
      <div class="form-row">
        <div class="form-item-container">
          <label class="form-label">路段</label>
          <div class="form-input-container">
            <el-select
              v-model="form.roadCode"
              placeholder="请选择路段"
              style="width: 100%"
              @change="handleRoadChange"
              :loading="loading.roads"
              filterable
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
              filterable
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

      <!-- 计费规则和入场时间 -->
      <div class="form-row">
        <div class="form-item-container">
          <label class="form-label">计费规则</label>
          <div class="form-input-container">
            <span class="fee-rule-display">{{ selectedRoadFeeRule }}</span>
          </div>
        </div>

        <div class="form-item-container">
          <label class="form-label">入场时间</label>
          <div class="form-input-container">
            <el-date-picker
              v-model="form.inTime"
              type="datetime"
              placeholder="不选则默认当前时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              style="width: 100%"
            />
          </div>
        </div>
      </div>

      <!-- 车位状态展示 -->
      <div
        v-if="showParkspaceStatus && (currentRoadParkspaces.length > 0 || loading.parkspaceStatus)"
        class="parkspace-status-container"
        v-loading="loading.parkspaceStatus"
      >
        <div class="parkspace-status-header">
          <h4>{{ getCurrentRoadName() }} - 车位状态</h4>
          <span class="parkspace-count">共 {{ currentRoadParkspaces.length }} 个车位</span>
        </div>
        <div class="parkspace-grid">
          <div
            v-for="parkspace in currentRoadParkspaces"
            :key="parkspace.parkspaceCode"
            class="parkspace-card"
            :class="{ 'occupied': isParkspaceOccupied(parkspace.parkspacePlate) }"
          >
            <div class="parkspace-code">{{ parkspace.parkspaceCode }}</div>
            <div class="parkspace-plate">{{ formatParkspacePlate(parkspace.parkspacePlate) }}</div>
          </div>
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
            @click="handleToggleParkspaceStatus"
            size="default"
            class="action-button"
            :disabled="!form.roadCode"
            :loading="loading.parkspaceStatus"
          >
            {{ showParkspaceStatus ? '隐藏路段车位状态' : '查看路段车位状态' }}
          </el-button>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
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
  RoadInfo,
  ParkspaceInfo
} from '../types'

const envStore = useRoadEnvironmentStore()
const historyStore = useRoadHistoryStore()

// 表单数据
const form = reactive({
  carNo: '',
  plateColor: '蓝',
  carType: CarType.SMALL,
  source: VehicleSource.POS,
  inTime: '',
  roadCode: '',
  parkspaceCode: ''
})

// 加载状态
const loading = reactive({
  carIn: false,
  carOut: false,
  roads: false,
  parkspaces: false,
  parkspaceStatus: false
})

// 路段和车位数据
const roadList = ref<RoadInfo[]>([])
const parkspaceList = ref<ParkspaceInfo[]>([])

// 车位状态展示相关
const showParkspaceStatus = ref(false)
const currentRoadParkspaces = ref<ParkspaceInfo[]>([])

// 常量已通过导入可直接在模板中使用

// 计算属性，用于获取并显示当前选定路段的计费规则名称
const selectedRoadFeeRule = computed(() => {
  if (!form.roadCode) {
    return '请先选择路段';
  }
  const selectedRoad = roadList.value.find(road => road.roadCode === form.roadCode);
  if (selectedRoad && selectedRoad.feeRuleName) {
    return selectedRoad.feeRuleName;
  } else {
    return '暂未配置计费规则';
  }
});

// 加载路段列表
const loadRoadList = async () => {
  if (!envStore.currentLotId) return

  loading.roads = true
  const startTime = Date.now()
  // 加载前先清空旧数据，避免显示上一个环境/车场的路段
  roadList.value = []

  try {
    const params = { lot_id: envStore.currentLotId }
    const result = await roadVehicleApi.roadPage(envStore.currentLotId)
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

    if (handleResult.success && result.data && Array.isArray(result.data.records)) {
      roadList.value = result.data.records

      // 设置默认路段
      setDefaultRoad()
    } else {
      // 如果响应失败，显示错误消息
      ElMessage.error(handleResult.toastMessage)
    }
  } catch (error: any) {
    // 网络错误或其他异常的处理
    const errorResult = ResponseHandler.handleError(error, '加载路段列表失败')

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
const loadParkspaceList = async (roadCode: string, autoShowStatus: boolean = false) => {
  if (!roadCode || !envStore.currentLotId) return

  loading.parkspaces = true
  const startTime = Date.now()
  // 加载前先清空旧数据，避免显示上一个路段/车场的车位
  parkspaceList.value = []
  if (autoShowStatus) {
    // 立刻展开状态卡并显示加载中，避免等待数据返回
    showParkspaceStatus.value = true
    currentRoadParkspaces.value = []
    loading.parkspaceStatus = true
  }

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

      // 设置默认车位
      setDefaultParkspace()

      // 如果需要自动显示车位状态，加载状态数据后结束loading
      if (autoShowStatus) {
        try {
          const statusRes = await roadVehicleApi.parkspacePage(roadCode, envStore.currentLotId)
          const statusHandled = ResponseHandler.handleResponse(statusRes, '', '', false)
          if (statusHandled.success && Array.isArray(statusRes.data)) {
            currentRoadParkspaces.value = statusRes.data
          }
        } finally {
          loading.parkspaceStatus = false
        }
      }
    } else {
      // 如果响应失败，显示错误消息
      ElMessage.error(handleResult.toastMessage)
      if (autoShowStatus) {
        loading.parkspaceStatus = false
      }
    }
  } catch (error: any) {
    // 网络错误或其他异常的处理
    const errorResult = ResponseHandler.handleError(error, '加载车位列表失败')
    // 请求失败时确保清空数据
    parkspaceList.value = []
    if (autoShowStatus) {
      loading.parkspaceStatus = false
    }

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

// 设置默认路段
const setDefaultRoad = async () => {
  if (roadList.value.length === 0) return

  let defaultRoadName = ''
  if (envStore.currentEnv === 'test') {
    defaultRoadName = 'dwb永策路段1'
  } else if (envStore.currentEnv === 'prod') {
    defaultRoadName = '守一路段'
  }

  if (defaultRoadName) {
    const defaultRoad = roadList.value.find(road => road.roadName === defaultRoadName)
    if (defaultRoad) {
      form.roadCode = defaultRoad.roadCode
      // 加载对应的车位列表并自动显示车位状态
      await loadParkspaceList(defaultRoad.roadCode, true)
    }
  }
}

// 设置默认车位
const setDefaultParkspace = () => {
  if (parkspaceList.value.length === 0) return

  let defaultParkspaceCode = ''
  if (envStore.currentEnv === 'test') {
    defaultParkspaceCode = 'GH1'
  } else if (envStore.currentEnv === 'prod') {
    defaultParkspaceCode = '1'
  }

  if (defaultParkspaceCode) {
    const defaultParkspace = parkspaceList.value.find(parkspace => parkspace.parkspaceCode === defaultParkspaceCode)
    if (defaultParkspace) {
      form.parkspaceCode = defaultParkspace.parkspaceCode
    }
  }
}

// 路段变化处理
const handleRoadChange = (roadCode: string) => {
  form.parkspaceCode = '' // 清空车位选择
  parkspaceList.value = [] // 清空车位列表

  if (roadCode) {
    // 无论是否展示状态，都需要刷新可选车位列表
    loadParkspaceList(roadCode)

    // 若当前处于“展开车位状态”，则在切换路段时刷新状态数据；
    // 若当前为收起状态，则保持不动作
    if (showParkspaceStatus.value) {
      loading.parkspaceStatus = true
      loadParkspaceListForStatus(roadCode)
        .finally(() => {
          loading.parkspaceStatus = false
        })
    }
  } else {
    // 清空路段（点X），直接收起车位状态
    showParkspaceStatus.value = false
    currentRoadParkspaces.value = []
  }
}

// 获取当前路段名称
const getCurrentRoadName = (): string => {
  const currentRoad = roadList.value.find(road => road.roadCode === form.roadCode)
  return currentRoad?.roadName || '未知路段'
}

// 判断车位是否被占用
const isParkspaceOccupied = (parkspacePlate?: string): boolean => {
  return parkspacePlate ? !parkspacePlate.includes('无车') : false
}

// 格式化车位车牌信息
const formatParkspacePlate = (parkspacePlate?: string): string => {
  if (!parkspacePlate) return '无车'

  if (parkspacePlate.includes('无车')) {
    return '无车'
  } else if (parkspacePlate.includes('有车(') && parkspacePlate.includes(')')) {
    // 提取括号内的车牌号
    const match = parkspacePlate.match(/有车\((.+?)\)/)
    return match ? match[1] : '有车'
  }

  return parkspacePlate
}

// 切换车位状态显示
const handleToggleParkspaceStatus = async () => {
  if (!form.roadCode) {
    ElMessage.warning('请先选择路段才能查看车位状态')
    return
  }

  if (!showParkspaceStatus.value) {
    // 显示车位状态，需要重新加载车位数据以获取最新状态
    loading.parkspaceStatus = true
    try {
      await loadParkspaceListForStatus(form.roadCode)
      showParkspaceStatus.value = true
    } finally {
      loading.parkspaceStatus = false
    }
  } else {
    // 隐藏车位状态，直接切换状态
    showParkspaceStatus.value = false
  }
}

// 刷新车位状态（静默刷新，不显示loading）
const refreshParkspaceStatus = async () => {
  if (!form.roadCode || !envStore.currentLotId) return

  try {
    const result = await roadVehicleApi.parkspacePage(form.roadCode, envStore.currentLotId)
    const handleResult = ResponseHandler.handleResponse(result, '', '', false)

    if (handleResult.success && Array.isArray(result.data)) {
      currentRoadParkspaces.value = result.data
    }
  } catch (error) {
    // 静默处理错误，不影响用户操作
    console.error('刷新车位状态失败:', error)
  }
}

// 专门为车位状态展示加载车位数据
const loadParkspaceListForStatus = async (roadCode: string) => {
  if (!roadCode || !envStore.currentLotId) return

  const startTime = Date.now()

  try {
    const params = { road_code: roadCode, lot_id: envStore.currentLotId }
    const result = await roadVehicleApi.parkspacePage(roadCode, envStore.currentLotId)
    const handleResult = ResponseHandler.handleResponse(result, '', '加载车位状态失败', false)

    // 记录操作历史
    historyStore.addHistory({
      operation: '查看车位状态',
      params,
      result: handleResult.historyResult,
      message: handleResult.historyMessage,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })

    if (handleResult.success && Array.isArray(result.data)) {
      currentRoadParkspaces.value = result.data
    } else {
      ElMessage.error(handleResult.toastMessage)
      throw new Error(handleResult.toastMessage)
    }
  } catch (error: any) {
    const errorResult = ResponseHandler.handleError(error, '加载车位状态失败')

    historyStore.addHistory({
      operation: '查看车位状态',
      params: { road_code: roadCode, lot_id: envStore.currentLotId },
      result: errorResult.historyResult,
      message: errorResult.message,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })

    console.error('加载车位状态失败:', error)
    throw error // 重新抛出错误，让上层处理
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

    // 重置车位状态显示
    showParkspaceStatus.value = false
    currentRoadParkspaces.value = []

    // 加载新的路段列表
    loadRoadList()
  }
}, { immediate: true })



// 路侧车辆入场
const handleCarIn = async () => {
  if (!envStore.currentLotId) {
    ElMessage.warning('请先选择路侧车场')
    return
  }
  if (!form.roadCode) {
    ElMessage.warning('请先选择路段')
    return
  }
  if (!form.parkspaceCode) {
    ElMessage.warning('请先选择车位')
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
      source: form.source,
      road_code: form.roadCode,
      park_space_code: form.parkspaceCode
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
        source: form.source,
        road_code: form.roadCode,
        park_space_code: form.parkspaceCode
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

    // 如果选择了路段，自动显示并刷新车位状态（无论成功失败还是异常）
    if (form.roadCode) {
      if (!showParkspaceStatus.value) {
        // 如果没有显示车位状态，先显示再刷新
        showParkspaceStatus.value = true
        await loadParkspaceListForStatus(form.roadCode)
      } else {
        // 如果已经显示，直接刷新
        await refreshParkspaceStatus()
      }
    }
  }
}

// 路侧车辆出场
const handleCarOut = async () => {
  if (!envStore.currentLotId) {
    ElMessage.warning('请先选择路侧车场')
    return
  }
  if (!form.roadCode) {
    ElMessage.warning('请先选择路段')
    return
  }
  if (!form.parkspaceCode) {
    ElMessage.warning('请先选择车位')
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
      source: form.source,
      road_code: form.roadCode,
      park_space_code: form.parkspaceCode
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
        source: form.source,
        road_code: form.roadCode,
        park_space_code: form.parkspaceCode
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

    // 如果选择了路段，自动显示并刷新车位状态（无论成功失败还是异常）
    if (form.roadCode) {
      if (!showParkspaceStatus.value) {
        // 如果没有显示车位状态，先显示再刷新
        showParkspaceStatus.value = true
        await loadParkspaceListForStatus(form.roadCode)
      } else {
        // 如果已经显示，直接刷新
        await refreshParkspaceStatus()
      }
    }
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
  flex-direction: row;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #606266;
  margin: 0;
  white-space: nowrap;
  min-width: 4rem;
  text-align: right;
}

.form-input-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
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

/* 计费规则显示样式 */
.fee-rule-display {
  display: inline-block;
  width: 100%;
  height: 32px; /* 匹配 Element Plus 默认输入框高度 */
  line-height: 32px;
  padding: 0 11px;
  font-size: 0.875rem;
  color: #606266; /* 类似禁用文本的颜色 */
  background-color: #f5f7fa; /* 类似禁用输入框的背景色 */
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-sizing: border-box;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 车位状态展示样式 */
.parkspace-status-container {
  margin: 1rem 0;
  padding: 1rem;
  background-color: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

.parkspace-status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.parkspace-status-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.parkspace-count {
  font-size: 0.875rem;
  color: #6b7280;
}

.parkspace-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 0.5rem;
}

.parkspace-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 0.25rem;
  background-color: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
  min-height: 60px;
  justify-content: center;
}

.parkspace-card.occupied {
  border-color: #ef4444;
  background-color: #fef2f2;
}

.parkspace-card:not(.occupied) {
  border-color: #22c55e;
  background-color: #f0fdf4;
}

.parkspace-code {
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
}

.parkspace-plate {
  font-size: 0.725rem; /* 放大车牌字体 */
  color: #6b7280;
  text-align: center;
  line-height: 1.2;
  word-break: break-all;
  margin-top: 2px;           /* 让分隔线更靠近上方“车位” */
  padding-top: 2px;
  position: relative;        /* 供伪元素定位使用 */
  width: 100%;               /* 占据整张卡片的宽度，分隔线长度固定为卡片宽度 */
  align-self: stretch;       /* 在flex容器中拉伸到整宽 */
}

/* 分隔线：略微加长（穿过卡片内边距），并上移一点 */
.parkspace-plate::before {
  content: '';
  position: absolute;
  top: -2px;                 /* 相对上移一点 */
  left: 4px;                 /* 固定长度：相对卡片左右各留出内边距 */
  right: 4px;
  height: 1px;
  background-color: rgba(0, 0, 0, 0.12);
  border-radius: 1px;
}

.parkspace-card.occupied .parkspace-plate {
  color: #dc2626;
  font-weight: 500;
}
.parkspace-card.occupied .parkspace-plate::before {
  background-color: rgba(220, 38, 38, 0.25); /* 占用时分隔线颜色 */
}

.parkspace-card:not(.occupied) .parkspace-plate {
  color: #16a34a;
}
.parkspace-card:not(.occupied) .parkspace-plate::before {
  background-color: rgba(22, 163, 74, 0.25); /* 空闲时分隔线颜色 */
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
