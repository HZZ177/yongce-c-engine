<template>
  <div class="road-app">
    <!-- 顶部配置栏 - 路侧环境配置 -->
    <div class="top-config-bar">
      <div class="config-section">
        <!-- 第一行：标题 -->
        <div class="config-header">
          <div class="section-title">路侧环境配置</div>
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

        <!-- 第三行：车场选择 -->
        <div class="config-row">
          <div class="lot-select">
            <el-select
              v-model="currentLotId"
              placeholder="请选择路侧车场"
              @change="handleLotChange"
              style="width: 300px"
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
    </div>

    <!-- 功能区域 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <!-- 车辆管理和查费管理 - 同一行平分宽度 -->
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="12">
            <VehicleManagement />
          </el-col>
          <el-col :span="12">
            <FeeInquiry />
          </el-col>
        </el-row>

        <!-- 操作历史 - 移到最下方 -->
        <OperationHistory />
      </el-col>
    </el-row>

    <!-- 路侧车场编辑器 -->
    <RoadParkingLotEditor
      v-model="parkingLotEditorVisible"
      :current-env="envStore.currentEnv"
      @refresh="handleParkingLotRefresh"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'
import { useRoadEnvironmentStore } from '../stores/environment'
import VehicleManagement from '../components/VehicleManagement.vue'
import FeeInquiry from '../components/FeeInquiry.vue'
import OperationHistory from '../components/OperationHistory.vue'
import RoadParkingLotEditor from '../components/RoadParkingLotEditor.vue'
import type { Environment } from '../types'

const envStore = useRoadEnvironmentStore()

// 计算属性
const currentEnv = computed(() => envStore.currentEnv)
const currentLotId = computed({
  get: () => envStore.currentLotId,
  set: (value) => envStore.setCurrentLotId(value)
})
const availableLots = computed(() => envStore.availableLots)

// 车场编辑器状态
const parkingLotEditorVisible = ref(false)

// 环境切换
const handleEnvSwitch = (env: Environment, event: Event) => {
  event.preventDefault()
  envStore.setEnvironment(env)
}

// 车场切换
const handleLotChange = (lotId: string) => {
  envStore.setCurrentLotId(lotId)
}

// 车场编辑器相关方法
const showParkingLotEditor = () => {
  parkingLotEditorVisible.value = true
}

const handleParkingLotRefresh = async () => {
  console.log('开始刷新路侧车场配置数据...')

  // 强制重新加载配置
  await envStore.loadConfig()

  console.log('路侧车场配置数据刷新完成')
  ElMessage.success('路侧车场配置已刷新')
}

// 组件挂载时初始化
onMounted(async () => {
  await envStore.loadConfig()
})
</script>

<style scoped>
/* 复用封闭车场的样式，但添加路侧特有的标识 */
.road-app {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  min-height: 100vh;
}

.top-config-bar {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 15px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  max-width: 800px;
}

.config-header {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  margin-bottom: 12px;
  position: relative;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.config-actions {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  margin-left: 120px;
  display: flex;
  gap: 8px;
}

.config-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  width: 100%;
}

.env-switch {
  display: flex;
  gap: 8px;
}

.env-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
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

.lot-select {
  display: flex;
  justify-content: center;
}



/* 移除旧的布局样式，使用Element Plus的栅格系统 */

@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
