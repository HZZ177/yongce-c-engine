<template>
  <!-- 查询结果展示卡片 -->
  <el-card v-if="queryResult" class="query-results-card">
    <template #header>
      <div class="card-header">

        <div class="header-content">
          <h3 class="card-title">在场车信息查询结果</h3>
          <div class="result-summary">
            共找到 {{ vehicleList.length }} 辆车辆
          </div>
        </div>
      </div>
    </template>

    <!-- 无数据提示 -->
    <div v-if="vehicleList.length === 0" class="no-data">
      <div class="no-data-icon">🚗</div>
      <div class="no-data-text">暂无在场车辆信息</div>
    </div>

    <!-- 车辆信息卡片列表 -->
    <div v-else class="vehicle-cards-container">
      <div class="vehicle-cards-grid">
        <div 
          v-for="vehicle in paginatedVehicles" 
          :key="vehicle.parkingRecordId || vehicle.carNo"
          class="vehicle-card"
        >
          <div class="vehicle-card-header">
            <div class="car-no">{{ vehicle.carNo || '未知车牌' }}</div>
            <div class="car-type" :class="getCarTypeClass(vehicle.carType)">{{ getCarTypeText(vehicle.carType) }}</div>
          </div>
          
          <div class="vehicle-card-body">
            <div class="info-row">
              <span class="info-label">停车场：</span>
              <span class="info-value">{{ vehicle.parkName || '未知停车场' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">路段：</span>
              <span class="info-value">{{ vehicle.roadName || '未知路段' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">车位：</span>
              <span class="info-value">{{ vehicle.parkspaceCode || '未知车位' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">入场时间：</span>
              <span class="info-value">{{ vehicle.inTime || '未知时间' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">车牌颜色：</span>
              <span class="info-value">{{ vehicle.plateColor || '未知颜色' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">停车记录ID：</span>
              <span class="info-value record-id">{{ vehicle.parkingRecordId || '无' }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 分页组件 -->
      <div v-if="totalPages > 1" class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="vehicleList.length"
          layout="prev, pager, next, jumper"
          @current-change="handlePageChange"
          small
        />
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Props
interface Props {
  queryResult?: any
}

const props = defineProps<Props>()

// 分页相关
const currentPage = ref(1)
const pageSize = ref(8) // 每页显示8个卡片

// 车辆列表（从查询结果中提取）
const vehicleList = computed(() => {
  if (!props.queryResult) {
    return []
  }
  
  // 处理嵌套的响应格式：queryResult.data.data
  let data = props.queryResult.data
  
  // 如果data是对象且包含data字段，则进一步提取
  if (data && typeof data === 'object' && data.data) {
    data = data.data
  }
  
  return Array.isArray(data) ? data : []
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(vehicleList.value.length / pageSize.value)
})

// 当前页的车辆数据
const paginatedVehicles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return vehicleList.value.slice(start, end)
})

// 分页处理
const handlePageChange = (page: number) => {
  currentPage.value = page
}

// 车辆类型映射
const getCarTypeText = (carType: number): string => {
  const carTypeMap: Record<number, string> = {
    0: '小型车',
    1: '中型车',
    2: '大型车',
    3: '新能源车',
    4: '特殊车辆',
    5: '非机动车',
    6: '摩托车',
    7: '三轮车',
    8: '新能源货车'
  }
  return carTypeMap[carType] || '未知类型'
}

// 车辆类型颜色样式映射
const getCarTypeClass = (carType: number): string => {
  const carTypeClassMap: Record<number, string> = {
    0: 'car-type-small',      // 小型车 - 蓝色
    1: 'car-type-medium',     // 中型车 - 橙色
    2: 'car-type-large',      // 大型车 - 红色
    3: 'car-type-new-energy', // 新能源车 - 绿色
    4: 'car-type-special',    // 特殊车辆 - 紫色
    5: 'car-type-non-motor',  // 非机动车 - 青色
    6: 'car-type-motorcycle', // 摩托车 - 黄色
    7: 'car-type-tricycle',   // 三轮车 - 棕色
    8: 'car-type-new-truck'   // 新能源货车 - 深绿色
  }
  return carTypeClassMap[carType] || 'car-type-unknown'
}
</script>

<style scoped>
.query-results-card {
  margin-top: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-top: 2px solid #3b82f6;
  position: relative;
}

.query-results-card::before {
  content: '';
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid #3b82f6;
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
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.result-summary {
  font-size: 0.875rem;
  color: #6b7280;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.no-data-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-data-text {
  font-size: 1rem;
  color: #6b7280;
}

.vehicle-cards-container {
  margin-top: 1rem;
}

.vehicle-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
  justify-items: center;
}

.vehicle-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 320px;
}

.vehicle-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.car-no {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.car-type {
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 500;
  color: white;
}

/* 车辆类型颜色样式 - 根据车牌颜色设计 */
.car-type-small {
  background-color: #2563eb; /* 蓝色 - 小型车(蓝牌) */
}

.car-type-medium {
  background-color: #dc2626; /* 红色 - 中型车 */
}

.car-type-large {
  background-color: #eab308; /* 黄色 - 大型车(黄牌) */
}

.car-type-new-energy {
  background-color: #16a34a; /* 绿色 - 新能源车(绿牌) */
}

.car-type-special {
  background-color: #7c3aed; /* 紫色 - 特殊车辆 */
}

.car-type-non-motor {
  background-color: #0891b2; /* 青色 - 非机动车 */
}

.car-type-motorcycle {
  background-color: #ea580c; /* 橙色 - 摩托车 */
}

.car-type-tricycle {
  background-color: #78716c; /* 棕色 - 三轮车 */
}

.car-type-new-truck {
  background-color: #059669; /* 深绿色 - 新能源货车(绿牌系) */
}

.car-type-unknown {
  background-color: #6b7280; /* 灰色 - 未知类型 */
}

.vehicle-card-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.info-value {
  font-size: 0.875rem;
  color: #1f2937;
  font-weight: 500;
}

.info-value.record-id {
  font-family: monospace;
  font-size: 0.75rem;
  color: #6b7280;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
}

@media (max-width: 768px) {
  .vehicle-cards-grid {
    grid-template-columns: 1fr;
  }
  
  .vehicle-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
