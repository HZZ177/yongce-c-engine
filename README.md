# 永策C端引擎测试工具

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.4+-4FC08D.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)
![Element Plus](https://img.shields.io/badge/Element%20Plus-2.4+-409EFF.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

一个专业的车场管理系统C端引擎测试工具，采用现代化的前后端分离架构，支持封闭车场和路侧车场的全面管理功能。

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目架构](#项目架构)
- [快速开始](#快速开始)
- [功能模块](#功能模块)
- [API接口](#api接口)
- [前端架构](#前端架构)

## 🚀 项目简介

永策C端引擎测试工具是一个面向车场管理系统的专业测试平台，提供完整的车场设备管理、车辆进出管理、支付管理等功能。项目采用前后端分离架构，支持多环境配置，具备良好的扩展性和维护性。

### 核心价值

- **🎯 专业测试**：专为车场管理系统C端引擎设计的测试工具
- **🏗️ 模块化架构**：清晰的模块划分，便于功能扩展和维护
- **🔧 多环境支持**：支持测试环境和灰度环境的无缝切换
- **📱 现代化UI**：基于Element Plus的现代化用户界面
- **⚡ 高性能**：FastAPI后端 + Vue3前端，提供卓越的性能体验

## ✨ 功能特性

### 封闭车场管理
- **设备管理**：设备上线/下线、状态监控、通道长抬控制
- **车辆管理**：车辆入场/出场、在场查询、多种开闸模式
- **支付管理**：订单支付、支付信息查询
- **环境配置**：多环境切换、车场选择、服务器配置
- **操作历史**：完整的操作记录和历史追踪

### 路侧车场管理（规划中）
- **设备监控**：路侧设备状态管理
- **车位管理**：路侧车位占用监控
- **收费管理**：路侧停车收费功能

### 系统功能
- **实时监控**：设备状态实时轮询更新
- **二维码管理**：通道二维码生成和管理
- **日志记录**：详细的操作日志和错误追踪
- **响应式设计**：支持多种屏幕尺寸的自适应布局

## 🛠️ 技术栈

### 后端技术
- **框架**：FastAPI 0.100.0 - 现代化的Python Web框架
- **运行时**：Python 3.8+ - 稳定的Python运行环境
- **HTTP服务器**：Uvicorn - 高性能ASGI服务器
- **数据验证**：Pydantic 2.0+ - 强类型数据验证
- **HTTP客户端**：HTTPX - 异步HTTP客户端
- **日志系统**：Loguru - 优雅的日志处理
- **配置管理**：PyYAML - YAML配置文件支持

### 前端技术
- **框架**：Vue.js 3.4+ - 渐进式JavaScript框架
- **语言**：TypeScript 5.3+ - 类型安全的JavaScript超集
- **UI组件库**：Element Plus 2.4+ - 基于Vue3的组件库
- **状态管理**：Pinia 2.1+ - Vue的现代状态管理库
- **路由管理**：Vue Router 4.2+ - Vue官方路由管理器
- **HTTP客户端**：Axios 1.6+ - 基于Promise的HTTP客户端
- **构建工具**：Vite 5.0+ - 下一代前端构建工具

### 开发工具
- **代码检查**：ESLint - JavaScript/TypeScript代码检查
- **类型检查**：Vue-tsc - Vue单文件组件类型检查
- **包管理**：npm - Node.js包管理器

## 🏗️ 项目架构

### 整体架构
```
┌─────────────────┐    HTTP/API    ┌─────────────────┐
│   前端应用      │ ◄─────────────► │   后端API       │
│   Vue3 + TS     │                │   FastAPI       │
│   Element Plus  │                │   Python        │
└─────────────────┘                └─────────────────┘
         │                                   │
         ▼                                   ▼
┌─────────────────┐                ┌─────────────────┐
│   静态资源      │                │   业务逻辑      │
│   Vite构建      │                │   模块化设计    │
└─────────────────┘                └─────────────────┘
```

### 后端架构
```
yongce-c-engine/
├── main.py                 # 应用入口
├── requirements.txt        # Python依赖
├── core/                   # 核心模块
│   ├── logger.py          # 日志配置
│   ├── middleware.py      # 中间件
│   └── file_path.py       # 文件路径工具
├── apps/                   # 业务应用
│   ├── closeApp/          # 封闭车场模块
│   │   ├── router.py      # 路由定义
│   │   ├── service.py     # 业务逻辑
│   │   ├── schema.py      # 数据模型
│   │   ├── config.py      # 配置管理
│   │   └── util.py        # 工具函数
│   └── roadApp/           # 路侧车场模块
└── static/                # 静态资源
```

### 前端架构（模块化设计）
```
frontend/src/
├── main.ts                # 应用入口
├── App.vue               # 根组件
├── router/               # 路由配置
├── modules/              # 功能模块
│   ├── closeApp/         # 封闭车场模块
│   │   ├── api/          # API接口
│   │   ├── components/   # 业务组件
│   │   ├── stores/       # 状态管理
│   │   ├── types/        # 类型定义
│   │   └── views/        # 页面组件
│   ├── roadApp/          # 路侧车场模块
│   └── shared/           # 共享模块
│       ├── components/   # 共享组件
│       └── types/        # 共享类型
├── views/                # 顶层页面
└── types/                # 全局类型
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **Node.js**: 16.0 或更高版本
- **npm**: 8.0 或更高版本

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd yongce-c-engine
```

#### 2. 后端环境搭建
```bash
# 安装Python依赖
pip install -r requirements.txt

# 启动后端服务
python main.py
```

后端服务将在 `http://localhost:17771` 启动

#### 3. 前端环境搭建
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:3000` 启动

#### 4. 访问应用
- **前端应用**: http://localhost:3000
- **API文档**: http://localhost:17771/docs
- **封闭车场**: http://localhost:3000/close
- **路侧车场**: http://localhost:3000/road

### 开发环境配置

#### 后端配置
在 `apps/closeApp/config.yml` 中配置相关参数：
```yaml
# 服务器配置
servers:
  test: "192.168.24.114"
  prod: "47.108.129.101"

# 车场配置
lots:
  test:
    - id: "280025535"
      name: "天府新谷测试环境车场1"
  prod:
    - id: "280030477"
      name: "成都灰度环境封闭测试车场"
```

#### 前端配置
前端配置通过环境变量和本地存储管理，支持：
- 环境切换（测试/灰度）
- 车场选择
- 设备IP配置
- 云助手Token设置

## 📦 功能模块

### 封闭车场管理模块

#### 环境配置
- **多环境支持**：测试环境和灰度环境一键切换
- **车场选择**：支持多个车场的动态选择
- **服务器配置**：自动适配不同环境的服务器IP

#### 设备管理
- **设备上线/下线**：支持单个或批量设备操作
- **实时状态监控**：5秒间隔自动轮询设备状态
- **通道长抬控制**：支持通道长抬状态的查询和变更
- **通道二维码**：生成和管理通道二维码

**主要功能**：
```typescript
// 设备操作示例
await deviceApi.deviceOn({
  device_list: "192.168.24.114,192.168.24.115",
  server_ip: "192.168.24.114"
})
```

#### 车辆管理
- **车辆入场**：支持有牌车和无牌车入场
- **车辆出场**：多种出场模式（压地感/直接开闸）
- **在场查询**：实时查询车辆在场状态
- **日期范围查询**：支持自定义时间范围查询

**开闸模式**：
- `0`: 压地感模式
- `1`: 相机直接开闸放行

#### 支付管理
- **订单支付**：模拟支付订单处理
- **支付查询**：查询订单支付状态和信息
- **支付历史**：完整的支付记录追踪

#### 操作历史
- **实时记录**：所有操作的详细记录
- **执行时长**：精确的操作耗时统计
- **结果追踪**：成功/失败状态和详细信息
- **参数记录**：完整的请求参数保存

### 路侧车场管理模块（开发中）

当前状态：基础架构已搭建，功能开发中

**规划功能**：
- 路侧设备管理
- 车位状态监控
- 路侧停车收费

## 🔌 API接口

### 封闭车场API

#### 设备管理接口
```http
# 设备上线
GET /closeApp/deviceOn?device_list=192.168.24.114&server_ip=192.168.24.114

# 设备下线
GET /closeApp/deviceOff?device_list=192.168.24.114&server_ip=192.168.24.114

# 设备状态查询
GET /closeApp/deviceStatus?device_ips=192.168.24.114&ttl_seconds=30
```

#### 车辆管理接口
```http
# 车辆入场
GET /closeApp/carIn?car_no=川A12345&lot_id=280025535&server_ip=192.168.24.114

# 车辆出场
GET /closeApp/carOut?car_no=川A12345&lot_id=280025535&server_ip=192.168.24.114

# 查询在场车辆
GET /closeApp/carOnPark?lot_id=280025535&car_no=川A12345
```

#### 支付管理接口
```http
# 支付订单
GET /closeApp/payOrder?car_no=川A12345&lot_id=280025535

# 查询支付信息
GET /closeApp/payInfo?car_no=川A12345&lot_id=280025535
```

#### 节点状态接口
```http
# 查询节点状态
GET /closeApp/nodeStatus?lot_id=280025535&cloud_kt_token=xxx

# 变更节点状态
GET /closeApp/changeNodeStatus?lot_id=280025535&node_ids=1&status=1
```

### API响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 响应数据
  }
}
```

### 错误处理
所有API接口都遵循统一的错误处理格式：
```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

## 🏛️ 前端架构

### 模块化设计

项目采用模块化架构，每个业务模块都有独立的文件结构：

```
modules/
├── closeApp/              # 封闭车场模块
│   ├── api/              # API接口层
│   │   └── index.ts      # 统一的API接口
│   ├── components/       # 业务组件
│   │   ├── VehicleManagement.vue    # 车辆管理
│   │   ├── PaymentManagement.vue    # 支付管理
│   │   ├── OperationHistory.vue     # 操作历史
│   │   └── QrCodeDialog.vue         # 二维码弹窗
│   ├── stores/           # 状态管理
│   │   ├── environment.ts           # 环境配置
│   │   └── history.ts               # 历史记录
│   ├── types/            # 类型定义
│   │   └── index.ts      # 模块类型
│   └── views/            # 页面组件
│       └── index.vue     # 主页面
├── roadApp/              # 路侧车场模块（预留）
└── shared/               # 共享模块
    ├── components/       # 共享组件
    │   └── StandardTooltip.vue
    └── types/            # 共享类型
        └── index.ts
```

### 状态管理

使用Pinia进行状态管理，每个模块有独立的store：

#### 环境配置Store
```typescript
// modules/closeApp/stores/environment.ts
export const useEnvironmentStore = defineStore('environment', () => {
  const currentEnv = ref<Environment>('test')
  const currentLotId = ref<string>('')
  const deviceStatus = ref({ inDevice: false, outDevice: false })

  // 环境切换
  const setEnvironment = (env: Environment) => {
    currentEnv.value = env
    localStorage.setItem('yongce-current-env', env)
  }

  return { currentEnv, currentLotId, deviceStatus, setEnvironment }
})
```

#### 历史记录Store
```typescript
// modules/closeApp/stores/history.ts
export const useHistoryStore = defineStore('history', () => {
  const history = ref<OperationHistory[]>([])

  const addHistory = (operation: Omit<OperationHistory, 'id' | 'timestamp'>) => {
    history.value.unshift({
      id: generateId(),
      timestamp: new Date().toISOString(),
      ...operation
    })
  }

  return { history, addHistory }
})
```

### 组件设计

#### 组件通信
- **Props/Emit**: 父子组件通信
- **Pinia Store**: 跨组件状态共享
- **Provide/Inject**: 深层组件通信

#### 组件复用
- **共享组件**: 放在 `modules/shared/components/`
- **业务组件**: 放在各自模块的 `components/` 目录
- **页面组件**: 放在模块的 `views/` 目录

### API层设计

每个模块有独立的API层，统一管理HTTP请求：

```typescript
// modules/closeApp/api/index.ts
export const deviceApi = {
  deviceOn: async (params: DeviceOnOffRequest): Promise<ApiResponse> => {
    const response = await api.get('/deviceOn', { params })
    return response.data
  },

  deviceOff: async (params: DeviceOnOffRequest): Promise<ApiResponse> => {
    const response = await api.get('/deviceOff', { params })
    return response.data
  }
}
```
