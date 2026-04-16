"""
API v1 路由定义

包含所有v1版本的API端点
"""

from fastapi import APIRouter

from app.api.v1.endpoints import students, professors, matches, documents

# 创建主路由器
api_router = APIRouter()

# 包含所有端点路由器
api_router.include_router(students.router)
api_router.include_router(professors.router)
api_router.include_router(matches.router)
api_router.include_router(documents.router)

# 导出路由器
__all__ = ["api_router"]