"""
PDF简历解析器

用于从PDF格式的简历中提取学生信息
支持中英文简历解析
"""

import pdfplumber
import re
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PDFResumeParser:
    """PDF简历解析器"""

    # 常见字段的关键词（中英文）
    FIELD_KEYWORDS = {
        "name": ["姓名", "名字", "name", "full name", "姓名：", "name:"],
        "university": ["学校", "大学", "院校", "university", "college", "school", "学校：", "university:"],
        "major": ["专业", "主修专业", "专业方向", "major", "专业：", "major:"],
        "gpa": ["gpa", "绩点", "平均成绩", "平均绩点", "gpa：", "绩点：", "gpa:", "grade point average"],
        "ranking": ["排名", "专业排名", "排名情况", "ranking", "rank", "排名：", "ranking:"],
        "contact": ["电话", "手机", "联系方式", "contact", "phone", "电话：", "phone:"],
        "email": ["邮箱", "电子邮件", "email", "电子邮箱", "邮箱：", "email:"],
        "skills": ["技能", "专业技能", "技术技能", "skills", "technical skills", "技能：", "skills:"],
        "experience": ["经历", "经验", "项目经历", "科研经历", "experience", "research experience", "经历：", "experience:"],
        "awards": ["奖项", "获奖", "荣誉", "奖励", "awards", "honors", "奖项：", "awards:"],
    }

    # 常见技能关键词
    SKILL_KEYWORDS = [
        "python", "java", "c++", "c#", "javascript", "html", "css", "react", "vue",
        "机器学习", "深度学习", "人工智能", "数据分析", "数据挖掘",
        "matlab", "ansys", "abaqus", "solidworks", "autocad",
        "英语", "日语", "德语", "法语", "cet-4", "cet-6", "托福", "雅思"
    ]

    def __init__(self, pdf_path: str):
        """初始化PDF解析器

        Args:
            pdf_path: PDF文件路径
        """
        self.pdf_path = pdf_path
        self.text_content = ""
        self.pages = []

    def extract_text(self) -> bool:
        """提取PDF文本内容

        Returns:
            是否成功提取
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                self.pages = pdf.pages
                # 提取所有页面的文本
                text_parts = []
                for i, page in enumerate(self.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                        logger.debug(f"第 {i + 1} 页文本长度: {len(page_text)}")

                self.text_content = "\n".join(text_parts)
                logger.info(f"成功提取PDF文本，总长度: {len(self.text_content)} 字符")
                return True
        except Exception as e:
            logger.error(f"提取PDF文本失败: {e}")
            return False

    def clean_text(self, text: str) -> str:
        """清理文本内容

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        # 去除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        # 标准化换行符
        text = re.sub(r'\n+', '\n', text)
        # 去除特殊字符（保留中英文、数字和常见标点）
        text = re.sub(r'[^\w\u4e00-\u9fff\s.,，。;；:：!！?？()（）\[\]【】\-]', ' ', text)
        return text.strip()

    def find_field(self, field_name: str, text: str) -> Optional[str]:
        """查找特定字段的值

        Args:
            field_name: 字段名
            text: 要搜索的文本

        Returns:
            字段值，如果未找到则返回None
        """
        if field_name not in self.FIELD_KEYWORDS:
            return None

        keywords = self.FIELD_KEYWORDS[field_name]
        text_lower = text.lower()

        # 查找字段标签
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # 使用正则表达式匹配字段标签和后面的值
            pattern = rf'{re.escape(keyword_lower)}\s*[:：]?\s*([^\n]+)'
            match = re.search(pattern, text_lower)

            if match:
                # 提取值并清理
                value = match.group(1).strip()
                # 去除可能的标点符号
                value = re.sub(r'^[:：\s]*', '', value)
                value = re.sub(r'[,，;；.]$', '', value)
                return value

        return None

    def extract_gpa(self, text: str) -> Optional[float]:
        """提取GPA值

        Args:
            text: 要搜索的文本

        Returns:
            GPA数值，如果未找到则返回None
        """
        # 查找GPA字段
        gpa_text = self.find_field("gpa", text)
        if gpa_text:
            # 尝试从文本中提取数字
            gpa_patterns = [
                r'(\d+\.\d+)',  # 小数格式：3.85
                r'(\d+/\d+)',   # 分数格式：3.8/4.0
                r'(\d+)\s*分',   # 中文格式：3.8分
            ]

            for pattern in gpa_patterns:
                match = re.search(pattern, gpa_text)
                if match:
                    try:
                        value = match.group(1)
                        # 处理分数格式
                        if '/' in value:
                            parts = value.split('/')
                            if len(parts) == 2:
                                numerator = float(parts[0])
                                denominator = float(parts[1])
                                if denominator > 0:
                                    return round(numerator / denominator * 4.0, 2)
                        else:
                            gpa = float(value)
                            # 如果GPA值看起来合理（通常在0-5或0-4之间）
                            if 0 <= gpa <= 5:
                                return gpa
                    except (ValueError, ZeroDivisionError):
                        continue

        # 如果没有明确找到GPA字段，尝试在整个文本中搜索GPA模式
        gpa_patterns = [
            r'gpa\s*[:：]?\s*(\d+\.\d+)',
            r'绩点\s*[:：]?\s*(\d+\.\d+)',
            r'(\d+\.\d+)\s*/\s*\d+\.\d+\s*\(gpa\)',
        ]

        for pattern in gpa_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    gpa = float(match.group(1))
                    if 0 <= gpa <= 5:
                        return gpa
                except ValueError:
                    continue

        return None

    def extract_ranking(self, text: str) -> Optional[int]:
        """提取专业排名

        Args:
            text: 要搜索的文本

        Returns:
            排名数值，如果未找到则返回None
        """
        # 查找排名字段
        rank_text = self.find_field("ranking", text)
        if rank_text:
            # 尝试提取数字
            rank_patterns = [
                r'(\d+)\s*/',      # 格式：10/100
                r'(\d+)\s*名',      # 格式：第10名
                r'(\d+)\s*位',      # 格式：第10位
                r'前\s*(\d+)',      # 格式：前10
                r'top\s*(\d+)',     # 格式：top 10
            ]

            for pattern in rank_patterns:
                match = re.search(pattern, rank_text)
                if match:
                    try:
                        return int(match.group(1))
                    except ValueError:
                        continue

        # 在整个文本中搜索排名模式
        rank_patterns = [
            r'(\d+)\s*/\s*\d+\s*\(rank\)',
            r'排名\s*[:：]?\s*(\d+)\s*/\s*\d+',
            r'专业排名\s*[:：]?\s*(\d+)',
        ]

        for pattern in rank_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue

        return None

    def extract_skills(self, text: str) -> List[str]:
        """提取技能列表

        Args:
            text: 要搜索的文本

        Returns:
            技能列表
        """
        # 查找技能字段
        skills_text = self.find_field("skills", text)
        all_skills_text = skills_text or text

        # 从技能文本中提取关键词
        found_skills = []
        text_lower = all_skills_text.lower()

        for skill in self.SKILL_KEYWORDS:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        # 如果没有找到特定技能，尝试提取技能列表
        if not found_skills:
            # 查找常见的技能列表格式（以逗号、分号或换行分隔）
            skill_patterns = [
                r'[:：]\s*([^。，；\n]+)',  # 冒号后的内容
                r'[：:]\s*((?:\w+[，,；;]?\s*)+)',  # 冒号后的多个单词
            ]

            for pattern in skill_patterns:
                matches = re.findall(pattern, all_skills_text)
                for match in matches:
                    # 分割技能
                    skills = re.split(r'[，,;；、\s]+', match)
                    found_skills.extend([s.strip() for s in skills if s.strip()])

        # 去重并清理
        unique_skills = []
        for skill in found_skills:
            skill_clean = skill.strip().lower()
            if skill_clean and skill_clean not in unique_skills:
                unique_skills.append(skill_clean)

        return unique_skills

    def extract_experience(self, text: str) -> List[str]:
        """提取科研经历

        Args:
            text: 要搜索的文本

        Returns:
            科研经历列表
        """
        experiences = []

        # 查找经历字段
        exp_text = self.find_field("experience", text)
        all_exp_text = exp_text or text

        # 尝试分割不同的经历
        # 常见分隔符：项目符号、数字编号、换行等
        exp_patterns = [
            r'[•·\-]\s*([^\n•·\-]+)',  # 项目符号
            r'\d+[\.\)]\s*([^\n]+)',   # 数字编号
            r'[一二三四五六七八九十]+[\.、]\s*([^\n]+)',  # 中文编号
        ]

        for pattern in exp_patterns:
            matches = re.findall(pattern, all_exp_text)
            for match in matches:
                exp = match.strip()
                if exp and len(exp) > 10:  # 只保留有内容的经历
                    experiences.append(exp)

        # 如果没有找到结构化内容，尝试提取段落
        if not experiences:
            # 查找包含关键词的段落
            exp_keywords = ["项目", "研究", "实验", "参与", "负责", "开发", "实现", "设计"]
            lines = all_exp_text.split('\n')
            for line in lines:
                line_clean = line.strip()
                if any(keyword in line_clean for keyword in exp_keywords) and len(line_clean) > 20:
                    experiences.append(line_clean)

        return experiences[:10]  # 最多返回10条经历

    def extract_awards(self, text: str) -> List[str]:
        """提取获奖情况

        Args:
            text: 要搜索的文本

        Returns:
            获奖列表
        """
        awards = []

        # 查找奖项字段
        awards_text = self.find_field("awards", text)
        all_awards_text = awards_text or text

        # 提取奖项
        award_patterns = [
            r'[•·\-]\s*([^\n•·\-]+)',  # 项目符号
            r'\d+[\.\)]\s*([^\n]+)',   # 数字编号
            r'获奖[：:]\s*([^\n]+)',    # 获奖标签
        ]

        for pattern in award_patterns:
            matches = re.findall(pattern, all_awards_text)
            for match in matches:
                award = match.strip()
                if award and any(keyword in award.lower() for keyword in ["奖", "award", "honor", "scholarship"]):
                    awards.append(award)

        return awards[:10]  # 最多返回10个奖项

    def parse(self) -> Dict[str, Any]:
        """解析PDF简历

        Returns:
            解析后的学生信息字典
        """
        # 提取文本
        if not self.extract_text():
            return {"error": "无法提取PDF文本"}

        # 清理文本
        clean_text = self.clean_text(self.text_content)

        # 提取各个字段
        student_info = {
            "name": self.find_field("name", clean_text),
            "university": self.find_field("university", clean_text),
            "major": self.find_field("major", clean_text),
            "gpa": self.extract_gpa(clean_text),
            "gpa_ranking": self.extract_ranking(clean_text),
            "contact": self.find_field("contact", clean_text),
            "email": self.find_field("email", clean_text),
            "skills": self.extract_skills(clean_text),
            "research_experience": self.extract_experience(clean_text),
            "competition_awards": self.extract_awards(clean_text),
            "resume_pdf_path": self.pdf_path,
            "parsed_at": datetime.now().isoformat(),
            "text_length": len(clean_text),
        }

        # 清理空值
        student_info = {k: v for k, v in student_info.items() if v not in [None, "", []]}

        logger.info(f"成功解析简历: {student_info.get('name')}, 提取字段数: {len(student_info)}")
        return student_info

    def get_text_segments(self) -> Dict[str, str]:
        """获取文本分段（用于调试）

        Returns:
            文本分段字典
        """
        if not self.text_content:
            self.extract_text()

        segments = {}
        lines = self.text_content.split('\n')

        # 尝试识别不同部分
        section_keywords = {
            "personal_info": ["姓名", "联系", "电话", "邮箱", "个人信息"],
            "education": ["教育", "学校", "学历", "专业", "gpa"],
            "skills": ["技能", "技术", "能力", "语言"],
            "experience": ["经历", "经验", "项目", "工作", "实习"],
            "awards": ["奖项", "荣誉", "奖励", "获奖", "证书"],
        }

        current_section = "other"
        section_text = []

        for line in lines:
            line_lower = line.lower()
            # 检查是否为新的部分标题
            for section, keywords in section_keywords.items():
                if any(keyword in line_lower for keyword in keywords) and len(line) < 50:
                    # 保存当前部分
                    if section_text:
                        segments[current_section] = "\n".join(section_text)
                    # 开始新部分
                    current_section = section
                    section_text = [line]
                    break
            else:
                # 如果不是标题，添加到当前部分
                section_text.append(line)

        # 保存最后一部分
        if section_text:
            segments[current_section] = "\n".join(section_text)

        return segments


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 示例：解析PDF简历
    parser = PDFResumeParser("path/to/your/resume.pdf")
    student_info = parser.parse()

    print("解析结果:")
    for key, value in student_info.items():
        if isinstance(value, list):
            print(f"{key}: {len(value)} 项")
            for item in value[:3]:  # 只显示前3项
                print(f"  - {item}")
            if len(value) > 3:
                print(f"  ... 还有 {len(value) - 3} 项")
        else:
            print(f"{key}: {value}")

    # 获取文本分段（用于调试）
    segments = parser.get_text_segments()
    print(f"\n文本分段: {list(segments.keys())}")