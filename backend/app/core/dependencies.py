"""
依赖注入模块

定义FastAPI依赖项，用于请求处理
"""

from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db, get_redis
# 尝试导入user_crud，如果不存在则使用模拟版本
try:
    from app.db.crud import user_crud
    USER_CRUD_AVAILABLE = True
except ImportError:
    USER_CRUD_AVAILABLE = False
    print("警告: user_crud 未找到，将使用模拟用户数据")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None),
) -> dict:
    """
    获取当前用户依赖

    从JWT令牌中解析用户信息并验证

    Args:
        db: 数据库会话
        authorization: Authorization请求头

    Returns:
        用户信息字典

    Raises:
        HTTPException: 认证失败
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 提取Bearer令牌
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("认证方案必须是Bearer")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证格式，应为: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 解码令牌
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 从数据库获取用户（可选）
    user_id = payload.get("sub")
    if user_id and USER_CRUD_AVAILABLE:
        try:
            user = await user_crud.get(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在",
                )
            return {"id": user.id, "username": user.username, "email": user.email}
        except Exception as e:
            print(f"用户查询错误: {e}")
            # 降级处理：返回基本用户信息
    elif user_id:
        # user_crud不可用，返回模拟数据
        return {
            "id": user_id,
            "username": payload.get("username", f"user_{user_id}"),
            "email": payload.get("email", f"user_{user_id}@example.com"),
        }

    # 如果令牌中没有用户ID，返回基本用户信息
    return {
        "id": payload.get("user_id"),
        "username": payload.get("username"),
        "email": payload.get("email"),
    }


async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None),
) -> Optional[dict]:
    """
    获取可选用户依赖

    与get_current_user类似，但不强制要求认证

    Args:
        db: 数据库会话
        authorization: Authorization请求头

    Returns:
        用户信息字典或None
    """
    if not authorization:
        return None

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id and USER_CRUD_AVAILABLE:
        try:
            user = await user_crud.get(db, user_id)
            if user:
                return {"id": user.id, "username": user.username, "email": user.email}
        except Exception as e:
            print(f"用户查询错误: {e}")
            # 降级处理
    elif user_id:
        # user_crud不可用，返回模拟数据
        return {
            "id": user_id,
            "username": payload.get("username", f"user_{user_id}"),
            "email": payload.get("email", f"user_{user_id}@example.com"),
        }

    return {
        "id": payload.get("user_id"),
        "username": payload.get("username"),
        "email": payload.get("email"),
    }


async def get_admin_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    获取管理员用户依赖

    要求当前用户必须是管理员

    Args:
        current_user: 当前用户信息

    Returns:
        管理员用户信息

    Raises:
        HTTPException: 非管理员用户
    """
    # 这里简化实现，实际应从数据库检查用户角色
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )

    return current_user


async def get_rate_limiter(
    redis_client: redis.Redis = Depends(get_redis),
    identifier: Optional[str] = Header(None, alias="X-Client-ID"),
    user: Optional[dict] = Depends(get_optional_user),
) -> str:
    """
    获取限流标识符依赖

    用于基于客户端或用户的限流

    Args:
        redis_client: Redis客户端
        identifier: 客户端标识符
        user: 用户信息

    Returns:
        限流标识符
    """
    # 优先使用用户ID
    if user and user.get("id"):
        return f"user:{user['id']}"

    # 其次使用客户端标识符
    if identifier:
        return f"client:{identifier}"

    # 最后使用IP地址（需要在中间件中设置）
    return "ip:unknown"


async def get_pagination_params(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
) -> dict:
    """
    获取分页参数依赖

    Args:
        page: 页码
        page_size: 每页数量

    Returns:
        包含分页参数的字典
    """
    return {
        "page": page,
        "page_size": page_size,
        "offset": (page - 1) * page_size,
        "limit": page_size,
    }


async def get_sorting_params(
    sort_by: Optional[str] = Query(None, description="排序字段"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="排序方向: asc或desc"),
) -> dict:
    """
    获取排序参数依赖

    Args:
        sort_by: 排序字段
        sort_order: 排序方向

    Returns:
        包含排序参数的字典
    """
    return {
        "sort_by": sort_by,
        "sort_order": sort_order,
    }


async def get_filtering_params(
    university: Optional[str] = Query(None, description="大学名称"),
    department: Optional[str] = Query(None, description="院系名称"),
    research_field: Optional[str] = Query(None, description="研究方向"),
    min_score: Optional[float] = Query(None, ge=1, le=5, description="最低人品得分"),
) -> dict:
    """
    获取筛选参数依赖（用于导师搜索）

    Args:
        university: 大学名称
        department: 院系名称
        research_field: 研究方向
        min_score: 最低人品得分

    Returns:
        包含筛选参数的字典
    """
    filters = {}

    if university:
        filters["university"] = university

    if department:
        filters["department"] = department

    if research_field:
        filters["research_field"] = research_field

    if min_score:
        filters["min_personality_score"] = min_score

    return filters


async def verify_captcha(
    captcha_token: str = Query(..., description="验证码令牌"),
    redis_client: redis.Redis = Depends(get_redis),
) -> bool:
    """
    验证验证码依赖

    Args:
        captcha_token: 验证码令牌
        redis_client: Redis客户端

    Returns:
        是否验证成功

    Raises:
        HTTPException: 验证失败
    """
    # 从Redis检查验证码
    captcha_key = f"captcha:{captcha_token}"
    captcha_data = await redis_client.get(captcha_key)

    if not captcha_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效或过期的验证码",
        )

    # 验证后删除验证码（一次性使用）
    await redis_client.delete(captcha_key)

    return True


# 服务依赖
async def get_matching_service():
    """
    获取匹配服务依赖

    延迟导入以避免循环依赖
    """
    from app.services.matching import MatchingService
    return MatchingService()


async def get_document_generation_service():
    """
    获取文书生成服务依赖
    """
    from app.services.document_generation import DocumentGenerationService
    return DocumentGenerationService()


async def get_crawler_service():
    """
    获取爬虫服务依赖
    """
    from app.services.data_collection import CrawlerService
    return CrawlerService()


# 导出
__all__ = [
    "get_current_user",
    "get_optional_user",
    "get_admin_user",
    "get_rate_limiter",
    "get_pagination_params",
    "get_sorting_params",
    "get_filtering_params",
    "verify_captcha",
    "get_matching_service",
    "get_document_generation_service",
    "get_crawler_service",
]