"""
文书模板模型

对应数据库中的document_templates表
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class DocumentTemplate(Base):
    """文书模板模型"""

    __tablename__ = "document_templates"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 模板信息
    name = Column(String(200), nullable=False, unique=True, comment="模板名称")
    category = Column(
        String(100),
        comment="模板分类: 通用, 力学, 机械, 智能制造, 其他",
        info={"check_constraint": "category IN ('通用', '力学', '机械', '智能制造', '其他')"}
    )
    content_template = Column(Text, nullable=False, comment="模板内容")

    # 模板变量
    variables = Column(JSONB, default=dict, comment="模板变量定义")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="软删除时间")

    # 表级约束和索引
    __table_args__ = (
        # 索引
        Index("idx_document_templates_category", "category"),
        {"comment": "文书模板表"},
    )

    def __repr__(self) -> str:
        return f"<DocumentTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的模板信息
        """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "content_template": self.content_template,
            "variables": self.variables or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentTemplate":
        """从字典创建模板实例

        Args:
            data: 模板数据字典

        Returns:
            DocumentTemplate实例
        """
        # 移除id等自动生成的字段
        create_data = {k: v for k, v in data.items() if k not in ["id", "created_at", "updated_at", "deleted_at"]}

        # 确保JSON字段正确初始化
        if "variables" not in create_data:
            create_data["variables"] = {}

        return cls(**create_data)

    def validate_variables(self, provided_vars: Dict[str, Any]) -> List[str]:
        """验证提供的变量是否符合模板要求

        Args:
            provided_vars: 提供的变量字典

        Returns:
            缺失的变量名列表
        """
        required_vars = set(self.variables.keys() if self.variables else [])
        provided_var_names = set(provided_vars.keys())

        missing_vars = list(required_vars - provided_var_names)
        return missing_vars

    def render(self, variables: Dict[str, Any]) -> str:
        """渲染模板

        Args:
            variables: 模板变量

        Returns:
            渲染后的文本
        """
        if not self.content_template:
            return ""

        # 验证变量
        missing_vars = self.validate_variables(variables)
        if missing_vars:
            raise ValueError(f"缺少必要的模板变量: {missing_vars}")

        # 简单模板渲染：使用字符串替换
        content = self.content_template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in content:
                content = content.replace(placeholder, str(value))

        return content