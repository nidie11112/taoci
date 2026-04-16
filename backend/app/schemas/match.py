"""
匹配数据模式

定义匹配相关的Pydantic模型，用于API请求/响应验证
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class MatchBase(BaseModel):
    """匹配基础模式"""

    student_id: int = Field(..., description="学生ID")
    professor_id: int = Field(..., description="导师ID")
    research_match_score: float = Field(None, ge=0, le=1, description="研究方向匹配度")
    background_match_score: float = Field(None, ge=0, le=1, description="背景匹配度")
    personality_match_score: float = Field(None, ge=0, le=1, description="性格匹配度")
    overall_score: float = Field(None, ge=0, le=1, description="综合匹配度")
    admission_probability: float = Field(None, ge=0, le=1, description="录取概率")
    match_reasons: Optional[str] = Field(None, description="匹配原因分析")

    @validator("overall_score")
    def calculate_overall_score(cls, v, values):
        """如果未提供综合匹配度，根据各维度分数计算"""
        if v is None:
            research = values.get("research_match_score", 0)
            background = values.get("background_match_score", 0)
            personality = values.get("personality_match_score", 0)

            # 默认权重：研究方向40%，背景30%，性格30%
            if all(score is not None for score in [research, background, personality]):
                v = 0.4 * research + 0.3 * background + 0.3 * personality
            else:
                v = 0.0
        return v


class MatchCreate(MatchBase):
    """匹配创建模式"""

    class Config:
        schema_extra = {
            "example": {
                "student_id": 1,
                "professor_id": 1,
                "research_match_score": 0.85,
                "background_match_score": 0.75,
                "personality_match_score": 0.60,
                "overall_score": 0.75,
                "admission_probability": 0.65,
                "match_reasons": "研究方向高度匹配：学生研究兴趣与导师的复合材料、智能材料方向一致；背景契合：学生来自西安交大，成绩优秀，有相关科研经历；性格匹配：学生认真踏实，适合该导师的课题组氛围。"
            }
        }


class MatchUpdate(BaseModel):
    """匹配更新模式"""

    research_match_score: Optional[float] = Field(None, ge=0, le=1, description="研究方向匹配度")
    background_match_score: Optional[float] = Field(None, ge=0, le=1, description="背景匹配度")
    personality_match_score: Optional[float] = Field(None, ge=0, le=1, description="性格匹配度")
    overall_score: Optional[float] = Field(None, ge=0, le=1, description="综合匹配度")
    admission_probability: Optional[float] = Field(None, ge=0, le=1, description="录取概率")
    match_reasons: Optional[str] = Field(None, description="匹配原因分析")

    class Config:
        schema_extra = {
            "example": {
                "admission_probability": 0.70,
                "match_reasons": "更新匹配原因：学生近期发表了相关领域的论文，增加了录取概率。"
            }
        }


class MatchResponse(MatchBase):
    """匹配响应模式"""

    id: int = Field(..., description="匹配ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "student_id": 1,
                "professor_id": 1,
                "research_match_score": 0.85,
                "background_match_score": 0.75,
                "personality_match_score": 0.60,
                "overall_score": 0.75,
                "admission_probability": 0.65,
                "match_reasons": "研究方向高度匹配：学生研究兴趣与导师的复合材料、智能材料方向一致；背景契合：学生来自西安交大，成绩优秀，有相关科研经历；性格匹配：学生认真踏实，适合该导师的课题组氛围。",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class MatchDetailResponse(MatchResponse):
    """匹配详情响应模式"""

    student: Dict[str, Any] = Field(..., description="学生信息")
    professor: Dict[str, Any] = Field(..., description="导师信息")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "student_id": 1,
                "professor_id": 1,
                "research_match_score": 0.85,
                "background_match_score": 0.75,
                "personality_match_score": 0.60,
                "overall_score": 0.75,
                "admission_probability": 0.65,
                "match_reasons": "研究方向高度匹配：学生研究兴趣与导师的复合材料、智能材料方向一致；背景契合：学生来自西安交大，成绩优秀，有相关科研经历；性格匹配：学生认真踏实，适合该导师的课题组氛围。",
                "created_at": "2024-01-15T10:30:00Z",
                "student": {
                    "id": 1,
                    "name": "张三",
                    "university": "西安交通大学",
                    "major": "工程力学",
                    "gpa": 3.85
                },
                "professor": {
                    "id": 1,
                    "name": "李教授",
                    "university": "上海交通大学",
                    "department": "机械与动力工程学院",
                    "title": "教授",
                    "research_fields": ["力学", "复合材料", "智能材料"]
                }
            }
        }


class MatchListResponse(BaseModel):
    """匹配列表响应模式"""

    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    matches: list[MatchResponse] = Field(..., description="匹配列表")

    class Config:
        schema_extra = {
            "example": {
                "total": 50,
                "page": 1,
                "page_size": 20,
                "matches": [
                    {
                        "id": 1,
                        "student_id": 1,
                        "professor_id": 1,
                        "research_match_score": 0.85,
                        "background_match_score": 0.75,
                        "personality_match_score": 0.60,
                        "overall_score": 0.75,
                        "admission_probability": 0.65,
                        "match_reasons": "研究方向高度匹配...",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ]
            }
        }


class MatchSearchParams(BaseModel):
    """匹配搜索参数"""

    student_id: Optional[int] = Field(None, description="按学生ID筛选")
    professor_id: Optional[int] = Field(None, description="按导师ID筛选")
    min_score: Optional[float] = Field(None, ge=0, le=1, description="最低综合匹配度")
    min_probability: Optional[float] = Field(None, ge=0, le=1, description="最低录取概率")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")