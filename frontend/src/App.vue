<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-container">
        <div class="header-left">
          <h1 class="app-title">永策C端测试工具</h1>
        </div>
        
        <!-- 导航标签 -->
        <div class="nav-tabs">
          <button 
            class="nav-tab" 
            :class="{ active: activeTab === 'close' }"
            @click="handleTabClick('close')"
          >
            封闭
          </button>
          <button 
            class="nav-tab" 
            :class="{ active: activeTab === 'road' }"
            @click="handleTabClick('road')"
          >
            路侧
          </button>
        </div>
        
        <div class="header-right">
          <a href="http://192.168.24.114:17771/docs" class="api-docs-link" target="_blank">
            <span>API 接口文档</span>
            <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </a>
        </div>
      </div>
    </header>
    
    <!-- 主要内容区域 -->
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 当前激活的标签页
const activeTab = ref('close')

// 监听路由变化，同步标签页状态
watch(() => route.path, (newPath) => {
  if (newPath === '/close') {
    activeTab.value = 'close'
  } else if (newPath === '/road') {
    activeTab.value = 'road'
  }
}, { immediate: true })

// 标签页点击事件
const handleTabClick = (tabName: string) => {
  if (tabName === 'close') {
    router.push('/close')
  } else if (tabName === 'road') {
    router.push('/road')
  }
}
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f7f8fa;
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 头部样式 - 参考Tailwind设计 */
.app-header {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

.header-left {
  position: absolute;
  left: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.header-right {
  position: absolute;
  right: 0;
}

.app-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0;
  line-height: 1.2;
}

.app-subtitle {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-weight: 400;
}

.api-docs-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: white;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.api-docs-link:hover {
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.arrow-icon {
  width: 1rem;
  height: 1rem;
}

/* 导航标签样式 */
.nav-tabs {
  display: flex;
  gap: 0.5rem;
}

.nav-tab {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-tab:hover {
  color: white;
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-tab.active {
  color: white;
  background-color: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 主内容区域 */
.app-main {
  flex: 1;
  background-color: #f7f8fa;
  padding: 2rem;
  overflow-y: auto;
}

/* 全局卡片样式优化 */
.el-card {
  border-radius: 0.75rem;
  border: none;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
  background-color: white;
}

.el-card:hover {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.el-card__header {
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  padding: 1.25rem 1.5rem;
  border-radius: 0.75rem 0.75rem 0 0;
}

.el-card__body {
  padding: 1.5rem;
}

/* 按钮样式优化 */
.el-button {
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.el-button--primary {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-color: #3b82f6;
}

.el-button--primary:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
}

.el-button--success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-color: #10b981;
}

.el-button--warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-color: #f59e0b;
}

.el-button--danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border-color: #ef4444;
}

/* 表单组件样式 */
.el-input__wrapper {
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  transition: all 0.2s ease;
}

.el-input__wrapper:hover {
  border-color: #3b82f6;
}

.el-input__wrapper.is-focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.el-select .el-input__wrapper {
  border-radius: 0.5rem;
}

/* 表格样式优化 */
.el-table {
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.el-table th {
  background-color: #f8fafc;
  color: #374151;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
}

.el-table td {
  border-bottom: 1px solid #f3f4f6;
}

.el-table tr:hover > td {
  background-color: #f9fafb;
}

/* 标签样式 */
.el-tag {
  border-radius: 0.375rem;
  font-weight: 500;
  border: none;
}

.el-tag--success {
  background-color: #d1fae5;
  color: #065f46;
}

.el-tag--danger {
  background-color: #fee2e2;
  color: #991b1b;
}

.el-tag--warning {
  background-color: #fef3c7;
  color: #92400e;
}

.el-tag--info {
  background-color: #dbeafe;
  color: #1e40af;
}

/* 单选按钮组样式 */
.el-radio-group {
  display: flex;
  gap: 1rem;
}

.el-radio {
  margin-right: 0;
}

.el-radio__input.is-checked .el-radio__inner {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .nav-tabs {
    gap: 0.25rem;
  }
  
  .nav-tab {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }
  
  .app-main {
    padding: 1rem;
  }
}
</style> 