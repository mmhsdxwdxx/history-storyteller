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
- 部署: Docker

## 快速启动

### 1. 配置环境变量
```bash
# 复制示例配置文件到项目根目录
cp backend/.env.example .env

# 编辑 .env 文件，填入你的AI代理配置
# 必须配置至少一个provider的URL和API KEY
```

### 2. 启动服务
```bash
# 禁用BuildKit构建（解决镜像拉取问题）
DOCKER_BUILDKIT=0 docker compose up -d --build
```

### 3. 访问
- 前端: http://your-server-ip:30200
- 后端API: http://your-server-ip:8000
- API文档: http://your-server-ip:8000/docs

## 注意事项
- 必须配置AI provider才能使用内容处理功能
- 支持OpenAI、Anthropic、Gemini三种格式的API代理
