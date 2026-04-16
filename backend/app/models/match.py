"""
匹配记录模型

对应数据库中的matches表
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, Numeric, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Match(Base):
    """匹配记录模型"""

    __tablename__ = "matches"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 外键关联
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, comment="学生ID")
    professor_id = Column(Integer, ForeignKey("professors.id", ondelete="CASCADE"), nullable=False, comment="导师ID")

    # 匹配分数
    research_match_score = Column(
        Numeric(5, 4),
        comment="研究方向匹配度 0-1",
        info={"check_constraint": "research_match_score >= 0 AND research_match_score <= 1"}
    )
    background_match_score = Column(
        Numeric(5, 4),
        comment="背景匹配度 0-1",
        info={"check_constraint": "background_match_score >= 0 AND background_match_score <= 1"}
    )
    personality_match_score = Column(
        Numeric(5, 4),
        comment="性格匹配度 0-1",
        info={"check_constraint": "personality_match_score >= 0 AND personality_match_score <= 1"}
    )
    overall_score = Column(
        Numeric(5, 4),
        comment="综合匹配度 0-1",
        info={"check_constraint": "overall_score >= 0 AND overall_score <= 1"}
    )
    admission_probability = Column(
        Numeric(5, 4),
        comment="录取概率 0-1",
        info={"check_constraint": "admission_probability >= 0 AND admission_probability <= 1"}
    )

    # 匹配分析
    match_reasons = Column(Text, comment="匹配原因分析")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关系
    student = relationship("Student", backref="matches")
    professor = relationship("Professor", backref="matches")

    # 表级约束和索引
    __table_args__ = (
        # 唯一约束：同一学生和导师只能有一条匹配记录
        Index("idx_matches_student_id", "student_id"),
        Index("idx_matches_professor_id", "professor_id"),
        Index("idx_matches_overall_score", "overall_score", postgresql_using="btree"),
        Index("idx_matches_admission_probability", "admission_probability", postgresql_using="btree"),
        Index("unique_match", "student_id", "professor_id", unique=True),
        {"comment": "匹配记录表"},
    )

    def __repr__(self) -> str:
        return f"<Match(id={self.id}, student_id={self.student_id}, professor_id={self.professor_id}, score={self.overall_score})>"

    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """转换为字典格式

        Args:
            include_details: 是否包含学生和导师的详细信息

        Returns:
            字典格式的匹配信息
        """
        data = {
            "id": self.id,
            "student_id": self.student_id,
            "professor_id": self.professor_id,
            "research_match_score": float(self.research_match_score) if self.research_match_score else None,
            "background_match_score": float(self.background_match_score) if self.background_match_score else None,
            "personality_match_score": float(self.personality_match_score) if self.personality_match_score else None,
            "overall_score": float(self.overall_score) if self.overall_score else None,
            "admission_probability": float(self.admission_probability) if self.admission_probability else None,
            "match_reasons": self.match_reasons,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_details and self.student:
            data["student"] = self.student.to_dict()
        if include_details and self.professor:
            data["professor"] = self.professor.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Match":
        """从字典创建匹配实例

        Args:
            data: 匹配数据字典

        Returns:
            Match实例
        """
        # 移除id等自动生成的字段
        create_data = {k: v for k, v in data.items() if k not in ["id", "created_at"]}

        return cls(**create_data)

    @property
    def is_high_match(self) -> bool:
        """判断是否为高匹配度（综合匹配度 > 0.8）

        Returns:
            是否为高匹配度
        """
        return self.overall_score > 0.8 if self.overall_score else False

    @property
    def is_high_admission_probability(self) -> bool:
        """判断是否为高录取概率（录取概率 > 0.7）

        Returns:
            是否为高录取概率
        """
        return self.admission_probability > 0.7 if self.admission_probability else False

    @property
    def match_level(self) -> str:
        """获取匹配等级

        Returns:
            匹配等级：高、中、低
        """
        if not self.overall_score:
            return "未知"

        if self.overall_score >= 0.8:
            return "高"
        elif self.overall_score >= 0.6:
            return "中"
        else:
            return "低"