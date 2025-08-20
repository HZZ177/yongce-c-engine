<template>
  <el-card class="fee-inquiry" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-content">
          <h3 class="card-title">路侧查费管理</h3>
          <p class="card-subtitle">查询路侧车辆停车费用信息</p>
        </div>
      </div>
    </template>
    
    <div class="fee-form-container">
      <!-- 车牌号输入 -->
      <div class="form-item-container">
        <label class="form-label">车牌号</label>
        <div class="form-input-container">
          <el-input 
            v-model="form.carNo" 
            placeholder="请输入车牌号"
            style="width: 100%"
            @keyup.enter="handleFeeInquiry"
          />
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="form-buttons-container">
        <div class="action-buttons">
          <el-button
            type="primary"
            @click="handleFeeInquiry"
            :loading="loading.inquiry"
            size="default"
            class="action-button"
            :disabled="!envStore.currentLotId || !form.carNo.trim()"
          >
            查费
          </el-button>
        </div>
      </div>
      
      <!-- 查费结果展示 -->
      <div v-if="feeResult" class="fee-result-container">
        <div class="result-header">
          <h4 class="result-title">查费结果</h4>
        </div>
        <div class="result-content">
          <div class="result-item">
            <span class="result-label">车牌号：</span>
            <span class="result-value">{{ feeResult.carNo }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">车场：</span>
            <span class="result-value">{{ feeResult.lotName }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">停车费用：</span>
            <span class="result-value fee-amount">¥{{ feeResult.fee }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">停车时长：</span>
            <span class="result-value">{{ formatDuration(feeResult.duration) }}</span>
          </div>
          <div v-if="feeResult.startTime" class="result-item">
            <span class="result-label">入场时间：</span>
            <span class="result-value">{{ feeResult.startTime }}</span>
          </div>
          <div v-if="feeResult.endTime" class="result-item">
            <span class="result-label">查费时间：</span>
            <span class="result-value">{{ feeResult.endTime }}</span>
          </div>
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
import { roadFeeApi } from '../api/roadApp'
import { ResponseHandler } from '@/modules/shared/utils'
import type { RoadFeeInquiryRequest, RoadFeeInfo } from '../types'

const envStore = useRoadEnvironmentStore()
const historyStore = useRoadHistoryStore()

// 表单数据
const form = reactive({
  carNo: ''
})

// 加载状态
const loading = reactive({
  inquiry: false
})

// 查费结果
const feeResult = ref<(RoadFeeInfo & { lotName: string }) | null>(null)

// 路侧查费
const handleFeeInquiry = async () => {
  if (!envStore.currentLotId) {
    ElMessage.warning('请先选择路侧车场')
    return
  }

  if (!form.carNo.trim()) {
    ElMessage.warning('请输入车牌号')
    return
  }

  loading.inquiry = true
  const startTime = Date.now()

  try {
    const params: RoadFeeInquiryRequest = {
      car_no: form.carNo.trim(),
      lot_id: envStore.currentLotId
    }

    const result = await roadFeeApi.feeInquiry(params)

    // 模拟查费结果数据（实际应该从API返回）
    const mockFeeData: RoadFeeInfo & { lotName: string } = {
      carNo: form.carNo.trim(),
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName(),
      fee: Math.floor(Math.random() * 50) + 10, // 随机费用 10-60元
      duration: Math.floor(Math.random() * 480) + 60, // 随机时长 1-8小时
      startTime: new Date(Date.now() - Math.random() * 8 * 60 * 60 * 1000).toLocaleString(),
      endTime: new Date().toLocaleString()
    }

    // 使用统一的响应处理，但优先使用业务逻辑消息
    const customSuccessMessage = ResponseHandler.isSuccess(result)
      ? `路侧查费成功，费用：¥${mockFeeData.fee}`
      : ''

    const handleResult = ResponseHandler.handleResponse(
      result,
      customSuccessMessage || '路侧查费成功',
      '路侧查费失败'
    )

    if (handleResult.success) {
      feeResult.value = mockFeeData
    } else {
      feeResult.value = null
    }

    // 记录操作历史（无论成功失败都记录一次）
    historyStore.addHistory({
      operation: '路侧查费',
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
    const errorResult = ResponseHandler.handleError(error, '路侧查费失败')
    feeResult.value = null

    // 记录网络错误历史
    historyStore.addHistory({
      operation: '路侧查费',
      params: { car_no: form.carNo },
      result: errorResult.historyResult,
      message: errorResult.message,
      duration: Date.now() - startTime,
      env: envStore.currentEnv,
      lotId: envStore.currentLotId,
      lotName: envStore.getCurrentLotName()
    })
  } finally {
    loading.inquiry = false
  }
}

// 格式化停车时长
const formatDuration = (minutes: number): string => {
  if (minutes < 60) {
    return `${minutes}分钟`
  }
  
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  
  if (remainingMinutes === 0) {
    return `${hours}小时`
  }
  
  return `${hours}小时${remainingMinutes}分钟`
}
</script>

<style scoped>
.fee-inquiry {
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

.fee-form-container {
  display: flex;
  flex-direction: column;
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

.fee-result-container {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
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

.fee-amount {
  font-weight: 600;
  color: #dc2626;
  font-size: 1rem;
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
  }
  
  .result-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
