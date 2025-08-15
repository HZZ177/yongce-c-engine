<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="true"
    @close="handleClose"
  >
    <div class="qr-dialog-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span class="loading-text">正在获取二维码...</span>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <el-icon class="error-icon"><Warning /></el-icon>
        <span class="error-text">{{ error }}</span>
        <el-button type="primary" size="small" @click="handleRetry" class="retry-button">
          重试
        </el-button>
      </div>
      
      <!-- 二维码内容 -->
      <div v-else-if="qrCodeUrl" class="qr-content">
        <div class="channel-info">
          <h4 class="channel-name">{{ channelName }}</h4>
          <p class="channel-type">{{ channelType === 'in' ? '入口通道' : '出口通道' }}</p>
        </div>
        
        <div class="qr-image-container">
                <img 
        :key="imgKey"
        :src="qrCodeUrl" 
        :alt="`${channelName}二维码`"
        class="qr-image"
        @error="handleImageError"
        @load="handleImageLoad"
      />
          <div v-if="imageLoading" class="image-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>图片加载中...</span>
          </div>
        </div>
        
        <div class="qr-actions">
          <el-button type="primary" @click="handleDownload" :disabled="imageLoading">
            下载二维码
          </el-button>
          <el-button @click="handleRefresh">
            刷新
          </el-button>
        </div>
      </div>
      
      <!-- 无数据状态 -->
      <div v-else class="no-data">
        <el-icon class="no-data-icon"><Picture /></el-icon>
        <span class="no-data-text">未找到对应的二维码</span>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Warning, Picture } from '@element-plus/icons-vue'
import { deviceApi } from '@/api/closeApp'
import { useHistoryStore } from '@/stores/history'
import { useEnvironmentStore } from '@/stores/environment'
import type { ChannelQrCode } from '@/types'

const props = defineProps<{
  modelValue: boolean
  channelName: string
  channelType: 'in' | 'out'
  lotId: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const historyStore = useHistoryStore()
const envStore = useEnvironmentStore()

// 响应式数据
const loading = ref(false)
const error = ref('')
const qrCodeUrl = ref('')
const imageLoading = ref(false)
const qrCodeData = ref<ChannelQrCode | null>(null)
const imgKey = ref(0)

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const dialogTitle = computed(() => `查看二维码 - ${props.channelName}`)

// 监听弹窗显示状态
watch(visible, (newVal) => {
  if (newVal) {
    fetchQrCode()
  } else {
    resetState()
  }
})

// 获取二维码
const fetchQrCode = async () => {
  if (!props.lotId) {
    error.value = '车场ID不能为空'
    return
  }
  
  loading.value = true
  error.value = ''
  qrCodeUrl.value = ''
  imageLoading.value = false
  qrCodeData.value = null
  
  const startTime = Date.now()
  
  try {
    // 首先尝试从缓存中获取数据
    const cachedData = envStore.getQrCodeData(props.channelName)
    
    if (cachedData) {
      // 缓存中有数据，直接使用
      qrCodeData.value = cachedData
      qrCodeUrl.value = cachedData.nodeQrCode
      imageLoading.value = true
      
      // 记录成功历史
      const duration = Date.now() - startTime
      historyStore.addHistory({
        operation: '获取通道二维码',
        params: {
          channelName: props.channelName,
          channelType: props.channelType,
          lotId: props.lotId
        },
        result: 'success',
        message: `成功获取${props.channelName}的二维码（缓存）`,
        duration
      })
    } else {
      // 缓存中没有数据，需要重新请求
      const result = await deviceApi.getChannelQrPic({
        lot_id: props.lotId
      })
      
      if (result.resultCode === 200 && result.data) {
        const responseData = result.data
        
        if (responseData.success && responseData.data?.records) {
          // 根据通道名称匹配对应的二维码
          console.log('查找通道名称:', props.channelName)
          console.log('可用通道列表:', responseData.data.records.map((r: ChannelQrCode) => ({ name: r.nodeName, hasQr: !!r.nodeQrCode })))
          
          const matchedChannel = responseData.data.records.find(
            (record: ChannelQrCode) => record.nodeName === props.channelName
          )
          
          if (matchedChannel) {
            // 检查二维码URL是否有效
            if (matchedChannel.nodeQrCode && matchedChannel.nodeQrCode.trim() !== '') {
              qrCodeData.value = matchedChannel
              qrCodeUrl.value = matchedChannel.nodeQrCode
              imageLoading.value = true
              
              // 记录成功历史
              const duration = Date.now() - startTime
              historyStore.addHistory({
                operation: '获取通道二维码',
                params: {
                  channelName: props.channelName,
                  channelType: props.channelType,
                  lotId: props.lotId
              },
                result: 'success',
                message: `成功获取${props.channelName}的二维码`,
                duration
              })
            } else {
              error.value = `通道"${props.channelName}"暂无二维码`
              
              // 记录失败历史
              const duration = Date.now() - startTime
              historyStore.addHistory({
                operation: '获取通道二维码',
                params: {
                  channelName: props.channelName,
                  channelType: props.channelType,
                  lotId: props.lotId
                },
                result: 'error',
                message: error.value,
                duration
              })
            }
          } else {
            error.value = `未找到通道"${props.channelName}"对应的二维码`
            
            // 记录失败历史
            const duration = Date.now() - startTime
            historyStore.addHistory({
              operation: '获取通道二维码',
              params: {
                channelName: props.channelName,
                channelType: props.channelType,
                lotId: props.lotId
              },
              result: 'error',
              message: error.value,
              duration
            })
          }
        } else {
          throw new Error(responseData.msg || '获取二维码失败')
        }
      } else {
        throw new Error(result.resultMsg || '获取二维码失败')
      }
    }
  } catch (err: any) {
    const errorMsg = err.response?.data?.detail || err.message || '获取二维码失败'
    error.value = errorMsg
    
    // 记录失败历史
    const duration = Date.now() - startTime
    historyStore.addHistory({
      operation: '获取通道二维码',
      params: {
        channelName: props.channelName,
        channelType: props.channelType,
        lotId: props.lotId
      },
      result: 'error',
      message: errorMsg,
      duration
    })
  } finally {
    loading.value = false
  }
}

// 图片加载成功
const handleImageLoad = () => {
  imageLoading.value = false
  loading.value = false
}

// 图片加载失败
const handleImageError = () => {
  imageLoading.value = false
  loading.value = false
  error.value = '二维码图片加载失败'
}

// 重试
const handleRetry = () => {
  fetchQrCode()
}

// 刷新
const handleRefresh = async () => {
  loading.value = true
  imageLoading.value = true
  // 先清空图片并强制重载
  qrCodeUrl.value = ''
  imgKey.value++
  
  // 刷新缓存数据
  await envStore.refreshQrCodeData()
  // 重新获取二维码
  await fetchQrCode()
}

// 下载二维码
const handleDownload = async () => {
  if (!qrCodeUrl.value) {
    ElMessage.warning('二维码地址为空')
    return
  }
  try {
    const response = await fetch(qrCodeUrl.value, { mode: 'cors' })
    if (!response.ok) throw new Error('网络错误')
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${props.channelName}_二维码.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (err) {
    ElMessage.error('下载失败，请稍后重试或右键图片另存为')
  }
}

// 关闭弹窗
const handleClose = () => {
  visible.value = false
}

// 重置状态
const resetState = () => {
  loading.value = false
  error.value = ''
  qrCodeUrl.value = ''
  imageLoading.value = false
  qrCodeData.value = null
}
</script>

<style scoped>
.qr-dialog-content {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-container,
.error-container,
.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}

.loading-text,
.error-text,
.no-data-text {
  font-size: 0.875rem;
  color: #6b7280;
}

.error-icon {
  font-size: 2rem;
  color: #f56c6c;
}

.no-data-icon {
  font-size: 2rem;
  color: #909399;
}

.retry-button {
  margin-top: 0.5rem;
}

.qr-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.channel-info {
  text-align: center;
}

.channel-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.channel-type {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.qr-image-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.qr-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.image-loading {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.qr-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}
</style> 