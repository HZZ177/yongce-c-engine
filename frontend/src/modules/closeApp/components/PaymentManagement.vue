<template>
  <el-card class="payment-management" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-content">
          <h3 class="card-title">支付管理</h3>
          <p class="card-subtitle">模拟支付和查询订单信息</p>
        </div>
      </div>
    </template>
    
    <div class="payment-form-container">
      <!-- 车牌号标签 -->
      <div class="form-label-container">
        <label class="form-label">车牌号<span class="required">*</span></label>
      </div>
      
      <!-- 车牌号输入框 -->
      <div class="form-input-container">
        <el-input 
          v-model="form.carNo" 
          placeholder="请输入车牌号，如：川A12345"
          style="width: 300px"
        />
      </div>
      
      <!-- 操作按钮 -->
      <div class="form-buttons-container">
        <div class="action-buttons">
          <el-button 
            type="warning" 
            @click="handlePayOrder" 
            :loading="loading.pay"
            size="default"
            class="action-button"
          >
            模拟支付
          </el-button>
          <el-button 
            type="primary" 
            @click="handleQueryOrder" 
            :loading="loading.query"
            size="default"
            class="action-button"
          >
            查询订单
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 统一结果显示区域 -->
    <div v-if="shouldShowResult" class="payment-result">
      <div class="result-header">
        <h4 class="result-title">{{ getResultTitle() }}</h4>
      </div>
      <div class="result-content">
        <!-- 支付加载状态 -->
        <div v-if="loading.pay" class="result-item" style="grid-column: 1 / -1; text-align: center;">
          <div class="loading-spinner">
            <div class="spinner"></div>
            <span class="loading-text">正在处理支付请求...</span>
          </div>
        </div>
        
        <!-- 查询加载状态 -->
        <div v-else-if="loading.query" class="result-item" style="grid-column: 1 / -1; text-align: center;">
          <div class="loading-spinner">
            <div class="spinner"></div>
            <span class="loading-text">正在查询订单信息...</span>
          </div>
        </div>
        
        <!-- 支付成功状态 -->
        <template v-else-if="payStatus === 'success'">
          <div class="result-item">
            <span class="result-label">车牌号</span>
            <span class="result-value">{{ paymentResult.carNo }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">支付金额</span>
            <span class="amount">¥{{ paymentResult.payMoney }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">支付状态</span>
            <div class="status-indicator success">
              <div class="status-dot"></div>
              <span class="status-text">支付成功</span>
            </div>
          </div>
          <div class="result-item" v-if="paymentResult.payTime">
            <span class="result-label">支付时间</span>
            <span class="result-value">{{ paymentResult.payTime }}</span>
          </div>
        </template>
        
        <!-- 无待缴费订单状态 -->
        <template v-else-if="payStatus === 'noOrder'">
          <div class="result-item">
            <span class="result-label">车牌号</span>
            <span class="result-value">{{ form.carNo }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">支付状态</span>
            <div class="status-indicator">
              <div class="status-dot"></div>
              <span class="status-text">暂无待缴费订单</span>
            </div>
          </div>
          <div class="result-item">
            <span class="result-label">提示信息</span>
            <span class="result-value">该车辆暂时没有需要支付的订单</span>
          </div>
        </template>
        
        <!-- 查询到订单信息 -->
        <template v-else-if="queryStatus === 'hasOrder'">
          <div class="result-item">
            <span class="result-label">车牌号</span>
            <span class="result-value">{{ orderInfo.carNo }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">订单号</span>
            <span class="result-value">{{ orderInfo.orderNo }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">应付金额</span>
            <span class="result-value">¥{{ orderInfo.payMoney }}</span>
          </div>
        </template>
        
        <!-- 无订单信息 -->
        <template v-else-if="queryStatus === 'noOrder'">
          <div class="result-item">
            <span class="result-label">车牌号</span>
            <span class="result-value">{{ form.carNo }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">订单状态</span>
            <span class="result-value">该车辆暂时没有订单信息</span>
          </div>
        </template>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useEnvironmentStore } from '../stores/environment'
import { useHistoryStore } from '../stores/history'
import { paymentApi } from '../api/closeApp'

const envStore = useEnvironmentStore()
const historyStore = useHistoryStore()

// 表单数据
const form = reactive({
  carNo: ''
})

// 加载状态
const loading = reactive({
  pay: false,
  query: false
})

// 支付结果
const paymentResult = ref<any>(null)
// 查询订单信息
const orderInfo = ref<any>(null)
// 查询状态：'none' | 'hasOrder' | 'noOrder'
const queryStatus = ref<'none' | 'hasOrder' | 'noOrder'>('none')
// 支付状态：'none' | 'success' | 'noOrder' | 'error'
const payStatus = ref<'none' | 'success' | 'noOrder' | 'error'>('none')

// 模拟支付
const handlePayOrder = async () => {
  if (!form.carNo) {
    ElMessage.warning('请输入车牌号')
    return
  }
  
  loading.pay = true
  const startTime = Date.now()
  
  // 重置支付状态
  payStatus.value = 'none'
  paymentResult.value = null
  
  try {
    const params = {
      car_no: form.carNo,
      lot_id: envStore.currentLotId
    }
    
    const result = await paymentApi.payOrder(params)
    const duration = Date.now() - startTime
    
    if (result.resultCode === 200) {
      // 解析支付结果 - 处理嵌套的data结构
      let message = ''
      let innerResultCode = 200
      
      if (typeof result.data === 'string') {
        message = result.data
      } else if (result.data && typeof result.data === 'object' && result.data.data) {
        message = result.data.data
        // 检查内层的resultCode
        innerResultCode = result.data.resultCode || 200
      } else {
        message = JSON.stringify(result.data)
      }
      
      // 判断是否有待缴费订单：检查内层resultCode和消息内容
      const hasOrderToPay = innerResultCode === 200 && !message.includes('未查询到') && !message.includes('没有')
      
      if (hasOrderToPay) {
        // 有待缴费订单，支付成功
        paymentResult.value = {
          carNo: form.carNo,
          orderNo: extractOrderNo(message),
          payMoney: extractPayMoney(message), // 已经是元为单位
          payTime: new Date().toLocaleString('zh-CN')
        }
        payStatus.value = 'success'
        // 清空查询结果卡片，避免混淆
        orderInfo.value = null
        queryStatus.value = 'none'
        
        ElMessage.success('支付操作完成')
      } else {
        // 无待缴费订单
        payStatus.value = 'noOrder'
        // 清空其他状态
        paymentResult.value = null
        orderInfo.value = null
        queryStatus.value = 'none'
      }
      
      // 记录操作历史
      historyStore.addHistory({
        operation: '模拟支付',
        params: { carNo: form.carNo, ...params },
        result: 'success', // 接口调用成功，状态应为成功
        message: hasOrderToPay ? '支付成功' : '暂无待缴费订单',
        duration
      })
    } else {
      throw new Error(typeof result.data === 'string' ? result.data : '支付失败')
    }
  } catch (error: any) {
    const duration = Date.now() - startTime
    const errorMsg = error.response?.data?.detail || error.message || '支付失败'
    
    paymentResult.value = {
      carNo: form.carNo,
      orderNo: '',
      payMoney: 0,
      success: false,
      payTime: new Date().toLocaleString('zh-CN'),
      errorMsg
    }
    
    ElMessage.error(errorMsg)
    
    // 记录操作历史
    historyStore.addHistory({
      operation: '模拟支付',
      params: { carNo: form.carNo },
      result: 'error',
      message: errorMsg,
      duration
    })
  } finally {
    loading.pay = false
  }
}

// 查询订单
const handleQueryOrder = async () => {
  if (!form.carNo) {
    ElMessage.warning('请输入车牌号')
    return
  }
  
  loading.query = true
  const startTime = Date.now()
  
  // 重置查询状态
  queryStatus.value = 'none'
  orderInfo.value = null
  paymentResult.value = null
  payStatus.value = 'none' // 同时重置支付状态，避免干扰查询结果显示
  
  try {
    const params = {
      car_no: form.carNo,
      lot_id: envStore.currentLotId
    }
    
    // 调用后端查询订单接口
    const result = await paymentApi.queryOrder(params)
    const duration = Date.now() - startTime
    
    if (result.resultCode === 200) {
      // 后端可能返回结构化数据或提示字符串，做兼容处理
      const data = result.data
      let hasOrder = false
      let orderNo = ''
      let payMoney = 0
      
      if (typeof data === 'string') {
        // 检查是否包含"没有订单"相关的提示信息
        hasOrder = !data.includes('未查询到') && !data.includes('没有找到') && !data.includes('没有该车辆的支付订单信息')
        orderNo = extractOrderNo(data)
        payMoney = extractPayMoney(data)
      } else if (data && typeof data === 'object') {
        hasOrder = !!data.orderNo
        orderNo = data.orderNo || ''
        // 后端返回的金额单位是分，需要转换为元
        payMoney = Number(data.payMoney) / 100 || 0
      }
      
      if (hasOrder) {
        orderInfo.value = {
          carNo: form.carNo,
          orderNo,
          payMoney
        }
        // 清空支付结果卡片，避免混淆
        paymentResult.value = null
        queryStatus.value = 'hasOrder'
      } else {
        orderInfo.value = null
        paymentResult.value = null
        queryStatus.value = 'noOrder'
      }
      
      // 记录操作历史
      historyStore.addHistory({
        operation: '查询订单',
        params: { carNo: form.carNo, ...params },
        result: 'success', // 接口调用成功，状态应为成功
        message: hasOrder ? '查询到订单' : '未找到订单',
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
      operation: '查询订单',
      params: { carNo: form.carNo },
      result: 'error',
      message: errorMsg,
      duration
    })
  } finally {
    loading.query = false
  }
}

// 辅助函数：提取订单号
const extractOrderNo = (message: string): string => {
  const match = message.match(/订单【(\d+)】/)
  return match ? match[1] : ''
}

// 辅助函数：提取支付金额（分转元）
const extractPayMoney = (message: string): number => {
  const match = message.match(/停车费【(\d+)】/)
  return match ? parseInt(match[1]) / 100 : 0
}

// 通用金额转换函数：分转元
const convertCentsToYuan = (cents: number): number => {
  return cents / 100
}

// 获取支付结果标题
const getPaymentResultTitle = () => {
  if (loading.pay) return '支付处理中...'
  if (payStatus.value === 'success') return '支付结果'
  if (payStatus.value === 'noOrder') return '支付结果'
  return '支付结果'
}

// 判断是否应该显示结果区域
const shouldShowResult = computed(() => {
  return payStatus.value !== 'none' || 
         queryStatus.value !== 'none' || 
         loading.pay || 
         loading.query
})

// 获取结果标题
const getResultTitle = () => {
  if (loading.pay) return '支付处理中...'
  if (loading.query) return '查询中...'
  if (payStatus.value === 'success') return '支付结果'
  if (payStatus.value === 'noOrder') return '支付结果'
  if (queryStatus.value === 'hasOrder') return '订单信息'
  if (queryStatus.value === 'noOrder') return '查询结果'
  return '结果'
}
</script>

<style scoped>
.payment-management {
  margin-bottom: 1.5rem;
  min-height: 500px; /* 与车辆管理卡片保持同高度 */
}

.payment-form-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 0;
}

.form-label-container {
  display: flex;
  justify-content: center;
  width: 100%;
}

.form-label {
  font-size: 0.875rem;
  color: #606266;
  font-weight: 500;
  margin: 0;
  position: relative; /* 为绝对定位的星号提供定位上下文 */
}

.required {
  color: #f56c6c;
  position: absolute; /* 绝对定位 */
  left: -0.5rem; /* 向左偏移，显示在左上角 */
  font-size: 0.75rem; /* 稍微调小星号大小 */
}

.form-input-container {
  display: flex;
  justify-content: center;
  width: 100%;
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

.payment-result {
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

.error-text {
  color: #dc2626;
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

.status-indicator.success .status-dot {
  background-color: #10b981;
}

.status-indicator.error .status-dot {
  background-color: #ef4444;
}

.status-indicator .status-dot {
  background-color: #6b7280; /* 默认状态（无待缴费订单）的颜色 */
}

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.status-indicator.success .status-text {
  color: #065f46;
}

.status-indicator.error .status-text {
  color: #991b1b;
}

.amount {
  color: #f59e0b;
  font-weight: 600;
  font-size: 1rem;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0;
}

.spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  color: #6b7280;
  font-size: 0.875rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 