# History Storyteller

小红书历史内容创作工具

## 功能
- V1.0: 史书原文 → 白话文 → 诙谐文稿
- 版本管理
- 素材库
- 发布计划

## 技术栈
- 后端: Python + FastAPI + PostgreSQL
- 前端: Vue 3 + Vite
- 部署: Docker + Nginx

## 快速启动

### 1. 配置环境变量
```bash
# 复制示例配置文件到项目根目录
cp backend/.env.example .env

# 编辑 .env 文件，至少配置一个AI provider的URL和API KEY
# 如果不指定DEFAULT_PROVIDER，系统会自动使用第一个已配置的provider
```

### 2. 启动服务（生产环境）
```bash
# 禁用BuildKit构建（解决镜像拉取问题）
DOCKER_BUILDKIT=0 docker compose up -d --build
```

### 3. 本地开发
```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端（会自动代理 /api 到 localhost:8000）
cd frontend
npm install
npm run dev
```

### 4. 访问
- 生产环境: http://your-server-ip:30200 (通过nginx统一入口)
- 本地开发: http://localhost:3000
- 后端API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health/ready

## 注意事项
- 必须配置至少一个AI provider才能使用内容处理功能
- 支持OpenAI、Anthropic、Gemini三种格式的API代理
- 生产环境通过nginx反向代理，前端访问 `/api` 路径
- 本地开发时Vite会自动代理API请求到后端
