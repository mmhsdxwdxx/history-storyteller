# 历史故事创作工具 - 部署教程

## 目录

1. [环境要求](#环境要求)
2. [快速部署（推荐）](#快速部署推荐)
3. [配置说明](#配置说明)
4. [手动部署](#手动部署)
5. [常见问题](#常见问题)

---

## 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存
- 至少 10GB 磁盘空间

---

## 快速部署（推荐）

### 第一步：克隆项目

```bash
git clone https://github.com/mmhsdxwdxx/history-storyteller.git
cd history-storyteller
```

### 第二步：创建环境变量文件

```bash
cp backend/.env.example .env
```

编辑 `.env` 文件，填入你的 AI Provider 配置：

```bash
# OpenAI 配置（支持自定义代理地址）
OPENAI_API_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o

# Anthropic 配置
ANTHROPIC_API_URL=https://api.anthropic.com/v1
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Gemini 配置
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro

# 默认使用的 Provider
DEFAULT_PROVIDER=openai
```

> **注意**：如果你想使用 OpenAI 代理服务，只需将 `OPENAI_API_URL` 改为代理地址即可。

### 第三步：启动服务

```bash
docker compose up -d --build
```

### 第四步：验证部署

```bash
# 检查服务状态
docker compose ps

# 查看后端日志
docker compose logs -f backend
```

### 第五步：访问应用

打开浏览器访问：`http://localhost:30200`

---

## 配置说明

### 端口配置

默认端口映射：
- **前端**: 30200 (可通过 `docker-compose.yml` 修改)
- **后端 API**: 8000 (容器内部)
- **数据库**: 5432 (容器内部)

如需修改前端端口，编辑 `docker-compose.yml`：

```yaml
frontend:
  ports:
    - "你的端口:80"
```

### 数据持久化

数据库数据存储在 Docker Volume `postgres_data` 中。

**备份数据库**：
```bash
docker compose exec db pg_dump -U user history_storyteller > backup.sql
```

**恢复数据库**：
```bash
cat backup.sql | docker compose exec -T db psql -U user history_storyteller
```

### 通过界面配置 Provider（新功能）

1. 访问应用后，点击右上角的 **齿轮图标**
2. 选择要配置的 Provider（OpenAI / Anthropic / Gemini）
3. 填写 API URL、API Key、Model
4. 勾选"设为默认"（可选）
5. 点击保存，配置立即生效

> 界面配置保存在数据库中，优先级高于环境变量。

---

## 手动部署

### 后端部署

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export DATABASE_URL=postgresql://user:password@localhost:5432/history_storyteller
export OPENAI_API_URL=https://api.openai.com/v1
export OPENAI_API_KEY=your-key

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 构建
npm run build

# 使用 nginx 托管
# 将 dist 目录内容复制到 nginx 的 html 目录
# 配置 nginx 反向代理 /api/ 到后端
```

---

## 常见问题

### Q: 如何查看日志？

```bash
# 所有服务日志
docker compose logs -f

# 特定服务日志
docker compose logs -f backend
docker compose logs -f frontend
```

### Q: 如何重启服务？

```bash
docker compose restart
```

### Q: 如何完全重置？

```bash
# 停止并删除容器、网络、卷
docker compose down -v

# 重新构建并启动
docker compose up -d --build
```

### Q: 数据库连接失败？

1. 确认数据库容器已启动：`docker compose ps`
2. 等待几秒让数据库完全启动
3. 检查 DATABASE_URL 格式是否正确

### Q: AI 生成失败？

1. 检查 API Key 是否正确
2. 检查 API URL 是否可访问
3. 查看后端日志：`docker compose logs backend`
4. 尝试在界面重新配置 Provider

### Q: 如何更新到最新版本？

```bash
git pull origin master
docker compose down
docker compose up -d --build
```

---

## 生产环境建议

1. **修改默认数据库密码**：编辑 `docker-compose.yml` 中的数据库凭据
2. **配置 HTTPS**：在 nginx 前面加一层反向代理（如 Caddy、Traefik）
3. **限制端口暴露**：不要将数据库端口暴露到公网
4. **定期备份**：设置定时任务备份数据库
5. **监控日志**：配置日志收集和告警
