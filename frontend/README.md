# 永策C端引擎测试工具前端

这是一个基于 Vue 3 + TypeScript + Element Plus 的停车场管理系统前端界面，用于方便地测试和管理封闭车场和路侧车场的各项功能。

## 功能特性

### 封闭车场管理
- **环境配置**: 支持测试环境和生产环境的快速切换
- **设备管理**: 设备上线/下线、批量操作、状态监控
- **车辆管理**: 车辆入场/出场、查询在场车辆
- **支付管理**: 模拟支付、查询订单
- **操作历史**: 记录所有操作的历史记录

### 路侧车场管理
- 预留页面，功能开发中

## 技术栈

- **Vue 3.4+**: 使用 Composition API
- **TypeScript 5.0+**: 类型安全
- **Vite 5.0+**: 快速构建工具
- **Element Plus 2.4+**: UI组件库
- **Pinia 2.1+**: 状态管理
- **Vue Router 4.2+**: 路由管理
- **Axios 1.6+**: HTTP客户端

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API接口封装
│   ├── components/       # 通用组件
│   ├── router/          # 路由配置
│   ├── stores/          # 状态管理
│   ├── types/           # TypeScript类型定义
│   ├── views/           # 页面组件
│   ├── App.vue          # 根组件
│   └── main.ts          # 应用入口
├── public/              # 静态资源
├── index.html           # HTML模板
├── package.json         # 项目配置
├── vite.config.ts       # Vite配置
└── tsconfig.json        # TypeScript配置
```

## 开发环境

### 环境要求
- Node.js 16.0+
- npm 或 yarn

### 安装依赖
```bash
cd frontend
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 预览生产版本
```bash
npm run preview
```

## 使用说明

### 环境配置
1. 在页面顶部选择测试环境或生产环境
2. 选择对应的车场ID
3. 系统会自动获取对应的服务器IP和设备信息

### 设备管理
1. 查看当前设备状态（在线/离线）
2. 点击单个设备的上线/下线按钮进行控制
3. 使用批量操作按钮同时控制所有设备

### 车辆管理
1. 输入车牌号
2. 选择车辆颜色、识别度等参数
3. 点击相应按钮执行车辆入场、出场或查询操作

### 支付管理
1. 输入车牌号
2. 点击模拟支付或查询订单
3. 查看支付结果和订单信息

### 操作历史
- 查看所有操作的历史记录
- 支持删除单条记录或清空所有记录
- 显示操作耗时和结果状态

## 配置说明

### 环境配置
在 `src/stores/environment.ts` 中配置不同环境的车场信息：

```typescript
const lotConfigs = {
  test: [
    {
      id: '280025535',
      name: '测试车场',
      serverIp: '192.168.0.183',
      inDeviceIp: '192.168.24.115',
      outDeviceIp: '192.168.24.116'
    }
  ],
  prod: [
    {
      id: '280030477',
      name: '生产车场',
      serverIp: '192.168.0.236',
      inDeviceIp: '',
      outDeviceIp: ''
    }
  ]
}
```

### API配置
在 `vite.config.ts` 中配置API代理：

```typescript
server: {
  proxy: {
    '/closeApp': {
      target: 'http://localhost:17771',
      changeOrigin: true
    }
  }
}
```

## 开发指南

### 添加新功能
1. 在 `src/api/` 中添加API接口
2. 在 `src/components/` 中创建组件
3. 在 `src/views/` 中创建页面
4. 在 `src/router/` 中配置路由

### 状态管理
使用 Pinia 进行状态管理：
- `environment.ts`: 环境配置状态
- `history.ts`: 操作历史状态

### 样式规范
- 使用 Element Plus 组件库
- 遵循响应式设计原则
- 支持深色模式

## 部署说明

### 构建
```bash
npm run build
```

### 部署到服务器
将 `dist` 目录下的文件部署到Web服务器即可。

### Nginx配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /closeApp {
        proxy_pass http://localhost:17771;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 注意事项

1. 确保后端API服务正常运行
2. 检查网络连接和防火墙设置
3. 注意环境配置的正确性
4. 定期清理操作历史记录

## 更新日志

### v1.0.0
- 初始版本发布
- 支持封闭车场管理功能
- 预留路侧车场功能页面 