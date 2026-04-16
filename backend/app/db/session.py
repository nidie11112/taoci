"""
数据库会话管理模块

提供数据库和Redis会话管理
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.core.config import settings
from app.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖

    Yields:
        AsyncSession: 数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Redis连接池
_redis_pool: redis.ConnectionPool = None


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """
    获取Redis客户端依赖

    Yields:
        redis.Redis: Redis客户端
    """
    global _redis_pool

    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool.from_url(
            str(settings.REDIS_URL),
            max_connections=settings.REDIS_POOL_SIZE,
            decode_responses=True,
        )

    client = redis.Redis(connection_pool=_redis_pool)
    try:
        yield client
    finally:
        await client.aclose()


async def init_redis() -> redis.Redis:
    """
    初始化Redis连接池（应用启动时调用）

    Returns:
        redis.Redis: Redis客户端
    """
    global _redis_pool

    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool.from_url(
            str(settings.REDIS_URL),
            max_connections=settings.REDIS_POOL_SIZE,
            decode_responses=True,
        )

    return redis.Redis(connection_pool=_redis_pool)


async def close_redis() -> None:
    """
    关闭Redis连接池（应用关闭时调用）
    """
    global _redis_pool

    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None


async def check_redis_health() -> dict:
    """
    检查Redis连接健康状况

    Returns:
        dict: 包含健康状态和详细信息
    """
    from datetime import datetime

    try:
        client = redis.Redis.from_pool(_redis_pool) if _redis_pool else await init_redis()

        # 测试连接
        pong = await client.ping()

        # 获取Redis信息
        info = await client.info()

        return {
            "status": "healthy" if pong else "unhealthy",
            "redis_version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory_human": info.get("used_memory_human"),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


# 导出
__all__ = [
    "get_db",
    "get_redis",
    "init_redis",
    "close_redis",
    "check_redis_health",
]