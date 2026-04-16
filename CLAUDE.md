# 保研导师信息搜集网站 - 开发规范与指南

## 项目概览

本项目为"保研导师信息搜集网站"，旨在帮助中国大学生（特别是工程力学专业学生吴凌钧与林静）在保研过程中智能化地搜索、匹配导师，并生成个性化申请文书。系统包含React前端、Python FastAPI后端、数据爬取引擎和智能匹配算法。

本文件定义了代码生成规范、项目配置注意事项以及开发工作流，确保项目高质量交付。

## 开发工作流要求

### 1. 研究优先原则
在实现任何功能前，必须按顺序执行：
1. **GitHub代码搜索**：`gh search repos` 和 `gh search code` 寻找现有导师匹配、学术爬虫、文书生成相关实现
2. **官方文档查阅**：React、FastAPI、PostgreSQL、相关库的官方文档
3. **Exa网络搜索**：仅当前两步不足时使用，搜索学术数据API、保研相关资源
4. **包注册表检查**：搜索npm、PyPI，优先使用成熟库（如pandas、scikit-learn、sentence-transformers）

### 2. 计划先行
- 复杂功能必须使用**planner** agent创建实施计划
- 生成规划文档：PRD、架构设计、技术文档、任务列表
- 识别依赖和风险，分阶段实施
- **特别重要**：数据爬取策略需谨慎设计，遵守目标网站robots.txt

### 3. TDD开发模式
- 使用**tdd-guide** agent进行测试驱动开发
- 红-绿-重构循环：先写测试，再实现，后优化
- 确保测试覆盖率≥80%
- 重点测试：匹配算法准确性、数据解析正确性、文书生成质量

### 4. 代码审查
- 代码编写后立即使用**code-reviewer** agent
- 修复CRITICAL和HIGH级别问题
- 尽可能修复MEDIUM级别问题
- **安全审查必须**：数据爬取不违反法律，用户隐私保护

## 前端开发规范（React + TypeScript）

### 1. 项目结构规范
```
frontend/
├── public/                    # 静态资源
├── src/
│   ├── components/           # 可复用组件
│   │   ├── common/          # 通用组件
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   ├── Modal/
│   │   │   └── ...
│   │   ├── professor/       # 导师相关组件
│   │   │   ├── ProfessorCard/
│   │   │   ├── ProfessorDetail/
│   │   │   ├── ProfessorSearch/
│   │   │   └── ...
│   │   ├── matching/        # 匹配相关组件
│   │   │   ├── MatchResult/
│   │   │   ├── ProbabilityIndicator/
│   │   │   ├── ResearchComparison/
│   │   │   └── ...
│   │   ├── documents/       # 文书相关组件
│   │   │   ├── DocumentEditor/
│   │   │   ├── TemplateSelector/
│   │   │   ├── DocumentPreview/
│   │   │   └── ...
│   │   └── dashboard/       # 仪表板组件
│   │       ├── PersonalProfile/
│   │       ├── ProgressTracker/
│   │       ├── StrengthWeaknessAnalysis/
│   │       └── ...
│   ├── pages/               # 页面组件
│   │   ├── Home/           # 首页
│   │   ├── Search/         # 导师搜索页
│   │   ├── ProfessorDetail/ # 导师详情页
│   │   ├── Dashboard/      # 个人仪表板
│   │   ├── Documents/      # 文书管理页
│   │   ├── Settings/       # 设置页
│   │   └── ...
│   ├── services/           # API服务
│   │   ├── api/           # API调用封装
│   │   │   ├── professors.ts
│   │   │   ├── students.ts
│   │   │   ├── matches.ts
│   │   │   ├── documents.ts
│   │   │   └── ...
│   │   ├── auth/          # 认证服务
│   │   └── ...
│   ├── store/             # 状态管理（Zustand）
│   │   ├── professorStore.ts
│   │   ├── userStore.ts
│   │   ├── uiStore.ts
│   │   └── ...
│   ├── utils/             # 工具函数
│   │   ├── formatters.ts  # 数据格式化
│   │   ├── validators.ts  # 表单验证
│   │   ├── pdfHelper.ts   # PDF处理工具
│   │   └── ...
│   ├── types/             # TypeScript类型定义
│   │   ├── professor.ts
│   │   ├── student.ts
│   │   ├── match.ts
│   │   ├── document.ts
│   │   └── ...
│   ├── styles/            # 全局样式
│   ├── hooks/             # 自定义Hook
│   ├── constants/         # 常量定义
│   ├── App.tsx           # 根组件
│   └── index.tsx         # 入口文件
├── package.json
├── tsconfig.json
├── .eslintrc.js
└── ...
```

### 2. TypeScript编码规范
- 使用严格模式（`strict: true`）
- 所有函数、组件必须有明确的类型定义
- 避免使用`any`类型，使用`unknown`或具体类型
- 接口命名以`I`开头或直接使用描述性名词

```typescript
// GOOD - 清晰的类型定义
interface Professor {
  id: number;
  name: string;
  university: string;
  department: string;
  title: string;
  researchFields: string[];
  personalPageUrl: string;
  email?: string;
  phone?: string;
}

interface ProfessorEvaluation {
  professorId: number;
  source: 'excel' | 'github' | 'manual';
  personalityScore: number; // 1-5
  groupAtmosphere: string;
  studentComments: string;
  evaluationDate: Date;
}

interface MatchResult {
  professor: Professor;
  researchMatchScore: number; // 0-1
  backgroundMatchScore: number;
  personalityMatchScore: number;
  overallScore: number;
  admissionProbability: number;
  matchReasons: string[];
}

// BAD - 避免any类型
const handleData = (data: any) => { /* ... */ };
```

### 3. React组件规范
- 使用函数组件 + Hooks
- 复杂组件使用`React.memo`优化性能
- 事件处理函数使用`useCallback`缓存
- 副作用使用`useEffect`，明确依赖项

```typescript
// GOOD - 清晰的函数组件
import React, { useState, useEffect, useCallback } from 'react';
import { Professor, MatchResult } from '@/types/professor';
import { getProfessorMatches } from '@/services/api/matches';
import ProfessorCard from '@/components/professor/ProfessorCard';
import MatchDetails from '@/components/matching/MatchDetails';

interface ProfessorMatchProps {
  studentId: number;
  initialProfessor?: Professor;
}

const ProfessorMatch: React.FC<ProfessorMatchProps> = ({ 
  studentId, 
  initialProfessor 
}) => {
  const [professor, setProfessor] = useState<Professor | undefined>(initialProfessor);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 获取匹配结果
  const fetchMatchResult = useCallback(async (profId: number) => {
    if (!studentId || !profId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await getProfessorMatches(studentId, profId);
      setMatchResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取匹配结果失败');
      console.error('获取匹配结果失败:', err);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  // 教授变化时重新获取匹配结果
  useEffect(() => {
    if (professor) {
      fetchMatchResult(professor.id);
    }
  }, [professor, fetchMatchResult]);

  const handleProfessorSelect = (selectedProfessor: Professor) => {
    setProfessor(selectedProfessor);
  };

  if (loading) {
    return <div className="loading-spinner">加载中...</div>;
  }

  if (error) {
    return <div className="error-message">错误: {error}</div>;
  }

  return (
    <div className="professor-match-container">
      <div className="professor-selection">
        <h2>选择导师</h2>
        {/* 导师选择组件 */}
      </div>
      
      {professor && (
        <>
          <div className="professor-info">
            <ProfessorCard professor={professor} />
          </div>
          
          {matchResult && (
            <div className="match-results">
              <MatchDetails matchResult={matchResult} />
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default React.memo(ProfessorMatch);
```

### 4. 状态管理规范
- 使用Zustand进行状态管理
- 将相关状态组织在同一store中
- 状态更新使用不可变数据

```typescript
// store/professorStore.ts
import { create } from 'zustand';
import { Professor, ProfessorFilter } from '@/types/professor';

interface ProfessorState {
  // 状态
  professors: Professor[];
  selectedProfessor: Professor | null;
  filters: ProfessorFilter;
  loading: boolean;
  error: string | null;
  
  // 操作
  setProfessors: (professors: Professor[]) => void;
  setSelectedProfessor: (professor: Professor | null) => void;
  updateFilters: (updates: Partial<ProfessorFilter>) => void;
  fetchProfessors: () => Promise<void>;
  clearError: () => void;
}

const useProfessorStore = create<ProfessorState>((set, get) => ({
  // 初始状态
  professors: [],
  selectedProfessor: null,
  filters: {
    university: '',
    department: '',
    researchField: '',
    minPersonalityScore: 3.0,
  },
  loading: false,
  error: null,
  
  // 操作方法
  setProfessors: (professors) => set({ professors }),
  
  setSelectedProfessor: (professor) => set({ selectedProfessor: professor }),
  
  updateFilters: (updates) => 
    set((state) => ({ 
      filters: { ...state.filters, ...updates } 
    })),
    
  fetchProfessors: async () => {
    const { filters } = get();
    set({ loading: true, error: null });
    
    try {
      // API调用获取教授列表
      const response = await fetchProfessorsApi(filters);
      set({ professors: response.data, loading: false });
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : '获取导师列表失败',
        loading: false 
      });
    }
  },
  
  clearError: () => set({ error: null }),
}));

export default useProfessorStore;
```

### 5. API服务规范
- 统一封装HTTP请求
- 错误统一处理
- 请求拦截器处理认证

```typescript
// services/api/client.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

class ApiClient {
  private client: AxiosInstance;
  
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        // 添加认证token
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // 响应拦截器
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response.data,
      (error) => {
        // 统一错误处理
        if (error.response) {
          const { status, data } = error.response;
          
          switch (status) {
            case 401:
              // 未授权，跳转登录
              window.location.href = '/login';
              break;
            case 403:
              console.error('权限不足:', data.detail);
              break;
            case 404:
              console.error('资源不存在:', data.detail);
              break;
            case 500:
              console.error('服务器错误:', data.detail);
              break;
            default:
              console.error(`请求错误 ${status}:`, data.detail);
          }
        } else if (error.request) {
          console.error('网络错误，请检查网络连接');
        } else {
          console.error('请求配置错误:', error.message);
        }
        
        return Promise.reject(error);
      }
    );
  }
  
  // 通用请求方法
  public async request<T>(config: AxiosRequestConfig): Promise<T> {
    return this.client.request(config);
  }
  
  public get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request({ ...config, method: 'GET', url });
  }
  
  public post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request({ ...config, method: 'POST', url, data });
  }
  
  public put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request({ ...config, method: 'PUT', url, data });
  }
  
  public delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request({ ...config, method: 'DELETE', url });
  }
}

export const apiClient = new ApiClient();
```

## 后端开发规范（Python FastAPI）

### 1. 项目结构规范
```
backend/
├── app/
│   ├── api/              # API端点
│   │   ├── v1/          # API版本1
│   │   │   ├── __init__.py
│   │   │   ├── professors.py
│   │   │   ├── students.py
│   │   │   ├── matches.py
│   │   │   ├── documents.py
│   │   │   ├── auth.py
│   │   │   └── ...
│   │   └── __init__.py
│   ├── core/            # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py    # 配置管理
│   │   ├── security.py  # 安全相关
│   │   ├── database.py  # 数据库连接
│   │   └── dependencies.py # 依赖注入
│   ├── db/              # 数据库模型
│   │   ├── __init__.py
│   │   ├── models.py    # SQLAlchemy模型
│   │   ├── crud.py      # CRUD操作
│   │   ├── session.py   # 数据库会话
│   │   └── migrations/  # 数据库迁移
│   ├── models/          # Pydantic模型
│   │   ├── __init__.py
│   │   ├── professor.py
│   │   ├── student.py
│   │   ├── match.py
│   │   ├── document.py
│   │   └── schemas.py   # 请求/响应模型
│   ├── services/        # 业务逻辑
│   │   ├── __init__.py
│   │   ├── data_collection/  # 数据采集服务
│   │   │   ├── __init__.py
│   │   │   ├── crawler.py    # 网页爬虫
│   │   │   ├── excel_parser.py # Excel解析
│   │   │   ├── pdf_parser.py # PDF解析
│   │   │   └── github_sync.py # GitHub同步
│   │   ├── matching/         # 匹配服务
│   │   │   ├── __init__.py
│   │   │   ├── research_matcher.py  # 研究方向匹配
│   │   │   ├── background_matcher.py # 背景匹配
│   │   │   ├── personality_matcher.py # 性格匹配
│   │   │   └── score_calculator.py   # 分数计算
│   │   ├── probability/      # 概率评估服务
│   │   │   ├── __init__.py
│   │   │   ├── predictor.py  # 概率预测
│   │   │   └── analyzer.py   # 分析器
│   │   ├── document_generation/ # 文书生成服务
│   │   │   ├── __init__.py
│   │   │   ├── template_manager.py # 模板管理
│   │   │   ├── generator.py    # 生成器
│   │   │   └── formatter.py    # 格式化
│   │   └── __init__.py
│   ├── utils/           # 工具函数
│   │   ├── __init__.py
│   │   ├── text_processing.py # 文本处理
│   │   ├── file_helpers.py    # 文件帮助
│   │   ├── validators.py      # 验证器
│   │   └── logger.py          # 日志
│   └── main.py          # 应用入口
├── scripts/              # 脚本
│   ├── data_import.py   # 数据导入
│   ├── crawler.py       # 爬虫脚本
│   ├── backup.py        # 备份脚本
│   └── ...
├── tests/               # 测试目录
├── requirements.txt     # Python依赖
├── requirements-dev.txt # 开发依赖
├── Dockerfile          # Docker配置
├── docker-compose.yml  # Docker Compose配置
├── alembic.ini         # 数据库迁移配置
└── .env.example        # 环境变量示例
```

### 2. Python编码规范
- Python 3.11+
- 使用类型提示（Type Hints）
- 异步优先（async/await）
- 遵循PEP 8规范
- 使用Black进行代码格式化
- 使用isort进行import排序

```python
# GOOD - 清晰的类型提示和异步代码
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Professor, Student, Match
from app.db.crud import professor_crud, student_crud, match_crud
from app.db.session import get_db
from app.models.professor import ProfessorCreate, ProfessorUpdate, ProfessorOut
from app.services.matching import MatchingService

router = APIRouter(prefix="/api/v1/professors", tags=["professors"])

class MatchRequest(BaseModel):
    """匹配请求模型"""
    student_id: int
    professor_id: int
    include_details: bool = Field(default=True, description="是否包含详细匹配信息")
    
    @validator('student_id', 'professor_id')
    def validate_ids(cls, v):
        if v <= 0:
            raise ValueError('ID必须大于0')
        return v

@router.post("/match", response_model=Dict[str, Any])
async def match_professor(
    match_request: MatchRequest,
    db: AsyncSession = Depends(get_db),
    matching_service: MatchingService = Depends()
) -> Dict[str, Any]:
    """
    匹配学生与导师
    
    Args:
        match_request: 匹配请求参数
        db: 数据库会话
        matching_service: 匹配服务
        
    Returns:
        匹配结果
        
    Raises:
        HTTPException: 学生或导师不存在，或匹配失败
    """
    try:
        # 验证学生和导师是否存在
        student = await student_crud.get(db, match_request.student_id)
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
            
        professor = await professor_crud.get(db, match_request.professor_id)
        if not professor:
            raise HTTPException(status_code=404, detail="导师不存在")
        
        # 执行匹配
        match_result = await matching_service.match_student_professor(
            student=student,
            professor=professor,
            include_details=match_request.include_details
        )
        
        # 保存匹配记录
        match_record = Match(
            student_id=student.id,
            professor_id=professor.id,
            research_match_score=match_result.research_match_score,
            background_match_score=match_result.background_match_score,
            personality_match_score=match_result.personality_match_score,
            overall_score=match_result.overall_score,
            admission_probability=match_result.admission_probability,
            match_reasons=','.join(match_result.match_reasons) if match_result.match_reasons else None,
            created_at=datetime.utcnow()
        )
        
        await match_crud.create(db, match_record)
        
        return {
            "success": True,
            "data": match_result.dict(),
            "message": "匹配成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 记录错误日志
        logger.error(f"匹配失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="匹配服务内部错误")
```

### 3. 数据库操作规范
- 使用SQLAlchemy 2.0+异步ORM
- 每个操作必须有事务管理
- 查询优化，避免N+1问题
- 使用连接池

```python
# app/db/crud.py
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import Professor
from app.models.professor import ProfessorCreate, ProfessorUpdate

class ProfessorCRUD:
    """导师CRUD操作"""
    
    @staticmethod
    async def create(db: AsyncSession, professor_data: ProfessorCreate) -> Professor:
        """创建导师记录"""
        try:
            professor = Professor(**professor_data.dict())
            db.add(professor)
            await db.commit()
            await db.refresh(professor)
            return professor
        except SQLAlchemyError as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def get(db: AsyncSession, professor_id: int) -> Optional[Professor]:
        """根据ID获取导师"""
        stmt = select(Professor).where(Professor.id == professor_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_multi(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Professor]:
        """获取导师列表（支持过滤）"""
        stmt = select(Professor)
        
        # 应用过滤器
        if filters:
            if university := filters.get('university'):
                stmt = stmt.where(Professor.university.ilike(f"%{university}%"))
            if department := filters.get('department'):
                stmt = stmt.where(Professor.department.ilike(f"%{department}%"))
            if research_field := filters.get('research_field'):
                stmt = stmt.where(Professor.research_fields.any(research_field))
            if min_score := filters.get('min_personality_score'):
                # 关联查询评价表获取人品得分
                pass
        
        stmt = stmt.offset(skip).limit(limit).order_by(Professor.name)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def update(
        db: AsyncSession, 
        professor_id: int, 
        professor_data: ProfessorUpdate
    ) -> Optional[Professor]:
        """更新导师信息"""
        try:
            stmt = (
                update(Professor)
                .where(Professor.id == professor_id)
                .values(**professor_data.dict(exclude_unset=True))
                .returning(Professor)
            )
            result = await db.execute(stmt)
            await db.commit()
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def delete(db: AsyncSession, professor_id: int) -> bool:
        """删除导师记录"""
        try:
            stmt = delete(Professor).where(Professor.id == professor_id)
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await db.rollback()
            raise e

# 创建实例
professor_crud = ProfessorCRUD()
```

### 4. 数据爬取规范（重要！）
- 严格遵守目标网站robots.txt
- 设置合理的请求间隔（至少2-3秒）
- 使用User-Agent标识自己
- 处理反爬机制（但不使用违法手段）
- 数据本地缓存，避免重复请求

```python
# app/services/data_collection/crawler.py
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class UniversityCrawler:
    """大学官网爬虫基类"""
    
    def __init__(self, base_url: str, delay: float = 2.0):
        self.base_url = base_url
        self.delay = delay  # 请求延迟（秒）
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; TaociWebBot/1.0; +https://taoci-web.example.com/bot)'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_professors(self) -> List[Dict[str, Any]]:
        """获取导师列表"""
        raise NotImplementedError("子类必须实现此方法")
    
    async def fetch_professor_detail(self, url: str) -> Dict[str, Any]:
        """获取导师详细信息"""
        raise NotImplementedError("子类必须实现此方法")
    
    async def _get(self, url: str, **kwargs) -> str:
        """发送GET请求"""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        try:
            await asyncio.sleep(self.delay)  # 礼貌性延迟
            async with self.session.get(url, **kwargs) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            logger.error(f"请求失败 {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误 {url}: {e}")
            raise
    
    def _parse_html(self, html: str) -> BeautifulSoup:
        """解析HTML"""
        return BeautifulSoup(html, 'html.parser')
    
    def _check_robots_txt(self) -> bool:
        """检查robots.txt（示例）"""
        # 实际实现需要解析robots.txt
        # 这里简化处理
        parsed_url = urlparse(self.base_url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        # 实际应该检查是否允许爬取目标路径
        return True

class SJTUMechanicsCrawler(UniversityCrawler):
    """上海交通大学力学系爬虫"""
    
    def __init__(self):
        super().__init__(
            base_url="https://mech.sjtu.edu.cn",
            delay=3.0  # 更长的延迟，避免给服务器造成压力
        )
    
    async def fetch_professors(self) -> List[Dict[str, Any]]:
        """获取上海交大力学系导师列表"""
        professors = []
        
        # 检查robots.txt
        if not self._check_robots_txt():
            logger.warning(f"可能违反robots.txt: {self.base_url}")
            return professors
        
        try:
            # 获取导师列表页
            list_url = urljoin(self.base_url, "/teacher/list")
            html = await self._get(list_url)
            soup = self._parse_html(html)
            
            # 解析导师列表（根据实际网页结构调整）
            professor_items = soup.select('.teacher-list .teacher-item')
            
            for item in professor_items:
                name_elem = item.select_one('.name')
                if not name_elem:
                    continue
                    
                name = name_elem.text.strip()
                detail_link = item.select_one('a')
                
                if detail_link and detail_link.get('href'):
                    detail_url = urljoin(self.base_url, detail_link['href'])
                    
                    professor_info = {
                        'name': name,
                        'university': '上海交通大学',
                        'department': '力学系',
                        'detail_url': detail_url,
                        'source': 'sjtu_mechanics',
                        'crawled_at': datetime.utcnow()
                    }
                    
                    professors.append(professor_info)
            
            logger.info(f"从上海交大力学系获取到 {len(professors)} 位导师")
            return professors
            
        except Exception as e:
            logger.error(f"获取上海交大力学系导师列表失败: {e}")
            return []
    
    async def fetch_professor_detail(self, url: str) -> Dict[str, Any]:
        """获取导师详细信息"""
        try:
            html = await self._get(url)
            soup = self._parse_html(html)
            
            # 解析详细信息（根据实际网页结构调整）
            detail = {
                'name': self._extract_text(soup, '.professor-name'),
                'title': self._extract_text(soup, '.professor-title'),
                'research_fields': self._extract_list(soup, '.research-fields li'),
                'email': self._extract_text(soup, '.email'),
                'phone': self._extract_text(soup, '.phone'),
                'personal_page': url,
                'education_background': self._extract_text(soup, '.education'),
                'work_experience': self._extract_text(soup, '.experience'),
                'research_direction': self._extract_text(soup, '.research-direction'),
                'publications': self._extract_list(soup, '.publications li'),
            }
            
            # 清理空值
            detail = {k: v for k, v in detail.items() if v}
            
            return detail
            
        except Exception as e:
            logger.error(f"获取导师详情失败 {url}: {e}")
            return {}
    
    def _extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """提取文本"""
        elem = soup.select_one(selector)
        return elem.text.strip() if elem else None
    
    def _extract_list(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """提取列表"""
        elems = soup.select(selector)
        return [elem.text.strip() for elem in elems if elem.text.strip()]
```

## 配置注意事项

### 1. 环境变量配置
```bash
# .env.example
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/taoci_web
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# JWT配置
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# 爬虫配置
CRAWLER_DELAY_SECONDS=2.5
CRAWLER_MAX_RETRIES=3
CRAWLER_USER_AGENT=TaociWebBot/1.0 (+https://taoci-web.example.com/bot)

# 文件存储
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# 机器学习模型
ML_MODEL_PATH=./models/match_model.pkl
SENTENCE_TRANSFORMER_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# 外部API（如有）
SCHOLAR_API_KEY=your_google_scholar_api_key
CNKI_API_KEY=your_cnki_api_key

# 前端配置
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 2. 安全配置
- 所有API必须使用HTTPS（生产环境）
- CORS配置：仅允许前端域名
- 请求频率限制：防止滥用
- SQL注入防护：使用参数化查询
- XSS防护：输入输出转义
- 文件上传限制：文件类型、大小检查

```python
# app/core/security.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# CORS配置
def setup_cors(app):
    origins = [
        "http://localhost:3000",  # 前端开发地址
        "http://localhost:8080",
        # 生产环境添加实际域名
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 信任主机头
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "*.example.com"]  # 生产环境配置
    )

# 限流配置
limiter = Limiter(key_func=get_remote_address)

def setup_rate_limit(app):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # 不同端点不同限制
    @app.middleware("http")
    async def rate_limit_middleware(request, call_next):
        # 根据路径设置不同限制
        path = request.url.path
        if path.startswith("/api/v1/auth"):
            # 认证端点更严格
            limiter.limit("5/minute")(lambda: None)
        elif path.startswith("/api/v1/crawler"):
            # 爬虫端点限制
            limiter.limit("10/minute")(lambda: None)
        else:
            # 普通端点
            limiter.limit("60/minute")(lambda: None)
        
        response = await call_next(request)
        return response
```

### 3. 日志配置
```python
# app/utils/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_dir: str = "logs"):
    """配置日志"""
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # 文件处理器（按大小轮转）
    file_handler = RotatingFileHandler(
        log_path / "taoci_web.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # 错误日志单独文件
    error_handler = RotatingFileHandler(
        log_path / "error.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # 爬虫日志单独文件
    crawler_handler = RotatingFileHandler(
        log_path / "crawler.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )
    crawler_handler.setFormatter(formatter)
    crawler_handler.setLevel(logging.INFO)
    
    # 配置根日志
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # 爬虫日志器
    crawler_logger = logging.getLogger("crawler")
    crawler_logger.addHandler(crawler_handler)
    crawler_logger.propagate = False
    
    # SQLAlchemy日志
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

## 数据隐私与合规性

### 1. 用户数据保护
- 学生个人信息本地加密存储
- 简历PDF解析后删除原始文件
- 不存储用户密码，使用哈希
- 敏感数据（如成绩、排名）仅在客户端处理

### 2. 爬虫伦理
- 严格遵守robots.txt
- 设置合理请求频率，不造成服务器负担
- 仅爬取公开信息，不尝试破解登录
- 尊重版权，合理使用数据

### 3. 数据使用声明
- 明确告知用户数据来源和使用方式
- 提供数据删除功能
- 不将用户数据用于商业用途或分享给第三方

## 测试策略

### 1. 单元测试
- 业务逻辑核心算法必须单元测试
- 数据库CRUD操作测试
- 工具函数测试

### 2. 集成测试
- API端点集成测试
- 数据库事务测试
- 外部服务模拟测试

### 3. 端到端测试
- 关键用户流程测试
- 跨浏览器兼容性测试
- 移动端响应式测试

### 4. 性能测试
- API响应时间测试
- 并发用户测试
- 大数据量处理测试

## 部署指南

### 1. 开发环境
```bash
# 克隆项目
git clone <repository-url>
cd taoci-web

# 启动后端服务
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 启动数据库
docker-compose up -d postgres redis

# 运行迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端
cd ../frontend
npm install
npm start
```

### 2. 生产环境部署
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DATABASE_NAME}
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
  
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - api
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## 维护与监控

### 1. 健康检查
- API健康检查端点：`/health`
- 数据库连接检查
- 外部服务可用性检查

### 2. 监控指标
- 请求响应时间
- 错误率
- 数据库连接池使用率
- 爬虫成功率

### 3. 备份策略
- 每日数据库备份
- 重要文件版本控制
- 配置文件备份

## 故障排查

### 常见问题
1. **数据库连接失败**：检查连接字符串、网络、防火墙
2. **爬虫被屏蔽**：检查User-Agent、请求频率、代理设置
3. **内存泄漏**：检查循环引用、未关闭的资源
4. **性能下降**：检查数据库索引、查询优化、缓存策略

### 调试命令
```bash
# 查看服务状态
docker-compose ps
docker-compose logs -f api

# 数据库连接测试
pg_isready -h localhost -p 5432 -d taoci_web

# Redis连接测试
redis-cli -h localhost ping

# API健康检查
curl -I http://localhost:8000/health

# 前端构建检查
npm run build -- --dry-run
```

## 版本发布流程

1. **开发分支**：feature/* 分支开发新功能
2. **测试分支**：develop 分支集成测试
3. **预发布**：release/* 分支进行最终测试
4. **生产发布**：main 分支打标签发布
5. **热修复**：hotfix/* 分支紧急修复

---

**重要提醒**：
- 本项目涉及数据爬取，必须遵守相关法律法规和网站条款
- 用户隐私数据必须严格保护，本地加密存储
- 算法结果仅供参考，实际保研决策需结合多方面因素
- 定期检查外部数据源变化，更新爬取策略

*本文件持续更新，每次架构变更需同步更新此文档*