"""
用户模型

对应数据库中的users表，用于用户认证和授权
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 认证信息
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="哈希密码")

    # 用户信息
    full_name = Column(String(100), comment="全名")

    # 权限标志
    is_active = Column(Boolean, default=True, comment="是否活跃")
    is_superuser = Column(Boolean, default=False, comment="是否为超级用户")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 表级约束和索引
    __table_args__ = (
        # 索引
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
        {"comment": "用户表"},
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """转换为字典格式

        Args:
            include_sensitive: 是否包含敏感信息（如hashed_password）

        Returns:
            字典格式的用户信息
        """
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_sensitive:
            data["hashed_password"] = self.hashed_password

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any], hashed_password: Optional[str] = None) -> "User":
        """从字典创建用户实例

        Args:
            data: 用户数据字典
            hashed_password: 哈希密码（如果单独提供）

        Returns:
            User实例
        """
        # 移除id等自动生成的字段
        create_data = {k: v for k, v in data.items() if k not in ["id", "created_at", "updated_at"]}

        # 如果有单独的哈希密码，使用它
        if hashed_password:
            create_data["hashed_password"] = hashed_password
        elif "password" in create_data:
            # 如果有明文密码，需要先哈希（这里不处理，由服务层处理）
            # 移除明文密码，避免存储
            create_data.pop("password")
            # 如果没有提供哈希密码，抛出异常
            raise ValueError("必须提供hashed_password参数或由服务层处理密码哈希")

        return cls(**create_data)

    @property
    def is_authenticated(self) -> bool:
        """用户是否已认证

        Returns:
            是否已认证
        """
        return self.is_active

    def can_access_admin(self) -> bool:
        """用户是否可以访问管理功能

        Returns:
            是否可以访问管理功能
        """
        return self.is_active and self.is_superuser

    def update_last_login(self) -> None:
        """更新最后登录时间（如果需要）

        注意：这个模型中没有last_login字段，如果需要可以添加
        这里提供方法接口，方便后续扩展
        """
        # 如果有last_login字段，可以在这里更新
        pass