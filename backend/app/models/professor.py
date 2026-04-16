"""
导师信息模型

对应数据库中的professors表
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, Index, JSON
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Professor(Base):
    """导师信息模型"""

    __tablename__ = "professors"

    # 主键
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, comment="UUID")

    # 基本信息
    name = Column(String(100), nullable=False, comment="姓名")
    university = Column(String(200), nullable=False, comment="学校")
    department = Column(String(200), comment="院系")
    title = Column(String(100), comment="职称")

    # 研究方向
    research_fields = Column(JSON, comment="研究方向数组（JSON格式）")

    # 联系信息
    personal_page_url = Column(String(500), unique=True, comment="个人主页URL")
    email = Column(String(100), unique=True, comment="邮箱")
    phone = Column(String(50), comment="电话")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="软删除时间")

    # 表级约束和索引
    __table_args__ = (
        # 索引
        Index("idx_professors_university", "university"),
        Index("idx_professors_department", "department"),
        Index("idx_professors_research_fields", "research_fields", postgresql_using="gin"),
        Index("idx_professors_created_at", "created_at"),
        # 约束在列定义中已经通过unique=True实现
        {"comment": "导师信息表"},
    )

    def __repr__(self) -> str:
        return f"<Professor(id={self.id}, name='{self.name}', university='{self.university}')>"

    def to_dict(self, include_related: bool = False) -> Dict[str, Any]:
        """转换为字典格式

        Args:
            include_related: 是否包含关联数据（如评价、论文等）

        Returns:
            字典格式的导师信息
        """
        data = {
            "id": self.id,
            "uuid": str(self.uuid) if self.uuid else None,
            "name": self.name,
            "university": self.university,
            "department": self.department,
            "title": self.title,
            "research_fields": self.research_fields or [],
            "personal_page_url": self.personal_page_url,
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Professor":
        """从字典创建导师实例

        Args:
            data: 导师数据字典

        Returns:
            Professor实例
        """
        # 移除id等自动生成的字段
        create_data = {k: v for k, v in data.items() if k not in ["id", "uuid", "created_at", "updated_at", "deleted_at"]}

        # 确保数组字段正确初始化
        if "research_fields" not in create_data:
            create_data["research_fields"] = []

        return cls(**create_data)

    def has_complete_profile(self) -> bool:
        """检查导师信息是否完整

        Returns:
            信息是否完整的布尔值
        """
        required_fields = [self.name, self.university, self.research_fields]
        return all(field is not None and (not isinstance(field, list) or len(field) > 0) for field in required_fields)