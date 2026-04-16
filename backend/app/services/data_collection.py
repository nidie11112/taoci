"""
数据采集服务

负责从外部数据源收集导师信息、评价数据等
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd

# 尝试导入Selenium（用于动态网页）
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("警告: selenium 未安装，动态网页爬取功能将不可用")


class CrawlerService:
    """爬虫服务类"""

    def __init__(self, user_agent: Optional[str] = None, delay: float = 1.0):
        """初始化爬虫服务

        Args:
            user_agent: 用户代理字符串
            delay: 请求延迟（秒）
        """
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
        self.delay = delay

        # 请求头
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # 会话（将在使用时创建）
        self.session: Optional[aiohttp.ClientSession] = None

        # 目标院校配置
        self.university_configs = {
            "上海交通大学": {
                "mechanics_url": "https://me.sjtu.edu.cn/faculty/",
                "mech_power_url": "https://me.sjtu.edu.cn/faculty/",
                "parser": self._parse_sjtu_faculty,
            },
            "浙江大学": {
                "mechanics_url": "https://mech.zju.edu.cn/",
                "parser": self._parse_zju_faculty,
            },
            "清华大学深圳研究院": {
                "smart_manufacturing_url": "https://www.sz.tsinghua.edu.cn/",
                "parser": self._parse_tsinghua_sz_faculty,
            }
        }

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    async def initialize(self):
        """初始化服务"""
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def close(self):
        """关闭服务"""
        if self.session:
            await self.session.close()
            self.session = None

    async def crawl_university_faculty(
        self,
        university: str,
        department: Optional[str] = None,
        max_pages: int = 10
    ) -> List[Dict[str, Any]]:
        """爬取大学教师信息

        Args:
            university: 大学名称
            department: 院系名称（可选）
            max_pages: 最大爬取页数

        Returns:
            教师信息列表
        """
        professors = []

        # 获取配置
        config = self.university_configs.get(university)
        if not config:
            print(f"警告: 未配置 {university} 的爬取规则")
            return professors

        # 获取解析器
        parser = config.get("parser")
        if not parser:
            print(f"警告: {university} 未配置解析器")
            return professors

        # 根据院系选择URL
        urls = []
        if department:
            dept_key = f"{department.lower().replace(' ', '_')}_url"
            url = config.get(dept_key)
            if url:
                urls.append(url)
        else:
            # 添加所有院系URL
            for key, value in config.items():
                if key.endswith("_url"):
                    urls.append(value)

        if not urls:
            print(f"警告: {university} 未找到可用的URL")
            return professors

        # 爬取每个URL
        for url in urls:
            try:
                print(f"开始爬取: {url}")
                page_professors = await self._crawl_page(url, parser, max_pages)
                professors.extend(page_professors)

                # 延迟以避免被封
                await asyncio.sleep(self.delay)

            except Exception as e:
                print(f"爬取失败 {url}: {e}")
                continue

        return professors

    async def crawl_professor_details(
        self,
        professor_url: str
    ) -> Dict[str, Any]:
        """爬取导师详细信息

        Args:
            professor_url: 导师个人主页URL

        Returns:
            导师详细信息
        """
        if not self.session:
            await self.initialize()

        try:
            # 获取页面内容
            async with self.session.get(professor_url) as response:
                if response.status != 200:
                    print(f"请求失败: {professor_url}, 状态码: {response.status}")
                    return {}

                html = await response.text()

            # 解析页面
            soup = BeautifulSoup(html, 'html.parser')

            # 提取基本信息
            professor_info = {
                "personal_page_url": professor_url,
                "crawled_at": datetime.now().isoformat(),
            }

            # 尝试提取姓名
            name_selectors = [
                "h1", "h2", ".name", ".professor-name", "#name",
                "title", "meta[property='og:title']"
            ]

            for selector in name_selectors:
                element = soup.select_one(selector)
                if element:
                    name = element.get_text(strip=True)
                    # 清理姓名
                    name = re.sub(r'[-|教授|副教授|讲师|博士|\s]+$', '', name)
                    if name and len(name) >= 2:
                        professor_info["name"] = name
                        break

            # 尝试提取职称
            title_selectors = [
                ".title", ".position", ".rank", ".professor-title",
                "meta[name='title']", "meta[property='og:description']"
            ]

            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    if title and any(word in title for word in ["教授", "副教授", "讲师", "研究员"]):
                        professor_info["title"] = title
                        break

            # 尝试提取邮箱
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, html)
            if emails:
                professor_info["email"] = emails[0]

            # 尝试提取研究方向
            research_patterns = [
                r'研究方向[:：]\s*(.+)',
                r'研究领域[:：]\s*(.+)',
                r'研究方向[：:]\s*([^<]+)',
                r'研究兴趣[:：]\s*(.+)'
            ]

            for pattern in research_patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    research_text = match.group(1).strip()
                    # 清理文本
                    research_text = re.sub(r'<[^>]+>', ' ', research_text)
                    research_text = re.sub(r'\s+', ' ', research_text)
                    # 分割研究方向
                    research_fields = self._extract_research_fields(research_text)
                    if research_fields:
                        professor_info["research_fields"] = research_fields
                    break

            # 尝试提取个人简介
            bio_selectors = [
                ".bio", ".introduction", ".profile", ".about",
                "p", "div[class*='intro']", "div[class*='bio']"
            ]

            for selector in bio_selectors[:3]:  # 只检查前几个选择器
                element = soup.select_one(selector)
                if element:
                    bio = element.get_text(strip=True)
                    if len(bio) > 50 and len(bio) < 1000:  # 合理长度
                        professor_info["bio"] = bio
                        break

            return professor_info

        except Exception as e:
            print(f"爬取导师详情失败 {professor_url}: {e}")
            return {}

    async def crawl_google_scholar(
        self,
        professor_name: str,
        university: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """爬取Google Scholar论文信息（模拟）

        Args:
            professor_name: 导师姓名
            university: 大学名称（可选）
            max_results: 最大结果数

        Returns:
            论文信息列表
        """
        # 注意：实际Google Scholar爬取需要处理反爬机制
        # 这里返回模拟数据
        print(f"模拟爬取Google Scholar: {professor_name}")

        papers = []
        for i in range(min(max_results, 5)):  # 最多5篇模拟论文
            papers.append({
                "title": f"{professor_name}的论文示例 {i+1}",
                "authors": [professor_name, "合作者1", "合作者2"],
                "publication_venue": "示例期刊/会议",
                "publication_year": 2023 - i,
                "abstract": f"这是{professor_name}教授的第{i+1}篇论文的模拟摘要。该论文研究了相关领域的重要问题。",
                "citations": 10 * (5 - i),
                "pdf_url": f"https://example.com/paper_{i+1}.pdf",
            })

        return papers

    async def sync_github_evaluations(
        self,
        repo_url: str = "https://github.com/wangzhiye-tiancai/mysupervisor_save"
    ) -> List[Dict[str, Any]]:
        """同步GitHub评价数据

        Args:
            repo_url: GitHub仓库URL

        Returns:
            评价数据列表
        """
        # 注意：实际GitHub API调用需要认证
        # 这里返回模拟数据
        print(f"模拟同步GitHub评价数据: {repo_url}")

        evaluations = []
        universities = ["上海交通大学", "浙江大学", "清华大学", "北京大学"]
        departments = ["力学系", "机械工程学院", "材料科学与工程学院", "计算机科学与技术系"]

        for i in range(20):  # 20条模拟评价
            university = universities[i % len(universities)]
            department = departments[i % len(departments)]

            evaluations.append({
                "professor_name": f"模拟导师{i+1}",
                "university": university,
                "department": department,
                "personality_score": round(3.0 + (i % 3) * 0.5, 1),  # 3.0-4.5分
                "group_atmosphere": ["严格", "宽松", "和谐", "高压"][i % 4],
                "student_comments": f"这是对{university}{department}模拟导师{i+1}的评价示例。",
                "source": "github_simulated",
                "evaluation_date": f"2024-{str(i%12+1).zfill(2)}-01",
            })

        return evaluations

    async def parse_excel_data(
        self,
        file_path: str,
        sheet_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """解析Excel评价数据

        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称（可选）

        Returns:
            评价数据列表
        """
        try:
            # 读取Excel文件
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)

            print(f"成功读取Excel文件: {file_path}, 形状: {df.shape}")

            evaluations = []

            # 假设Excel列结构
            # 实际应根据具体文件结构调整
            for _, row in df.iterrows():
                evaluation = {}

                # 尝试匹配常见列名
                column_mapping = {
                    "姓名": "professor_name",
                    "导师姓名": "professor_name",
                    "学校": "university",
                    "大学": "university",
                    "院系": "department",
                    "专业": "department",
                    "人品得分": "personality_score",
                    "评分": "personality_score",
                    "得分": "personality_score",
                    "课题组氛围": "group_atmosphere",
                    "氛围": "group_atmosphere",
                    "学生评价": "student_comments",
                    "评价": "student_comments",
                    "评论": "student_comments",
                }

                for excel_col, target_field in column_mapping.items():
                    if excel_col in df.columns:
                        value = row[excel_col]
                        if pd.notna(value):
                            evaluation[target_field] = value

                # 确保必要字段存在
                if "professor_name" in evaluation and "university" in evaluation:
                    evaluation["source"] = "excel"
                    evaluation["crawled_at"] = datetime.now().isoformat()
                    evaluations.append(evaluation)

            print(f"从Excel解析出 {len(evaluations)} 条评价")
            return evaluations

        except Exception as e:
            print(f"解析Excel文件失败 {file_path}: {e}")
            return []

    # ==================== 私有方法 ====================

    async def _crawl_page(
        self,
        url: str,
        parser,
        max_pages: int
    ) -> List[Dict[str, Any]]:
        """爬取单个页面"""
        if not self.session:
            await self.initialize()

        professors = []

        for page in range(1, max_pages + 1):
            try:
                # 构建分页URL（如果需要）
                page_url = url
                if page > 1:
                    # 简单的分页处理，实际应根据网站结构调整
                    if "?" in url:
                        page_url = f"{url}&page={page}"
                    else:
                        page_url = f"{url}?page={page}"

                # 获取页面
                async with self.session.get(page_url) as response:
                    if response.status != 200:
                        print(f"页面 {page_url} 请求失败: {response.status}")
                        break

                    html = await response.text()

                # 使用解析器解析页面
                page_professors = parser(html, page_url)
                professors.extend(page_professors)

                print(f"页面 {page} 解析出 {len(page_professors)} 位导师")

                # 如果没有数据，可能已到达最后一页
                if not page_professors and page > 1:
                    break

                # 延迟
                await asyncio.sleep(self.delay)

            except Exception as e:
                print(f"爬取页面 {page_url} 失败: {e}")
                break

        return professors

    def _parse_sjtu_faculty(self, html: str, url: str) -> List[Dict[str, Any]]:
        """解析上海交通大学教师页面（模拟）"""
        print(f"解析上海交通大学页面: {url}")

        # 模拟数据
        professors = [
            {
                "name": "张教授",
                "university": "上海交通大学",
                "department": "机械与动力工程学院",
                "title": "教授",
                "research_fields": ["力学", "复合材料", "智能材料"],
                "personal_page_url": "https://me.sjtu.edu.cn/faculty/zhang",
            },
            {
                "name": "李教授",
                "university": "上海交通大学",
                "department": "机械与动力工程学院",
                "title": "副教授",
                "research_fields": ["机械设计", "机器人", "智能制造"],
                "personal_page_url": "https://me.sjtu.edu.cn/faculty/li",
            },
            {
                "name": "王教授",
                "university": "上海交通大学",
                "department": "材料科学与工程学院",
                "title": "教授",
                "research_fields": ["材料科学", "纳米材料", "功能材料"],
                "personal_page_url": "https://mse.sjtu.edu.cn/faculty/wang",
            },
        ]

        return professors

    def _parse_zju_faculty(self, html: str, url: str) -> List[Dict[str, Any]]:
        """解析浙江大学教师页面（模拟）"""
        print(f"解析浙江大学页面: {url}")

        # 模拟数据
        professors = [
            {
                "name": "陈教授",
                "university": "浙江大学",
                "department": "力学系",
                "title": "教授",
                "research_fields": ["固体力学", "计算力学", "实验力学"],
                "personal_page_url": "https://mech.zju.edu.cn/faculty/chen",
            },
            {
                "name": "刘教授",
                "university": "浙江大学",
                "department": "机械工程学院",
                "title": "教授",
                "research_fields": ["机械制造", "数字化设计", "工业4.0"],
                "personal_page_url": "https://me.zju.edu.cn/faculty/liu",
            },
        ]

        return professors

    def _parse_tsinghua_sz_faculty(self, html: str, url: str) -> List[Dict[str, Any]]:
        """解析清华大学深圳研究院教师页面（模拟）"""
        print(f"解析清华大学深圳研究院页面: {url}")

        # 模拟数据
        professors = [
            {
                "name": "赵教授",
                "university": "清华大学深圳研究院",
                "department": "智能制造系",
                "title": "教授",
                "research_fields": ["智能制造", "工业互联网", "数字孪生"],
                "personal_page_url": "https://www.sz.tsinghua.edu.cn/faculty/zhao",
            },
            {
                "name": "孙教授",
                "university": "清华大学深圳研究院",
                "department": "先进制造系",
                "title": "副教授",
                "research_fields": ["3D打印", "智能装备", "机器人技术"],
                "personal_page_url": "https://www.sz.tsinghua.edu.cn/faculty/sun",
            },
        ]

        return professors

    def _extract_research_fields(self, research_text: str) -> List[str]:
        """从文本中提取研究方向"""
        if not research_text:
            return []

        # 分割研究方向
        separators = ['；', ';', '、', ',', '，', '，', '/', '|']

        for sep in separators:
            if sep in research_text:
                fields = [f.strip() for f in research_text.split(sep) if f.strip()]
                if len(fields) > 1:
                    return fields

        # 如果没有明显分隔符，尝试按长度分割
        if len(research_text) > 30:
            # 尝试按常见连接词分割
            patterns = [
                r'以及\s*',
                r'还有\s*',
                r'同时\s*',
                r'另外\s*',
                r'涉及\s*',
            ]

            for pattern in patterns:
                if re.search(pattern, research_text):
                    fields = re.split(pattern, research_text)
                    fields = [f.strip() for f in fields if f.strip()]
                    if len(fields) > 1:
                        return fields

        # 如果无法分割，返回整个文本作为一个方向
        return [research_text.strip()]

    async def _fetch_with_selenium(self, url: str, wait_time: int = 10) -> Optional[str]:
        """使用Selenium获取动态页面（如果需要）"""
        if not SELENIUM_AVAILABLE:
            print("警告: selenium 不可用")
            return None

        driver = None
        try:
            # 配置Chrome选项
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # 无头模式
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'user-agent={self.user_agent}')

            driver = webdriver.Chrome(options=options)
            driver.get(url)

            # 等待页面加载
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # 获取页面源码
            html = driver.page_source
            return html

        except Exception as e:
            print(f"Selenium获取页面失败 {url}: {e}")
            return None

        finally:
            if driver:
                driver.quit()