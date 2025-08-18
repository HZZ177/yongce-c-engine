from core.logger import logger
import json
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    def __init__(self, app, filtered_urls=None):
        """
        初始化请求日志中间件

        Args:
            app: FastAPI应用实例
            filtered_urls: 需要过滤日志的URL列表，默认包含轮询接口
        """
        super().__init__(app)
        # 默认过滤轮询接口，也可以通过参数自定义，默认过滤设备状态轮询接口
        self.filtered_urls = filtered_urls or ["/closeApp/deviceStatus"]

    def _should_skip_logging(self, url: str) -> bool:
        """
        检查URL是否需要跳过详细日志记录

        Args:
            url: 请求的URL字符串

        Returns:
            bool: 如果需要跳过日志记录返回True，否则返回False
        """
        for filtered_url in self.filtered_urls:
            if filtered_url in url:
                return True
        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        
        # 获取请求参数
        query_params = dict(request.query_params)
        
        # 获取请求体（如果是POST/PUT等）
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    # 尝试解析JSON
                    try:
                        body = json.loads(body_bytes.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        body = body_bytes.decode('utf-8', errors='ignore')
                
                # 重新构造request，因为body只能读取一次
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                
                request._receive = receive
            except Exception as e:
                logger.warning(f"读取请求体失败: {e}")
        
        # 检查是否需要跳过详细日志记录
        skip_detailed_logging = self._should_skip_logging(url)

        # 记录请求日志（如果不在过滤列表中）
        if not skip_detailed_logging:
            log_data = {
                "method": method,
                "url": url,
                "client_ip": client_ip,
                "query_params": query_params if query_params else None,
                "body": body if body else None
            }

            logger.info(f"请求开始 - {method} {url} - 客户端IP: {client_ip}")
            if query_params:
                logger.info(f"查询参数: {json.dumps(query_params, ensure_ascii=False)}")
            if body:
                logger.info(f"请求体: {json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else body}")
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time

            # 记录响应日志
            if skip_detailed_logging:
                # 对于过滤的URL，不记录日志
                pass
            else:
                logger.info(f"请求完成 - {method} {url} - 状态码: {response.status_code} - 耗时: {process_time:.3f}s")
            
            return response
            
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(f"请求异常 - {method} {url} - 错误: {str(e)} - 耗时: {process_time:.3f}s")
            raise 