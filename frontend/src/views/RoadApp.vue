<template>
  <div class="road-app">
    <div class="page-header">
      <h2>路侧车场管理</h2>
      <p>路侧车场功能正在开发中，敬请期待</p>
    </div>
    
    <el-card class="placeholder-card" shadow="hover">
      <div class="placeholder-content">
        <el-icon class="placeholder-icon" size="80">
          <Tools />
        </el-icon>
        <h3>功能开发中</h3>
        <p>路侧车场管理功能正在开发中，预计将在后续版本中发布</p>
        <el-button type="primary" @click="handleBackToClose">
          返回封闭车场
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Tools } from '@element-plus/icons-vue'

const router = useRouter()

const handleBackToClose = () => {
  router.push('/close')
}
</script>

<style scoped>
.road-app {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h2 {
  color: #303133;
  margin-bottom: 10px;
}

.page-header p {
  color: #909399;
  font-size: 14px;
}

.placeholder-card {
  max-width: 600px;
  margin: 0 auto;
}

.placeholder-content {
  text-align: center;
  padding: 60px 20px;
}

.placeholder-icon {
  color: #909399;
  margin-bottom: 20px;
}

.placeholder-content h3 {
  color: #303133;
  margin-bottom: 15px;
  font-size: 24px;
}

.placeholder-content p {
  color: #909399;
  margin-bottom: 30px;
  font-size: 16px;
  line-height: 1.6;
}
</style> 