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
    
    <el-form :model="form" label-width="120px" size="default">
      <!-- 车牌号输入 -->
      <el-form-item label="车牌号" required>
        <el-input 
          v-model="form.carNo" 
          placeholder="请输入车牌号，如：川A12345"
          style="width: 300px"
        />
      </el-form-item>
      
      <!-- 操作按钮 -->
      <el-form-item>
        <div class="action-buttons">
          <el-button 
            type="info" 
            @click="handleQueryOrder" 
            :loading="loading.query"
            size="default"
            class="action-button"
          >
            查询订单
          </el-button>
          <el-button 
            type="primary" 
            @click="handlePayOrder" 
            :loading="loading.pay"
            size="default"
            class="action-button"
          >
            模拟支付
          </el-button>
        </div>
      </el-form-item>
    </el-form>
    
    <!-- 支付结果 -->
    <div v-if="paymentResult" class="payment-result">
      <div class="result-header">
        <h4 class="result-title">支付结果</h4>
      </div>
      <div class="result-content">
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
          <div class="status-indicator" :class="paymentResult.success ? 'success' : 'error'">
            <div class="status-dot"></div>
            <span class="status-text">{{ paymentResult.success ? '支付成功' : '支付失败' }}</span>
          </div>
        </div>
        <div class="result-item" v-if="paymentResult.payTime">
          <span class="result-label">支付时间</span>
          <span class="result-value">{{ paymentResult.payTime }}</span>
        </div>
        <div class="result-item" v-if="paymentResult.errorMsg">
          <span class="result-label">错误信息</span>
          <span class="result-value error-text">{{ paymentResult.errorMsg }}</span>
        </div>
      </div>
    </div>

    <!-- 订单信息（查询） -->
    <div v-if="orderInfo" class="payment-result" style="margin-top: 1rem;">
      <div class="result-header">
        <h4 class="result-title">订单信息</h4>
      </div>
      <div class="result-content">
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
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useEnvironmentStore } from '@/stores/environment'
import { useHistoryStore } from '@/stores/history'
import { paymentApi } from '@/api/closeApp'

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

// 模拟支付
const handlePayOrder = async () => {
  if (!form.carNo) {
    ElMessage.warning('请输入车牌号')
    return
  }
  
  loading.pay = true
  const startTime = Date.now()
  
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
      if (typeof result.data === 'string') {
        message = result.data
      } else if (result.data && typeof result.data === 'object' && result.data.data) {
        message = result.data.data
      } else {
        message = JSON.stringify(result.data)
      }
      
      // 判断支付成功：检查状态码和消息
      const success = result.resultCode === 200 && result.resultMsg === '成功'
      
      paymentResult.value = {
        carNo: form.carNo,
        orderNo: extractOrderNo(message),
        payMoney: extractPayMoney(message), // 已经是元为单位
        success,
        payTime: new Date().toLocaleString('zh-CN'),
        errorMsg: success ? '' : message
      }
      // 清空查询结果卡片，避免混淆
      orderInfo.value = null
      
      ElMessage.success('支付操作完成')
      
      // 记录操作历史
      historyStore.addHistory({
        operation: '模拟支付',
        params: { carNo: form.carNo, ...params },
        result: success ? 'success' : 'error',
        message: typeof result.data === 'string' ? result.data : JSON.stringify(result.data),
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
        hasOrder = !data.includes('未查询到') && !data.includes('没有找到')
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
        ElMessage.success('查询成功')
      } else {
        orderInfo.value = null
        paymentResult.value = null
        ElMessage.info('未找到相关订单')
      }
      
      // 记录操作历史
      historyStore.addHistory({
        operation: '查询订单',
        params: { carNo: form.carNo, ...params },
        result: hasOrder ? 'success' : 'error',
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
</script>

<style scoped>
.payment-management {
  margin-bottom: 1.5rem;
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
</style> 