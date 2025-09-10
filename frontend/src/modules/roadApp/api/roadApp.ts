import axios from 'axios'
import type {
  ApiResponse,
  RoadCarInOutRequest,
  RoadCarOnParkRequest,
  RoadFeeInquiryRequest,
  RoadPresentCarInfoRequest
} from '../types'

// 创建axios实例
const api = axios.create({
  baseURL: '/roadApp',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('路侧API请求:', config.method?.toUpperCase(), config.url, config.params || config.data)
    return config
  },
  (error) => {
    console.error('路侧API请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('路侧API响应:', response.status, response.data)
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
    console.error('路侧API响应错误:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)



// 路侧车辆管理API
export const roadVehicleApi = {
  // 路侧车辆入场
  carIn: async (params: RoadCarInOutRequest): Promise<ApiResponse> => {
    const response = await api.get('/carIn', { params })
    return response.data
  },

  // 路侧车辆出场
  carOut: async (params: RoadCarInOutRequest): Promise<ApiResponse> => {
    const response = await api.get('/carOut', { params })
    return response.data
  },

  // 路侧车辆出场(同时无感)
  carOutSettle: async (params: RoadCarInOutRequest): Promise<ApiResponse> => {
    const response = await api.get('/carOutSettle', { params })
    return response.data
  },

  // 查询路侧在场车辆
  carOnPark: async (params: RoadCarOnParkRequest): Promise<ApiResponse> => {
    const response = await api.get('/carOnPark', { params })
    return response.data
  },

  // 查询路侧在场车信息（新接口）
  presentCarInfo: async (params: RoadPresentCarInfoRequest): Promise<ApiResponse> => {
    const response = await api.get('/presentCarInfo', { params })
    return response.data
  },

  // 获取路段列表
  roadPage: async (lotId: string): Promise<ApiResponse> => {
    const response = await api.get('/roadPage', { params: { lot_id: lotId } })
    return response.data
  },

  // 获取车位列表
  parkspacePage: async (roadCode: string, lotId: string): Promise<ApiResponse> => {
    const response = await api.get('/parkspacePage', { params: { road_code: roadCode, lot_id: lotId } })
    return response.data
  }
}

// 路侧查费API
export const roadFeeApi = {
  // 路侧查费
  feeInquiry: async (params: RoadFeeInquiryRequest): Promise<ApiResponse> => {
    const response = await api.get('/feeInquiry', { params })
    return response.data
  }
}



// 路侧配置管理API
export const roadConfigApi = {
  // 获取路侧配置信息
  getConfig: async (): Promise<ApiResponse> => {
    const response = await api.get('/config')
    return response.data
  },

  // 添加路侧车场配置
  addParkingLot: async (env: string, lotConfig: any): Promise<ApiResponse> => {
    const response = await api.post('/config/parking-lot', lotConfig, {
      params: { env }
    })
    return response.data
  },

  // 更新路侧车场配置
  updateParkingLot: async (lotId: string, updates: any): Promise<ApiResponse> => {
    const response = await api.put(`/config/parking-lot/${lotId}`, updates)
    return response.data
  },

  // 删除路侧车场配置
  deleteParkingLot: async (lotId: string): Promise<ApiResponse> => {
    const response = await api.delete(`/config/parking-lot/${lotId}`)
    return response.data
  },

  // 获取单个路侧车场配置
  getParkingLot: async (lotId: string): Promise<ApiResponse> => {
    const response = await api.get(`/config/parking-lot/${lotId}`)
    return response.data
  }
}

export default api
