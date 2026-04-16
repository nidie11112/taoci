"""
匹配API端点

提供匹配记录的CRUD操作
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.dependencies import get_db, get_current_user, get_pagination_params, get_matching_service
from app.models.match import Match
from app.models.student import Student
from app.models.professor import Professor
from app.models.professor_evaluation import ProfessorEvaluation
from app.models.academic_paper import AcademicPaper
from app.schemas.match import (
    MatchCreate,
    MatchUpdate,
    MatchResponse,
    MatchDetailResponse,
    MatchListResponse,
    MatchSearchParams,
)
from app.services.matching import MatchResult

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/", response_model=MatchListResponse)
async def list_matches(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    pagination: dict = Depends(get_pagination_params),
    student_id: Optional[int] = Query(None, description="按学生ID筛选"),
    professor_id: Optional[int] = Query(None, description="按导师ID筛选"),
    min_score: Optional[float] = Query(None, ge=0, le=1, description="最低综合匹配度"),
    min_probability: Optional[float] = Query(None, ge=0, le=1, description="最低录取概率"),
):
    """获取匹配列表

    Args:
        db: 数据库会话
        current_user: 当前用户
        pagination: 分页参数
        student_id: 学生ID筛选
        professor_id: 导师ID筛选
        min_score: 最低综合匹配度
        min_probability: 最低录取概率

    Returns:
        匹配列表
    """
    # 构建查询
    query = select(Match)

    if student_id:
        query = query.where(Match.student_id == student_id)
    if professor_id:
        query = query.where(Match.professor_id == professor_id)
    if min_score is not None:
        query = query.where(Match.overall_score >= min_score)
    if min_probability is not None:
        query = query.where(Match.admission_probability >= min_probability)

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页和排序
    query = query.order_by(Match.overall_score.desc(), Match.created_at.desc())
    query = query.offset(pagination["offset"]).limit(pagination["limit"])

    # 执行查询
    result = await db.execute(query)
    matches = result.scalars().all()

    return MatchListResponse(
        total=total,
        page=pagination["page"],
        page_size=pagination["limit"],
        matches=matches,
    )


@router.get("/{match_id}", response_model=MatchDetailResponse)
async def get_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取单个匹配信息

    Args:
        match_id: 匹配ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        匹配信息

    Raises:
        HTTPException: 匹配不存在
    """
    query = select(Match).where(Match.id == match_id)
    result = await db.execute(query)
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="匹配不存在"
        )

    # 获取学生和导师信息
    student_query = select(Student).where(Student.id == match.student_id, Student.deleted_at.is_(None))
    student_result = await db.execute(student_query)
    student = student_result.scalar_one_or_none()

    professor_query = select(Professor).where(Professor.id == match.professor_id, Professor.deleted_at.is_(None))
    professor_result = await db.execute(professor_query)
    professor = professor_result.scalar_one_or_none()

    if not student or not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联的学生或导师不存在"
        )

    return MatchDetailResponse(
        id=match.id,
        student_id=match.student_id,
        professor_id=match.professor_id,
        research_match_score=float(match.research_match_score) if match.research_match_score else None,
        background_match_score=float(match.background_match_score) if match.background_match_score else None,
        personality_match_score=float(match.personality_match_score) if match.personality_match_score else None,
        overall_score=float(match.overall_score) if match.overall_score else None,
        admission_probability=float(match.admission_probability) if match.admission_probability else None,
        match_reasons=match.match_reasons,
        created_at=match.created_at,
        student=student.to_dict(),
        professor=professor.to_dict(),
    )


@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(
    match_data: MatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建匹配记录

    Args:
        match_data: 匹配数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        创建的匹配信息

    Raises:
        HTTPException: 学生或导师不存在，或匹配已存在
    """
    # 检查学生是否存在
    student_query = select(Student).where(
        Student.id == match_data.student_id,
        Student.deleted_at.is_(None)
    )
    student_result = await db.execute(student_query)
    student = student_result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    # 检查导师是否存在
    professor_query = select(Professor).where(
        Professor.id == match_data.professor_id,
        Professor.deleted_at.is_(None)
    )
    professor_result = await db.execute(professor_query)
    professor = professor_result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师不存在"
        )

    # 检查是否已存在匹配
    existing_query = select(Match).where(
        Match.student_id == match_data.student_id,
        Match.professor_id == match_data.professor_id
    )
    existing_result = await db.execute(existing_query)
    existing_match = existing_result.scalar_one_or_none()

    if existing_match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该学生与导师的匹配记录已存在"
        )

    # 创建匹配实例
    match = Match.from_dict(match_data.dict())

    # 保存到数据库
    db.add(match)
    await db.commit()
    await db.refresh(match)

    return match


@router.put("/{match_id}", response_model=MatchResponse)
async def update_match(
    match_id: int,
    match_data: MatchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新匹配信息

    Args:
        match_id: 匹配ID
        match_data: 匹配更新数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        更新后的匹配信息

    Raises:
        HTTPException: 匹配不存在
    """
    # 获取现有匹配
    query = select(Match).where(Match.id == match_id)
    result = await db.execute(query)
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="匹配不存在"
        )

    # 更新字段
    update_data = match_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(match, field, value)

    # 保存更改
    await db.commit()
    await db.refresh(match)

    return match


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除匹配记录

    Args:
        match_id: 匹配ID
        db: 数据库会话
        current_user: 当前用户

    Raises:
        HTTPException: 匹配不存在
    """
    # 获取匹配
    query = select(Match).where(Match.id == match_id)
    result = await db.execute(query)
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="匹配不存在"
        )

    # 删除匹配
    await db.delete(match)
    await db.commit()


@router.get("/student/{student_id}/recommendations", response_model=List[Dict[str, Any]])
async def get_student_recommendations(
    student_id: int,
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取学生推荐导师

    Args:
        student_id: 学生ID
        limit: 推荐数量
        db: 数据库会话
        current_user: 当前用户

    Returns:
        推荐导师列表

    Raises:
        HTTPException: 学生不存在
    """
    # 检查学生是否存在
    student_query = select(Student).where(
        Student.id == student_id,
        Student.deleted_at.is_(None)
    )
    student_result = await db.execute(student_query)
    student = student_result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    # TODO: 实现推荐算法
    # 目前返回该学生的现有匹配，按匹配度排序
    match_query = select(Match).where(
        Match.student_id == student_id
    ).order_by(Match.overall_score.desc()).limit(limit)

    match_result = await db.execute(match_query)
    matches = match_result.scalars().all()

    recommendations = []
    for match in matches:
        # 获取导师信息
        professor_query = select(Professor).where(
            Professor.id == match.professor_id,
            Professor.deleted_at.is_(None)
        )
        professor_result = await db.execute(professor_query)
        professor = professor_result.scalar_one_or_none()

        if professor:
            recommendations.append({
                "match": match.to_dict(),
                "professor": professor.to_dict(),
                "recommendation_reason": match.match_reasons or "基于研究方向、背景和性格的综合匹配",
            })

    return recommendations


@router.get("/professor/{professor_id}/recommendations", response_model=List[Dict[str, Any]])
async def get_professor_recommendations(
    professor_id: int,
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取导师推荐学生

    Args:
        professor_id: 导师ID
        limit: 推荐数量
        db: 数据库会话
        current_user: 当前用户

    Returns:
        推荐学生列表

    Raises:
        HTTPException: 导师不存在
    """
    # 检查导师是否存在
    professor_query = select(Professor).where(
        Professor.id == professor_id,
        Professor.deleted_at.is_(None)
    )
    professor_result = await db.execute(professor_query)
    professor = professor_result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师不存在"
        )

    # TODO: 实现推荐算法
    # 目前返回该导师的现有匹配，按匹配度排序
    match_query = select(Match).where(
        Match.professor_id == professor_id
    ).order_by(Match.overall_score.desc()).limit(limit)

    match_result = await db.execute(match_query)
    matches = match_result.scalars().all()

    recommendations = []
    for match in matches:
        # 获取学生信息
        student_query = select(Student).where(
            Student.id == match.student_id,
            Student.deleted_at.is_(None)
        )
        student_result = await db.execute(student_query)
        student = student_result.scalar_one_or_none()

        if student:
            recommendations.append({
                "match": match.to_dict(),
                "student": student.to_dict(),
                "recommendation_reason": match.match_reasons or "基于研究方向、背景和性格的综合匹配",
            })

    return recommendations


@router.post("/calculate", response_model=Dict[str, Any])
async def calculate_match(
    student_id: int,
    professor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    matching_service = Depends(get_matching_service),
):
    """计算学生和导师的匹配度

    Args:
        student_id: 学生ID
        professor_id: 导师ID
        db: 数据库会话
        current_user: 当前用户
        matching_service: 匹配服务

    Returns:
        匹配计算结果

    Raises:
        HTTPException: 学生或导师不存在
    """
    # 检查学生是否存在
    student_query = select(Student).where(
        Student.id == student_id,
        Student.deleted_at.is_(None)
    )
    student_result = await db.execute(student_query)
    student = student_result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    # 检查导师是否存在
    professor_query = select(Professor).where(
        Professor.id == professor_id,
        Professor.deleted_at.is_(None)
    )
    professor_result = await db.execute(professor_query)
    professor = professor_result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师不存在"
        )

    # 获取导师的论文数据
    papers_query = select(AcademicPaper).where(
        AcademicPaper.professor_id == professor_id
    ).order_by(AcademicPaper.publication_year.desc()).limit(20)  # 最近20篇论文
    papers_result = await db.execute(papers_query)
    papers = papers_result.scalars().all()
    professor_papers = [paper.to_dict() for paper in papers]

    # 获取导师的评价数据
    evaluations_query = select(ProfessorEvaluation).where(
        ProfessorEvaluation.professor_id == professor_id
    ).order_by(ProfessorEvaluation.evaluation_date.desc()).limit(50)  # 最近50条评价
    evaluations_result = await db.execute(evaluations_query)
    evaluations = evaluations_result.scalars().all()
    professor_evaluations = [eval_.to_dict() for eval_ in evaluations]

    # 转换为字典格式
    student_dict = student.to_dict()
    professor_dict = professor.to_dict()

    # 使用匹配服务计算匹配度
    match_result: MatchResult = matching_service.match_student_professor(
        student=student_dict,
        professor=professor_dict,
        professor_papers=professor_papers,
        professor_evaluations=professor_evaluations
    )

    # 返回结果
    return {
        "student_id": student_id,
        "professor_id": professor_id,
        "research_match_score": match_result.research_match_score,
        "background_match_score": match_result.background_match_score,
        "personality_match_score": match_result.personality_match_score,
        "overall_score": match_result.overall_score,
        "admission_probability": match_result.admission_probability,
        "match_reasons": match_result.match_reasons,
        "calculation_time": datetime.now().isoformat(),
        "algorithm_version": "v1.0",
        "details": match_result.details,
    }


@router.get("/stats/overall", response_model=Dict[str, Any])
async def get_match_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取匹配统计信息

    Args:
        db: 数据库会话
        current_user: 当前用户

    Returns:
        匹配统计信息
    """
    # 获取匹配总数
    total_query = select(func.count()).select_from(Match)
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # 获取平均匹配度
    avg_score_query = select(func.avg(Match.overall_score))
    avg_score_result = await db.execute(avg_score_query)
    avg_score = avg_score_result.scalar()

    # 获取平均录取概率
    avg_prob_query = select(func.avg(Match.admission_probability))
    avg_prob_result = await db.execute(avg_prob_query)
    avg_probability = avg_prob_result.scalar()

    # 获取高匹配度（>0.8）的数量
    high_match_query = select(func.count()).where(Match.overall_score >= 0.8)
    high_match_result = await db.execute(high_match_query)
    high_matches = high_match_result.scalar()

    # 获取高录取概率（>0.7）的数量
    high_prob_query = select(func.count()).where(Match.admission_probability >= 0.7)
    high_prob_result = await db.execute(high_prob_query)
    high_probability = high_prob_result.scalar()

    return {
        "total_matches": total or 0,
        "avg_overall_score": round(float(avg_score or 0), 3),
        "avg_admission_probability": round(float(avg_probability or 0), 3),
        "high_match_count": high_matches or 0,
        "high_match_percentage": round((high_matches or 0) / (total or 1) * 100, 1),
        "high_probability_count": high_probability or 0,
        "high_probability_percentage": round((high_probability or 0) / (total or 1) * 100, 1),
    }