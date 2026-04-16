"""
CRUD操作模块

提供数据库的通用CRUD操作
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.ext.declarative import DeclarativeMeta

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """CRUD基础类"""

    def __init__(self, model: Type[ModelType]):
        """初始化

        Args:
            model: SQLAlchemy模型类
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """根据ID获取记录

        Args:
            db: 数据库会话
            id: 记录ID

        Returns:
            模型实例或None
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Optional[ModelType]:
        """根据UUID获取记录

        Args:
            db: 数据库会话
            uuid: 记录UUID

        Returns:
            模型实例或None
        """
        query = select(self.model).where(self.model.uuid == uuid)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        """获取多条记录

        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 返回的最大记录数
            **filters: 筛选条件

        Returns:
            模型实例列表
        """
        query = select(self.model)

        # 应用筛选条件
        for attr, value in filters.items():
            if hasattr(self.model, attr) and value is not None:
                if isinstance(value, list):
                    query = query.where(getattr(self.model, attr).in_(value))
                else:
                    query = query.where(getattr(self.model, attr) == value)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: Dict[str, Any]) -> ModelType:
        """创建记录

        Args:
            db: 数据库会话
            obj_in: 输入数据字典

        Returns:
            创建的模型实例
        """
        # 使用模型的from_dict方法（如果存在）
        if hasattr(self.model, 'from_dict'):
            db_obj = self.model.from_dict(obj_in)
        else:
            db_obj = self.model(**obj_in)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """更新记录

        Args:
            db: 数据库会话
            db_obj: 数据库中的模型实例
            obj_in: 更新数据字典

        Returns:
            更新后的模型实例
        """
        update_data = obj_in
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_by_id(
        self,
        db: AsyncSession,
        *,
        id: Any,
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """根据ID更新记录

        Args:
            db: 数据库会话
            id: 记录ID
            obj_in: 更新数据字典

        Returns:
            更新后的模型实例或None
        """
        db_obj = await self.get(db, id)
        if db_obj is None:
            return None

        return await self.update(db, db_obj=db_obj, obj_in=obj_in)

    async def remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """删除记录

        Args:
            db: 数据库会话
            id: 记录ID

        Returns:
            删除的模型实例或None
        """
        db_obj = await self.get(db, id)
        if db_obj is None:
            return None

        await db.delete(db_obj)
        await db.commit()
        return db_obj

    async def soft_remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """软删除记录

        Args:
            db: 数据库会话
            id: 记录ID

        Returns:
            更新的模型实例或None
        """
        db_obj = await self.get(db, id)
        if db_obj is None:
            return None

        if hasattr(db_obj, 'deleted_at'):
            from sqlalchemy.sql import func
            setattr(db_obj, 'deleted_at', func.now())
            await db.commit()
            await db.refresh(db_obj)

        return db_obj

    async def count(self, db: AsyncSession, **filters) -> int:
        """统计记录数量

        Args:
            db: 数据库会话
            **filters: 筛选条件

        Returns:
            记录数量
        """
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model)

        # 应用筛选条件
        for attr, value in filters.items():
            if hasattr(self.model, attr) and value is not None:
                if isinstance(value, list):
                    query = query.where(getattr(self.model, attr).in_(value))
                else:
                    query = query.where(getattr(self.model, attr) == value)

        result = await db.execute(query)
        return result.scalar()


# 创建特定模型的CRUD类

from app.models.user import User
from app.models.student import Student
from app.models.professor import Professor
from app.models.professor_evaluation import ProfessorEvaluation
from app.models.academic_paper import AcademicPaper
from app.models.match import Match
from app.models.document_template import DocumentTemplate
from app.models.generated_document import GeneratedDocument


class CRUDUser(CRUDBase[User]):
    """用户CRUD操作"""

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户

        Args:
            db: 数据库会话
            email: 用户邮箱

        Returns:
            用户实例或None
        """
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户

        Args:
            db: 数据库会话
            username: 用户名

        Returns:
            用户实例或None
        """
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def authenticate(
        self,
        db: AsyncSession,
        *,
        username: str,
        password: str
    ) -> Optional[User]:
        """用户认证

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码

        Returns:
            用户实例或None
        """
        user = await self.get_by_username(db, username=username)
        if not user:
            return None

        # 验证密码
        if not user.verify_password(password):
            return None

        return user


class CRUDStudent(CRUDBase[Student]):
    """学生CRUD操作"""

    async def get_by_name_and_university(
        self,
        db: AsyncSession,
        *,
        name: str,
        university: str
    ) -> Optional[Student]:
        """根据姓名和学校获取学生

        Args:
            db: 数据库会话
            name: 学生姓名
            university: 学校名称

        Returns:
            学生实例或None
        """
        query = select(Student).where(
            Student.name == name,
            Student.university == university,
            Student.deleted_at.is_(None)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


class CRUDProfessor(CRUDBase[Professor]):
    """导师CRUD操作"""

    async def get_by_name_and_university(
        self,
        db: AsyncSession,
        *,
        name: str,
        university: str
    ) -> Optional[Professor]:
        """根据姓名和学校获取导师

        Args:
            db: 数据库会话
            name: 导师姓名
            university: 学校名称

        Returns:
            导师实例或None
        """
        query = select(Professor).where(
            Professor.name == name,
            Professor.university == university,
            Professor.deleted_at.is_(None)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def search(
        self,
        db: AsyncSession,
        *,
        keyword: Optional[str] = None,
        university: Optional[str] = None,
        department: Optional[str] = None,
        research_field: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Professor]:
        """搜索导师

        Args:
            db: 数据库会话
            keyword: 关键词
            university: 学校
            department: 院系
            research_field: 研究方向
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            导师列表
        """
        from sqlalchemy import or_

        query = select(Professor).where(Professor.deleted_at.is_(None))

        if keyword:
            query = query.where(or_(
                Professor.name.ilike(f"%{keyword}%"),
                Professor.university.ilike(f"%{keyword}%"),
                Professor.department.ilike(f"%{keyword}%"),
                Professor.title.ilike(f"%{keyword}%"),
            ))

        if university:
            query = query.where(Professor.university.ilike(f"%{university}%"))

        if department:
            query = query.where(Professor.department.ilike(f"%{department}%"))

        if research_field:
            # 使用数组包含操作符
            query = query.where(Professor.research_fields.contains([research_field]))

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


class CRUDMatch(CRUDBase[Match]):
    """匹配CRUD操作"""

    async def get_by_student_and_professor(
        self,
        db: AsyncSession,
        *,
        student_id: int,
        professor_id: int
    ) -> Optional[Match]:
        """根据学生和导师获取匹配记录

        Args:
            db: 数据库会话
            student_id: 学生ID
            professor_id: 导师ID

        Returns:
            匹配实例或None
        """
        query = select(Match).where(
            Match.student_id == student_id,
            Match.professor_id == professor_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


# 实例化CRUD类
user_crud = CRUDUser(User)
student_crud = CRUDStudent(Student)
professor_crud = CRUDProfessor(Professor)
professor_evaluation_crud = CRUDBase(ProfessorEvaluation)
academic_paper_crud = CRUDBase(AcademicPaper)
match_crud = CRUDMatch(Match)
document_template_crud = CRUDBase(DocumentTemplate)
generated_document_crud = CRUDBase(GeneratedDocument)

# 导出
__all__ = [
    "CRUDBase",
    "CRUDUser",
    "CRUDStudent",
    "CRUDProfessor",
    "CRUDMatch",
    "user_crud",
    "student_crud",
    "professor_crud",
    "professor_evaluation_crud",
    "academic_paper_crud",
    "match_crud",
    "document_template_crud",
    "generated_document_crud",
]