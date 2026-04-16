"""
数据库模型定义

基于SQLAlchemy ORM定义所有数据库表模型
"""

from app.core.database import Base

# 导入所有模型
from app.models.student import Student
from app.models.professor import Professor
from app.models.professor_evaluation import ProfessorEvaluation
from app.models.academic_paper import AcademicPaper
from app.models.match import Match
from app.models.document_template import DocumentTemplate
from app.models.generated_document import GeneratedDocument
from app.models.user import User

# 导出所有模型
__all__ = [
    "Student",
    "Professor",
    "ProfessorEvaluation",
    "AcademicPaper",
    "Match",
    "DocumentTemplate",
    "GeneratedDocument",
    "User",
    "Base",
]