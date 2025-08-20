<template>
  <el-card class="operation-history" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-content">
          <h3 class="card-title">路侧操作历史</h3>
          <p class="card-subtitle">记录所有路侧车场操作的详细历史</p>
        </div>
        <div class="header-actions">
          <el-button
            type="danger"
            size="small"
            @click="handleClearHistory"
            :disabled="historyStore.history.length === 0"
          >
            <svg class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            清空历史
          </el-button>
        </div>
      </div>
    </template>
    
    <el-table :data="historyStore.history" style="width: 100%" max-height="450" class="history-table">
      <template #empty>
        <div class="empty-table">
          <el-icon class="empty-icon" size="60">
            <Document />
          </el-icon>
          <p class="empty-text">暂无操作历史</p>
        </div>
      </template>
      <el-table-column prop="timestamp" label="时间" width="180" />
      <el-table-column prop="operation" label="操作" width="150" />
      <el-table-column prop="result" label="结果" width="100">
        <template #default="{ row }">
          <div class="status-indicator" :class="row.result === 'success' ? 'success' : 'error'">
            <div class="status-dot"></div>
            <span class="status-text">{{ row.result === 'success' ? '成功' : '失败' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="耗时" width="100">
        <template #default="{ row }">
          <span v-if="row.duration">{{ row.duration }}ms</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="message" label="消息" min-width="300">
        <template #default="{ row }">
          <div class="message-cell">
            <span class="message-text">{{ row.message }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button
            type="danger"
            size="small"
            @click="handleRemoveHistory(row.id)"
            class="delete-button"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { ElMessageBox, ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { useRoadHistoryStore } from '../stores/history'

const historyStore = useRoadHistoryStore()

// 清空历史记录
const handleClearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有路侧操作历史记录吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    historyStore.clearHistory()
    ElMessage.success('路侧操作历史已清空')
  } catch {
    // 用户取消操作
  }
}

// 删除单条历史
const handleRemoveHistory = (id: string) => {
  historyStore.removeHistoryItem(id)
  ElMessage.success('删除成功')
}
</script>

<style scoped>
.operation-history {
  margin-bottom: 1.5rem;
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

.header-actions {
  position: absolute;
  right: 0;
}

.clear-button {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.button-icon {
  width: 0.875rem;
  height: 0.875rem;
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

/* 表格最小高度 */
.history-table {
  min-height: 400px !important;
}

/* 空数据状态样式 */
.empty-table {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 350px;
  color: #909399;
}

.empty-icon {
  margin-bottom: 16px;
  color: #c0c4cc;
}

.empty-text {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 消息列样式 */
.message-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 8px;
}

.message-text {
  text-align: center;
  word-break: break-all;
  line-height: 1.4;
  white-space: pre-wrap;
}

/* 表格表头居中 */
.operation-history :deep(.el-table th) {
  text-align: center;
}

.operation-history :deep(.el-table .cell) {
  text-align: center;
}

/* 删除按钮样式 */
.delete-button {
  padding: 4px 8px;
  font-size: 12px;
}
</style>
