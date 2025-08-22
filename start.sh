#!/bin/bash

ROOT="/opt/test-tool-c"
cd ${ROOT} && source venv/bin/activate

# (1)杀旧进程（忽略不存在）
pkill -f "${ROOT}/main_c\.py" >/dev/null 2>&1 || true
pkill -f "uvicorn.*main_c:app" >/dev/null 2>&1 || true
pkill -f "vite" >/dev/null 2>&1 || true
pkill -f "npm.*run dev" >/dev/null 2>&1 || true

# (2)后端依赖（清华源）
pip install -r "${ROOT}/requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple

# (3)启动后端
nohup python -u "${ROOT}/main_c.py" > "${ROOT}/backend.out" 2>&1 &

# (4)前端依赖并启动
cd "${ROOT}/frontend"
npm install
nohup npm run dev > "${ROOT}/frontend.out" 2>&1 &
