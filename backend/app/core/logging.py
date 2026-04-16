"""
日志配置模块

提供结构化的日志记录，支持不同日志级别和输出目标
"""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.core.config import settings


def setup_logging() -> None:
    """
    配置日志系统

    根据环境配置不同的日志处理器：
    - 开发环境：控制台输出，详细日志
    - 生产环境：文件输出，按级别分离
    """
    log_level = getattr(logging, settings.LOG_LEVEL)

    # 创建日志目录
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 获取根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除现有处理器
    root_logger.handlers.clear()

    # 控制台处理器（始终启用）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if settings.is_development:
        # 开发环境：仅控制台输出
        logging.info(f"日志系统配置完成（开发环境，级别: {settings.LOG_LEVEL}）")
        return

    # 生产环境：文件输出
    # 应用日志文件
    app_log_file = log_dir / "app.log"
    app_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setLevel(log_level)
    app_handler.setFormatter(formatter)
    root_logger.addHandler(app_handler)

    # 错误日志文件（单独）
    error_log_file = log_dir / "error.log"
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # 爬虫日志（单独）
    crawler_log_file = log_dir / "crawler.log"
    crawler_handler = RotatingFileHandler(
        crawler_log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    crawler_handler.setLevel(logging.INFO)
    crawler_handler.setFormatter(formatter)

    crawler_logger = logging.getLogger("crawler")
    crawler_logger.addHandler(crawler_handler)
    crawler_logger.propagate = False

    # API访问日志（单独）
    access_log_file = log_dir / "access.log"
    access_handler = RotatingFileHandler(
        access_log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(formatter)

    access_logger = logging.getLogger("api.access")
    access_logger.addHandler(access_handler)
    access_logger.propagate = False

    # 数据库日志（可选，调试用）
    if settings.DATABASE_ECHO:
        db_log_file = log_dir / "database.log"
        db_handler = RotatingFileHandler(
            db_log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=2,
            encoding='utf-8'
        )
        db_handler.setLevel(logging.DEBUG)
        db_handler.setFormatter(formatter)

        db_logger = logging.getLogger("sqlalchemy.engine")
        db_logger.addHandler(db_handler)
        db_logger.setLevel(logging.INFO)

    logging.info(f"日志系统配置完成（生产环境，级别: {settings.LOG_LEVEL}）")
    logging.info(f"日志目录: {log_dir.absolute()}")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志器实例

    Args:
        name: 日志器名称，通常使用 __name__

    Returns:
        配置好的日志器实例
    """
    if name is None:
        name = "taoci_web"

    # 确保日志系统已配置
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        setup_logging()

    return logging.getLogger(name)


class StructuredLogger:
    """
    结构化日志记录器

    提供更结构化的日志记录方式，便于后续分析
    """

    def __init__(self, name: str):
        self.logger = get_logger(name)

    def info(self, message: str, **kwargs):
        """记录信息日志"""
        extra = self._format_extra(kwargs)
        self.logger.info(f"{message} {extra}")

    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        extra = self._format_extra(kwargs)
        self.logger.warning(f"{message} {extra}")

    def error(self, message: str, **kwargs):
        """记录错误日志"""
        extra = self._format_extra(kwargs)
        self.logger.error(f"{message} {extra}")

    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        extra = self._format_extra(kwargs)
        self.logger.debug(f"{message} {extra}")

    def exception(self, message: str, exc: Exception, **kwargs):
        """记录异常日志"""
        extra = self._format_extra(kwargs)
        self.logger.error(f"{message} {extra}", exc_info=exc)

    def _format_extra(self, kwargs: dict) -> str:
        """格式化额外参数"""
        if not kwargs:
            return ""

        formatted = []
        for key, value in kwargs.items():
            if isinstance(value, (dict, list)):
                # 复杂对象转换为字符串
                import json
                try:
                    value = json.dumps(value, ensure_ascii=False)
                except:
                    value = str(value)
            formatted.append(f"{key}={value}")

        return " | ".join(formatted)


# 导出
__all__ = ["setup_logging", "get_logger", "StructuredLogger"]