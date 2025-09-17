"""
HTTP请求封装模块
基于requests库的简单封装，提供完整的日志记录功能
"""

import json
import time
import traceback
from typing import Dict, Any, Optional, Union
from urllib.parse import urlparse

import requests
from core.logger import logger


class RequestClient:
    """HTTP请求客户端封装类"""
    
    def __init__(self, timeout: int = 10, log_sensitive: bool = False):
        """
        初始化请求客户端
        
        Args:
            timeout: 请求超时时间（秒）
            log_sensitive: 是否记录敏感信息（如密码、token等）
        """
        self.timeout = timeout
        self.log_sensitive = log_sensitive
        self.session = requests.Session()
        
        # 敏感字段列表（这些字段在日志中会被脱敏）
        # self.sensitive_fields = {
        #     'password', 'token', 'authorization', 'api_key', 'secret',
        #     'access_token', 'refresh_token', 'session_id', 'kt-token'
        # }
        self.sensitive_fields = {}
    
    def _sanitize_data(self, data: Any) -> Any:
        """脱敏处理数据"""
        if not self.log_sensitive and isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if key.lower() in self.sensitive_fields:
                    sanitized[key] = '***'
                else:
                    sanitized[key] = value
            return sanitized
        return data
    
    def _log_request(self, method: str, url: str, headers: Optional[Dict] = None, 
                    data: Any = None, json_data: Any = None, **kwargs):
        """记录请求日志"""
        try:
            # 解析URL
            parsed_url = urlparse(url)
            
            # 构建日志信息
            log_info = {
                "请求方法": method.upper(),
                "请求地址": url,
                "请求域名": parsed_url.netloc,
                "请求路径": parsed_url.path,
                "请求参数": parsed_url.query if parsed_url.query else "无"
            }
            
            # 记录请求头
            if headers:
                sanitized_headers = self._sanitize_data(headers)
                log_info["请求头"] = sanitized_headers
            
            # 记录请求体
            if data:
                log_info["请求数据"] = self._sanitize_data(data)
            elif json_data:
                log_info["请求JSON"] = self._sanitize_data(json_data)
            elif 'json' in kwargs:
                log_info["请求JSON"] = self._sanitize_data(kwargs['json'])
            
            # 记录其他参数
            if kwargs:
                other_params = {k: v for k, v in kwargs.items() 
                              if k not in ['headers', 'data', 'json_data', 'json', 'timeout']}
                if other_params:
                    log_info["其他参数"] = other_params
            
            logger.info(f"发送HTTP请求: {json.dumps(log_info, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"记录请求日志失败: {str(e)}")
    
    def _log_response(self, response: requests.Response, duration: float):
        """记录响应日志"""
        try:
            log_info = {
                "响应状态码": response.status_code,
                "响应耗时": f"{duration:.3f}秒",
                "响应头": dict(response.headers),
                "响应大小": len(response.content)
            }
            
            # 记录响应内容
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    response_json = response.json()
                    log_info["响应内容"] = self._sanitize_data(response_json)
                else:
                    # 对于非JSON响应，只记录前500个字符
                    content = response.text[:500]
                    if len(response.text) > 500:
                        content += "..."
                    log_info["响应内容"] = content
            except Exception:
                log_info["响应内容"] = "无法解析响应内容"
            
            if response.status_code >= 400:
                logger.error(f"HTTP请求失败，返回响应: {json.dumps(log_info, ensure_ascii=False)}")
            else:
                logger.info(f"HTTP请求成功，返回响应: {json.dumps(log_info, ensure_ascii=False)}")
                
        except Exception as e:
            logger.error(f"记录响应日志失败: {str(e)}")
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """执行HTTP请求并记录日志"""
        start_time = time.time()
        
        # 设置默认超时
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        # 记录请求日志
        self._log_request(method, url, **kwargs)
        
        try:
            # 执行请求
            response = self.session.request(method, url, **kwargs)
            duration = time.time() - start_time
            
            # 记录响应日志
            self._log_response(response, duration)
            
            return response
            
        except requests.RequestException as e:
            duration = time.time() - start_time
            logger.error(f"HTTP请求异常: {method.upper()} {url} - {str(e)} - 耗时: {duration:.3f}秒")
            logger.error(f"异常详情: {traceback.format_exc()}")
            raise
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"HTTP请求未知异常: {method.upper()} {url} - {str(e)} - 耗时: {duration:.3f}秒")
            logger.error(f"异常详情: {traceback.format_exc()}")
            raise
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """发送GET请求"""
        return self._make_request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """发送POST请求"""
        return self._make_request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """发送PUT请求"""
        return self._make_request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """发送DELETE请求"""
        return self._make_request('DELETE', url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> requests.Response:
        """发送PATCH请求"""
        return self._make_request('PATCH', url, **kwargs)
    
    def head(self, url: str, **kwargs) -> requests.Response:
        """发送HEAD请求"""
        return self._make_request('HEAD', url, **kwargs)
    
    def options(self, url: str, **kwargs) -> requests.Response:
        """发送OPTIONS请求"""
        return self._make_request('OPTIONS', url, **kwargs)


# 导出主要接口
__all__ = ['RequestClient']
