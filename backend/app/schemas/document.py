"""
文书数据模式

定义文书相关的Pydantic模型，用于API请求/响应验证
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class DocumentTemplateBase(BaseModel):
    """文书模板基础模式"""

    name: str = Field(..., min_length=1, max_length=200, description="模板名称")
    category: str = Field(..., description="模板分类: 通用, 力学, 机械, 智能制造, 其他")
    content_template: str = Field(..., min_length=10, description="模板内容")
    variables: Optional[Dict[str, Any]] = Field(default_factory=dict, description="模板变量定义")

    @validator("category")
    def validate_category(cls, v):
        """验证分类是否有效"""
        valid_categories = ["通用", "力学", "机械", "智能制造", "其他"]
        if v not in valid_categories:
            raise ValueError(f"分类必须是以下之一: {', '.join(valid_categories)}")
        return v

    @validator("variables")
    def validate_variables(cls, v):
        """验证变量定义"""
        if v is None:
            return {}
        return v


class DocumentTemplateCreate(DocumentTemplateBase):
    """文书模板创建模式"""

    class Config:
        schema_extra = {
            "example": {
                "name": "力学专业套磁信模板",
                "category": "力学",
                "content_template": "尊敬的{professor_name}教授：\n\n您好！\n\n我是{student_name}，来自{student_university}{student_major}专业的一名学生。我对您的研究方向{professor_research_fields}非常感兴趣，特别是{research_match}方面的工作。\n\n在本科期间，我学习了{relevant_courses}等课程，并在{research_experience}方面有了一定的研究经验。\n\n希望能够有机会加入您的课题组继续深造。\n\n此致\n敬礼！\n\n{student_name}\n{date}",
                "variables": {
                    "professor_name": "导师姓名",
                    "student_name": "学生姓名",
                    "student_university": "学生学校",
                    "student_major": "学生专业",
                    "professor_research_fields": "导师研究方向",
                    "research_match": "研究方向匹配点",
                    "relevant_courses": "相关课程",
                    "research_experience": "科研经历",
                    "date": "日期"
                }
            }
        }


class DocumentTemplateUpdate(BaseModel):
    """文书模板更新模式"""

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="模板名称")
    category: Optional[str] = Field(None, description="模板分类: 通用, 力学, 机械, 智能制造, 其他")
    content_template: Optional[str] = Field(None, min_length=10, description="模板内容")
    variables: Optional[Dict[str, Any]] = Field(None, description="模板变量定义")

    class Config:
        schema_extra = {
            "example": {
                "category": "机械",
                "variables": {
                    "professor_name": "导师姓名",
                    "student_name": "学生姓名",
                    "student_university": "学生学校",
                    "student_major": "学生专业",
                    "professor_research_fields": "导师研究方向",
                    "research_match": "研究方向匹配点",
                    "relevant_courses": "相关课程",
                    "research_experience": "科研经历",
                    "date": "日期",
                    "specific_project": "具体项目经验"
                }
            }
        }


class DocumentTemplateResponse(DocumentTemplateBase):
    """文书模板响应模式"""

    id: int = Field(..., description="模板ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "力学专业套磁信模板",
                "category": "力学",
                "content_template": "尊敬的{professor_name}教授：\n\n您好！\n\n我是{student_name}，来自{student_university}{student_major}专业的一名学生。我对您的研究方向{professor_research_fields}非常感兴趣，特别是{research_match}方面的工作。\n\n在本科期间，我学习了{relevant_courses}等课程，并在{research_experience}方面有了一定的研究经验。\n\n希望能够有机会加入您的课题组继续深造。\n\n此致\n敬礼！\n\n{student_name}\n{date}",
                "variables": {
                    "professor_name": "导师姓名",
                    "student_name": "学生姓名",
                    "student_university": "学生学校",
                    "student_major": "学生专业",
                    "professor_research_fields": "导师研究方向",
                    "research_match": "研究方向匹配点",
                    "relevant_courses": "相关课程",
                    "research_experience": "科研经历",
                    "date": "日期"
                },
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "deleted_at": None
            }
        }


class GeneratedDocumentBase(BaseModel):
    """生成文书基础模式"""

    student_id: int = Field(..., description="学生ID")
    professor_id: Optional[int] = Field(None, description="导师ID")
    template_id: Optional[int] = Field(None, description="模板ID")
    document_type: str = Field(..., description="文书类型: 套磁信, 个人陈述, 自我介绍, 推荐信, 其他")
    content: str = Field(..., min_length=10, description="文书内容")
    file_path: Optional[str] = Field(None, description="文件保存路径")

    @validator("document_type")
    def validate_document_type(cls, v):
        """验证文书类型是否有效"""
        valid_types = ["套磁信", "个人陈述", "自我介绍", "推荐信", "其他"]
        if v not in valid_types:
            raise ValueError(f"文书类型必须是以下之一: {', '.join(valid_types)}")
        return v


class GeneratedDocumentCreate(GeneratedDocumentBase):
    """生成文书创建模式"""

    class Config:
        schema_extra = {
            "example": {
                "student_id": 1,
                "professor_id": 1,
                "template_id": 1,
                "document_type": "套磁信",
                "content": "尊敬的李教授：\n\n您好！\n\n我是张三，来自西安交通大学工程力学专业的一名学生。我对您的研究方向力学、复合材料、智能材料非常感兴趣，特别是复合材料方面的工作。\n\n在本科期间，我学习了材料力学、结构力学、复合材料力学等课程，并在复合材料力学性能研究方面有了一定的研究经验。\n\n希望能够有机会加入您的课题组继续深造。\n\n此致\n敬礼！\n\n张三\n2024-01-15",
                "file_path": "/documents/student_1_professor_1_cover_letter_20240115.pdf"
            }
        }


class GeneratedDocumentUpdate(BaseModel):
    """生成文书更新模式"""

    content: Optional[str] = Field(None, min_length=10, description="文书内容")
    file_path: Optional[str] = Field(None, description="文件保存路径")

    class Config:
        schema_extra = {
            "example": {
                "content": "更新后的套磁信内容...",
                "file_path": "/documents/student_1_professor_1_cover_letter_20240116_v2.pdf"
            }
        }


class GeneratedDocumentResponse(GeneratedDocumentBase):
    """生成文书响应模式"""

    id: int = Field(..., description="文书ID")
    generated_at: datetime = Field(..., description="生成时间")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "student_id": 1,
                "professor_id": 1,
                "template_id": 1,
                "document_type": "套磁信",
                "content": "尊敬的李教授：\n\n您好！\n\n我是张三，来自西安交通大学工程力学专业的一名学生。我对您的研究方向力学、复合材料、智能材料非常感兴趣，特别是复合材料方面的工作。\n\n在本科期间，我学习了材料力学、结构力学、复合材料力学等课程，并在复合材料力学性能研究方面有了一定的研究经验。\n\n希望能够有机会加入您的课题组继续深造。\n\n此致\n敬礼！\n\n张三\n2024-01-15",
                "file_path": "/documents/student_1_professor_1_cover_letter_20240115.pdf",
                "generated_at": "2024-01-15T10:30:00Z"
            }
        }


class GeneratedDocumentDetailResponse(GeneratedDocumentResponse):
    """生成文书详情响应模式"""

    student: Optional[Dict[str, Any]] = Field(None, description="学生信息")
    professor: Optional[Dict[str, Any]] = Field(None, description="导师信息")
    template: Optional[Dict[str, Any]] = Field(None, description="模板信息")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "student_id": 1,
                "professor_id": 1,
                "template_id": 1,
                "document_type": "套磁信",
                "content": "尊敬的李教授：\n\n您好！\n\n我是张三，来自西安交通大学工程力学专业的一名学生。我对您的研究方向力学、复合材料、智能材料非常感兴趣，特别是复合材料方面的工作。\n\n在本科期间，我学习了材料力学、结构力学、复合材料力学等课程，并在复合材料力学性能研究方面有了一定的研究经验。\n\n希望能够有机会加入您的课题组继续深造。\n\n此致\n敬礼！\n\n张三\n2024-01-15",
                "file_path": "/documents/student_1_professor_1_cover_letter_20240115.pdf",
                "generated_at": "2024-01-15T10:30:00Z",
                "student": {
                    "id": 1,
                    "name": "张三",
                    "university": "西安交通大学",
                    "major": "工程力学"
                },
                "professor": {
                    "id": 1,
                    "name": "李教授",
                    "university": "上海交通大学",
                    "department": "机械与动力工程学院",
                    "title": "教授"
                },
                "template": {
                    "id": 1,
                    "name": "力学专业套磁信模板",
                    "category": "力学"
                }
            }
        }


class DocumentGenerationRequest(BaseModel):
    """文书生成请求"""

    student_id: int = Field(..., description="学生ID")
    professor_id: Optional[int] = Field(None, description="导师ID")
    template_id: Optional[int] = Field(None, description="模板ID（如不提供，自动选择最合适的模板）")
    document_type: str = Field(..., description="文书类型: 套磁信, 个人陈述, 自我介绍, 推荐信, 其他")
    custom_variables: Optional[Dict[str, Any]] = Field(default_factory=dict, description="自定义变量")

    class Config:
        schema_extra = {
            "example": {
                "student_id": 1,
                "professor_id": 1,
                "template_id": 1,
                "document_type": "套磁信",
                "custom_variables": {
                    "research_match": "复合材料方向",
                    "relevant_courses": "材料力学、结构力学、复合材料力学",
                    "research_experience": "复合材料力学性能研究"
                }
            }
        }


class DocumentGenerationResponse(BaseModel):
    """文书生成响应"""

    success: bool = Field(..., description="是否成功")
    document_id: Optional[int] = Field(None, description="生成的文书ID")
    document_content: Optional[str] = Field(None, description="文书内容")
    error_message: Optional[str] = Field(None, description="错误信息")
    warnings: List[str] = Field(default_factory=list, description="警告信息")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "document_id": 1,
                "document_content": "生成的信件内容...",
                "error_message": None,
                "warnings": ["缺少部分变量信息，已使用默认值填充"]
            }
        }


class DocumentTemplateListResponse(BaseModel):
    """文书模板列表响应模式"""

    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    templates: List[DocumentTemplateResponse] = Field(..., description="模板列表")

    class Config:
        schema_extra = {
            "example": {
                "total": 10,
                "page": 1,
                "page_size": 20,
                "templates": [
                    {
                        "id": 1,
                        "name": "力学专业套磁信模板",
                        "category": "力学",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                ]
            }
        }


class GeneratedDocumentListResponse(BaseModel):
    """生成文书列表响应模式"""

    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    documents: List[GeneratedDocumentResponse] = Field(..., description="文书列表")

    class Config:
        schema_extra = {
            "example": {
                "total": 50,
                "page": 1,
                "page_size": 20,
                "documents": [
                    {
                        "id": 1,
                        "student_id": 1,
                        "professor_id": 1,
                        "document_type": "套磁信",
                        "generated_at": "2024-01-15T10:30:00Z"
                    }
                ]
            }
        }