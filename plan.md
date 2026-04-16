# 保研导师信息搜集网站 - 项目需求与技术方案

## 项目概述

本项目旨在为中国大学生保研过程提供一个智能化的导师信息搜集与匹配平台。平台将整合多源导师数据（官方主页、评价数据、论文成果等），结合学生个人背景（院校、成绩、科研、竞赛等），通过智能算法实现导师-学生双向匹配，并提供个性化的保研文书生成服务。

**目标用户**：西安交通大学工程力学专业学生吴凌钧与林静（及其他有保研需求的学生）

**核心目标**：
1. 自动化搜集目标院校导师信息
2. 智能匹配学生研究方向与导师课题
3. 评估录取概率并提供策略建议
4. 生成个性化保研文书材料

## 需求分析

### 1. 数据需求
- **导师基础信息**：姓名、院校、院系、职称、研究方向、个人主页
- **导师评价数据**：人品得分、课题组氛围、学生评价（来自Excel和GitHub数据源）
- **学术成果**：经典论文、研究项目、专利、获奖
- **学校/院系信息**：招生政策、录取要求、竞争情况
- **学生个人信息**：院校背景、GPA、科研经历、竞赛获奖、技能证书

### 2. 功能需求

#### 2.1 数据采集与整合模块
- 从学校官网爬取导师信息
- 解析Excel评价数据（12-全国高校导师评价数据.xlsx）
- 同步GitHub评价数据（wangzhiye-tiancai/mysupervisor_save）
- 集成学术数据库（知网、Google Scholar）获取论文信息
- 学生简历PDF解析（吴凌钧个人简历.pdf、林静个人简历.pdf）

#### 2.2 智能匹配模块
- 研究方向关键词匹配
- 论文内容相似度分析
- 背景契合度评估（院校层级、成绩要求）
- 性格/课题组文化匹配度
- 综合匹配评分算法

#### 2.3 概率评估模块
- 基于历史录取数据的统计模型
- 考虑因素：院校背景、GPA排名、科研产出、竞赛成绩
- 导师招生偏好分析
- 动态调整的概率预测

#### 2.4 文书生成模块
- 套磁信模板库（基于"保研文书大礼包"）
- 个性化内容填充
- 针对不同导师的定制化修改
- 个人陈述、自我介绍、推荐信生成
- 多版本管理

#### 2.5 用户界面
- 导师搜索与筛选
- 匹配结果可视化展示
- 个人仪表板（长短板分析、进度追踪）
- 文书编辑与导出

### 3. 非功能需求
- 数据隐私保护（学生个人信息本地存储）
- 爬虫礼貌性（遵守robots.txt，限速请求）
- 离线功能支持（部分数据缓存）
- 响应式设计（支持PC和移动端）
- 中英文双语支持

## 技术架构

### 1. 总体架构
```
┌─────────────────────────────────────────────────────────────┐
│                         用户界面层                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  导师搜索 │  │ 匹配结果  │  │ 概率评估  │  │ 文书生成  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                         API网关层                            │
│                   认证、限流、请求路由                         │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                        业务逻辑层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │数据采集服务│  │匹配算法服务│  │概率评估服务│  │文书生成服务│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                        数据层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 关系数据库 │  │ 文档数据库 │  │ 缓存数据库 │  │ 文件存储  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                        外部数据源                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 学校官网  │  │ Excel数据 │  │ GitHub库 │  │学术数据库 │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2. 技术栈选择

#### 前端
- **框架**：React 18 + TypeScript（组件化，类型安全）
- **UI库**：Ant Design / Material-UI（成熟组件库）
- **状态管理**：Zustand（轻量级状态管理）
- **路由**：React Router v6
- **数据可视化**：ECharts / Recharts
- **PDF处理**：pdf.js / @react-pdf/renderer

#### 后端
- **主要框架**：Python FastAPI（高性能，异步支持）
- **数据爬虫**：Scrapy + BeautifulSoup + Selenium（动态页面）
- **数据处理**：Pandas（Excel处理）、PyPDF2（PDF解析）
- **自然语言处理**：jieba（中文分词）、sentence-transformers（文本相似度）
- **机器学习**：scikit-learn（分类模型）、LightGBM（概率预测）
- **数据库ORM**：SQLAlchemy + Alembic（迁移）

#### 数据库
- **主数据库**：PostgreSQL（关系数据，导师信息、用户数据）
- **缓存**：Redis（会话、临时数据）
- **文件存储**：本地文件系统 + 备份到云存储

#### 部署与运维
- **容器化**：Docker + Docker Compose
- **Web服务器**：Nginx（反向代理）
- **进程管理**：PM2（Node进程）或 Gunicorn（Python进程）
- **监控**：Prometheus + Grafana（可选）

### 3. 数据模型设计

#### 3.1 核心实体
```sql
-- 导师信息
CREATE TABLE professors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    university VARCHAR(200) NOT NULL,
    department VARCHAR(200),
    title VARCHAR(100),
    research_fields TEXT[],  -- 研究方向数组
    personal_page_url VARCHAR(500),
    email VARCHAR(100),
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 导师评价
CREATE TABLE professor_evaluations (
    id SERIAL PRIMARY KEY,
    professor_id INTEGER REFERENCES professors(id),
    source VARCHAR(50),  -- 'excel', 'github', 'manual'
    personality_score DECIMAL(3,2),  -- 人品得分 1-5
    group_atmosphere TEXT,  -- 课题组氛围描述
    student_comments TEXT,
    evaluation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学术论文
CREATE TABLE academic_papers (
    id SERIAL PRIMARY KEY,
    professor_id INTEGER REFERENCES professors(id),
    title TEXT NOT NULL,
    authors TEXT[],
    publication_venue VARCHAR(300),
    publication_year INTEGER,
    abstract TEXT,
    keywords TEXT[],
    pdf_url VARCHAR(500),
    citations INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学生信息
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    university VARCHAR(200) NOT NULL,
    major VARCHAR(200),
    gpa DECIMAL(3,2),
    gpa_ranking INTEGER,  -- 专业排名
    research_experience JSONB,  -- 科研经历
    competition_awards JSONB,  -- 竞赛获奖
    skills TEXT[],
    resume_pdf_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 匹配记录
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    professor_id INTEGER REFERENCES professors(id),
    research_match_score DECIMAL(5,4),  -- 研究方向匹配度
    background_match_score DECIMAL(5,4), -- 背景匹配度
    personality_match_score DECIMAL(5,4), -- 性格匹配度
    overall_score DECIMAL(5,4),  -- 综合匹配度
    admission_probability DECIMAL(5,4),  -- 录取概率
    match_reasons TEXT,  -- 匹配原因分析
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文书模板
CREATE TABLE document_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,  -- '套磁信', '个人陈述', '推荐信'
    category VARCHAR(100),  -- '通用', '力学', '机械'
    content_template TEXT NOT NULL,  -- 模板内容，含占位符
    variables JSONB,  -- 模板变量定义
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 生成文书
CREATE TABLE generated_documents (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    professor_id INTEGER REFERENCES professors(id),
    template_id INTEGER REFERENCES document_templates(id),
    document_type VARCHAR(100),
    content TEXT NOT NULL,
    file_path VARCHAR(500),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 实施路线图

### 阶段一：基础架构与数据采集（第1-2周）
#### 目标：搭建基础框架，实现核心数据采集
1. **项目初始化**
   - 创建React前端项目
   - 创建FastAPI后端项目
   - 配置数据库（PostgreSQL + Redis）
   - 设置开发环境（Docker Compose）

2. **数据采集模块开发**
   - Excel数据解析器（Pandas）
   - GitHub数据同步工具
   - 学校官网爬虫（针对目标院校：上海交大、浙大、清华深研院）
   - PDF简历解析器（提取学生信息）

3. **基础数据模型实现**
   - 数据库表创建与迁移
   - 基础CRUD API
   - 数据导入脚本

### 阶段二：匹配算法与概率评估（第3-4周）
#### 目标：开发智能匹配核心算法
1. **文本处理与特征提取**
   - 中文分词与关键词提取
   - 论文摘要向量化
   - 研究方向相似度计算

2. **匹配算法开发**
   - 多维度匹配权重配置
   - 综合评分算法
   - 相似导师推荐

3. **概率评估模型**
   - 历史数据统计分析
   - 基于机器学习的概率预测
   - 置信区间计算

### 阶段三：文书生成与用户界面（第5-6周）
#### 目标：实现文书生成和用户交互界面
1. **文书模板系统**
   - 模板管理（增删改查）
   - 变量替换引擎
   - 多版本支持

2. **前端界面开发**
   - 导师搜索与筛选页面
   - 匹配结果展示页面
   - 个人仪表板
   - 文书编辑器

3. **文书生成集成**
   - 基于模板的自动生成
   - 手动编辑与调整
   - 导出功能（PDF、Word）

### 阶段四：系统集成与优化（第7-8周）
#### 目标：系统集成、测试与优化
1. **系统集成测试**
   - 端到端测试
   - 性能测试
   - 安全测试

2. **用户体验优化**
   - 响应式设计优化
   - 加载性能优化
   - 错误处理与用户反馈

3. **部署与文档**
   - 生产环境部署
   - 用户使用文档
   - 维护手册

## 关键技术实现细节

### 1. 数据爬取策略
- **尊重robots.txt**：设置合理爬取间隔
- **动态内容处理**：Selenium处理JavaScript渲染页面
- **数据去重**：基于导师唯一标识（姓名+院校+院系）
- **增量更新**：定期检查数据更新

### 2. 研究方向匹配算法
```python
def calculate_research_similarity(student_interests, professor_fields, professor_papers):
    """
    计算学生研究方向与导师研究方向的相似度
    
    参数:
        student_interests: 学生研究方向列表
        professor_fields: 导师研究方向列表
        professor_papers: 导师论文列表（含摘要）
    
    返回:
        相似度得分 (0-1)
    """
    # 1. 关键词匹配（精确匹配）
    keyword_match = len(set(student_interests) & set(professor_fields)) / max(len(student_interests), 1)
    
    # 2. 文本相似度（基于论文摘要）
    if professor_papers:
        paper_abstracts = [paper['abstract'] for paper in professor_papers if paper.get('abstract')]
        student_interests_text = ' '.join(student_interests)
        # 使用sentence-transformers计算文本相似度
        text_similarity = calculate_text_similarity(student_interests_text, ' '.join(paper_abstracts))
    else:
        text_similarity = 0
    
    # 3. 综合得分（加权平均）
    similarity_score = 0.6 * keyword_match + 0.4 * text_similarity
    
    return similarity_score
```

### 3. 录取概率评估模型
```python
class AdmissionProbabilityModel:
    def __init__(self):
        self.features = [
            'university_tier_diff',      # 院校层级差异
            'gpa_percentile',           # GPA百分位
            'research_experience_score', # 科研经历评分
            'competition_score',        # 竞赛获奖评分
            'research_match_score',     # 研究方向匹配度
            'professor_popularity',     # 导师热门程度
        ]
        
    def predict(self, student_features, professor_features, match_score):
        """
        基于多因素预测录取概率
        
        使用梯度提升树模型，结合历史数据训练
        若无历史数据，使用规则-based初始模型
        """
        # 特征工程
        feature_vector = self.extract_features(
            student_features, 
            professor_features, 
            match_score
        )
        
        # 模型预测
        if self.model_trained:
            probability = self.model.predict_proba([feature_vector])[0][1]
        else:
            # 初始规则-based估计
            probability = self.rule_based_estimate(feature_vector)
        
        return probability
```

### 4. 文书生成引擎
```python
class DocumentGenerator:
    def __init__(self, template_repository):
        self.templates = template_repository
        
    def generate_cover_letter(self, student, professor, match_info):
        """
        生成个性化套磁信
        
        参数:
            student: 学生信息对象
            professor: 导师信息对象
            match_info: 匹配分析结果
        
        返回:
            生成的套磁信文本
        """
        # 选择最合适的模板
        template = self.select_template(student, professor)
        
        # 提取填充变量
        variables = {
            'student_name': student.name,
            'professor_name': professor.name,
            'professor_title': professor.title,
            'university': professor.university,
            'department': professor.department,
            'research_match': match_info.research_match_description,
            'student_background': self.format_background(student),
            'specific_reasons': self.generate_specific_reasons(student, professor),
            'closing_remarks': self.get_closing_remarks()
        }
        
        # 模板渲染
        document = self.render_template(template, variables)
        
        return document
```

## 数据源与集成

### 1. 初始数据源
- **本地Excel文件**：`12-全国高校导师评价数据.xlsx`
- **GitHub仓库**：`https://github.com/wangzhiye-tiancai/mysupervisor_save`
- **目标院校官网**：
  - 上海交通大学力学系、机械与动力学院
  - 浙江大学力学系、机械学院
  - 清华大学深圳研究院智能制造系
- **学术数据库**（后续扩展）：
  - 知网（CNKI）
  - Google Scholar
  - Web of Science

### 2. 数据更新策略
- **定时任务**：每周自动检查更新
- **手动触发**：用户可手动刷新数据
- **增量更新**：只获取变更数据
- **数据验证**：新旧数据对比，异常检测

## 项目目录结构

```
taoci-web/
├── frontend/                    # React前端
│   ├── public/
│   ├── src/
│   │   ├── components/         # 可复用组件
│   │   │   ├── ProfessorCard/
│   │   │   ├── MatchResult/
│   │   │   ├── DocumentEditor/
│   │   │   └── ...
│   │   ├── pages/             # 页面组件
│   │   │   ├── Home/
│   │   │   ├── Search/
│   │   │   ├── Dashboard/
│   │   │   └── ...
│   │   ├── services/          # API服务
│   │   ├── utils/             # 工具函数
│   │   ├── types/             # TypeScript类型定义
│   │   └── ...
│   ├── package.json
│   └── ...
├── backend/                    # FastAPI后端
│   ├── app/
│   │   ├── api/              # API端点
│   │   │   ├── v1/
│   │   │   │   ├── professors.py
│   │   │   │   ├── students.py
│   │   │   │   ├── matches.py
│   │   │   │   └── documents.py
│   │   ├── core/             # 核心配置
│   │   ├── db/               # 数据库相关
│   │   ├── models/           # Pydantic模型
│   │   ├── services/         # 业务逻辑
│   │   │   ├── data_collection.py
│   │   │   ├── matching.py
│   │   │   ├── probability.py
│   │   │   └── document_generation.py
│   │   ├── utils/            # 工具函数
│   │   └── main.py
│   ├── scripts/              # 脚本
│   │   ├── data_import.py
│   │   ├── crawler.py
│   │   └── ...
│   ├── requirements.txt
│   └── ...
├── data/                      # 数据文件
│   ├── raw/                  # 原始数据
│   ├── processed/            # 处理后的数据
│   └── exports/              # 导出文件
├── docs/                      # 文档
├── docker-compose.yml         # Docker编排
├── .env.example              # 环境变量示例
├── README.md                  # 项目说明
└── CLAUDE.md                  # Claude开发规范
```

## 风险评估与应对策略

### 技术风险
1. **数据爬取被封**：使用代理IP、限速请求、遵守robots.txt
2. **算法准确率不足**：采用多算法融合，提供人工调整接口
3. **性能瓶颈**：数据库索引优化、缓存策略、异步处理

### 数据风险
1. **数据质量不一**：数据清洗、验证、多源对比
2. **隐私合规问题**：本地存储敏感数据，匿名化处理
3. **数据更新滞后**：定期更新机制，用户反馈渠道

### 用户接受度风险
1. **界面复杂**：渐进式引导、详细帮助文档
2. **结果可信度**：透明展示算法依据，提供解释
3. **需求变化**：模块化设计，易于扩展

## 成功指标
- **数据覆盖**：目标院校导师信息覆盖率达90%以上
- **匹配准确率**：用户反馈匹配满意度达80%以上
- **文书生成质量**：生成文书可直接使用率70%以上
- **系统性能**：页面加载时间<3秒，API响应时间<1秒
- **用户活跃**：日活跃用户>10，周留存率>50%

## 后续扩展方向
1. **移动端应用**：微信小程序或原生APP
2. **更多院校支持**：扩展至全国985/211高校
3. **面试准备**：模拟面试题库、常见问题回答
4. **社区功能**：学长学姐经验分享、互助交流
5. **多语言支持**：英文界面，支持海外留学申请

---

**项目启动时间**：2026年4月15日  
**预期完成时间**：2026年6月15日（8周开发周期）  
**主要负责人**：吴凌钧、林静  
**技术支持**：Claude Code开发助手