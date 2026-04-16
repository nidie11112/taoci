# 保研导师信息搜集网站 - 后端服务

## 项目概述
基于Python FastAPI的后端服务，提供导师信息管理、智能匹配、文书生成等功能。

## 技术栈
- Python 3.11+
- FastAPI (异步Web框架)
- SQLAlchemy 2.0 (异步ORM)
- PostgreSQL (主数据库)
- Redis (缓存)
- Pydantic (数据验证)
- Alembic (数据库迁移)

## 开发环境设置

### 1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 3. 数据库设置
```bash
# 启动PostgreSQL和Redis（Docker）
docker-compose up -d postgres redis

# 创建数据库迁移
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

### 4. 运行开发服务器
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 项目结构
```
backend/
├── app/                    # 应用代码
│   ├── api/               # API端点
│   ├── core/              # 核心配置
│   ├── db/                # 数据库模型
│   ├── models/            # Pydantic模型
│   ├── services/          # 业务逻辑
│   ├── utils/             # 工具函数
│   └── main.py            # 应用入口
├── tests/                 # 测试
├── scripts/               # 脚本
├── requirements.txt       # 生产依赖
├── requirements-dev.txt   # 开发依赖
├── alembic.ini           # 数据库迁移配置
└── docker-compose.yml    # Docker编排
```

## API文档
启动服务后访问：http://localhost:8000/docs

## 环境变量
复制 `.env.example` 为 `.env` 并配置相关变量。

## 测试
```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

## 部署
```bash
# 构建Docker镜像
docker build -t taoci-backend .

# 使用Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

## 注意事项
- 数据爬取需遵守robots.txt和网站条款
- 用户隐私数据需加密存储
- 生产环境必须使用HTTPS