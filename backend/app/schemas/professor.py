"""
导师数据模式

定义导师相关的Pydantic模型，用于API请求/响应验证
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator, HttpUrl, UUID4
import uuid


class ProfessorBase(BaseModel):
    """导师基础模式"""

    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    university: str = Field(..., min_length=1, max_length=200, description="学校")
    department: Optional[str] = Field(None, max_length=200, description="院系")
    title: Optional[str] = Field(None, max_length=100, description="职称")
    research_fields: Optional[List[str]] = Field(default_factory=list, description="研究方向列表")
    personal_page_url: Optional[str] = Field(None, max_length=500, description="个人主页URL")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=50, description="电话")

    @validator("research_fields")
    def validate_research_fields(cls, v):
        """验证研究方向列表"""
        if v is None:
            return []
        return v

    @validator("email")
    def validate_email(cls, v):
        """验证邮箱格式"""
        if v is not None:
            # 简单的邮箱格式验证
            if "@" not in v or "." not in v:
                raise ValueError("邮箱格式无效")
        return v


class ProfessorCreate(ProfessorBase):
    """导师创建模式"""

    class Config:
        schema_extra = {
            "example": {
                "name": "李教授",
                "university": "上海交通大学",
                "department": "机械与动力工程学院",
                "title": "教授",
                "research_fields": ["力学", "复合材料", "智能材料"],
                "personal_page_url": "https://me.sjtu.edu.cn/faculty/li",
                "email": "li.professor@sjtu.edu.cn",
                "phone": "021-3420XXXX"
            }
        }


class ProfessorUpdate(BaseModel):
    """导师更新模式"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="姓名")
    university: Optional[str] = Field(None, min_length=1, max_length=200, description="学校")
    department: Optional[str] = Field(None, max_length=200, description="院系")
    title: Optional[str] = Field(None, max_length=100, description="职称")
    research_fields: Optional[List[str]] = Field(None, description="研究方向列表")
    personal_page_url: Optional[str] = Field(None, max_length=500, description="个人主页URL")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=50, description="电话")

    class Config:
        schema_extra = {
            "example": {
                "title": "博士生导师",
                "research_fields": ["力学", "复合材料", "智能材料", "3D打印"],
                "email": "li.professor@sjtu.edu.cn"
            }
        }


class ProfessorResponse(ProfessorBase):
    """导师响应模式"""

    id: int = Field(..., description="导师ID")
    uuid: UUID4 = Field(..., description="导师UUID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "name": "李教授",
                "university": "上海交通大学",
                "department": "机械与动力工程学院",
                "title": "教授",
                "research_fields": ["力学", "复合材料", "智能材料"],
                "personal_page_url": "https://me.sjtu.edu.cn/faculty/li",
                "email": "li.professor@sjtu.edu.cn",
                "phone": "021-3420XXXX",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "deleted_at": None
            }
        }


class ProfessorListResponse(BaseModel):
    """导师列表响应模式"""

    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    professors: List[ProfessorResponse] = Field(..., description="导师列表")

    class Config:
        schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "professors": [
                    {
                        "id": 1,
                        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "name": "李教授",
                        "university": "上海交通大学",
                        "department": "机械与动力工程学院",
                        "title": "教授",
                        "research_fields": ["力学", "复合材料", "智能材料"],
                        "personal_page_url": "https://me.sjtu.edu.cn/faculty/li",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                ]
            }
        }


class ProfessorSearchParams(BaseModel):
    """导师搜索参数"""

    university: Optional[str] = Field(None, description="按学校筛选")
    department: Optional[str] = Field(None, description="按院系筛选")
    title: Optional[str] = Field(None, description="按职称筛选")
    research_field: Optional[str] = Field(None, description="按研究方向筛选")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")