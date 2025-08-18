import axios from 'axios'
import type { 
  ApiResponse, 
  DeviceOnOffRequest, 
  CarInOutRequest, 
  CarOnParkRequest, 
  PayOrderRequest,
  NodeStatusRequest,
  NodeStatusResponse,
  ChangeNodeStatusRequest,
  GetChannelQrPicResponse
} from '../types'

// 创建axios实例
const api = axios.create({
  baseURL: '/closeApp',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API请求:', config.method?.toUpperCase(), config.url, config.params || config.data)
    return config
  },
  (error) => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API响应:', response.status, response.data)
    // 适配新的响应格式 { code, message, data }
    if (response.data && typeof response.data === 'object') {
      // 将新的响应格式转换为前端期望的格式
      const { code, message, data } = response.data
      response.data = {
        resultCode: code,
        resultMsg: message,
        data: data
      }
    }
    return response
  },
  (error) => {
    console.error('API响应错误:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// 设备管理API
export const deviceApi = {
  // 设备上线
  deviceOn: async (params: DeviceOnOffRequest): Promise<ApiResponse> => {
    const response = await api.get('/deviceOn', { params })
    return response.data
  },

  // 设备下线
  deviceOff: async (params: DeviceOnOffRequest): Promise<ApiResponse> => {
    const response = await api.get('/deviceOff', { params })
    return response.data
  },

  // 查询设备真实在线状态
  deviceStatus: async (params: { device_ips: string, ttl_seconds?: number }): Promise<ApiResponse> => {
    const response = await api.get('/deviceStatus', { params })
    return response.data
  },

  // 获取通道二维码图片
  getChannelQrPic: async (params: { lot_id: string }): Promise<ApiResponse<GetChannelQrPicResponse>> => {
    const response = await api.get('/getChannelQrPic', { params })
    return response.data
  }
}

// 车辆管理API
export const vehicleApi = {
  // 车辆入场
  carIn: async (params: CarInOutRequest): Promise<ApiResponse> => {
    const response = await api.get('/carIn', { params })
    return response.data
  },

  // 车辆出场
  carOut: async (params: CarInOutRequest): Promise<ApiResponse> => {
    const response = await api.get('/carOut', { params })
    return response.data
  },

  // 查询在场车辆
  carOnPark: async (params: CarOnParkRequest): Promise<ApiResponse> => {
    const response = await api.get('/carOnPark', { params })
    return response.data
  }
}

// 支付管理API
export const paymentApi = {
  // 模拟支付订单
  payOrder: async (params: PayOrderRequest): Promise<ApiResponse> => {
    const response = await api.get('/payOrder', { params })
    return response.data
  },
  // 查询订单（获取支付信息）
  queryOrder: async (params: PayOrderRequest): Promise<ApiResponse> => {
    const response = await api.get('/payInfo', { params })
    return response.data
  }
}

// 节点状态API
export const nodeApi = {
  nodeStatus: async (params: NodeStatusRequest): Promise<NodeStatusResponse> => {
    const response = await api.get('/nodeStatus', { params })
    // 此接口保持原始格式返回
    return response.data as unknown as NodeStatusResponse
  },
  
  changeNodeStatus: async (params: ChangeNodeStatusRequest): Promise<ApiResponse> => {
    const response = await api.get('/changeNodeStatus', { params })
    return response.data
  }
}

export default api
