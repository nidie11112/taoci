"""
文书API端点

提供文书模板和生成文书的CRUD操作
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.dependencies import get_db, get_current_user, get_pagination_params, get_document_generation_service
from app.models.document_template import DocumentTemplate
from app.models.generated_document import GeneratedDocument
from app.models.student import Student
from app.models.professor import Professor
from app.models.match import Match
from app.schemas.document import (
    DocumentTemplateCreate,
    DocumentTemplateUpdate,
    DocumentTemplateResponse,
    DocumentTemplateListResponse,
    GeneratedDocumentCreate,
    GeneratedDocumentUpdate,
    GeneratedDocumentResponse,
    GeneratedDocumentDetailResponse,
    GeneratedDocumentListResponse,
    DocumentGenerationRequest,
    DocumentGenerationResponse,
)

router = APIRouter(prefix="/documents", tags=["documents"])


# ==================== 文书模板相关端点 ====================

@router.get("/templates", response_model=DocumentTemplateListResponse)
async def list_document_templates(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    pagination: dict = Depends(get_pagination_params),
    category: Optional[str] = Query(None, description="按分类筛选"),
    search: Optional[str] = Query(None, description="搜索模板名称"),
):
    """获取文书模板列表

    Args:
        db: 数据库会话
        current_user: 当前用户
        pagination: 分页参数
        category: 按分类筛选
        search: 搜索模板名称

    Returns:
        模板列表
    """
    # 构建查询
    query = select(DocumentTemplate).where(DocumentTemplate.deleted_at.is_(None))

    if category:
        query = query.where(DocumentTemplate.category == category)
    if search:
        query = query.where(DocumentTemplate.name.ilike(f"%{search}%"))

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页和排序
    query = query.order_by(DocumentTemplate.created_at.desc())
    query = query.offset(pagination["offset"]).limit(pagination["limit"])

    # 执行查询
    result = await db.execute(query)
    templates = result.scalars().all()

    return DocumentTemplateListResponse(
        total=total,
        page=pagination["page"],
        page_size=pagination["limit"],
        templates=templates,
    )


@router.get("/templates/{template_id}", response_model=DocumentTemplateResponse)
async def get_document_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取单个文书模板

    Args:
        template_id: 模板ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        模板信息

    Raises:
        HTTPException: 模板不存在
    """
    query = select(DocumentTemplate).where(
        DocumentTemplate.id == template_id,
        DocumentTemplate.deleted_at.is_(None)
    )
    result = await db.execute(query)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文书模板不存在"
        )

    return template


@router.post("/templates", response_model=DocumentTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_document_template(
    template_data: DocumentTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建文书模板

    Args:
        template_data: 模板数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        创建的模板信息

    Raises:
        HTTPException: 模板名称已存在
    """
    # 检查模板名称是否已存在
    existing_query = select(DocumentTemplate).where(
        DocumentTemplate.name == template_data.name,
        DocumentTemplate.deleted_at.is_(None)
    )
    existing_result = await db.execute(existing_query)
    existing_template = existing_result.scalar_one_or_none()

    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该模板名称已存在"
        )

    # 创建模板实例
    template = DocumentTemplate.from_dict(template_data.dict())

    # 保存到数据库
    db.add(template)
    await db.commit()
    await db.refresh(template)

    return template


@router.put("/templates/{template_id}", response_model=DocumentTemplateResponse)
async def update_document_template(
    template_id: int,
    template_data: DocumentTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新文书模板

    Args:
        template_id: 模板ID
        template_data: 模板更新数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        更新后的模板信息

    Raises:
        HTTPException: 模板不存在
    """
    # 获取现有模板
    query = select(DocumentTemplate).where(
        DocumentTemplate.id == template_id,
        DocumentTemplate.deleted_at.is_(None)
    )
    result = await db.execute(query)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文书模板不存在"
        )

    # 如果更新名称，检查名称是否已被其他模板使用
    if template_data.name and template_data.name != template.name:
        existing_query = select(DocumentTemplate).where(
            DocumentTemplate.name == template_data.name,
            DocumentTemplate.deleted_at.is_(None),
            DocumentTemplate.id != template_id
        )
        existing_result = await db.execute(existing_query)
        existing_template = existing_result.scalar_one_or_none()

        if existing_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该模板名称已被其他模板使用"
            )

    # 更新字段
    update_data = template_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    # 保存更改
    await db.commit()
    await db.refresh(template)

    return template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除文书模板（软删除）

    Args:
        template_id: 模板ID
        db: 数据库会话
        current_user: 当前用户

    Raises:
        HTTPException: 模板不存在
    """
    # 获取模板
    query = select(DocumentTemplate).where(
        DocumentTemplate.id == template_id,
        DocumentTemplate.deleted_at.is_(None)
    )
    result = await db.execute(query)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文书模板不存在"
        )

    # 软删除：设置删除时间
    template.deleted_at = db.func.now()
    await db.commit()


# ==================== 生成文书相关端点 ====================

@router.get("/generated", response_model=GeneratedDocumentListResponse)
async def list_generated_documents(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    pagination: dict = Depends(get_pagination_params),
    student_id: Optional[int] = Query(None, description="按学生ID筛选"),
    professor_id: Optional[int] = Query(None, description="按导师ID筛选"),
    document_type: Optional[str] = Query(None, description="按文书类型筛选"),
):
    """获取生成文书列表

    Args:
        db: 数据库会话
        current_user: 当前用户
        pagination: 分页参数
        student_id: 学生ID筛选
        professor_id: 导师ID筛选
        document_type: 文书类型筛选

    Returns:
        文书列表
    """
    # 构建查询
    query = select(GeneratedDocument)

    if student_id:
        query = query.where(GeneratedDocument.student_id == student_id)
    if professor_id:
        query = query.where(GeneratedDocument.professor_id == professor_id)
    if document_type:
        query = query.where(GeneratedDocument.document_type == document_type)

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页和排序
    query = query.order_by(GeneratedDocument.generated_at.desc())
    query = query.offset(pagination["offset"]).limit(pagination["limit"])

    # 执行查询
    result = await db.execute(query)
    documents = result.scalars().all()

    return GeneratedDocumentListResponse(
        total=total,
        page=pagination["page"],
        page_size=pagination["limit"],
        documents=documents,
    )


@router.get("/generated/{document_id}", response_model=GeneratedDocumentDetailResponse)
async def get_generated_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取单个生成文书

    Args:
        document_id: 文书ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        文书信息

    Raises:
        HTTPException: 文书不存在
    """
    query = select(GeneratedDocument).where(GeneratedDocument.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生成文书不存在"
        )

    # 获取学生信息
    student_query = select(Student).where(
        Student.id == document.student_id,
        Student.deleted_at.is_(None)
    )
    student_result = await db.execute(student_query)
    student = student_result.scalar_one_or_none()

    # 获取导师信息（如果有关联）
    professor = None
    if document.professor_id:
        professor_query = select(Professor).where(
            Professor.id == document.professor_id,
            Professor.deleted_at.is_(None)
        )
        professor_result = await db.execute(professor_query)
        professor = professor_result.scalar_one_or_none()

    # 获取模板信息（如果有关联）
    template = None
    if document.template_id:
        template_query = select(DocumentTemplate).where(
            DocumentTemplate.id == document.template_id,
            DocumentTemplate.deleted_at.is_(None)
        )
        template_result = await db.execute(template_query)
        template = template_result.scalar_one_or_none()

    return GeneratedDocumentDetailResponse(
        id=document.id,
        student_id=document.student_id,
        professor_id=document.professor_id,
        template_id=document.template_id,
        document_type=document.document_type,
        content=document.content,
        file_path=document.file_path,
        generated_at=document.generated_at,
        student=student.to_dict() if student else None,
        professor=professor.to_dict() if professor else None,
        template=template.to_dict() if template else None,
    )


@router.post("/generated", response_model=GeneratedDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_generated_document(
    document_data: GeneratedDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建生成文书

    Args:
        document_data: 文书数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        创建的文书信息

    Raises:
        HTTPException: 学生不存在
    """
    # 检查学生是否存在
    student_query = select(Student).where(
        Student.id == document_data.student_id,
        Student.deleted_at.is_(None)
    )
    student_result = await db.execute(student_query)
    student = student_result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    # 检查导师是否存在（如果提供了导师ID）
    if document_data.professor_id:
        professor_query = select(Professor).where(
            Professor.id == document_data.professor_id,
            Professor.deleted_at.is_(None)
        )
        professor_result = await db.execute(professor_query)
        professor = professor_result.scalar_one_or_none()

        if not professor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="导师不存在"
            )

    # 检查模板是否存在（如果提供了模板ID）
    if document_data.template_id:
        template_query = select(DocumentTemplate).where(
            DocumentTemplate.id == document_data.template_id,
            DocumentTemplate.deleted_at.is_(None)
        )
        template_result = await db.execute(template_query)
        template = template_result.scalar_one_or_none()

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文书模板不存在"
            )

    # 创建文书实例
    document = GeneratedDocument.from_dict(document_data.dict())

    # 保存到数据库
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document


@router.put("/generated/{document_id}", response_model=GeneratedDocumentResponse)
async def update_generated_document(
    document_id: int,
    document_data: GeneratedDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新生成文书

    Args:
        document_id: 文书ID
        document_data: 文书更新数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        更新后的文书信息

    Raises:
        HTTPException: 文书不存在
    """
    # 获取现有文书
    query = select(GeneratedDocument).where(GeneratedDocument.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生成文书不存在"
        )

    # 更新字段
    update_data = document_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)

    # 保存更改
    await db.commit()
    await db.refresh(document)

    return document


@router.delete("/generated/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_generated_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除生成文书

    Args:
        document_id: 文书ID
        db: 数据库会话
        current_user: 当前用户

    Raises:
        HTTPException: 文书不存在
    """
    # 获取文书
    query = select(GeneratedDocument).where(GeneratedDocument.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生成文书不存在"
        )

    # 删除文书
    await db.delete(document)
    await db.commit()


# ==================== 文书生成相关端点 ====================

@router.post("/generate", response_model=DocumentGenerationResponse)
async def generate_document(
    generation_request: DocumentGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    document_generation_service = Depends(get_document_generation_service),
):
    """生成文书

    Args:
        generation_request: 生成请求
        background_tasks: 后台任务
        db: 数据库会话
        current_user: 当前用户
        document_generation_service: 文书生成服务

    Returns:
        生成结果
    """
    # 检查学生是否存在
    student_query = select(Student).where(
        Student.id == generation_request.student_id,
        Student.deleted_at.is_(None)
    )
    student_result = await db.execute(student_query)
    student = student_result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )

    # 检查导师是否存在（如果提供了导师ID）
    professor = None
    if generation_request.professor_id:
        professor_query = select(Professor).where(
            Professor.id == generation_request.professor_id,
            Professor.deleted_at.is_(None)
        )
        professor_result = await db.execute(professor_query)
        professor = professor_result.scalar_one_or_none()

        if not professor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="导师不存在"
            )

    # 转换为字典格式
    student_dict = student.to_dict()
    professor_dict = professor.to_dict() if professor else {}

    # 获取匹配信息（如果提供了学生和导师）
    match_info = None
    if generation_request.student_id and generation_request.professor_id:
        match_query = select(Match).where(
            Match.student_id == generation_request.student_id,
            Match.professor_id == generation_request.professor_id
        ).order_by(Match.created_at.desc()).limit(1)
        match_result = await db.execute(match_query)
        match = match_result.scalar_one_or_none()
        if match:
            match_info = {
                "research_match_score": float(match.research_match_score) if match.research_match_score else None,
                "background_match_score": float(match.background_match_score) if match.background_match_score else None,
                "overall_score": float(match.overall_score) if match.overall_score else None,
                "admission_probability": float(match.admission_probability) if match.admission_probability else None,
                "match_reasons": match.match_reasons,
            }

    # 根据文档类型调用相应的生成方法
    document_type = generation_request.document_type
    try:
        if document_type == "套磁信":
            result = document_generation_service.generate_cover_letter(
                student=student_dict,
                professor=professor_dict,
                match_info=match_info,
                template_id=generation_request.template_id,
                custom_variables=generation_request.custom_variables
            )
        elif document_type == "个人陈述":
            result = document_generation_service.generate_personal_statement(
                student=student_dict,
                target_university=professor_dict.get("university") if professor_dict else None,
                target_major=student_dict.get("major"),
                template_id=generation_request.template_id,
                custom_variables=generation_request.custom_variables
            )
        elif document_type == "推荐信":
            # 获取推荐人信息
            recommender = generation_request.custom_variables.get("recommender", {})
            if not recommender and professor_dict:
                # 如果没有提供推荐人，使用教授作为默认推荐人
                recommender = {
                    "name": professor_dict.get("name", "推荐人"),
                    "title": professor_dict.get("title", "教授"),
                    "university": professor_dict.get("university", "所在大学"),
                    "department": professor_dict.get("department", "相关院系"),
                    "relationship": "导师"
                }
            elif not recommender:
                # 创建默认推荐人
                recommender = {
                    "name": "推荐人",
                    "title": "教授",
                    "university": student_dict.get("university", "所在大学"),
                    "department": student_dict.get("major", "相关专业") + "系",
                    "relationship": "导师"
                }

            result = document_generation_service.generate_recommendation_letter(
                student=student_dict,
                recommender=recommender,
                relationship=recommender.get("relationship", "导师"),
                template_id=generation_request.template_id,
                custom_variables=generation_request.custom_variables
            )
        else:
            return DocumentGenerationResponse(
                success=False,
                error_message=f"不支持的文书类型: {document_type}",
                warnings=[]
            )
    except Exception as e:
        return DocumentGenerationResponse(
            success=False,
            error_message=f"文书生成失败: {str(e)}",
            warnings=[]
        )

    # 创建文书记录
    document = GeneratedDocument(
        student_id=generation_request.student_id,
        professor_id=generation_request.professor_id,
        template_id=None,  # TODO: 从结果中获取模板ID
        document_type=generation_request.document_type,
        content=result.get("content", ""),
        file_path=result.get("file_path"),
        generated_at=datetime.now()
    )

    # 保存到数据库
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # 后台任务：保存为文件（如果服务尚未保存）
    if result.get("file_path") and not Path(result["file_path"]).exists():
        # 这里可以添加后台任务来保存文件
        pass

    return DocumentGenerationResponse(
        success=result.get("success", True),
        document_id=document.id,
        document_content=result.get("content", ""),
        error_message=result.get("error_message"),
        warnings=result.get("warnings", []),
        file_path=result.get("file_path"),
        template_used=result.get("template_used", "默认模板"),
    )


@router.get("/student/{student_id}/generated", response_model=List[GeneratedDocumentResponse])
async def get_student_documents(
    student_id: int,
    document_type: Optional[str] = Query(None, description="按文书类型筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取学生的生成文书

    Args:
        student_id: 学生ID
        document_type: 文书类型筛选
        limit: 返回数量
        db: 数据库会话
        current_user: 当前用户

    Returns:
        文书列表

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

    # 构建查询
    query = select(GeneratedDocument).where(
        GeneratedDocument.student_id == student_id
    )

    if document_type:
        query = query.where(GeneratedDocument.document_type == document_type)

    # 排序和限制
    query = query.order_by(GeneratedDocument.generated_at.desc()).limit(limit)

    result = await db.execute(query)
    documents = result.scalars().all()

    return documents


@router.get("/professor/{professor_id}/generated", response_model=List[GeneratedDocumentResponse])
async def get_professor_documents(
    professor_id: int,
    document_type: Optional[str] = Query(None, description="按文书类型筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取导师相关的生成文书

    Args:
        professor_id: 导师ID
        document_type: 文书类型筛选
        limit: 返回数量
        db: 数据库会话
        current_user: 当前用户

    Returns:
        文书列表

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

    # 构建查询
    query = select(GeneratedDocument).where(
        GeneratedDocument.professor_id == professor_id
    )

    if document_type:
        query = query.where(GeneratedDocument.document_type == document_type)

    # 排序和限制
    query = query.order_by(GeneratedDocument.generated_at.desc()).limit(limit)

    result = await db.execute(query)
    documents = result.scalars().all()

    return documents


@router.get("/stats", response_model=Dict[str, Any])
async def get_document_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取文书统计信息

    Args:
        db: 数据库会话
        current_user: 当前用户

    Returns:
        统计信息
    """
    # 获取模板总数
    template_query = select(func.count()).where(DocumentTemplate.deleted_at.is_(None))
    template_result = await db.execute(template_query)
    template_count = template_result.scalar()

    # 获取生成文书总数
    document_query = select(func.count()).select_from(GeneratedDocument)
    document_result = await db.execute(document_query)
    document_count = document_result.scalar()

    # 按类型统计文书
    type_query = select(
        GeneratedDocument.document_type,
        func.count().label("count")
    ).group_by(GeneratedDocument.document_type)

    type_result = await db.execute(type_query)
    type_stats = {row.document_type: row.count for row in type_result.all()}

    return {
        "total_templates": template_count or 0,
        "total_documents": document_count or 0,
        "documents_by_type": type_stats,
        "avg_documents_per_day": round((document_count or 0) / 30, 2) if document_count else 0,  # 假设30天
    }