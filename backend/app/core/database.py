"""
数据库配置模块

数据库连接池、会话管理、异步ORM配置
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from app.core.config import settings

# SQLAlchemy基类
Base = declarative_base()

# 创建异步引擎
# 根据环境选择不同的连接池策略
if settings.is_testing:
    # 测试环境使用NullPool，每个测试独立连接
    engine = create_async_engine(
        str(settings.DATABASE_URL),
        echo=settings.DATABASE_ECHO,
        poolclass=NullPool,
        future=True,
    )
else:
    # 开发和生产环境使用连接池
    engine = create_async_engine(
        str(settings.DATABASE_URL),
        echo=settings.DATABASE_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,  # 连接前ping，检测连接是否有效
        pool_recycle=3600,  # 连接回收时间（秒）
        future=True,
    )

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不使实例过期
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖

    在请求处理期间提供数据库会话，请求完成后自动关闭

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


async def init_db() -> None:
    """
    初始化数据库

    创建所有表（仅用于开发环境）
    生产环境应使用Alembic迁移
    """
    import logging
    logger = logging.getLogger(__name__)

    if settings.is_production:
        logger.warning("生产环境不应使用init_db创建表，请使用Alembic迁移")
        return

    try:
        async with engine.begin() as conn:
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建完成")
    except Exception as e:
        logger.error(f"数据库表创建失败: {e}")
        raise


async def close_db() -> None:
    """
    关闭数据库连接池

    应用关闭时调用
    """
    import logging
    logger = logging.getLogger(__name__)

    if engine:
        await engine.dispose()
        logger.info("数据库连接池已关闭")


# 数据库健康检查
async def check_db_health() -> dict:
    """
    检查数据库连接健康状况

    Returns:
        dict: 包含健康状态和详细信息
    """
    import logging
    from sqlalchemy import text
    from datetime import datetime

    logger = logging.getLogger(__name__)

    try:
        async with AsyncSessionLocal() as session:
            # 执行简单查询测试连接
            result = await session.execute(text("SELECT 1"))
            test_value = result.scalar()

            # 获取连接池信息
            pool = engine.pool
            pool_status = {
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "size": pool.size(),
                "checked_in": pool.checkedin(),
            }

            return {
                "status": "healthy" if test_value == 1 else "unhealthy",
                "database": settings.DATABASE_URL.host,
                "test_query": "success" if test_value == 1 else "failed",
                "pool_status": pool_status,
                "timestamp": datetime.utcnow().isoformat(),
            }
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


# 数据库工具函数
async def execute_in_transaction(session: AsyncSession, operation, *args, **kwargs):
    """
    在事务中执行操作

    提供事务管理，自动提交或回滚

    Args:
        session: 数据库会话
        operation: 要执行的操作（函数）
        *args: 操作参数
        **kwargs: 操作关键字参数

    Returns:
        操作结果

    Raises:
        Exception: 操作失败时抛出异常
    """
    try:
        result = await operation(session, *args, **kwargs)
        await session.commit()
        return result
    except Exception:
        await session.rollback()
        raise


# 导出
__all__ = [
    "Base",
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "init_db",
    "close_db",
    "check_db_health",
    "execute_in_transaction",
]