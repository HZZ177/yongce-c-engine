<template>
  <el-card class="operation-history" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-content">
          <h3 class="card-title">操作历史</h3>
          <p class="card-subtitle">查看所有操作记录和结果</p>
        </div>
        <div class="header-actions">
          <el-button type="danger" size="small" @click="handleClearHistory" class="clear-button">
            <svg class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            清空历史
          </el-button>
        </div>
      </div>
    </template>
    
    <el-table :data="historyList" style="width: 100%" max-height="450" class="history-table">
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
            <el-tooltip
              placement="top"
              :disabled="!isMessageTruncated(row.message)"
              :show-after="500"
              popper-class="message-tooltip"
              effect="dark"
            >
              <template #content>
                <div class="tooltip-content">
                  {{ row.message }}
                </div>
              </template>
              <span class="message-text" :class="{ 'truncated': isMessageTruncated(row.message) }">
                {{ row.message }}
              </span>
            </el-tooltip>
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
import { computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { useHistoryStore } from '../stores/history'

const historyStore = useHistoryStore()

// 历史记录列表
const historyList = computed(() => historyStore.historyList)

// 清空历史
const handleClearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有操作历史吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    historyStore.clearHistory()
    ElMessage.success('历史记录已清空')
  } catch {
    // 用户取消操作
  }
}

// 删除单条历史
const handleRemoveHistory = (id: string) => {
  historyStore.removeHistory(id)
  ElMessage.success('删除成功')
}

// 判断消息是否需要截断（超过5行）
const isMessageTruncated = (message: string): boolean => {
  if (!message) return false

  // 考虑换行符的情况
  const lines = message.split('\n')
  if (lines.length > 5) return true

  // 考虑长文本自动换行的情况
  // 估算每行大约能容纳的字符数（根据容器宽度和字体大小）
  const charsPerLine = 35 // 大约每行35个字符（考虑中英文混合）
  const maxLines = 5

  // 计算所有行的总长度是否会超过5行
  let totalLines = 0
  for (const line of lines) {
    totalLines += Math.ceil(line.length / charsPerLine) || 1
    if (totalLines > maxLines) return true
  }

  return false
}
</script>

<style scoped>
.operation-history {
  margin-bottom: 1.5rem;
  min-height: 500px;
  max-height: 600px;
}

.card-header {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
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

.header-actions {
  position: absolute;
  right: 0;
  display: flex;
  gap: 0.75rem;
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

.delete-button {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
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
  display: block;
  width: 100%;
}

.message-text.truncated {
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  cursor: help;
}

/* 悬浮提示内容样式 */
.tooltip-content {
  max-width: 700px;
  max-height: 250px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.4;
  font-size: 13px;
}

/* 自定义悬浮提示样式 */
:deep(.message-tooltip) {
  max-width: 720px !important;
}

/* 美化滚动条 */
.tooltip-content::-webkit-scrollbar {
  width: 4px;
}

.tooltip-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.tooltip-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.tooltip-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 表格表头居中 */
.operation-history :deep(.el-table th) {
  text-align: center;
}

.operation-history :deep(.el-table .cell) {
  text-align: center;
}


</style>

 