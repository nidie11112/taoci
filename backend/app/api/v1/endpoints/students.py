"""
学生API端点

提供学生信息的CRUD操作
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.dependencies import get_db, get_current_user, get_pagination_params
from app.models.student import Student

# 临时模式定义（TODO: 移动到schemas模块）
class StudentCreate(BaseModel):
    """学生创建模式"""
    name: str
    university: str
    major: Optional[str] = None
    gpa: Optional[float] = None
    gpa_ranking: Optional[int] = None
    skills: Optional[List[str]] = []
    research_experience: Optional[List[Dict[str, Any]]] = []
    competition_awards: Optional[List[Dict[str, Any]]] = []
    resume_pdf_path: Optional[str] = None

class StudentUpdate(BaseModel):
    """学生更新模式"""
    name: Optional[str] = None
    university: Optional[str] = None
    major: Optional[str] = None
    gpa: Optional[float] = None
    gpa_ranking: Optional[int] = None
    skills: Optional[List[str]] = None
    research_experience: Optional[List[Dict[str, Any]]] = None
    competition_awards: Optional[List[Dict[str, Any]]] = None
    resume_pdf_path: Optional[str] = None

class StudentResponse(BaseModel):
    """学生响应模式"""
    id: int
    uuid: str
    name: str
    university: str
    major: Optional[str]
    gpa: Optional[float]
    gpa_ranking: Optional[int]
    skills: List[str]
    research_experience: List[Dict[str, Any]]
    competition_awards: List[Dict[str, Any]]
    resume_pdf_path: Optional[str]
    created_at: str
    updated_at: str
    deleted_at: Optional[str]

    class Config:
        from_attributes = True

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=List[StudentResponse])
async def list_students(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    pagination: dict = Depends(get_pagination_params),
    university: Optional[str] = Query(None, description="按学校筛选"),
    major: Optional[str] = Query(None, description="按专业筛选"),
):
    """获取学生列表

    Args:
        db: 数据库会话
        current_user: 当前用户
        pagination: 分页参数
        university: 学校筛选
        major: 专业筛选

    Returns:
        学生列表
    """
    # 构建查询
    query = select(Student).where(Student.deleted_at.is_(None))

    if university:
        query = query.where(Student.university.ilike(f"%{university}%"))
    if major:
        query = query.where(Student.major.ilike(f"%{major}%"))

    # 分页
    query = query.offset(pagination["offset"]).limit(pagination["limit"])

    # 执行查询
    result = await db.execute(query)
    students = result.scalars().all()

    return students


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取单个学生信息

    Args:
        student_id: 学生ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        学生信息

    Raises:
        HTTPException: 学生不存在
    """
    query = select(Student).where(
        Student.id == student_id,
        Student.deleted_at.is_(None)
    )
    result = await db.execute(query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    return student


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建学生

    Args:
        student_data: 学生数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        创建的学生信息
    """
    # 创建学生实例
    student = Student.from_dict(student_data.dict())

    # 保存到数据库
    db.add(student)
    await db.commit()
    await db.refresh(student)

    return student


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新学生信息

    Args:
        student_id: 学生ID
        student_data: 学生更新数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        更新后的学生信息

    Raises:
        HTTPException: 学生不存在
    """
    # 获取现有学生
    query = select(Student).where(
        Student.id == student_id,
        Student.deleted_at.is_(None)
    )
    result = await db.execute(query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    # 更新字段
    update_data = student_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)

    # 保存更改
    await db.commit()
    await db.refresh(student)

    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除学生（软删除）

    Args:
        student_id: 学生ID
        db: 数据库会话
        current_user: 当前用户

    Raises:
        HTTPException: 学生不存在
    """
    # 获取学生
    query = select(Student).where(
        Student.id == student_id,
        Student.deleted_at.is_(None)
    )
    result = await db.execute(query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    # 软删除：设置删除时间
    student.deleted_at = db.func.now()
    await db.commit()


@router.get("/{student_id}/matches", response_model=List[dict])
async def get_student_matches(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取学生的匹配记录

    Args:
        student_id: 学生ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        匹配记录列表

    Raises:
        HTTPException: 学生不存在
    """
    # 获取学生
    query = select(Student).where(
        Student.id == student_id,
        Student.deleted_at.is_(None)
    )
    result = await db.execute(query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    # 返回匹配记录
    matches = []
    for match in student.matches:
        match_dict = match.to_dict(include_details=True)
        matches.append(match_dict)

    return matches


@router.post("/{student_id}/upload-resume", response_model=dict)
async def upload_student_resume(
    student_id: int,
    resume_path: str = Query(..., description="简历文件路径"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """上传学生简历

    Args:
        student_id: 学生ID
        resume_path: 简历文件路径
        db: 数据库会话
        current_user: 当前用户

    Returns:
        上传结果

    Raises:
        HTTPException: 学生不存在
    """
    # 获取学生
    query = select(Student).where(
        Student.id == student_id,
        Student.deleted_at.is_(None)
    )
    result = await db.execute(query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    # 更新简历路径
    student.resume_pdf_path = resume_path
    await db.commit()

    return {
        "message": "简历上传成功",
        "student_id": student_id,
        "resume_path": resume_path
    }