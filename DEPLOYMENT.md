# 保研导师信息搜集网站 - 生产部署指南

## 项目状态

✅ 已完成所有开发工作，包括：
- 前端React应用（TypeScript + Ant Design）
- 后端FastAPI服务（Python + SQLite）
- 数据导入工具（解析Excel评价数据）
- 数据库模型和API端点
- Docker容器化配置
- 生产环境部署配置

## 快速启动（Docker Compose - 推荐）

### 1. 前提条件
- 安装 Docker 和 Docker Compose
- 确保80、3000、8000端口可用

### 2. 启动服务
```bash
cd /d/陶瓷/taoci-web

# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api
```

### 3. 访问应用
- 前端应用：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 4. 导入数据
```bash
# 进入API容器
docker-compose exec api bash

# 在容器内导入Excel数据（前1000行测试）
python scripts/import_excel_data.py --file /app/data/raw/12-全国高校导师评价数据.xlsx --limit 1000 --init-db

# 导入全部数据（约15000行，需要时间）
python scripts/import_excel_data.py --file /app/data/raw/12-全国高校导师评价数据.xlsx --init-db
```

### 5. 服务管理
```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 删除所有数据（谨慎！）
docker-compose down -v
```

## 手动部署（开发环境）

### 1. 后端服务
```bash
cd /d/陶瓷/taoci-web/backend

# 安装Python依赖
pip install -r requirements.prod.txt

# 初始化数据库
python scripts/init_database.py

# 导入数据
python scripts/import_excel_data.py --file ../data/raw/12-全国高校导师评价数据.xlsx --limit 1000

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端服务
```bash
cd /d/陶瓷/taoci-web/frontend

# 安装Node依赖
npm install

# 启动开发服务器
npm start
# 或构建生产版本
npm run build
```

## 数据文件说明

项目包含以下数据文件：

### 1. 导师评价数据
- 位置：`data/raw/12-全国高校导师评价数据.xlsx`
- 内容：全国高校导师评价信息（15370条记录）
- 字段：学校、学院、姓名、分数、评价

### 2. 学生简历
- `data/raw/吴凌钧个人简历.pdf`
- `data/raw/林静个人简历.pdf`

### 3. 文书模板
- 位置：`data/raw/document_templates/`
- 包含：简历模板、个人陈述、套磁信、推荐信等

## 功能特性

### 已实现功能
1. **导师搜索与筛选**
   - 按学校、院系、研究方向筛选
   - 实时搜索建议
   - 分页显示

2. **导师详情查看**
   - 基本信息展示
   - 评价信息显示
   - 统计信息

3. **数据管理**
   - Excel数据导入
   - 数据库初始化
   - 数据统计

4. **用户界面**
   - 响应式设计
   - 现代化UI（Ant Design）
   - 中英文支持

### 待开发功能（计划中）
1. 智能匹配算法
2. 录取概率评估
3. 文书生成系统
4. 用户认证系统

## 项目结构

```
taoci-web/
├── frontend/              # React前端应用
│   ├── src/              # 源代码
│   ├── public/           # 静态资源
│   ├── Dockerfile        # 前端Docker配置
│   └── nginx.conf        # Nginx配置
├── backend/              # FastAPI后端服务
│   ├── app/             # 应用代码
│   ├── scripts/         # 工具脚本
│   ├── requirements.prod.txt  # 生产依赖
│   └── Dockerfile       # 后端Docker配置
├── data/                 # 数据文件
│   ├── raw/             # 原始数据
│   ├── processed/       # 处理后的数据
│   └── exports/         # 导出文件
├── docker-compose.yml   # Docker编排配置
├── DEPLOYMENT.md        # 部署指南（本文档）
├── CLAUDE.md           # 开发规范
└── plan.md             # 项目计划
```

## API接口

### 主要端点
- `GET /api/v1/professors/` - 获取导师列表
- `GET /api/v1/professors/{id}` - 获取导师详情
- `GET /api/v1/professors/{id}/evaluations` - 获取导师评价
- `GET /api/v1/professors/search/suggest` - 搜索建议

### 数据导入
- `POST /api/v1/professors/import` - 导入导师数据
- `GET /api/v1/health` - 健康检查

## 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 修改docker-compose.yml中的端口映射
   ports:
     - "8080:8000"  # 后端
     - "3001:80"    # 前端
   ```

2. **数据库初始化失败**
   ```bash
   # 删除现有数据库文件
   rm -f data/taoci.db
   
   # 重新初始化
   python scripts/init_database.py
   ```

3. **Docker构建失败**
   ```bash
   # 清理Docker缓存
   docker system prune -f
   
   # 重新构建
   docker-compose build --no-cache
   ```

4. **数据导入缓慢**
   - 使用`--limit`参数限制导入行数
   - 分批导入数据

### 日志查看
```bash
# Docker容器日志
docker-compose logs -f

# 后端应用日志
tail -f backend/app.log

# 数据库日志
tail -f data/database.log
```

## 生产环境配置

### 环境变量
创建`.env`文件：
```bash
DATABASE_URL=sqlite+aiosqlite:///./data/taoci.db
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-change-in-production
```

### 安全性建议
1. 修改默认SECRET_KEY
2. 启用HTTPS（Nginx配置SSL）
3. 设置访问限制（IP白名单）
4. 定期备份数据库

### 性能优化
1. 数据库索引优化
2. API响应缓存
3. 静态文件CDN
4. 负载均衡（多实例部署）

## 维护与监控

### 日常维护
```bash
# 备份数据库
cp data/taoci.db data/backups/taoci_$(date +%Y%m%d).db

# 清理日志
find . -name "*.log" -type f -size +10M -exec truncate -s 5M {} \;

# 更新依赖
docker-compose build --no-cache
```

### 监控指标
- API响应时间（< 500ms）
- 错误率（< 1%）
- 数据库连接数
- 内存使用率

## 技术支持

如需技术支持，请提供：
1. 错误日志
2. 环境信息
3. 复现步骤
4. 期望结果

## 版本历史

- v1.0.0 (2026-04-16): 初始版本发布
  - 基础架构完成
  - 数据导入功能
  - 生产部署配置
  - 基本用户界面

---

**重要提醒**：
1. 首次部署后请立即修改默认密码和密钥
2. 定期备份重要数据
3. 遵守数据隐私相关法律法规
4. 本工具仅供教育研究使用

*祝您使用愉快！*