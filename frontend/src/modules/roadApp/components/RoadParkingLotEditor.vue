<template>
  <el-dialog
    v-model="visible"
    :title="`${currentEnv === 'test' ? '测试' : '灰度'}环境路侧车场管理`"
    width="700px"
    :before-close="handleClose"
  >
    <!-- 车场列表 -->
    <div class="parking-lot-list">
      <div class="list-header">
        <h3>路侧车场列表</h3>
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          新增车场
        </el-button>
      </div>
      
      <div class="lot-card-grid" v-loading="lotsLoading">
        <div v-if="!lotsLoading && currentLots.length === 0" class="empty-tip">暂无路侧车场配置</div>
        <div v-for="lot in currentLots" :key="lot.id" class="lot-card">
          <div class="lot-card-header">
            <div class="lot-title">{{ lot.name || '未命名车场' }}</div>
            <div class="lot-actions">
              <el-tooltip content="编辑" placement="top">
                <el-button circle size="small" type="primary" @click="editLot(lot)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" placement="top">
                <el-button circle size="small" type="danger" @click="deleteLot(lot)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>
          <div class="lot-card-body">
            <div class="kv"><span class="k">车场ID</span><span class="v">{{ lot.id }}</span></div>
            <div class="kv"><span class="k">路侧ID</span><span class="v">{{ lot.road_lot_id }}</span></div>
            <div class="desc" v-if="lot.description">{{ lot.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑车场对话框 -->
    <el-dialog
      v-model="formDialogVisible"
      :title="isEditing ? '编辑路侧车场' : '新增路侧车场'"
      width="500px"
      append-to-body
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="车场ID" prop="id">
          <el-input v-model="formData.id" placeholder="请输入车场ID" :disabled="isEditing" />
        </el-form-item>
        <el-form-item label="路侧ID" prop="road_lot_id">
          <el-input v-model="formData.road_lot_id" placeholder="请输入路侧车场ID (如: LC5110000001)" />
        </el-form-item>
        <el-form-item label="车场名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入车场名称" />
        </el-form-item>
        <el-form-item label="车场描述" prop="description">
          <el-input v-model="formData.description" type="textarea" placeholder="请输入车场描述" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEditing ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import type { Environment, RoadLotConfig } from '../types'
import { roadConfigApi } from '../api/roadApp'

interface Props {
  modelValue: boolean
  currentEnv: Environment
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'refresh'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 对话框显示状态
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 车场数据
const currentLots = ref<RoadLotConfig[]>([])
const lotsLoading = ref(false)

// 表单相关
const formDialogVisible = ref(false)
const formRef = ref()
const isEditing = ref(false)
const submitting = ref(false)
const editingLotId = ref('')

const formData = ref({
  id: '',
  road_lot_id: '',
  name: '',
  description: ''
})

const formRules = {
  id: [{ required: true, message: '请输入车场ID', trigger: 'blur' }],
  road_lot_id: [{ required: true, message: '请输入路侧车场ID', trigger: 'blur' }],
  name: [{ required: true, message: '请输入车场名称', trigger: 'blur' }]
}

// 加载车场列表
const loadLots = async () => {
  lotsLoading.value = true
  try {
    // 从路侧后端API获取配置数据
    const result = await roadConfigApi.getConfig()

    if (result.resultCode === 200 && result.data) {
      const backendConfig = result.data
      const allLots = backendConfig.parking_lots || {}

      // 根据当前环境获取车场列表
      currentLots.value = allLots[props.currentEnv] || []

      console.log(`加载${props.currentEnv}环境路侧车场列表:`, currentLots.value)
    } else {
      throw new Error(result.resultMsg || '获取路侧配置失败')
    }
  } catch (error) {
    console.error('加载路侧车场列表失败:', error)
    ElMessage.error('加载路侧车场列表失败')
    currentLots.value = []
  } finally {
    lotsLoading.value = false
  }
}

// 显示新增对话框
const showAddDialog = () => {
  isEditing.value = false
  formData.value = { id: '', road_lot_id: '', name: '', description: '' }
  formDialogVisible.value = true
}

// 编辑车场
const editLot = (lot: RoadLotConfig) => {
  isEditing.value = true
  editingLotId.value = lot.id
  formData.value = { ...lot }
  formDialogVisible.value = true
}

// 删除车场
const deleteLot = async (lot: RoadLotConfig) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除路侧车场"${lot.name}"吗？此操作不可恢复。`,
      '确认删除',
      { type: 'warning' }
    )

    // 调用路侧后端API删除车场
    const result = await roadConfigApi.deleteParkingLot(lot.id)

    if (result.resultCode === 200) {
      ElMessage.success('路侧车场删除成功')
      await loadLots()
      emit('refresh')
    } else {
      throw new Error(result.resultMsg || '删除失败')
    }
  } catch (error: any) {
    if (error.message && error.message !== 'cancel') {
      console.error('删除路侧车场失败:', error)
      ElMessage.error(`删除路侧车场失败: ${error.message}`)
    }
    // 用户取消时不显示错误
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    // 调用路侧后端API保存车场
    let result
    if (isEditing.value) {
      // 编辑车场
      result = await roadConfigApi.updateParkingLot(editingLotId.value, formData.value)
    } else {
      // 新增车场
      result = await roadConfigApi.addParkingLot(props.currentEnv, formData.value)
    }

    if (result.resultCode === 200) {
      ElMessage.success(isEditing.value ? '路侧车场更新成功' : '路侧车场创建成功')
      formDialogVisible.value = false
      await loadLots()
      emit('refresh')
    } else {
      throw new Error(result.resultMsg || '保存失败')
    }
  } catch (error: any) {
    console.error('保存路侧车场失败:', error)
    if (error.message) {
      ElMessage.error(`保存路侧车场失败: ${error.message}`)
    } else {
      ElMessage.error('表单验证失败')
    }
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}

// 监听对话框显示状态
watch(visible, (newVal) => {
  if (newVal) {
    loadLots()
  }
})
</script>

<style scoped>
.parking-lot-list {
  margin-bottom: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.list-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.lot-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  min-height: 200px;
}

.empty-tip {
  grid-column: 1 / -1;
  text-align: center;
  color: #909399;
  padding: 40px;
}

.lot-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
}

.lot-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.lot-title {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.lot-actions {
  display: flex;
  gap: 8px;
}

.lot-card-body .kv {
  display: flex;
  margin-bottom: 8px;
}

.lot-card-body .k {
  width: 80px;
  color: #909399;
  font-size: 12px;
}

.lot-card-body .v {
  flex: 1;
  color: #303133;
  font-size: 12px;
  font-family: monospace;
}

.lot-card-body .desc {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
}
</style>
