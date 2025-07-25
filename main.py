from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.closeApp.router import close_dsp_router
import uvicorn

app = FastAPI(title="Yongce-Pro-C端 引擎 API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(close_dsp_router, prefix="/closeApp", tags=["封闭dsp"])

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=17771,
        reload=True
    )
