<template>
  <el-card class="environment-config" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <h3 class="card-title">环境配置</h3>
          <p class="card-subtitle">选择测试环境或生产环境</p>
        </div>
        <div class="header-right">
          <div class="env-status">
            <div class="status-dot" :class="currentEnv === 'test' ? 'test' : 'prod'"></div>
            <span class="status-text">{{ currentEnv === 'test' ? '测试环境' : '生产环境' }}</span>
          </div>
        </div>
      </div>
    </template>
    
    <el-form :model="form" size="default">
      <!-- 环境选择 -->
      <el-form-item>
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
            <div class="env-content">
              <span class="env-name">测试环境</span>
            </div>
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
            <div class="env-content">
              <span class="env-name">生产环境</span>
            </div>
          </button>
        </div>
      </el-form-item>
      
      <!-- 车场选择 -->
      <el-form-item label="车场选择">
        <el-select 
          v-model="currentLotId" 
          placeholder="请选择车场"
          @change="handleLotChange"
          style="width: 100%"
          :loading="envStore.configLoading"
          :disabled="envStore.configLoading || availableLots.length === 0"
        >
          <el-option
            v-for="lot in availableLots"
            :key="lot.id"
            :label="`${lot.name} (${lot.id})`"
            :value="lot.id"
          />
        </el-select>
        <div v-if="envStore.configLoaded && !envStore.configLoading && availableLots.length === 0" class="config-error">
          <el-alert
            title="配置加载失败"
            description="无法获取车场配置信息，请检查后端服务是否正常运行"
            type="error"
            :closable="false"
            show-icon
          />
        </div>
      </el-form-item>
      
      <!-- 服务器信息 -->
      <el-form-item label="服务器IP">
        <el-input v-model="serverIp" readonly>
          <template #append>
            <el-tag type="info">自动获取</el-tag>
          </template>
        </el-input>
      </el-form-item>
      

    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useEnvironmentStore } from '@/stores/environment'

const envStore = useEnvironmentStore()

// 组件挂载时加载配置
onMounted(async () => {
  if (!envStore.configLoaded) {
    await envStore.loadConfig()
  }
})

// 表单数据
const form = computed(() => ({
  env: envStore.currentEnv,
  lotId: envStore.currentLotId
}))

// 计算属性
const currentEnv = computed({
  get: () => envStore.currentEnv,
  set: (value) => envStore.setEnvironment(value)
})

const currentLotId = computed({
  get: () => envStore.currentLotId,
  set: (value) => envStore.setLotId(value)
})

const serverIp = computed(() => envStore.serverIp)
const availableLots = computed(() => envStore.availableLots)

// 事件处理
const handleEnvSwitch = (env: 'test' | 'prod', event?: Event) => {
  // 阻止默认行为，防止页面刷新
  if (event) {
    event.preventDefault()
  }
  console.log('环境切换:', env)
  envStore.setEnvironment(env)
}

const handleLotChange = (lotId: string) => {
  console.log('车场切换:', lotId)
}
</script>

<style scoped>
.environment-config {
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
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

.env-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background-color: #f3f4f6;
  border-radius: 0.5rem;
}

.status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.status-dot.test {
  background-color: #10b981;
}

.status-dot.prod {
  background-color: #f59e0b;
}

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}



/* 环境切换按钮样式 */
.env-switch {
  display: flex;
  gap: 1rem;
  justify-content: center;
  width: 100%;
}

.env-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background-color: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 160px;
}

.env-button:hover {
  border-color: #3b82f6;
  background-color: #eff6ff;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1);
}

.env-button.active {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2);
}

.env-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  flex-shrink: 0;
}

.env-icon svg {
  width: 1.25rem;
  height: 1.25rem;
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

.env-content {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  text-align: left;
}

.env-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.env-desc {
  font-size: 0.75rem;
  color: #6b7280;
}

.config-error {
  margin-top: 0.5rem;
}

.env-button.active .env-name {
  color: #1e40af;
}

.env-button.active .env-desc {
  color: #3b82f6;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .env-switch {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .env-button {
    min-width: auto;
    width: 100%;
  }
}
</style> 