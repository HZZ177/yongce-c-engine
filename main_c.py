from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from apps.closeApp.router import close_dsp_router
from apps.roadApp.router import road_dsp_router
from core.middleware import RequestLoggingMiddleware
import uvicorn

app = FastAPI(title="Yongce-Pro-C端 引擎 API")

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路径重定向到文档页面
@app.get("/", include_in_schema=False)
async def root():
    """根路径重定向到API文档"""
    return RedirectResponse(url="/docs")

# 注册路由
app.include_router(close_dsp_router, prefix="/closeApp", tags=["封闭dsp"])
app.include_router(road_dsp_router, prefix="/roadApp", tags=["路侧服务"])

if __name__ == "__main__":
    uvicorn.run(
        app="main_c:app",
        host="0.0.0.0",
        port=17771,
        reload=True,
        access_log=False  # 禁用uvicorn访问日志，避免与自定义中间件重复
    )
