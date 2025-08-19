<template>
  <el-dialog
    v-model="visible"
    :title="`${currentEnv === 'test' ? '测试' : '灰度'}环境车场管理`"
    width="800px"
    :before-close="handleClose"
  >
    <!-- 车场列表 -->
    <div class="parking-lot-list">
      <div class="list-header">
        <h3>车场列表</h3>
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          新增车场
        </el-button>
      </div>
      
      <div class="lot-card-grid" v-loading="lotsLoading">
        <div v-if="!lotsLoading && currentLots.length === 0" class="empty-tip">暂无车场配置</div>
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
            <div class="kv"><span class="k">服务器IP</span><span class="v">{{ lot.server_ip || '-' }}</span></div>
            <div class="kv"><span class="k">入口设备IP</span><span class="v">{{ lot.devices?.in_device || '-' }}</span></div>
            <div class="kv"><span class="k">出口设备IP</span><span class="v">{{ lot.devices?.out_device || '-' }}</span></div>
            <div class="desc" v-if="lot.description">{{ lot.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑车场对话框 -->
    <el-dialog
      v-model="formDialogVisible"
      :title="isEditing ? '编辑车场' : '新增车场'"
      width="500px"
      append-to-body
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="车场ID" prop="id">
          <el-input
            v-model="formData.id"
            :disabled="isEditing"
            placeholder="请输入车场ID"
          />
        </el-form-item>
        <el-form-item label="车场名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入车场名称"
          />
        </el-form-item>
        <el-form-item label="服务器IP" prop="serverIp">
          <el-input
            v-model="formData.serverIp"
            placeholder="请输入服务器IP"
          />
        </el-form-item>
        <el-form-item label="入口设备IP" prop="inDeviceIp">
          <el-input
            v-model="formData.inDeviceIp"
            placeholder="请输入入口设备IP"
          />
        </el-form-item>
        <el-form-item label="出口设备IP" prop="outDeviceIp">
          <el-input
            v-model="formData.outDeviceIp"
            placeholder="请输入出口设备IP"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            placeholder="请输入车场描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ isEditing ? '更新' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { Environment } from '@/modules/shared/types'
import { parkingLotApi } from '../api/closeApp'
import api from '../api/closeApp'

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

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 车场列表数据
const currentLots = ref<any[]>([])
const lotsLoading = ref(false)

// 获取车场配置数据
const loadParkingLots = async () => {
  try {
    lotsLoading.value = true
    const response = await api.get('/config')
    const configData = response.data.data

    console.log('获取到的配置数据:', configData) // 调试日志

    // 根据当前环境获取车场列表
    const parkingLots = configData.parking_lots?.[props.currentEnv] || []
    console.log('当前环境车场列表:', parkingLots) // 调试日志

    currentLots.value = parkingLots
  } catch (error) {
    console.error('获取车场配置失败:', error)
    ElMessage.error('获取车场配置失败')
    currentLots.value = []
  } finally {
    lotsLoading.value = false
  }
}

// 表单相关
const formDialogVisible = ref(false)
const formRef = ref<FormInstance>()
const isEditing = ref(false)
const submitting = ref(false)
const editingLotId = ref('')

const formData = ref({
  id: '',
  name: '',
  serverIp: '',
  description: '',
  inDeviceIp: '',
  outDeviceIp: ''
})

// 表单验证规则
const formRules: FormRules = {
  id: [
    { required: true, message: '请输入车场ID', trigger: 'blur' },
    { pattern: /^\d+$/, message: '车场ID必须为数字', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入车场名称', trigger: 'blur' }
  ],
  serverIp: [
    { required: true, message: '请输入服务器IP', trigger: 'blur' },
    {
      pattern: /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
      message: '请输入正确的IP地址格式',
      trigger: 'blur'
    }
  ],
  inDeviceIp: [
    { required: true, message: '请输入入口设备IP', trigger: 'blur' },
    {
      pattern: /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
      message: '请输入正确的IP地址格式',
      trigger: 'blur'
    }
  ],
  outDeviceIp: [
    { required: true, message: '请输入出口设备IP', trigger: 'blur' },
    {
      pattern: /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
      message: '请输入正确的IP地址格式',
      trigger: 'blur'
    }
  ]
}

// 重置表单
const resetForm = () => {
  formData.value = {
    id: '',
    name: '',
    serverIp: '',
    description: '',
    inDeviceIp: '',
    outDeviceIp: ''
  }
  isEditing.value = false
  editingLotId.value = ''
}

// 显示新增对话框
const showAddDialog = () => {
  resetForm()
  formDialogVisible.value = true
}

// 编辑车场
const editLot = (lot: any) => {
  isEditing.value = true
  editingLotId.value = lot.id

  console.log('编辑车场数据:', lot) // 调试日志

  formData.value = {
    id: lot.id,
    name: lot.name,
    serverIp: lot.server_ip || '', // 使用原始数据结构
    description: lot.description || '',
    inDeviceIp: lot.devices?.in_device || '',
    outDeviceIp: lot.devices?.out_device || ''
  }

  console.log('表单数据:', formData.value) // 调试日志

  formDialogVisible.value = true
}

// 删除车场
const deleteLot = async (lot: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除车场 "${lot.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const result = await parkingLotApi.deleteParkingLot(lot.id)
    if (result.resultCode === 200) {
      ElMessage.success('车场删除成功')
      // 先通知主界面刷新缓存数据
      emit('refresh')
      // 等待一下，然后刷新编辑器数据
      await new Promise(resolve => setTimeout(resolve, 100))
      await loadParkingLots()
    } else {
      ElMessage.error(result.resultMsg || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除车场失败:', error)
      ElMessage.error('删除车场失败')
    }
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    let result
    if (isEditing.value) {
      // 更新车场
      const updates = {
        name: formData.value.name,
        server_ip: formData.value.serverIp,
        description: formData.value.description,
        devices: {
          in_device: formData.value.inDeviceIp,
          out_device: formData.value.outDeviceIp
        }
      }
      result = await parkingLotApi.updateParkingLot(editingLotId.value, updates)
    } else {
      // 添加车场
      const lotConfig = {
        id: formData.value.id,
        name: formData.value.name,
        server_ip: formData.value.serverIp,
        description: formData.value.description,
        devices: {
          in_device: formData.value.inDeviceIp,
          out_device: formData.value.outDeviceIp
        }
      }
      result = await parkingLotApi.addParkingLot(props.currentEnv, lotConfig)
    }

    if (result.resultCode === 200) {
      ElMessage.success(isEditing.value ? '车场更新成功' : '车场添加成功')
      formDialogVisible.value = false
      // 先通知主界面刷新缓存数据
      emit('refresh')
      // 等待一下，然后刷新编辑器数据
      await new Promise(resolve => setTimeout(resolve, 100))
      await loadParkingLots()
    } else {
      ElMessage.error(result.resultMsg || '操作失败')
    }
  } catch (error: any) {
    console.error('提交表单失败:', error)
    if (error.fields) {
      // 表单验证失败
      return
    }
    ElMessage.error('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 关闭主对话框
const handleClose = () => {
  visible.value = false
}

// 监听弹窗打开，加载数据
watch(visible, (newVal) => {
  if (newVal) {
    loadParkingLots()
  }
})

// 监听表单对话框关闭，重置表单
watch(formDialogVisible, (newVal) => {
  if (!newVal) {
    formRef.value?.resetFields()
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

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

/* 卡片网格布局 */
.lot-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.empty-tip {
  text-align: center;
  color: #94a3b8;
  padding: 16px 0;
}

.lot-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.lot-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.lot-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.lot-actions {
  display: flex;
  gap: 8px;
}

.lot-card-body {
  display: grid;
  grid-template-columns: 1fr;
  gap: 6px;
}

.kv {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #374151;
}
.kv .k { color: #6b7280; }
.kv .v { font-weight: 500; }

.desc {
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
  background: #f9fafb;
  border-radius: 6px;
  padding: 8px;
  line-height: 1.4;
  word-break: break-all;
}
</style>
