"""
安全配置模块

包含CORS、认证、限流等安全相关配置
"""

from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

from app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    """
    配置CORS中间件

    根据环境设置不同的CORS策略：
    - 开发环境：允许所有来源
    - 生产环境：仅允许配置的来源
    """
    origins = settings.get_cors_origins()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"]  # 允许前端下载文件
    )

    # 信任主机头
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )


def setup_rate_limit(app: FastAPI) -> None:
    """
    配置请求限流

    生产环境启用限流，防止滥用
    """
    if not settings.RATE_LIMIT_ENABLED:
        return

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_PERIOD}second"]
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希

    Args:
        password: 明文密码

    Returns:
        哈希后的密码
    """
    # 使用passlib或bcrypt
    # 这里使用简化实现，实际应使用安全哈希算法
    import hashlib
    import secrets

    # 生成盐
    salt = secrets.token_hex(16)
    # 计算哈希
    hash_obj = hashlib.sha256(f"{password}{salt}".encode())
    return f"sha256${salt}${hash_obj.hexdigest()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码

    Returns:
        是否匹配
    """
    try:
        # 解析哈希格式：算法$盐$哈希值
        algorithm, salt, stored_hash = hashed_password.split("$", 2)

        if algorithm == "sha256":
            import hashlib
            hash_obj = hashlib.sha256(f"{plain_password}{salt}".encode())
            return hash_obj.hexdigest() == stored_hash
        else:
            # 不支持的算法
            return False
    except (ValueError, AttributeError):
        return False


def create_access_token(data: dict) -> str:
    """
    创建JWT访问令牌

    Args:
        data: 包含用户信息的字典

    Returns:
        JWT令牌字符串
    """
    import jwt
    from datetime import datetime, timedelta

    to_encode = data.copy()

    # 设置过期时间
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # 编码JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str):
    """
    解码JWT访问令牌

    Args:
        token: JWT令牌字符串

    Returns:
        解码后的数据或None（如果无效）
    """
    import jwt
    from jwt.exceptions import PyJWTError

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except PyJWTError:
        return None


def sanitize_input(input_str: str) -> str:
    """
    清理用户输入，防止XSS攻击

    Args:
        input_str: 用户输入的字符串

    Returns:
        清理后的字符串
    """
    import html

    # HTML转义
    sanitized = html.escape(input_str)

    # 移除危险字符
    dangerous_chars = ["<script>", "</script>", "javascript:", "onload=", "onerror="]
    for dangerous in dangerous_chars:
        sanitized = sanitized.replace(dangerous, "")

    return sanitized.strip()


def validate_file_extension(filename: str) -> bool:
    """
    验证文件扩展名是否允许

    Args:
        filename: 文件名

    Returns:
        是否允许
    """
    import os

    _, ext = os.path.splite(filename.lower())
    return ext in settings.ALLOWED_UPLOAD_EXTENSIONS


def validate_file_size(file_size: int) -> bool:
    """
    验证文件大小是否允许

    Args:
        file_size: 文件大小（字节）

    Returns:
        是否允许
    """
    return file_size <= settings.MAX_UPLOAD_SIZE


# 导出
__all__ = [
    "setup_cors",
    "setup_rate_limit",
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "sanitize_input",
    "validate_file_extension",
    "validate_file_size",
]