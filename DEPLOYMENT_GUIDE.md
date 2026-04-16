# 保研导师信息搜集网站 (taoci-web) 部署上线指南

## 概述

本指南提供从本地测试到生产环境部署的完整流程，帮助您将保研导师信息搜集网站成功上线。网站采用前后端分离架构：
- **前端**：React + TypeScript + Vite
- **后端**：Python FastAPI + PostgreSQL + Redis

## 目录

1. [环境准备](#环境准备)
2. [本地运行测试](#本地运行测试)
3. [构建生产版本](#构建生产版本)
4. [容器化部署（推荐）](#容器化部署推荐)
5. [传统服务器部署](#传统服务器部署)
6. [云平台部署选项](#云平台部署选项)
7. [域名与HTTPS配置](#域名与https配置)
8. [监控与维护](#监控与维护)
9. [故障排除](#故障排除)
10. 

## 环境准备

### 系统要求
- **操作系统**：Windows 10/11, macOS 10.15+, Ubuntu 18.04+ 或其他 Linux 发行版
- **内存**：至少 4GB RAM（推荐 8GB+）
- **存储**：至少 2GB 可用空间

### 必备工具安装

#### 1. Git（版本控制）
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install git

# macOS
brew install git

# Windows
# 下载 Git for Windows：https://git-scm.com/download/win
```

#### 2. Node.js 和 npm（前端）
```bash
# 使用 nvm（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# 或直接从官网下载：https://nodejs.org/
```

验证安装：
```bash
node --version  # 应显示 v18.x.x
npm --version   # 应显示 9.x.x
```

#### 3. Python 3.11+（后端）
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# macOS
brew install python@3.11

# Windows
# 下载 Python 3.11+：https://www.python.org/downloads/
```

验证安装：
```bash
python3 --version  # 应显示 Python 3.11.x
pip3 --version
```

#### 4. Docker 和 Docker Compose（容器化部署）
```bash
# 安装 Docker
# 参考官方文档：https://docs.docker.com/engine/install/

# 安装 Docker Compose
# Docker Desktop 已包含，Linux 需单独安装
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

验证安装：
```bash
docker --version
docker-compose --version
```

#### 5. PostgreSQL 和 Redis（可选，本地开发）
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib redis-server

# macOS
brew install postgresql redis

# Windows
# 使用 Docker 或下载安装包
```

## 部署前准备

在开始部署前，请完成以下项目初始化检查：

### 1. 项目结构验证
确保项目包含以下关键目录和文件：
```
taoci-web/
├── backend/           # 后端服务
│   ├── app/          # 应用代码
│   ├── requirements.txt
│   ├── docker-compose.yml
│   └── .env.example
├── frontend/         # 前端应用
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
└── DEPLOYMENT_GUIDE.md
```

### 2. 数据库迁移配置检查
当前项目使用SQLAlchemy ORM，但未配置Alembic数据库迁移。您可以选择：

**选项A：使用自动建表（开发环境）**
- 在 `backend/app/main.py` 中取消注释第51行：
  ```python
  await conn.run_sync(Base.metadata.create_all)
  ```
- 仅适用于开发环境，生产环境建议使用迁移

**选项B：配置Alembic迁移（推荐）**
```bash
cd backend
pip install alembic

# 初始化Alembic
alembic init alembic

# 配置alembic.ini中的数据库连接
# 编辑 alembic/env.py 导入Base模型

# 创建初始迁移
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

### 3. 测试套件检查
项目目前没有测试文件。建议在部署前添加基本测试：

**后端测试**：在 `backend/tests/` 目录创建测试文件
**前端测试**：运行 `npm run test` 查看现有测试

### 4. 环境变量配置
确保已复制并配置环境变量文件：
```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，设置数据库连接、JWT密钥等

cd ../frontend
cp .env.example .env  # 如果没有，创建 .env 文件
# 设置 VITE_API_BASE_URL 等变量
```

### 5. 依赖安装验证
```bash
# 后端依赖
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 前端依赖
cd ../frontend
npm install
```

完成以上检查后，继续本地运行测试。

## 本地运行测试

在部署前，确保所有功能在本地正常工作。

### 1. 获取项目代码
```bash
# 如果项目在本地，直接进入目录
cd /d/陶瓷/taoci-web

# 如果从远程仓库克隆
git clone <repository-url>
cd taoci-web
```

### 2. 后端服务测试

#### 环境配置
```bash
cd backend

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，配置数据库连接等
# 主要修改：
# DATABASE_URL=postgresql://taoci_user:taoci_password@localhost:5432/taoci_web
# REDIS_URL=redis://localhost:6379/0
# JWT_SECRET=your-secure-jwt-secret-key-here
```

#### 启动依赖服务（Docker）
```bash
# 启动 PostgreSQL 和 Redis
docker-compose up -d postgres redis

# 检查服务状态
docker-compose ps
```

#### 安装 Python 依赖
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖，包含测试工具
```

#### 数据库迁移
当前项目未配置Alembic迁移。您可以选择：

**选项A：自动创建表（开发环境）**
在 `backend/app/main.py` 中取消注释第51行（约）：
```python
await conn.run_sync(Base.metadata.create_all)
```
然后启动服务，表将自动创建。

**选项B：配置Alembic迁移（推荐生产环境）**
```bash
# 安装alembic
pip install alembic

# 初始化（如果尚未初始化）
alembic init alembic

# 配置 alembic.ini 中的数据库连接
# 编辑 alembic/env.py，添加：
# from app.db.session import Base
# target_metadata = Base.metadata

# 创建初始迁移
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

**选项C：使用现有迁移（如果已有）**
```bash
# 检查是否有alembic.ini文件
ls -la alembic.ini 2>/dev/null || echo "未找到迁移配置"

# 如果有迁移配置，运行
alembic upgrade head
```

#### 运行后端服务
```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
# uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

访问 API 文档：http://localhost:8000/docs

#### 运行后端测试
当前项目测试目录为空。您可以选择：

**选项A：创建基本测试（推荐）**
```bash
# 安装测试依赖（如果尚未安装）
pip install pytest pytest-asyncio httpx

# 创建测试目录结构
mkdir -p tests/unit tests/integration

# 创建示例测试文件 tests/test_health.py
cat > tests/test_health.py << 'EOF'
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
EOF

# 运行测试
pytest tests/ -v
```

**选项B：跳过测试（不推荐）**
如果您希望跳过测试直接部署，可以暂时不运行测试，但生产环境建议至少添加健康检查测试。

**选项C：仅运行现有测试**
```bash
# 检查是否有测试文件
find tests/ -name "*.py" 2>/dev/null

# 如果有测试文件，运行它们
pytest tests/ -v  # 如果存在测试文件
```

### 3. 前端应用测试

#### 环境配置
```bash
cd ../frontend

# 创建环境变量文件
cat > .env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=保研导师信息搜集网站
VITE_DEBUG=true
EOF
```

#### 安装依赖
```bash
npm install
# 或使用 yarn
# yarn install
```

#### 运行开发服务器
```bash
npm run dev
# 或
# yarn dev
```

访问前端应用：http://localhost:3000

#### 运行前端测试
```bash
# 类型检查
npm run type-check

# 代码检查
npm run lint

# 运行测试
npm run test

# 测试UI界面
npm run test:ui

# 覆盖率报告
npm run test:coverage
```

### 4. 集成测试

确保前后端能够正常通信：

1. 前端访问 http://localhost:3000
2. 尝试搜索导师功能
3. 检查API调用是否成功（浏览器开发者工具 Network 标签）
4. 验证数据是否正确显示

## 构建生产版本

### 1. 前端构建
```bash
cd frontend

# 创建生产环境变量
cat > .env.production << 'EOF'
VITE_API_BASE_URL=https://api.your-domain.com/api  # 替换为实际API地址
VITE_APP_NAME=保研导师信息搜集网站
VITE_DEBUG=false
EOF

# 使用生产环境变量构建
cp .env.production .env
npm run build

# 构建结果在 dist/ 目录
ls -la dist/
```

### 2. 后端构建准备

#### 优化生产配置
编辑 `backend/.env` 文件：
```env
# 修改为生产环境配置
APP_ENV=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-domain.com  # 前端域名

# 数据库使用强密码
DATABASE_URL=postgresql://taoci_user:StrongPassword123@postgres:5432/taoci_web

# 使用强JWT密钥
JWT_SECRET=very-strong-secret-key-change-in-production

# 关闭调试功能
ENABLE_ANALYTICS=false
```

## 容器化部署（推荐）

使用 Docker 可以确保环境一致性，简化部署流程。

### 1. 创建 Docker 配置文件

#### 后端 Dockerfile
在 `backend/` 目录创建 `Dockerfile`：
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 前端 Dockerfile
在 `frontend/` 目录创建 `Dockerfile`：
```dockerfile
# 构建阶段
FROM node:18-alpine AS build

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建结果
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
```

#### Nginx 配置
在 `frontend/` 目录创建 `nginx.conf`：
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss 
               application/json;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # 处理前端路由（单页应用）
        location / {
            try_files $uri $uri/ /index.html;
        }

        # API代理
        location /api/ {
            proxy_pass http://api:8000/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # 静态资源缓存
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

#### 生产环境 Docker Compose
在项目根目录创建 `docker-compose.prod.yml`：
```yaml
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    container_name: taoci-postgres
    environment:
      POSTGRES_DB: ${DATABASE_NAME:-taoci_web}
      POSTGRES_USER: ${DATABASE_USER:-taoci_user}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD:-StrongPassword123}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    networks:
      - taoci-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DATABASE_USER:-taoci_user} -d ${DATABASE_NAME:-taoci_web}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: taoci-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - taoci-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 后端API服务
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: taoci-api
    environment:
      - DATABASE_URL=postgresql://${DATABASE_USER:-taoci_user}:${DATABASE_PASSWORD:-StrongPassword123}@postgres:5432/${DATABASE_NAME:-taoci_web}
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET:-your-secure-jwt-secret}
      - APP_ENV=production
      - CORS_ORIGINS=https://${FRONTEND_DOMAIN:-your-domain.com}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - taoci-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  # 前端应用
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: taoci-frontend
    depends_on:
      - api
    networks:
      - taoci-network
    restart: unless-stopped

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: taoci-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - frontend
      - api
    networks:
      - taoci-network
    restart: unless-stopped

networks:
  taoci-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### 2. 构建和运行容器

#### 环境变量文件
在项目根目录创建 `.env.prod`：
```env
# 数据库配置
DATABASE_NAME=taoci_web
DATABASE_USER=taoci_user
DATABASE_PASSWORD=StrongPassword123ChangeThis

# 安全配置
JWT_SECRET=your-very-strong-jwt-secret-key-change-this

# 域名配置
FRONTEND_DOMAIN=your-domain.com
API_DOMAIN=api.your-domain.com
```

#### 构建和启动
```bash
# 构建所有镜像
docker-compose -f docker-compose.prod.yml build

# 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f frontend

# 停止服务
docker-compose -f docker-compose.prod.yml down

# 停止并删除数据卷
docker-compose -f docker-compose.prod.yml down -v
```

### 3. 数据库初始化

如果首次部署，可能需要初始化数据：

```bash
# 进入PostgreSQL容器
docker exec -it taoci-postgres psql -U taoci_user -d taoci_web

# 或运行初始化脚本（如果存在）
docker exec -it taoci-postgres bash -c "psql -U taoci_user -d taoci_web -f /docker-entrypoint-initdb.d/init-db.sql"
```

## 传统服务器部署

如果不使用Docker，可以在传统服务器上手动部署。

### 1. 服务器准备

#### 系统更新
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y curl wget git nginx postgresql postgresql-contrib redis-server
```

#### 防火墙配置
```bash
# 启用防火墙
sudo ufw enable

# 开放端口
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw allow 5432/tcp   # PostgreSQL（可选，建议仅本地）
sudo ufw allow 6379/tcp   # Redis（可选，建议仅本地）

# 查看状态
sudo ufw status
```

### 2. 后端部署

#### 创建系统用户
```bash
sudo useradd -m -s /bin/bash taoci
sudo passwd taoci
```

#### 设置项目目录
```bash
sudo mkdir -p /opt/taoci-web
sudo chown -R taoci:taoci /opt/taoci-web
sudo -u taoci git clone <repository-url> /opt/taoci-web
```

#### 配置Python环境
```bash
cd /opt/taoci-web/backend
sudo apt install -y python3.11-venv python3.11-dev
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 配置PostgreSQL
```bash
# 创建数据库和用户
sudo -u postgres psql

# 在PostgreSQL shell中执行
CREATE DATABASE taoci_web;
CREATE USER taoci_user WITH PASSWORD 'StrongPassword123';
GRANT ALL PRIVILEGES ON DATABASE taoci_web TO taoci_user;
ALTER DATABASE taoci_web OWNER TO taoci_user;
\q
```

#### 配置环境变量
```bash
cp .env.example .env
nano .env  # 编辑配置
```

#### 数据库迁移
当前项目未配置Alembic迁移。根据您的选择：

**选项A：自动创建表（开发/测试环境）**
确保 `backend/app/main.py` 中的自动建表代码已启用（取消注释）：
```python
await conn.run_sync(Base.metadata.create_all)
```

**选项B：配置Alembic迁移（生产环境推荐）**
```bash
source venv/bin/activate

# 安装alembic（如果尚未安装）
pip install alembic

# 初始化迁移（如果首次）
alembic init alembic

# 配置迁移后运行
alembic upgrade head
```

**选项C：手动创建表（简单部署）**
```bash
source venv/bin/activate
python -c "
from app.db.session import engine, Base
import asyncio

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(create_tables())
"
```

#### 配置Systemd服务
创建 `/etc/systemd/system/taoci-api.service`：
```ini
[Unit]
Description=Taoci Web API Service
After=network.target postgresql.service redis-server.service
Requires=postgresql.service redis-server.service

[Service]
Type=simple
User=taoci
Group=taoci
WorkingDirectory=/opt/taoci-web/backend
Environment="PATH=/opt/taoci-web/backend/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=/opt/taoci-web/backend/.env
ExecStart=/opt/taoci-web/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=taoci-api

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable taoci-api
sudo systemctl start taoci-api
sudo systemctl status taoci-api
```

### 3. 前端部署

#### 安装Node.js
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 构建前端
```bash
cd /opt/taoci-web/frontend
npm install
npm run build
```

#### 配置Nginx
创建 `/etc/nginx/sites-available/taoci-web`：
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    root /opt/taoci-web/frontend/dist;
    index index.html;

    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/taoci-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 云平台部署选项

### 1. Docker 平台部署

#### Docker Hub / 容器注册表
```bash
# 登录Docker Hub
docker login

# 构建并推送镜像
docker build -t yourusername/taoci-api:latest ./backend
docker build -t yourusername/taoci-frontend:latest ./frontend
docker push yourusername/taoci-api:latest
docker push yourusername/taoci-frontend:latest
```

#### 使用云服务
- **AWS ECS/EKS**：托管容器服务
- **Google Cloud Run**：无服务器容器
- **Azure Container Instances**：简单容器部署
- **阿里云容器服务**：国内用户

### 2. 平台即服务 (PaaS)

#### 后端部署
- **Render**：支持Python FastAPI，简单配置
- **Railway**：一键部署，自动配置数据库
- **Heroku**：经典PaaS平台
- **Fly.io**：全球边缘部署

#### 前端部署
- **Vercel**：React应用最佳选择
- **Netlify**：静态站点托管
- **GitHub Pages**：免费静态托管

### 3. 虚拟机部署
- **DigitalOcean Droplet**：简单VPS
- **AWS EC2**：灵活虚拟机
- **Google Compute Engine**：Google云虚拟机
- **阿里云ECS**：国内服务器

## 域名与HTTPS配置

### 1. 域名购买和解析
1. 购买域名（阿里云、腾讯云、GoDaddy等）
2. 添加DNS记录：
   - A记录：@ → 服务器IP
   - A记录：www → 服务器IP
   - CNAME记录：api → your-domain.com（如果需要子域名）

### 2. 获取SSL证书

#### 使用 Let's Encrypt（免费）
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

#### 手动配置Nginx SSL
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # 其他配置同前...
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. 更新应用配置

#### 前端环境变量
```env
VITE_API_BASE_URL=https://api.your-domain.com/api
```

#### 后端CORS配置
```env
CORS_ORIGINS=https://your-domain.com
```

## 监控与维护

### 1. 日志管理

#### 查看日志
```bash
# Docker容器日志
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml logs -f api --tail=100

# 系统日志（传统部署）
sudo journalctl -u taoci-api -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

#### 日志轮转
配置 `/etc/logrotate.d/taoci`：
```bash
/opt/taoci-web/backend/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 taoci taoci
    sharedscripts
    postrotate
        systemctl reload taoci-api > /dev/null 2>&1 || true
    endscript
}
```

### 2. 性能监控

#### 基础监控命令
```bash
# 查看系统资源
htop
free -h
df -h

# 查看网络连接
ss -tulpn

# 查看进程
ps aux | grep taoci
```

#### 应用健康检查
```bash
# API健康检查
curl -f http://localhost:8000/health || echo "API服务异常"

# 数据库连接检查
pg_isready -h localhost -p 5432 -d taoci_web

# Redis连接检查
redis-cli -h localhost ping
```

### 3. 备份策略

#### 数据库备份
```bash
# 创建备份脚本 /opt/taoci-web/scripts/backup.sh
#!/bin/bash
BACKUP_DIR="/opt/taoci-web/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="taoci_web"

mkdir -p $BACKUP_DIR
pg_dump -U taoci_user $DB_NAME > $BACKUP_DIR/taoci_web_$DATE.sql
gzip $BACKUP_DIR/taoci_web_$DATE.sql

# 保留最近7天备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

# 添加到cron定时任务
# crontab -e
# 0 2 * * * /opt/taoci-web/scripts/backup.sh
```

#### 配置文件备份
```bash
# 备份重要配置
tar -czf /opt/taoci-web/backups/config_$(date +%Y%m%d).tar.gz \
    /opt/taoci-web/backend/.env \
    /opt/taoci-web/frontend/.env \
    /etc/nginx/sites-available/taoci-web \
    /etc/systemd/system/taoci-api.service
```

### 4. 安全维护

#### 定期更新
```bash
# 系统更新
sudo apt update && sudo apt upgrade -y

# 容器镜像更新
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Node.js依赖更新
cd /opt/taoci-web/frontend
npm update

# Python依赖更新
cd /opt/taoci-web/backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

#### 安全扫描
```bash
# 容器漏洞扫描
docker scan taoci-api
docker scan taoci-frontend

# 依赖安全扫描
npm audit  # 前端
pip-audit  # 后端（需要安装）
```

## 故障排除

### 常见问题及解决方案

#### 1. 数据库连接失败
```bash
# 检查PostgreSQL服务状态
sudo systemctl status postgresql

# 检查连接配置
echo $DATABASE_URL

# 测试连接
psql $DATABASE_URL -c "SELECT 1;"

# 查看日志
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

#### 2. Redis连接失败
```bash
# 检查Redis服务
sudo systemctl status redis-server

# 测试连接
redis-cli -h localhost ping

# 查看配置
cat /etc/redis/redis.conf | grep -v "^#" | grep -v "^$"
```

#### 3. API服务启动失败
```bash
# 查看服务状态
sudo systemctl status taoci-api

# 查看详细日志
sudo journalctl -u taoci-api -n 50 --no-pager

# 检查端口占用
sudo lsof -i :8000
```

#### 4. 前端无法访问API
```bash
# 检查CORS配置
curl -I -H "Origin: https://your-domain.com" http://localhost:8000/health

# 检查网络连接
curl -v http://localhost:8000/health

# 查看Nginx配置
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

#### 5. 内存不足
```bash
# 查看内存使用
free -h

# 查看进程内存
ps aux --sort=-%mem | head -20

# 调整数据库配置（PostgreSQL）
# 编辑 /etc/postgresql/15/main/postgresql.conf
# shared_buffers = 256MB -> 128MB
# work_mem = 4MB -> 2MB
```

#### 6. 磁盘空间不足
```bash
# 查看磁盘使用
df -h

# 查找大文件
sudo find / -type f -size +100M 2>/dev/null | head -20

# 清理Docker资源
docker system prune -a
docker volume prune
```

### 紧急恢复步骤

1. **停止服务**
   ```bash
   docker-compose -f docker-compose.prod.yml down
   # 或
   sudo systemctl stop taoci-api nginx
   ```

2. **恢复数据库备份**
   ```bash
   # 恢复最新备份
   gzip -d /opt/taoci-web/backups/taoci_web_latest.sql.gz
   psql -U taoci_user -d taoci_web < /opt/taoci-web/backups/taoci_web_latest.sql
   ```

3. **回滚代码**
   ```bash
   cd /opt/taoci-web
   git log --oneline -10
   git reset --hard <stable-commit-hash>
   ```

4. **重启服务**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   # 或
   sudo systemctl start taoci-api nginx
   ```

## 结语

通过本指南，您应该能够完成从本地测试到生产环境部署的全过程。建议：

1. **先在生产环境测试**：使用临时域名或IP进行测试
2. **逐步上线**：先部署后端API，再部署前端
3. **监控关键指标**：响应时间、错误率、资源使用
4. **定期备份**：数据库和配置文件
5. **安全第一**：使用HTTPS、强密码、定期更新

如果在部署过程中遇到问题，请参考故障排除部分或查看项目文档。祝您部署顺利！

---
*最后更新：2026年4月16日*
*项目版本：taoci-web v1.0.0*