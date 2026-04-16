"""
导师评价模型

对应数据库中的professor_evaluations表
"""

from datetime import date, datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, Text, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ProfessorEvaluation(Base):
    """导师评价模型"""

    __tablename__ = "professor_evaluations"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 外键关联
    professor_id = Column(Integer, ForeignKey("professors.id", ondelete="CASCADE"), nullable=False, comment="导师ID")

    # 评价来源
    source = Column(
        String(50),
        nullable=False,
        comment="评价来源: excel, github, manual, web"
    )

    # 评价内容
    personality_score = Column(
        Numeric(3, 2),
        comment="人品得分 1-5",
        info={"check_constraint": "personality_score >= 1 AND personality_score <= 5"}
    )
    group_atmosphere = Column(Text, comment="课题组氛围描述")
    student_comments = Column(Text, comment="学生评价")
    evaluation_date = Column(Date, comment="评价日期")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    professor = relationship("Professor", backref="evaluations")

    # 表级约束和索引
    __table_args__ = (
        # 唯一约束：同一导师、同一来源、同一天的唯一评价
        Index("idx_professor_evaluations_professor_id", "professor_id"),
        Index("idx_professor_evaluations_source", "source"),
        Index("idx_professor_evaluations_personality_score", "personality_score"),
        Index("unique_evaluation_source", "professor_id", "source", "evaluation_date", unique=True),
        {"comment": "导师评价表"},
    )

    def __repr__(self) -> str:
        return f"<ProfessorEvaluation(id={self.id}, professor_id={self.professor_id}, source='{self.source}')>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的导师评价信息
        """
        return {
            "id": self.id,
            "professor_id": self.professor_id,
            "source": self.source,
            "personality_score": float(self.personality_score) if self.personality_score else None,
            "group_atmosphere": self.group_atmosphere,
            "student_comments": self.student_comments,
            "evaluation_date": self.evaluation_date.isoformat() if self.evaluation_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProfessorEvaluation":
        """从字典创建导师评价实例

        Args:
            data: 导师评价数据字典

        Returns:
            ProfessorEvaluation实例
        """
        # 移除id等自动生成的字段
        create_data = {k: v for k, v in data.items() if k not in ["id", "created_at", "updated_at"]}

        # 转换日期字符串为date对象
        if "evaluation_date" in create_data and isinstance(create_data["evaluation_date"], str):
            create_data["evaluation_date"] = date.fromisoformat(create_data["evaluation_date"])

        return cls(**create_data)

    @property
    def is_recent(self) -> bool:
        """判断是否为近期评价（一年内）

        Returns:
            是否为近期评价
        """
        if not self.evaluation_date:
            return False

        today = date.today()
        one_year_ago = date(today.year - 1, today.month, today.day)
        return self.evaluation_date >= one_year_ago