"""
导师API端点

提供导师信息的CRUD操作
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.dependencies import get_db, get_current_user, get_pagination_params
from app.models.professor import Professor
from app.models.professor_evaluation import ProfessorEvaluation
from app.schemas.professor import (
    ProfessorCreate,
    ProfessorUpdate,
    ProfessorResponse,
    ProfessorListResponse,
    ProfessorSearchParams,
)

router = APIRouter(prefix="/professors", tags=["professors"])


@router.get("/", response_model=ProfessorListResponse)
async def list_professors(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    pagination: dict = Depends(get_pagination_params),
    university: Optional[str] = Query(None, description="按学校筛选"),
    department: Optional[str] = Query(None, description="按院系筛选"),
    title: Optional[str] = Query(None, description="按职称筛选"),
    research_field: Optional[str] = Query(None, description="按研究方向筛选"),
):
    """获取导师列表

    Args:
        db: 数据库会话
        current_user: 当前用户
        pagination: 分页参数
        university: 学校筛选
        department: 院系筛选
        title: 职称筛选
        research_field: 研究方向筛选

    Returns:
        导师列表
    """
    # 构建查询
    query = select(Professor).where(Professor.deleted_at.is_(None))

    if university:
        query = query.where(Professor.university.ilike(f"%{university}%"))
    if department:
        query = query.where(Professor.department.ilike(f"%{department}%"))
    if title:
        query = query.where(Professor.title.ilike(f"%{title}%"))
    if research_field:
        # 使用PostgreSQL的数组包含操作符
        query = query.where(Professor.research_fields.contains([research_field]))

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    query = query.order_by(Professor.created_at.desc())
    query = query.offset(pagination["offset"]).limit(pagination["limit"])

    # 执行查询
    result = await db.execute(query)
    professors = result.scalars().all()

    return ProfessorListResponse(
        total=total,
        page=pagination["page"],
        page_size=pagination["limit"],
        professors=professors,
    )


@router.get("/{professor_id}", response_model=ProfessorResponse)
async def get_professor(
    professor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取单个导师信息

    Args:
        professor_id: 导师ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        导师信息

    Raises:
        HTTPException: 导师不存在
    """
    query = select(Professor).where(
        Professor.id == professor_id,
        Professor.deleted_at.is_(None)
    )
    result = await db.execute(query)
    professor = result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师不存在"
        )

    return professor


@router.post("/", response_model=ProfessorResponse, status_code=status.HTTP_201_CREATED)
async def create_professor(
    professor_data: ProfessorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建导师

    Args:
        professor_data: 导师数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        创建的导师信息
    """
    # 检查邮箱是否已存在
    if professor_data.email:
        existing_query = select(Professor).where(
            Professor.email == professor_data.email,
            Professor.deleted_at.is_(None)
        )
        existing_result = await db.execute(existing_query)
        existing_professor = existing_result.scalar_one_or_none()
        if existing_professor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )

    # 创建导师实例
    professor = Professor.from_dict(professor_data.dict())

    # 保存到数据库
    db.add(professor)
    await db.commit()
    await db.refresh(professor)

    return professor


@router.put("/{professor_id}", response_model=ProfessorResponse)
async def update_professor(
    professor_id: int,
    professor_data: ProfessorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新导师信息

    Args:
        professor_id: 导师ID
        professor_data: 导师更新数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        更新后的导师信息

    Raises:
        HTTPException: 导师不存在
    """
    # 获取现有导师
    query = select(Professor).where(
        Professor.id == professor_id,
        Professor.deleted_at.is_(None)
    )
    result = await db.execute(query)
    professor = result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师不存在"
        )

    # 检查邮箱是否已存在（如果提供了新邮箱）
    if professor_data.email and professor_data.email != professor.email:
        existing_query = select(Professor).where(
            Professor.email == professor_data.email,
            Professor.deleted_at.is_(None),
            Professor.id != professor_id
        )
        existing_result = await db.execute(existing_query)
        existing_professor = existing_result.scalar_one_or_none()
        if existing_professor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被其他导师使用"
            )

    # 更新字段
    update_data = professor_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(professor, field, value)

    # 保存更改
    await db.commit()
    await db.refresh(professor)

    return professor


@router.delete("/{professor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_professor(
    professor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除导师（软删除）

    Args:
        professor_id: 导师ID
        db: 数据库会话
        current_user: 当前用户

    Raises:
        HTTPException: 导师不存在
    """
    # 获取导师
    query = select(Professor).where(
        Professor.id == professor_id,
        Professor.deleted_at.is_(None)
    )
    result = await db.execute(query)
    professor = result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师不存在"
        )

    # 软删除：设置删除时间
    professor.deleted_at = db.func.now()
    await db.commit()


@router.get("/{professor_id}/evaluations", response_model=List[Dict[str, Any]])
async def get_professor_evaluations(
    professor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取导师评价

    Args:
        professor_id: 导师ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        评价列表

    Raises:
        HTTPException: 导师不存在
    """
    # 获取导师
    query = select(Professor).where(
        Professor.id == professor_id,
        Professor.deleted_at.is_(None)
    )
    result = await db.execute(query)
    professor = result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师不存在"
        )

    # 获取评价
    eval_query = select(ProfessorEvaluation).where(
        ProfessorEvaluation.professor_id == professor_id
    ).order_by(ProfessorEvaluation.evaluation_date.desc())
    eval_result = await db.execute(eval_query)
    evaluations = eval_result.scalars().all()

    # 转换为字典
    evaluations_list = []
    for eval in evaluations:
        eval_dict = eval.to_dict()
        evaluations_list.append(eval_dict)

    return evaluations_list


@router.get("/{professor_id}/papers", response_model=List[Dict[str, Any]])
async def get_professor_papers(
    professor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取导师论文

    Args:
        professor_id: 导师ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        论文列表

    Raises:
        HTTPException: 导师不存在
    """
    # 获取导师
    query = select(Professor).where(
        Professor.id == professor_id,
        Professor.deleted_at.is_(None)
    )
    result = await db.execute(query)
    professor = result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师不存在"
        )

    # 获取论文
    papers_list = []
    for paper in professor.papers:
        paper_dict = paper.to_dict()
        papers_list.append(paper_dict)

    return papers_list


@router.get("/search/suggest", response_model=List[Dict[str, Any]])
async def search_suggest(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """搜索建议

    Args:
        q: 搜索关键词
        db: 数据库会话
        current_user: 当前用户

    Returns:
        搜索建议列表
    """
    # 构建搜索查询
    query = select(Professor).where(
        Professor.deleted_at.is_(None),
        or_(
            Professor.name.ilike(f"%{q}%"),
            Professor.university.ilike(f"%{q}%"),
            Professor.department.ilike(f"%{q}%"),
            Professor.title.ilike(f"%{q}%"),
        )
    ).limit(10)

    result = await db.execute(query)
    professors = result.scalars().all()

    # 构建建议列表
    suggestions = []
    for professor in professors:
        suggestions.append({
            "id": professor.id,
            "name": professor.name,
            "university": professor.university,
            "department": professor.department,
            "title": professor.title,
            "research_fields": professor.research_fields or [],
        })

    return suggestions


@router.post("/{professor_id}/add-evaluation", response_model=Dict[str, Any])
async def add_professor_evaluation(
    professor_id: int,
    evaluation_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """添加导师评价

    Args:
        professor_id: 导师ID
        evaluation_data: 评价数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        添加结果

    Raises:
        HTTPException: 导师不存在
    """
    # 获取导师
    query = select(Professor).where(
        Professor.id == professor_id,
        Professor.deleted_at.is_(None)
    )
    result = await db.execute(query)
    professor = result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师不存在"
        )

    # 创建评价
    evaluation = ProfessorEvaluation(
        professor_id=professor_id,
        source=evaluation_data.get("source", "manual"),
        personality_score=evaluation_data.get("personality_score"),
        group_atmosphere=evaluation_data.get("group_atmosphere"),
        student_comments=evaluation_data.get("student_comments"),
        evaluation_date=evaluation_data.get("evaluation_date"),
    )

    # 保存评价
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)

    return {
        "message": "评价添加成功",
        "evaluation_id": evaluation.id,
        "professor_id": professor_id,
    }


@router.get("/{professor_id}/stats", response_model=Dict[str, Any])
async def get_professor_stats(
    professor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取导师统计信息

    Args:
        professor_id: 导师ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        统计信息

    Raises:
        HTTPException: 导师不存在
    """
    # 获取导师
    query = select(Professor).where(
        Professor.id == professor_id,
        Professor.deleted_at.is_(None)
    )
    result = await db.execute(query)
    professor = result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师不存在"
        )

    # 获取评价统计
    eval_query = select(
        func.count().label("total_evaluations"),
        func.avg(ProfessorEvaluation.personality_score).label("avg_personality_score")
    ).where(ProfessorEvaluation.professor_id == professor_id)

    eval_result = await db.execute(eval_query)
    eval_stats = eval_result.first()

    # 获取论文统计
    paper_count = len(professor.papers)

    # 获取匹配统计
    match_count = len(professor.matches)

    return {
        "professor_id": professor_id,
        "total_evaluations": eval_stats.total_evaluations or 0,
        "avg_personality_score": round(float(eval_stats.avg_personality_score or 0), 2),
        "paper_count": paper_count,
        "match_count": match_count,
        "profile_completeness": professor.has_complete_profile(),
    }