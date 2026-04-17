# 保研导师信息搜集网站

一个帮助大学生搜集保研导师信息、管理申请材料的全栈Web应用。

## 功能特性

- **导师搜索与筛选**：按学校、院系、研究方向筛选导师
- **导师详情查看**：查看导师基本信息、评价统计
- **数据导入**：支持Excel格式的导师评价数据导入
- **文书管理**：管理个人简历、个人陈述、套磁信等申请材料
- **响应式设计**：适配桌面和移动设备
- **生产就绪**：完整的Docker容器化部署方案

## 技术栈

- **前端**：React 18 + TypeScript + Vite + Ant Design + Zustand
- **后端**：Python FastAPI + SQLAlchemy + SQLite
- **部署**：Docker + Docker Compose + Nginx
- **数据库**：SQLite（支持异步操作）

## 快速开始

### 使用Docker Compose（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/nidie11112/taoci-web.git
cd taoci-web

# 2. 启动服务
docker-compose up -d

# 3. 导入测试数据（可选）
docker-compose exec api python scripts/import_excel_data.py --file /app/data/raw/12-全国高校导师评价数据.xlsx --limit 1000 --init-db

# 4. 访问应用
# 前端：http://localhost:3000
# 后端API文档：http://localhost:8000/docs
```

### 手动部署

#### 后端服务
```bash
cd backend
pip install -r requirements.prod.txt
python scripts/init_database.py
python scripts/import_excel_data.py --file ../data/raw/12-全国高校导师评价数据.xlsx --limit 1000
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端服务
```bash
cd frontend
npm install
npm start  # 开发模式
# 或 npm run build  # 生产构建
```

## 项目结构

```
taoci-web/
├── frontend/          # React前端应用
├── backend/           # FastAPI后端服务
├── data/              # 数据文件目录
├── docker-compose.yml # Docker编排配置
├── DEPLOYMENT.md      # 详细部署指南
├── CLAUDE.md          # 开发规范
└── plan.md           # 项目计划
```

## 数据文件说明

项目包含以下示例数据：
- `data/raw/12-全国高校导师评价数据.xlsx`：导师评价数据（15370条记录）
- `data/raw/document_templates/`：文书模板目录

**注意**：生产部署时请替换为实际数据文件。

## API文档

启动后端服务后，访问：
- OpenAPI文档：http://localhost:8000/docs
- ReDoc文档：http://localhost:8000/redoc

主要API端点：
- `GET /api/v1/professors/` - 获取导师列表
- `GET /api/v1/professors/{id}` - 获取导师详情
- `GET /api/v1/professors/search/suggest` - 搜索建议
- `POST /api/v1/professors/import` - 导入导师数据

## 生产部署

### 环境变量配置
创建`.env`文件：
```bash
DATABASE_URL=sqlite+aiosqlite:///./data/taoci.db
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
SECRET_KEY=your-secret-key-change-in-production
```

### 安全建议
1. 修改默认SECRET_KEY
2. 启用HTTPS（配置Nginx SSL证书）
3. 设置访问限制（IP白名单）
4. 定期备份数据库

## 故障排除

常见问题请参考[DEPLOYMENT.md](DEPLOYMENT.md)中的故障排除章节。

## 许可证

本项目仅供教育研究使用，请遵守相关数据隐私法律法规。

## 技术支持

如需技术支持，请提供：
1. 错误日志
2. 环境信息
3. 复现步骤
4. 期望结果
