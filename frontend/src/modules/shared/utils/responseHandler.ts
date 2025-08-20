import { ElMessage } from 'element-plus'
import type { ApiResponse } from '../types'

/**
 * 统一的API响应处理工具类
 * 用于标准化处理后端返回的成功/失败状态和消息提取
 */
export class ResponseHandler {
  /**
   * 判断API响应是否成功
   * @param response API响应对象
   * @returns 是否成功
   */
  static isSuccess(response: ApiResponse): boolean {
    return response.resultCode === 200
  }

  /**
   * 提取API响应中的消息
   * @param response API响应对象
   * @param defaultMessage 默认消息（当响应中没有消息时使用）
   * @returns 消息字符串
   */
  static getMessage(response: ApiResponse, defaultMessage?: string): string {
    return response.resultMsg || defaultMessage || '操作完成'
  }

  /**
   * 显示成功消息提示
   * @param response API响应对象
   * @param defaultMessage 默认成功消息
   */
  static showSuccessMessage(response: ApiResponse, defaultMessage?: string): void {
    const message = this.getMessage(response, defaultMessage)
    ElMessage.success(message)
  }

  /**
   * 显示错误消息提示
   * @param response API响应对象或错误对象
   * @param defaultMessage 默认错误消息
   */
  static showErrorMessage(response: ApiResponse | Error, defaultMessage?: string): void {
    let message: string
    
    if (response instanceof Error) {
      message = response.message || defaultMessage || '操作失败'
    } else {
      message = this.getMessage(response, defaultMessage)
    }
    
    ElMessage.error(message)
  }

  /**
   * 获取操作历史记录的结果状态
   * @param response API响应对象
   * @returns 'success' | 'error'
   */
  static getHistoryResult(response: ApiResponse): 'success' | 'error' {
    return this.isSuccess(response) ? 'success' : 'error'
  }

  /**
   * 处理API调用的完整流程
   * @param response API响应对象
   * @param successMessage 成功时的默认消息
   * @param errorMessage 失败时的默认消息
   * @param showToast 是否显示顶部提示（默认true）
   * @returns 处理结果对象
   */
  static handleResponse(
    response: ApiResponse,
    successMessage?: string,
    errorMessage?: string,
    showToast: boolean = true
  ): {
    success: boolean
    message: string
    historyResult: 'success' | 'error'
    toastMessage: string
    historyMessage: string
  } {
    const success = this.isSuccess(response)
    const historyResult = this.getHistoryResult(response)

    // 获取后端返回的消息和数据
    const backendMessage = response.resultMsg || ''
    const data = response.data

    // 顶部提示消息：成功时显示操作成功，失败时显示操作失败+data
    let toastMessage: string
    if (success) {
      toastMessage = backendMessage || successMessage || '操作成功'
    } else {
      const baseMessage = backendMessage || errorMessage || '操作失败'
      const dataStr = data ? `，详情：${typeof data === 'string' ? data : JSON.stringify(data)}` : ''
      toastMessage = baseMessage + dataStr
    }

    // 历史记录消息：无论成功失败都显示完整信息包括data
    let historyMessage: string
    const baseHistoryMessage = backendMessage || (success ? successMessage : errorMessage) || (success ? '操作成功' : '操作失败')
    const dataStr = data ? `，数据：${typeof data === 'string' ? data : JSON.stringify(data)}` : ''
    historyMessage = baseHistoryMessage + dataStr

    // 显示顶部提示
    if (showToast) {
      if (success) {
        ElMessage.success(toastMessage)
      } else {
        ElMessage.error(toastMessage)
      }
    }

    return {
      success,
      message: historyMessage, // 返回历史记录用的消息
      historyResult,
      toastMessage,
      historyMessage
    }
  }

  /**
   * 处理异常错误的统一方法
   * @param error 错误对象
   * @param defaultMessage 默认错误消息
   * @returns 错误处理结果
   */
  static handleError(error: any, defaultMessage?: string): {
    success: false
    message: string
    historyResult: 'error'
  } {
    const message = error?.message || error?.response?.data?.message || defaultMessage || '操作失败'
    ElMessage.error(message)

    return {
      success: false,
      message,
      historyResult: 'error'
    }
  }
}

// 导出便捷方法
export const {
  isSuccess,
  getMessage,
  showSuccessMessage,
  showErrorMessage,
  getHistoryResult,
  handleResponse,
  handleError
} = ResponseHandler
