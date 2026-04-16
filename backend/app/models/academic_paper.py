"""
学术论文模型

对应数据库中的academic_papers表
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AcademicPaper(Base):
    """学术论文模型"""

    __tablename__ = "academic_papers"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 外键关联
    professor_id = Column(Integer, ForeignKey("professors.id", ondelete="CASCADE"), nullable=False, comment="导师ID")

    # 论文信息
    title = Column(Text, nullable=False, comment="论文标题")
    authors = Column(ARRAY(Text), comment="作者列表")
    publication_venue = Column(String(300), comment="发表期刊/会议")
    publication_year = Column(
        Integer,
        comment="发表年份",
        info={"check_constraint": "publication_year >= 1900 AND publication_year <= EXTRACT(YEAR FROM CURRENT_DATE) + 5"}
    )
    abstract = Column(Text, comment="摘要")
    keywords = Column(ARRAY(Text), comment="关键词列表")
    pdf_url = Column(String(500), comment="PDF文件URL")
    citations = Column(Integer, default=0, comment="引用次数", info={"check_constraint": "citations >= 0"})

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关系
    professor = relationship("Professor", backref="papers")

    # 表级约束和索引
    __table_args__ = (
        # 索引
        Index("idx_academic_papers_professor_id", "professor_id"),
        Index("idx_academic_papers_publication_year", "publication_year"),
        Index("idx_academic_papers_keywords", "keywords", postgresql_using="gin"),
        {"comment": "学术论文表"},
    )

    def __repr__(self) -> str:
        return f"<AcademicPaper(id={self.id}, title='{self.title[:50]}...', professor_id={self.professor_id})>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的论文信息
        """
        return {
            "id": self.id,
            "professor_id": self.professor_id,
            "title": self.title,
            "authors": self.authors or [],
            "publication_venue": self.publication_venue,
            "publication_year": self.publication_year,
            "abstract": self.abstract,
            "keywords": self.keywords or [],
            "pdf_url": self.pdf_url,
            "citations": self.citations,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AcademicPaper":
        """从字典创建论文实例

        Args:
            data: 论文数据字典

        Returns:
            AcademicPaper实例
        """
        # 移除id等自动生成的字段
        create_data = {k: v for k, v in data.items() if k not in ["id", "created_at"]}

        # 确保数组字段正确初始化
        if "authors" not in create_data:
            create_data["authors"] = []
        if "keywords" not in create_data:
            create_data["keywords"] = []

        return cls(**create_data)

    @property
    def is_recent(self) -> bool:
        """判断是否为近期论文（近5年）

        Returns:
            是否为近期论文
        """
        if not self.publication_year:
            return False

        from datetime import datetime
        current_year = datetime.now().year
        return self.publication_year >= (current_year - 5)

    @property
    def is_highly_cited(self) -> bool:
        """判断是否为高被引论文（引用超过100次）

        Returns:
            是否为高被引论文
        """
        return self.citations > 100 if self.citations else False