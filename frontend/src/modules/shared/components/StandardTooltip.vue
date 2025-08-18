<template>
  <el-tooltip
    :content="content"
    :placement="placement"
    effect="light"
    :raw-content="rawContent"
    :show-after="showAfter"
    :hide-after="hideAfter"
    :disabled="disabled"
    class="standard-tooltip"
  >
    <slot>
      <!-- 默认问号图标 -->
      <el-icon class="help-icon">
        <QuestionFilled />
      </el-icon>
    </slot>
  </el-tooltip>
</template>

<script setup lang="ts">
import { QuestionFilled } from '@element-plus/icons-vue'

interface Props {
  content: string
  placement?: 'top' | 'top-start' | 'top-end' | 'bottom' | 'bottom-start' | 'bottom-end' | 'left' | 'left-start' | 'left-end' | 'right' | 'right-start' | 'right-end'
  rawContent?: boolean
  showAfter?: number
  hideAfter?: number
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  placement: 'top',
  rawContent: false,
  showAfter: 0,
  hideAfter: 0,
  disabled: false
})
</script>

<style scoped>
.help-icon {
  color: #909399;
  cursor: help;
  transition: color 0.2s;
}

.help-icon:hover {
  color: #409eff;
}

/* 全局悬浮窗样式覆盖 */
:deep(.el-tooltip__popper) {
  background-color: #ffffff !important;
  color: #333333 !important;
  border: 1px solid #e4e7ed !important;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1) !important;
  max-width: 400px !important;
  word-wrap: break-word !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  padding: 8px 12px !important;
}

:deep(.el-tooltip__popper .el-popper__arrow::before) {
  background-color: #ffffff !important;
  border-color: #e4e7ed !important;
}

/* 备用选择器 */
:deep(.el-popper.el-tooltip) {
  background-color: #ffffff !important;
  color: #333333 !important;
  border: 1px solid #e4e7ed !important;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1) !important;
  max-width: 400px !important;
  word-wrap: break-word !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  padding: 8px 12px !important;
}

:deep(.el-popper.el-tooltip .el-popper__arrow::before) {
  background-color: #ffffff !important;
  border-color: #e4e7ed !important;
}
</style>
