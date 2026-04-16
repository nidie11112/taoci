#!/usr/bin/env python3
"""
数据导入脚本

用于导入各种数据源到数据库：
1. Excel评价数据
2. PDF简历数据
3. GitHub同步数据

使用示例：
python scripts/data_import.py --source excel --file path/to/data.xlsx
python scripts/data_import.py --source pdf --dir path/to/resumes
python scripts/data_import.py --source github --repo owner/repo
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import init_db, get_db
from app.core.config import settings
from app.models import Student, Professor, ProfessorEvaluation
from app.utils.excel_parser import ExcelParser, ProfessorDataImporter
from app.utils.pdf_resume_parser import PDFResumeParser
from app.utils.github_sync import GitHubSyncManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataImporter:
    """数据导入器"""

    def __init__(self, db_url: Optional[str] = None):
        """初始化数据导入器

        Args:
            db_url: 数据库URL，如果为None则使用配置中的URL
        """
        self.db_url = db_url or str(settings.DATABASE_URL)

    async def import_excel_data(self, file_path: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """导入Excel数据

        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称

        Returns:
            导入结果
        """
        logger.info(f"开始导入Excel数据: {file_path}")

        # 创建Excel解析器
        parser = ExcelParser(file_path, sheet_name)
        if not parser.load():
            return {"success": False, "error": "无法加载Excel文件"}

        # 解析数据
        data = parser.parse_all()
        if not data:
            return {"success": False, "error": "未解析到有效数据"}

        # 转换为模型数据
        importer = ProfessorDataImporter(parser)
        professors_data, evaluations_data = importer.transform_to_models()

        # 导入到数据库
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import AsyncSessionLocal

        imported_count = 0
        async with AsyncSessionLocal() as session:
            try:
                # 导入教授数据
                for prof_data in professors_data:
                    # 检查是否已存在
                    from sqlalchemy import select
                    query = select(Professor).where(
                        Professor.name == prof_data["name"],
                        Professor.university == prof_data["university"]
                    )
                    result = await session.execute(query)
                    existing = result.scalar_one_or_none()

                    if not existing:
                        # 创建新教授
                        professor = Professor.from_dict(prof_data)
                        session.add(professor)
                        await session.flush()  # 获取ID
                        imported_count += 1
                        logger.info(f"导入教授: {professor.name} - {professor.university}")
                    else:
                        professor = existing

                    # 如果有评价数据，导入评价
                    # 注意：这里简化处理，实际应该匹配教授

                await session.commit()
                logger.info(f"Excel数据导入完成，共导入 {imported_count} 位教授")

                return {
                    "success": True,
                    "imported_professors": imported_count,
                    "total_professors": len(professors_data),
                    "total_evaluations": len(evaluations_data),
                }

            except Exception as e:
                await session.rollback()
                logger.error(f"导入Excel数据失败: {e}")
                return {"success": False, "error": str(e)}

    async def import_pdf_resumes(self, directory: str) -> Dict[str, Any]:
        """导入PDF简历数据

        Args:
            directory: 包含PDF简历的目录

        Returns:
            导入结果
        """
        logger.info(f"开始导入PDF简历数据: {directory}")

        # 查找PDF文件
        pdf_files = []
        for ext in [".pdf", ".PDF"]:
            pdf_files.extend(Path(directory).glob(f"**/*{ext}"))

        if not pdf_files:
            return {"success": False, "error": f"目录中未找到PDF文件: {directory}"}

        logger.info(f"找到 {len(pdf_files)} 个PDF文件")

        imported_count = 0
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            try:
                for pdf_file in pdf_files:
                    logger.info(f"处理简历: {pdf_file.name}")

                    # 解析PDF简历
                    parser = PDFResumeParser(str(pdf_file))
                    student_info = parser.parse()

                    if "error" in student_info:
                        logger.warning(f"解析简历失败 {pdf_file.name}: {student_info['error']}")
                        continue

                    # 检查必要字段
                    if not student_info.get("name") or not student_info.get("university"):
                        logger.warning(f"简历缺少必要信息 {pdf_file.name}: 姓名或学校")
                        continue

                    # 检查是否已存在
                    from sqlalchemy import select
                    query = select(Student).where(
                        Student.name == student_info["name"],
                        Student.university == student_info["university"]
                    )
                    result = await session.execute(query)
                    existing = result.scalar_one_or_none()

                    if existing:
                        logger.info(f"学生已存在: {student_info['name']} - {student_info['university']}")
                        continue

                    # 创建学生
                    student_data = {
                        "name": student_info["name"],
                        "university": student_info["university"],
                        "major": student_info.get("major"),
                        "gpa": student_info.get("gpa"),
                        "gpa_ranking": student_info.get("gpa_ranking"),
                        "skills": student_info.get("skills", []),
                        "research_experience": student_info.get("research_experience", []),
                        "competition_awards": student_info.get("competition_awards", []),
                        "resume_pdf_path": str(pdf_file),
                    }

                    student = Student.from_dict(student_data)
                    session.add(student)
                    imported_count += 1
                    logger.info(f"导入学生: {student.name} - {student.university}")

                await session.commit()
                logger.info(f"PDF简历导入完成，共导入 {imported_count} 名学生")

                return {
                    "success": True,
                    "imported_students": imported_count,
                    "total_files": len(pdf_files),
                }

            except Exception as e:
                await session.rollback()
                logger.error(f"导入PDF简历失败: {e}")
                return {"success": False, "error": str(e)}

    async def import_github_data(self, repo_owner: str, repo_name: str, github_token: Optional[str] = None) -> Dict[str, Any]:
        """导入GitHub数据

        Args:
            repo_owner: 仓库所有者
            repo_name: 仓库名称
            github_token: GitHub令牌

        Returns:
            导入结果
        """
        logger.info(f"开始导入GitHub数据: {repo_owner}/{repo_name}")

        sync_config = {
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "github_token": github_token,
        }

        manager = GitHubSyncManager(sync_config)
        results = await manager.run_sync()

        if not results.get("success"):
            return results

        # 实际数据导入（GitHub同步管理器已经返回了数据，这里简化处理）
        logger.info(f"GitHub数据同步完成，找到 {results.get('professors_found', 0)} 位教授，{results.get('evaluations_found', 0)} 条评价")

        return results

    async def init_database(self) -> bool:
        """初始化数据库（创建表）

        Returns:
            是否成功初始化
        """
        try:
            await init_db()
            logger.info("数据库初始化完成")
            return True
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据导入工具")
    parser.add_argument("--source", required=True,
                       choices=["excel", "pdf", "github", "init-db"],
                       help="数据源类型")
    parser.add_argument("--file", help="Excel文件路径")
    parser.add_argument("--sheet", help="Excel工作表名称")
    parser.add_argument("--dir", help="PDF简历目录路径")
    parser.add_argument("--repo", help="GitHub仓库（格式：owner/repo）")
    parser.add_argument("--token", help="GitHub个人访问令牌")
    parser.add_argument("--init-db", action="store_true", help="初始化数据库")

    args = parser.parse_args()

    # 创建导入器
    importer = DataImporter()

    async def run_import():
        if args.init_db or args.source == "init-db":
            # 初始化数据库
            success = await importer.init_database()
            if not success:
                sys.exit(1)
            return

        if args.source == "excel":
            if not args.file:
                print("错误: Excel导入需要 --file 参数")
                sys.exit(1)

            result = await importer.import_excel_data(args.file, args.sheet)
            if result["success"]:
                print(f"成功导入 {result.get('imported_professors', 0)} 位教授")
            else:
                print(f"导入失败: {result.get('error', '未知错误')}")
                sys.exit(1)

        elif args.source == "pdf":
            if not args.dir:
                print("错误: PDF导入需要 --dir 参数")
                sys.exit(1)

            result = await importer.import_pdf_resumes(args.dir)
            if result["success"]:
                print(f"成功导入 {result.get('imported_students', 0)} 名学生")
            else:
                print(f"导入失败: {result.get('error', '未知错误')}")
                sys.exit(1)

        elif args.source == "github":
            if not args.repo:
                print("错误: GitHub导入需要 --repo 参数（格式：owner/repo）")
                sys.exit(1)

            if '/' not in args.repo:
                print("错误: --repo 参数格式应为 owner/repo")
                sys.exit(1)

            repo_owner, repo_name = args.repo.split('/', 1)
            result = await importer.import_github_data(repo_owner, repo_name, args.token)

            if result.get("success"):
                print(f"GitHub数据同步成功")
                print(f"找到教授: {result.get('professors_found', 0)}")
                print(f"找到评价: {result.get('evaluations_found', 0)}")
            else:
                print(f"GitHub同步失败: {result.get('errors', ['未知错误'])}")
                sys.exit(1)

    # 运行异步任务
    asyncio.run(run_import())


if __name__ == "__main__":
    main()