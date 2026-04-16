"""
异常处理器模块

提供全局异常处理，统一错误响应格式
"""

from typing import Dict, Any
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求验证异常处理器

    将Pydantic验证错误转换为统一的错误响应格式
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"]) if error["loc"] else "body"
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "errors": errors,
            "path": request.url.path,
            "method": request.method
        }
    )


async def http_exception_handler(request: Request, exc: Exception):
    """
    HTTP异常处理器

    处理一般的HTTP异常
    """
    return JSONResponse(
        status_code=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        content={
            "status": "error",
            "code": getattr(exc, "code", "INTERNAL_SERVER_ERROR"),
            "message": str(exc) or "服务器内部错误",
            "path": request.url.path,
            "method": request.method
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    通用异常处理器

    处理未捕获的异常
    """
    # 记录异常日志
    # logger.error(f"未处理异常: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误" if not getattr(exc, "expose", False) else str(exc),
            "path": request.url.path,
            "method": request.method
        }
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    设置异常处理器

    注册全局异常处理器到FastAPI应用
    """
    # 请求验证异常
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # HTTP异常
    app.add_exception_handler(Exception, generic_exception_handler)

    # 可以添加更多特定异常处理器
    # app.add_exception_handler(HTTPException, http_exception_handler)

    # Pydantic验证错误
    app.add_exception_handler(ValidationError, validation_exception_handler)