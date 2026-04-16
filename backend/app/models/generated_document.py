"""
生成文书模型

对应数据库中的generated_documents表
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class GeneratedDocument(Base):
    """生成文书模型"""

    __tablename__ = "generated_documents"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 外键关联
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, comment="学生ID")
    professor_id = Column(
        Integer,
        ForeignKey("professors.id", ondelete="SET NULL"),
        nullable=True,
        comment="导师ID"
    )
    template_id = Column(
        Integer,
        ForeignKey("document_templates.id", ondelete="SET NULL"),
        nullable=True,
        comment="模板ID"
    )

    # 文书信息
    document_type = Column(
        String(100),
        nullable=False,
        comment="文书类型: 套磁信, 个人陈述, 自我介绍, 推荐信, 其他",
        info={"check_constraint": "document_type IN ('套磁信', '个人陈述', '自我介绍', '推荐信', '其他')"}
    )
    content = Column(Text, nullable=False, comment="文书内容")
    file_path = Column(String(500), comment="文件保存路径")

    # 生成时间
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), comment="生成时间")

    # 关系
    student = relationship("Student", backref="generated_documents")
    professor = relationship("Professor", backref="generated_documents")
    template = relationship("DocumentTemplate", backref="generated_documents")

    # 表级约束和索引
    __table_args__ = (
        # 索引
        Index("idx_generated_documents_student_id", "student_id"),
        Index("idx_generated_documents_professor_id", "professor_id"),
        Index("idx_generated_documents_document_type", "document_type"),
        {"comment": "生成文书表"},
    )

    def __repr__(self) -> str:
        return f"<GeneratedDocument(id={self.id}, student_id={self.student_id}, document_type='{self.document_type}')>"

    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """转换为字典格式

        Args:
            include_details: 是否包含学生、导师和模板的详细信息

        Returns:
            字典格式的文书信息
        """
        data = {
            "id": self.id,
            "student_id": self.student_id,
            "professor_id": self.professor_id,
            "template_id": self.template_id,
            "document_type": self.document_type,
            "content": self.content,
            "file_path": self.file_path,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }

        if include_details:
            if self.student:
                data["student"] = self.student.to_dict()
            if self.professor:
                data["professor"] = self.professor.to_dict()
            if self.template:
                data["template"] = self.template.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeneratedDocument":
        """从字典创建文书实例

        Args:
            data: 文书数据字典

        Returns:
            GeneratedDocument实例
        """
        # 移除id等自动生成的字段
        create_data = {k: v for k, v in data.items() if k not in ["id", "generated_at"]}

        return cls(**create_data)

    @property
    def is_cover_letter(self) -> bool:
        """判断是否为套磁信

        Returns:
            是否为套磁信
        """
        return self.document_type == "套磁信"

    @property
    def has_professor(self) -> bool:
        """判断是否有关联的导师

        Returns:
            是否有关联的导师
        """
        return self.professor_id is not None

    def get_summary(self, max_length: int = 200) -> str:
        """获取文书摘要

        Args:
            max_length: 摘要最大长度

        Returns:
            文书摘要
        """
        if not self.content:
            return ""

        # 去除空白字符
        content = self.content.strip()

        if len(content) <= max_length:
            return content

        # 截取摘要
        summary = content[:max_length]
        # 避免在单词中间截断
        last_space = summary.rfind(' ')
        if last_space > max_length * 0.8:  # 如果截断位置在80%之后有空格
            summary = summary[:last_space]

        return summary + "..."