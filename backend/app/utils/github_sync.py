"""
GitHub数据同步工具

用于从GitHub仓库同步导师评价数据
支持公开仓库的数据获取和增量同步
"""

import aiohttp
import asyncio
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, date
import logging
import re
import os

logger = logging.getLogger(__name__)


class GitHubSync:
    """GitHub数据同步工具"""

    def __init__(self, repo_owner: str, repo_name: str, github_token: Optional[str] = None):
        """初始化GitHub同步工具

        Args:
            repo_owner: 仓库所有者
            repo_name: 仓库名称
            github_token: GitHub个人访问令牌（可选，用于提高API限制）
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "TaociWebBot/1.0"
        }

        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    async def make_request(self, url: str) -> Optional[Dict[str, Any]]:
        """发送HTTP请求

        Args:
            url: 请求URL

        Returns:
            响应数据，如果失败则返回None
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 404:
                        logger.warning(f"资源不存在: {url}")
                    elif response.status == 403:
                        # API限制
                        rate_limit = response.headers.get('X-RateLimit-Remaining', 'unknown')
                        logger.warning(f"API限制，剩余请求次数: {rate_limit}")
                    else:
                        logger.error(f"请求失败 {response.status}: {url}")
        except Exception as e:
            logger.error(f"请求异常: {e}")

        return None

    async def get_repo_contents(self, path: str = "") -> List[Dict[str, Any]]:
        """获取仓库目录内容

        Args:
            path: 目录路径

        Returns:
            目录内容列表
        """
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"
        data = await self.make_request(url)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and data.get("type") == "file":
            return [data]  # 单个文件
        else:
            return []

    async def get_file_content(self, file_path: str) -> Optional[str]:
        """获取文件内容

        Args:
            file_path: 文件路径

        Returns:
            文件内容，如果失败则返回None
        """
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
        data = await self.make_request(url)

        if data and data.get("type") == "file":
            # 文件内容可能是base64编码的
            content = data.get("content", "")
            encoding = data.get("encoding")

            if encoding == "base64":
                import base64
                try:
                    content = base64.b64decode(content).decode("utf-8")
                    return content
                except Exception as e:
                    logger.error(f"解码base64内容失败: {e}")
            else:
                return content

        return None

    async def find_evaluation_files(self, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """查找评价数据文件

        Args:
            extensions: 文件扩展名列表，默认为[".json", ".md", ".txt"]

        Returns:
            文件信息列表
        """
        if extensions is None:
            extensions = [".json", ".md", ".txt"]

        all_files = []

        async def search_directory(current_path: str = ""):
            """递归搜索目录"""
            contents = await self.get_repo_contents(current_path)

            for item in contents:
                if item["type"] == "dir":
                    # 递归搜索子目录
                    await search_directory(item["path"])
                elif item["type"] == "file":
                    # 检查文件扩展名
                    file_name = item["name"].lower()
                    if any(file_name.endswith(ext) for ext in extensions):
                        all_files.append(item)

        await search_directory()
        logger.info(f"找到 {len(all_files)} 个评价文件")
        return all_files

    def parse_json_file(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """解析JSON格式的评价文件

        Args:
            content: 文件内容
            file_path: 文件路径（用于日志）

        Returns:
            解析后的评价数据列表
        """
        try:
            data = json.loads(content)

            if isinstance(data, dict):
                # 单个评价对象
                return [self._normalize_evaluation_data(data, file_path)]
            elif isinstance(data, list):
                # 评价对象列表
                evaluations = []
                for item in data:
                    if isinstance(item, dict):
                        normalized = self._normalize_evaluation_data(item, file_path)
                        evaluations.append(normalized)
                return evaluations
            else:
                logger.warning(f"JSON文件格式不支持: {file_path}")
                return []
        except json.JSONDecodeError as e:
            logger.error(f"解析JSON失败 {file_path}: {e}")
            return []

    def parse_markdown_file(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """解析Markdown格式的评价文件

        Args:
            content: 文件内容
            file_path: 文件路径

        Returns:
            解析后的评价数据列表
        """
        try:
            # 尝试从Markdown中提取结构化数据
            evaluation = {
                "source": "github",
                "file_path": file_path,
                "raw_content": content[:500] + "..." if len(content) > 500 else content,
            }

            # 尝试提取导师信息
            professor_info = self._extract_professor_from_markdown(content)
            if professor_info:
                evaluation["professor_info"] = professor_info

            # 尝试提取评价信息
            eval_info = self._extract_evaluation_from_markdown(content)
            if eval_info:
                evaluation["evaluation_info"] = eval_info

            # 如果提取到足够的信息，返回
            if professor_info or eval_info:
                return [evaluation]
            else:
                # 如果没有提取到结构化信息，尝试将整个内容作为学生评论
                if content.strip():
                    return [{
                        "source": "github",
                        "file_path": file_path,
                        "evaluation_info": {
                            "student_comments": content.strip(),
                        }
                    }]
                return []
        except Exception as e:
            logger.error(f"解析Markdown失败 {file_path}: {e}")
            return []

    def parse_text_file(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """解析纯文本格式的评价文件

        Args:
            content: 文件内容
            file_path: 文件路径

        Returns:
            解析后的评价数据列表
        """
        # 纯文本文件处理类似于Markdown
        return self.parse_markdown_file(content, file_path)

    def _normalize_evaluation_data(self, data: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """规范化评价数据

        Args:
            data: 原始评价数据
            file_path: 文件路径

        Returns:
            规范化后的评价数据
        """
        normalized = {
            "source": "github",
            "file_path": file_path,
            "professor_info": {},
            "evaluation_info": {},
        }

        # 映射字段
        field_mapping = {
            # 教授信息
            "name": ["name", "教授姓名", "导师姓名", "老师姓名"],
            "university": ["university", "学校", "大学"],
            "department": ["department", "院系", "学院"],
            "title": ["title", "职称", "职位"],
            "research_fields": ["research_fields", "研究方向", "研究领域"],

            # 评价信息
            "personality_score": ["personality_score", "人品得分", "人品分数"],
            "group_atmosphere": ["group_atmosphere", "课题组氛围", "实验室氛围"],
            "student_comments": ["student_comments", "学生评价", "学生反馈"],
            "evaluation_date": ["evaluation_date", "评价日期", "日期"],
        }

        # 处理教授信息
        professor_info = {}
        for field, possible_keys in field_mapping.items():
            if field in ["personality_score", "group_atmosphere", "student_comments", "evaluation_date"]:
                continue  # 这些是评价信息

            for key in possible_keys:
                if key in data:
                    value = data[key]
                    # 处理特殊字段
                    if field == "research_fields" and isinstance(value, str):
                        # 分割研究方向
                        research_fields = re.split(r'[,;，；\n]', value)
                        research_fields = [field.strip() for field in research_fields if field.strip()]
                        professor_info[field] = research_fields
                    else:
                        professor_info[field] = value
                    break

        if professor_info:
            normalized["professor_info"] = professor_info

        # 处理评价信息
        evaluation_info = {}
        for field, possible_keys in field_mapping.items():
            if field not in ["personality_score", "group_atmosphere", "student_comments", "evaluation_date"]:
                continue

            for key in possible_keys:
                if key in data:
                    value = data[key]

                    # 处理特殊字段
                    if field == "evaluation_date" and isinstance(value, str):
                        # 尝试解析日期
                        try:
                            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
                                try:
                                    evaluation_info[field] = datetime.strptime(value, fmt).date()
                                    break
                                except ValueError:
                                    continue
                        except Exception:
                            evaluation_info[field] = value
                    elif field == "personality_score":
                        try:
                            evaluation_info[field] = float(value)
                        except (ValueError, TypeError):
                            evaluation_info[field] = value
                    else:
                        evaluation_info[field] = value
                    break

        if evaluation_info:
            normalized["evaluation_info"] = evaluation_info

        # 如果没有明确提取到教授信息，但数据中有类似字段，尝试提取
        if not professor_info and not evaluation_info:
            # 尝试从原始数据中提取
            for key, value in data.items():
                if isinstance(value, str):
                    # 检查是否包含教授姓名
                    if any(name_key in key.lower() for name_key in ["name", "姓名"]):
                        professor_info["name"] = value
                    # 检查是否包含学校
                    elif any(school_key in key.lower() for school_key in ["university", "学校", "大学"]):
                        professor_info["university"] = value

            if professor_info:
                normalized["professor_info"] = professor_info

        return normalized

    def _extract_professor_from_markdown(self, content: str) -> Dict[str, Any]:
        """从Markdown中提取教授信息

        Args:
            content: Markdown内容

        Returns:
            教授信息字典
        """
        professor_info = {}

        # 尝试查找标题或一级标题
        title_pattern = r'^#\s+(.+教授|[^\n]+老师|[^\n]+导师)'
        match = re.search(title_pattern, content, re.MULTILINE)
        if match:
            professor_info["name"] = match.group(1).strip()

        # 查找关键信息行
        info_patterns = {
            "university": r'(?:学校|大学)[：:]\s*([^\n]+)',
            "department": r'(?:院系|学院)[：:]\s*([^\n]+)',
            "title": r'(?:职称|职位)[：:]\s*([^\n]+)',
            "research_fields": r'(?:研究方向|研究领域)[：:]\s*([^\n]+)',
        }

        for field, pattern in info_patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1).strip()
                if field == "research_fields":
                    # 分割研究方向
                    research_fields = re.split(r'[,;，；]', value)
                    research_fields = [field.strip() for field in research_fields if field.strip()]
                    professor_info[field] = research_fields
                else:
                    professor_info[field] = value

        return professor_info

    def _extract_evaluation_from_markdown(self, content: str) -> Dict[str, Any]:
        """从Markdown中提取评价信息

        Args:
            content: Markdown内容

        Returns:
            评价信息字典
        """
        evaluation_info = {}

        # 查找评价部分
        sections = {
            "人品得分": r'(?:人品得分|人品评价)[：:]\s*([^\n]+)',
            "课题组氛围": r'(?:课题组氛围|实验室氛围)[：:]\s*([^\n]+)',
            "学生评价": r'(?:学生评价|学生反馈)[：:]\s*([^\n]+)',
            "评价日期": r'(?:评价日期|日期)[：:]\s*([^\n]+)',
        }

        for chinese_key, pattern in sections.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1).strip()

                # 映射到英文键名
                if chinese_key == "人品得分":
                    try:
                        evaluation_info["personality_score"] = float(value)
                    except (ValueError, TypeError):
                        evaluation_info["personality_score"] = value
                elif chinese_key == "课题组氛围":
                    evaluation_info["group_atmosphere"] = value
                elif chinese_key == "学生评价":
                    evaluation_info["student_comments"] = value
                elif chinese_key == "评价日期":
                    # 尝试解析日期
                    try:
                        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
                            try:
                                evaluation_info["evaluation_date"] = datetime.strptime(value, fmt).date()
                                break
                            except ValueError:
                                continue
                    except Exception:
                        evaluation_info["evaluation_date"] = value

        return evaluation_info

    async def sync_evaluations(self) -> List[Dict[str, Any]]:
        """同步所有评价数据

        Returns:
            同步的评价数据列表
        """
        logger.info(f"开始同步GitHub仓库: {self.repo_owner}/{self.repo_name}")

        # 查找评价文件
        evaluation_files = await self.find_evaluation_files()
        all_evaluations = []

        for file_info in evaluation_files:
            file_path = file_info["path"]
            logger.info(f"处理文件: {file_path}")

            # 获取文件内容
            content = await self.get_file_content(file_path)
            if not content:
                continue

            # 根据文件扩展名选择解析器
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == ".json":
                evaluations = self.parse_json_file(content, file_path)
            elif file_ext == ".md":
                evaluations = self.parse_markdown_file(content, file_path)
            elif file_ext == ".txt":
                evaluations = self.parse_text_file(content, file_path)
            else:
                logger.warning(f"不支持的文件格式: {file_ext}")
                continue

            all_evaluations.extend(evaluations)

        logger.info(f"同步完成，共获取 {len(all_evaluations)} 条评价数据")
        return all_evaluations

    def transform_to_models(self, evaluations: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
        """将同步的数据转换为数据库模型格式

        Args:
            evaluations: 评价数据列表

        Returns:
            (教授数据列表, 评价数据列表)
        """
        professors = []
        professor_evaluations = []

        for eval_data in evaluations:
            prof_info = eval_data.get("professor_info", {})
            eval_info = eval_data.get("evaluation_info", {})

            # 创建教授数据（如果有足够信息）
            if prof_info.get("name") and prof_info.get("university"):
                professor_data = {
                    "name": prof_info["name"],
                    "university": prof_info["university"],
                    "department": prof_info.get("department"),
                    "title": prof_info.get("title"),
                    "research_fields": prof_info.get("research_fields", []),
                }
                professors.append(professor_data)

            # 创建评价数据
            if eval_info:
                evaluation_data = {
                    "source": "github",
                    "personality_score": eval_info.get("personality_score"),
                    "group_atmosphere": eval_info.get("group_atmosphere"),
                    "student_comments": eval_info.get("student_comments"),
                    "evaluation_date": eval_info.get("evaluation_date"),
                }
                professor_evaluations.append(evaluation_data)

        return professors, professor_evaluations


class GitHubSyncManager:
    """GitHub同步管理器"""

    def __init__(self, sync_config: Dict[str, Any]):
        """初始化同步管理器

        Args:
            sync_config: 同步配置
        """
        self.sync_config = sync_config
        self.synced_files = set()

    async def run_sync(self) -> Dict[str, Any]:
        """运行同步任务

        Returns:
            同步结果
        """
        results = {
            "success": False,
            "professors_found": 0,
            "evaluations_found": 0,
            "errors": [],
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # 创建GitHub同步实例
            github_sync = GitHubSync(
                repo_owner=self.sync_config.get("repo_owner", ""),
                repo_name=self.sync_config.get("repo_name", ""),
                github_token=self.sync_config.get("github_token"),
            )

            # 同步评价数据
            evaluations = await github_sync.sync_evaluations()

            # 转换为模型数据
            professors, professor_evaluations = github_sync.transform_to_models(evaluations)

            results.update({
                "success": True,
                "professors_found": len(professors),
                "evaluations_found": len(professor_evaluations),
                "total_files": len(evaluations),
            })

        except Exception as e:
            results["errors"].append(str(e))
            logger.error(f"同步失败: {e}")

        return results


# 使用示例
if __name__ == "__main__":
    import asyncio

    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 示例配置
    sync_config = {
        "repo_owner": "example-owner",
        "repo_name": "example-repo",
        "github_token": os.getenv("GITHUB_TOKEN"),  # 从环境变量获取
    }

    async def main():
        manager = GitHubSyncManager(sync_config)
        results = await manager.run_sync()

        print("同步结果:")
        for key, value in results.items():
            if key != "errors" or value:
                print(f"{key}: {value}")

    asyncio.run(main())