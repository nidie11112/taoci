"""
学生信息模型

对应数据库中的students表
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func

from app.core.database import Base


class Student(Base):
    """学生信息模型"""

    __tablename__ = "students"

    # 主键
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    # 基本信息
    name = Column(String(100), nullable=False, comment="姓名")
    university = Column(String(200), nullable=False, comment="学校")
    major = Column(String(200), comment="专业")

    # 学术成绩
    gpa = Column(Numeric(3, 2), comment="GPA", info={"check_constraint": "gpa >= 0 AND gpa <= 5"})
    gpa_ranking = Column(Integer, comment="专业排名", info={"check_constraint": "gpa_ranking >= 1"})

    # 能力与经历
    research_experience = Column(JSON, default=list, comment="科研经历JSON数组")
    competition_awards = Column(JSON, default=list, comment="竞赛获奖JSON数组")
    skills = Column(ARRAY(Text), default=[], comment="技能列表")

    # 文件路径
    resume_pdf_path = Column(String(500), comment="简历PDF文件路径")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="软删除时间")

    # 表级约束（通过__table_args__定义）
    __table_args__ = (
        # 约束条件
        Index("idx_students_university", "university"),
        Index("idx_students_gpa", "gpa"),
        Index("idx_students_created_at", "created_at"),
        {"comment": "学生信息表"},
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name='{self.name}', university='{self.university}')>"

    def to_dict(self, include_related: bool = False) -> Dict[str, Any]:
        """转换为字典格式

        Args:
            include_related: 是否包含关联数据

        Returns:
            字典格式的学生信息
        """
        data = {
            "id": self.id,
            "uuid": str(self.uuid) if self.uuid else None,
            "name": self.name,
            "university": self.university,
            "major": self.major,
            "gpa": float(self.gpa) if self.gpa else None,
            "gpa_ranking": self.gpa_ranking,
            "research_experience": self.research_experience or [],
            "competition_awards": self.competition_awards or [],
            "skills": self.skills or [],
            "resume_pdf_path": self.resume_pdf_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        """从字典创建学生实例

        Args:
            data: 学生数据字典

        Returns:
            Student实例
        """
        # 移除id等自动生成的字段
        create_data = {k: v for k, v in data.items() if k not in ["id", "uuid", "created_at", "updated_at", "deleted_at"]}

        # 确保JSON字段正确初始化
        if "research_experience" not in create_data:
            create_data["research_experience"] = []
        if "competition_awards" not in create_data:
            create_data["competition_awards"] = []
        if "skills" not in create_data:
            create_data["skills"] = []

        return cls(**create_data)