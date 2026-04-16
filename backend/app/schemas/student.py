"""
学生数据模式

定义学生相关的Pydantic模型，用于API请求/响应验证
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class StudentBase(BaseModel):
    """学生基础模式"""

    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    university: str = Field(..., min_length=1, max_length=200, description="学校")
    major: Optional[str] = Field(None, max_length=200, description="专业")
    gpa: Optional[float] = Field(None, ge=0, le=5, description="GPA")
    gpa_ranking: Optional[int] = Field(None, ge=1, description="专业排名")
    skills: Optional[List[str]] = Field(default_factory=list, description="技能列表")
    resume_pdf_path: Optional[str] = Field(None, max_length=500, description="简历PDF文件路径")

    @validator("gpa")
    def validate_gpa(cls, v):
        """验证GPA格式"""
        if v is not None:
            # 保留两位小数
            return round(v, 2)
        return v


class StudentCreate(StudentBase):
    """学生创建模式"""

    research_experience: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="科研经历"
    )
    competition_awards: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="竞赛获奖"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "张三",
                "university": "西安交通大学",
                "major": "工程力学",
                "gpa": 3.85,
                "gpa_ranking": 10,
                "skills": ["Python", "有限元分析", "MATLAB"],
                "research_experience": [
                    {
                        "project": "复合材料力学性能研究",
                        "role": "项目负责人",
                        "duration": "2023.03-2023.12",
                        "description": "研究复合材料的力学性能和失效机制"
                    }
                ],
                "competition_awards": [
                    {
                        "name": "全国大学生力学竞赛",
                        "level": "国家级",
                        "award": "一等奖",
                        "year": 2023
                    }
                ]
            }
        }


class StudentUpdate(BaseModel):
    """学生更新模式"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="姓名")
    university: Optional[str] = Field(None, min_length=1, max_length=200, description="学校")
    major: Optional[str] = Field(None, max_length=200, description="专业")
    gpa: Optional[float] = Field(None, ge=0, le=5, description="GPA")
    gpa_ranking: Optional[int] = Field(None, ge=1, description="专业排名")
    skills: Optional[List[str]] = Field(None, description="技能列表")
    research_experience: Optional[List[Dict[str, Any]]] = Field(None, description="科研经历")
    competition_awards: Optional[List[Dict[str, Any]]] = Field(None, description="竞赛获奖")
    resume_pdf_path: Optional[str] = Field(None, max_length=500, description="简历PDF文件路径")

    class Config:
        schema_extra = {
            "example": {
                "gpa": 3.9,
                "skills": ["Python", "有限元分析", "MATLAB", "ANSYS"],
                "research_experience": [
                    {
                        "project": "复合材料力学性能研究",
                        "role": "项目负责人",
                        "duration": "2023.03-2023.12",
                        "description": "研究复合材料的力学性能和失效机制"
                    },
                    {
                        "project": "智能材料结构设计",
                        "role": "参与研究",
                        "duration": "2024.01-2024.06",
                        "description": "参与智能材料结构的设计与优化"
                    }
                ]
            }
        }


class StudentResponse(StudentBase):
    """学生响应模式"""

    id: int = Field(..., description="学生ID")
    uuid: uuid.UUID = Field(..., description="学生UUID")
    research_experience: List[Dict[str, Any]] = Field(..., description="科研经历")
    competition_awards: List[Dict[str, Any]] = Field(..., description="竞赛获奖")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "name": "张三",
                "university": "西安交通大学",
                "major": "工程力学",
                "gpa": 3.85,
                "gpa_ranking": 10,
                "skills": ["Python", "有限元分析", "MATLAB"],
                "research_experience": [
                    {
                        "project": "复合材料力学性能研究",
                        "role": "项目负责人",
                        "duration": "2023.03-2023.12",
                        "description": "研究复合材料的力学性能和失效机制"
                    }
                ],
                "competition_awards": [
                    {
                        "name": "全国大学生力学竞赛",
                        "level": "国家级",
                        "award": "一等奖",
                        "year": 2023
                    }
                ],
                "resume_pdf_path": "/uploads/resumes/student_1_resume.pdf",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "deleted_at": None
            }
        }


class StudentListResponse(BaseModel):
    """学生列表响应模式"""

    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    students: List[StudentResponse] = Field(..., description="学生列表")

    class Config:
        schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "students": [
                    {
                        "id": 1,
                        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "name": "张三",
                        "university": "西安交通大学",
                        "major": "工程力学",
                        "gpa": 3.85,
                        "gpa_ranking": 10,
                        "skills": ["Python", "有限元分析", "MATLAB"],
                        "resume_pdf_path": "/uploads/resumes/student_1_resume.pdf",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                ]
            }
        }