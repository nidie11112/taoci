"""
保研导师信息搜集网站 - FastAPI应用入口

主要功能：
1. 导师信息管理
2. 智能匹配算法
3. 文书生成服务
4. 数据采集与同步
"""

import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.security import setup_cors, setup_rate_limit
from app.api.v1 import api_router
from app.core.database import engine, Base
from app.utils.exception_handlers import setup_exception_handlers

# 配置日志
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    - 启动时：初始化数据库连接、加载模型等
    - 关闭时：清理资源、关闭连接等
    """
    # 启动时
    logger.info("应用启动中...")
    logger.info(f"环境: {settings.APP_ENV}")
    logger.info(f"数据库: {settings.DATABASE_URL}")

    # 创建数据库表（开发环境）
    if settings.APP_ENV == "development":
        try:
            async with engine.begin() as conn:
                # 注意：生产环境应使用Alembic迁移
                await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表创建完成（开发环境）")
        except Exception as e:
            logger.warning(f"数据库表创建失败: {e}")

    # 加载机器学习模型（如果有）
    # if settings.ML_MODEL_PATH and os.path.exists(settings.ML_MODEL_PATH):
    #     app.state.match_model = load_model(settings.ML_MODEL_PATH)
    #     logger.info("机器学习模型加载完成")

    yield

    # 关闭时
    logger.info("应用关闭中...")

    # 关闭数据库连接池
    if engine:
        await engine.dispose()
        logger.info("数据库连接池已关闭")

    logger.info("应用关闭完成")

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="保研导师信息搜集网站 - 智能匹配与文书生成平台",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.APP_ENV != "production" else None,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    lifespan=lifespan,
)

# 中间件：记录请求日志
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"请求: {request.method} {request.url.path}")

        # 记录请求体（排除文件上传等大请求）
        if request.method in ["POST", "PUT", "PATCH"] and "multipart/form-data" not in request.headers.get("content-type", ""):
            try:
                body = await request.body()
                if body and len(body) < 1000:  # 只记录小请求体
                    logger.debug(f"请求体: {body.decode()}")
            except Exception:
                pass

        response = await call_next(request)

        logger.info(f"响应: {request.method} {request.url.path} - 状态码: {response.status_code}")
        return response

# 添加中间件
app.add_middleware(LoggingMiddleware)

# 配置CORS
setup_cors(app)

# 配置限流（根据环境）
if settings.APP_ENV == "production":
    setup_rate_limit(app)

# 设置异常处理器
setup_exception_handlers(app)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 健康检查端点
@app.get("/health", tags=["健康检查"])
async def health_check():
    """
    健康检查端点

    返回应用状态，用于监控和负载均衡
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }

@app.get("/", tags=["根目录"])
async def root():
    """
    根端点

    返回应用基本信息
    """
    return {
        "message": f"欢迎使用{settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.APP_ENV != "production" else None,
        "health": "/health",
    }

# 开发服务器启动
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_ENV == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True if settings.APP_ENV == "development" else False,
    )