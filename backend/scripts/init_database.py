#!/usr/bin/env python3
"""
数据库初始化脚本
创建所有表结构
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import logging
from sqlalchemy import text
from app.core.database import engine, Base
from app.models import (
    Professor, ProfessorEvaluation, Student, Match,
    AcademicPaper, DocumentTemplate, GeneratedDocument, User
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """初始化数据库（创建所有表）"""
    try:
        # 创建所有表
        async with engine.begin() as conn:
            # 检查表是否已存在
            tables = await conn.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """))
            existing_tables = [row[0] for row in tables.fetchall()]

            if existing_tables:
                logger.info(f"数据库已存在以下表: {existing_tables}")
                return False

            logger.info("开始创建数据库表...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表创建完成")

            # 创建索引
            await create_indexes(conn)

        return True

    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False


async def create_indexes(conn):
    """创建额外索引"""
    try:
        # 教授表索引
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_professors_university
            ON professors(university)
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_professors_department
            ON professors(department)
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_professors_name
            ON professors(name)
        """))

        # 评价表索引
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_evaluations_professor_id
            ON professor_evaluations(professor_id)
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_evaluations_personality_score
            ON professor_evaluations(personality_score)
        """))

        # 学生表索引
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_students_university
            ON students(university)
        """))

        logger.info("数据库索引创建完成")

    except Exception as e:
        logger.warning(f"创建索引失败: {e}")


async def check_database_connection():
    """检查数据库连接"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("数据库连接正常")
            return True
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="数据库初始化工具")
    parser.add_argument("--check", action="store_true", help="只检查数据库连接")
    parser.add_argument("--force", action="store_true", help="强制重新创建表（危险！）")

    args = parser.parse_args()

    if args.check:
        success = asyncio.run(check_database_connection())
        sys.exit(0 if success else 1)

    success = asyncio.run(init_database())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()