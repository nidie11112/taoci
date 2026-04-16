"""
应用配置管理

从环境变量加载配置，提供类型安全的配置访问
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from pydantic.networks import AnyHttpUrl, RedisDsn
import secrets


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = Field(default="保研导师信息搜集网站", description="应用名称")
    APP_VERSION: str = Field(default="1.0.0", description="应用版本")
    APP_ENV: str = Field(default="development", description="运行环境: development, testing, production")
    DEBUG: bool = Field(default=False, description="调试模式")

    # API配置
    API_V1_STR: str = Field(default="/api/v1", description="API v1前缀")
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), description="应用密钥")
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "127.0.0.1"], description="允许的主机")

    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./taoci.db",
        description="数据库连接URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, description="数据库连接池大小")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="数据库连接池最大溢出")
    DATABASE_ECHO: bool = Field(default=False, description="是否输出SQL日志")

    # Redis配置
    REDIS_URL: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis连接URL"
    )
    REDIS_POOL_SIZE: int = Field(default=10, description="Redis连接池大小")

    # JWT配置
    JWT_SECRET: str = Field(default="your-super-secret-jwt-key-change-in-production", description="JWT密钥")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT算法")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="访问令牌过期时间(分钟)")

    # 爬虫配置
    CRAWLER_DELAY_SECONDS: float = Field(default=2.5, description="爬虫请求延迟(秒)")
    CRAWLER_MAX_RETRIES: int = Field(default=3, description="爬虫最大重试次数")
    CRAWLER_USER_AGENT: str = Field(
        default="TaociWebBot/1.0 (+https://taoci-web.example.com/bot)",
        description="爬虫User-Agent"
    )
    CRAWLER_TIMEOUT: int = Field(default=30, description="爬虫请求超时时间(秒)")

    # 文件存储配置
    UPLOAD_DIR: str = Field(default="./data/uploads", description="上传文件目录")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="最大上传文件大小(字节)")
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png"],
        description="允许上传的文件扩展名"
    )

    # 机器学习模型配置
    ML_MODEL_PATH: Optional[str] = Field(default=None, description="匹配模型路径")
    SENTENCE_TRANSFORMER_MODEL: str = Field(
        default="paraphrase-multilingual-MiniLM-L12-v2",
        description="句子转换器模型名称"
    )

    # 外部API配置（可选）
    SCHOLAR_API_KEY: Optional[str] = Field(default=None, description="Google Scholar API密钥")
    CNKI_API_KEY: Optional[str] = Field(default=None, description="知网API密钥")

    # 前端配置
    FRONTEND_URL: AnyHttpUrl = Field(default="http://localhost:3000", description="前端URL")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS允许的来源"
    )

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    LOG_DIR: str = Field(default="./logs", description="日志目录")

    # 功能开关
    ENABLE_CRAWLER: bool = Field(default=True, description="是否启用爬虫")
    ENABLE_ANALYTICS: bool = Field(default=False, description="是否启用分析")
    ENABLE_DOCUMENT_GENERATION: bool = Field(default=True, description="是否启用文书生成")

    # 安全配置
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="是否启用限流")
    RATE_LIMIT_REQUESTS: int = Field(default=60, description="每分钟请求限制")
    RATE_LIMIT_PERIOD: int = Field(default=60, description="限流周期(秒)")

    # 邮件配置（可选）
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP主机")
    SMTP_PORT: Optional[int] = Field(default=587, description="SMTP端口")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP用户名")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP密码")
    EMAIL_FROM: Optional[str] = Field(default=None, description="发件人邮箱")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        """验证数据库URL"""
        if not v:
            raise ValueError("DATABASE_URL不能为空")
        return v

    @validator("ALLOWED_HOSTS", pre=True)
    def validate_allowed_hosts(cls, v):
        """验证允许的主机"""
        if isinstance(v, str):
            # 如果是字符串，按逗号分割
            return [host.strip() for host in v.split(",") if host.strip()]
        return v

    @validator("ALLOWED_UPLOAD_EXTENSIONS", pre=True)
    def validate_allowed_upload_extensions(cls, v):
        """验证允许的上传文件扩展名"""
        if isinstance(v, str):
            # 如果是字符串，按逗号分割
            return [ext.strip() for ext in v.split(",") if ext.strip()]
        return v

    @validator("CORS_ORIGINS", pre=True)
    def validate_cors_origins(cls, v):
        """验证CORS来源"""
        if isinstance(v, str):
            # 如果是字符串，按逗号分割
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @validator("APP_ENV")
    def validate_app_env(cls, v):
        """验证运行环境"""
        allowed_envs = ["development", "testing", "production"]
        if v not in allowed_envs:
            raise ValueError(f"APP_ENV必须是 {allowed_envs} 之一")
        return v

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """验证日志级别"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"LOG_LEVEL必须是 {allowed_levels} 之一")
        return v.upper()

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.APP_ENV == "production"

    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.APP_ENV == "testing"

    def get_cors_origins(self) -> List[str]:
        """获取CORS来源列表"""
        if self.is_development:
            # 开发环境允许所有来源
            return ["*"]
        return self.CORS_ORIGINS

    def get_upload_dir(self) -> str:
        """获取上传目录绝对路径"""
        if os.path.isabs(self.UPLOAD_DIR):
            return self.UPLOAD_DIR
        # 相对于项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(project_root, self.UPLOAD_DIR)


# 全局配置实例
settings = Settings()

# 导出配置
__all__ = ["settings"]