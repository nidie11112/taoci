"""
Excel数据解析器

用于解析导师评价数据的Excel文件，支持多种格式和来源
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
import logging
import re

logger = logging.getLogger(__name__)


class ExcelParser:
    """Excel数据解析器"""

    # 支持的列名映射（不同来源可能使用不同的列名）
    COLUMN_MAPPINGS = {
        # 导师基本信息
        "name": ["姓名", "导师姓名", "教授姓名", "老师姓名", "name", "professor_name"],
        "university": ["学校", "大学", "高校", "university", "school"],
        "department": ["院系", "学院", "部门", "department", "college"],
        "title": ["职称", "职位", "title", "position"],
        "research_fields": ["研究方向", "研究领域", "研究兴趣", "research_fields", "research_areas"],

        # 评价信息
        "personality_score": ["人品得分", "人品分数", "人品评价", "personality_score", "character_score"],
        "group_atmosphere": ["课题组氛围", "实验室氛围", "团队氛围", "group_atmosphere", "lab_atmosphere"],
        "student_comments": ["学生评价", "学生反馈", "学生评论", "student_comments", "student_feedback"],
        "evaluation_date": ["评价日期", "日期", "时间", "evaluation_date", "date"],

        # 数据来源
        "source": ["来源", "数据来源", "source", "data_source"],
    }

    def __init__(self, file_path: str, sheet_name: Optional[str] = None):
        """初始化Excel解析器

        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称，如果为None则读取第一个工作表
        """
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.df = None
        self.column_mapping = {}

    def load(self) -> bool:
        """加载Excel文件

        Returns:
            是否成功加载
        """
        try:
            if self.sheet_name:
                self.df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
            else:
                self.df = pd.read_excel(self.file_path)

            logger.info(f"成功加载Excel文件: {self.file_path}, 数据形状: {self.df.shape}")
            return True
        except Exception as e:
            logger.error(f"加载Excel文件失败: {e}")
            return False

    def detect_columns(self) -> Dict[str, str]:
        """检测列名映射

        自动识别Excel中的列名并映射到标准列名

        Returns:
            列名映射字典
        """
        if self.df is None:
            return {}

        column_mapping = {}
        actual_columns = list(self.df.columns)

        for standard_name, possible_names in self.COLUMN_MAPPINGS.items():
            for actual_name in actual_columns:
                # 检查列名是否匹配（不区分大小写，支持中文）
                if isinstance(actual_name, str):
                    actual_name_lower = actual_name.lower().strip()
                    for possible_name in possible_names:
                        possible_name_lower = possible_name.lower().strip()
                        if actual_name_lower == possible_name_lower:
                            column_mapping[standard_name] = actual_name
                            break
                    if standard_name in column_mapping:
                        break

        self.column_mapping = column_mapping
        logger.info(f"检测到的列名映射: {column_mapping}")
        return column_mapping

    def parse_row(self, row: pd.Series) -> Dict[str, Any]:
        """解析单行数据

        Args:
            row: pandas Series对象，表示一行数据

        Returns:
            解析后的数据字典
        """
        data = {
            "professor_info": {},
            "evaluation_info": {},
            "source_info": {},
        }

        # 解析导师基本信息
        if "name" in self.column_mapping:
            data["professor_info"]["name"] = str(row[self.column_mapping["name"]]).strip()

        if "university" in self.column_mapping:
            data["professor_info"]["university"] = str(row[self.column_mapping["university"]]).strip()

        if "department" in self.column_mapping:
            dept_value = row[self.column_mapping["department"]]
            if pd.notna(dept_value):
                data["professor_info"]["department"] = str(dept_value).strip()

        if "title" in self.column_mapping:
            title_value = row[self.column_mapping["title"]]
            if pd.notna(title_value):
                data["professor_info"]["title"] = str(title_value).strip()

        # 解析研究方向（可能包含多个研究方向，用逗号、分号或换行分隔）
        if "research_fields" in self.column_mapping:
            research_value = row[self.column_mapping["research_fields"]]
            if pd.notna(research_value):
                research_str = str(research_value).strip()
                # 使用多种分隔符分割研究方向
                research_fields = re.split(r'[,;，；\n]', research_str)
                research_fields = [field.strip() for field in research_fields if field.strip()]
                data["professor_info"]["research_fields"] = research_fields

        # 解析评价信息
        if "personality_score" in self.column_mapping:
            score_value = row[self.column_mapping["personality_score"]]
            if pd.notna(score_value):
                try:
                    # 尝试转换为浮点数
                    score = float(score_value)
                    if 1 <= score <= 5:  # 人品得分通常在1-5分之间
                        data["evaluation_info"]["personality_score"] = score
                except (ValueError, TypeError):
                    pass

        if "group_atmosphere" in self.column_mapping:
            atmosphere_value = row[self.column_mapping["group_atmosphere"]]
            if pd.notna(atmosphere_value):
                data["evaluation_info"]["group_atmosphere"] = str(atmosphere_value).strip()

        if "student_comments" in self.column_mapping:
            comments_value = row[self.column_mapping["student_comments"]]
            if pd.notna(comments_value):
                data["evaluation_info"]["student_comments"] = str(comments_value).strip()

        if "evaluation_date" in self.column_mapping:
            date_value = row[self.column_mapping["evaluation_date"]]
            if pd.notna(date_value):
                try:
                    # 尝试解析日期
                    if isinstance(date_value, (datetime, pd.Timestamp)):
                        data["evaluation_info"]["evaluation_date"] = date_value.date()
                    elif isinstance(date_value, str):
                        # 尝试多种日期格式
                        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
                            try:
                                parsed_date = datetime.strptime(date_value, fmt).date()
                                data["evaluation_info"]["evaluation_date"] = parsed_date
                                break
                            except ValueError:
                                continue
                except Exception as e:
                    logger.warning(f"解析日期失败: {date_value}, 错误: {e}")

        # 解析数据来源
        if "source" in self.column_mapping:
            source_value = row[self.column_mapping["source"]]
            if pd.notna(source_value):
                data["source_info"]["source"] = str(source_value).strip()
        else:
            # 如果没有指定来源，默认使用excel
            data["source_info"]["source"] = "excel"

        return data

    def parse_all(self) -> List[Dict[str, Any]]:
        """解析所有数据

        Returns:
            解析后的数据列表
        """
        if self.df is None:
            logger.error("请先加载Excel文件")
            return []

        # 检测列名映射
        self.detect_columns()

        # 检查必要的列
        required_columns = ["name", "university"]
        missing_columns = [col for col in required_columns if col not in self.column_mapping]

        if missing_columns:
            logger.warning(f"缺少必要的列: {missing_columns}，可能无法正确解析所有数据")

        # 解析每一行
        parsed_data = []
        for idx, row in self.df.iterrows():
            try:
                row_data = self.parse_row(row)
                # 只保留有基本信息的行
                if row_data["professor_info"].get("name") and row_data["professor_info"].get("university"):
                    parsed_data.append(row_data)
                else:
                    logger.warning(f"跳过第 {idx + 1} 行: 缺少必要信息")
            except Exception as e:
                logger.error(f"解析第 {idx + 1} 行失败: {e}")

        logger.info(f"成功解析 {len(parsed_data)} 条数据")
        return parsed_data

    def get_summary(self) -> Dict[str, Any]:
        """获取数据摘要

        Returns:
            数据摘要信息
        """
        if self.df is None:
            return {}

        summary = {
            "file_path": self.file_path,
            "total_rows": len(self.df),
            "columns": list(self.df.columns),
            "column_mapping": self.column_mapping,
            "missing_columns": [],
            "data_types": {},
        }

        # 检查数据列
        required_columns = ["name", "university"]
        summary["missing_columns"] = [col for col in required_columns if col not in self.column_mapping]

        # 获取数据类型信息
        for col in self.df.columns:
            non_null_count = self.df[col].count()
            total_count = len(self.df)
            null_percentage = ((total_count - non_null_count) / total_count * 100) if total_count > 0 else 0

            summary["data_types"][col] = {
                "dtype": str(self.df[col].dtype),
                "non_null_count": non_null_count,
                "null_percentage": round(null_percentage, 2),
                "sample_values": self.df[col].dropna().head(3).tolist() if non_null_count > 0 else [],
            }

        return summary


class ProfessorDataImporter:
    """导师数据导入器（使用Excel解析器）"""

    def __init__(self, excel_parser: ExcelParser):
        self.excel_parser = excel_parser
        self.parsed_data = []

    def import_data(self) -> bool:
        """导入数据

        Returns:
            是否成功导入
        """
        # 加载并解析Excel数据
        if not self.excel_parser.load():
            return False

        self.parsed_data = self.excel_parser.parse_all()
        return len(self.parsed_data) > 0

    def get_professor_records(self) -> List[Dict[str, Any]]:
        """获取导师记录列表

        Returns:
            导师记录列表
        """
        return self.parsed_data

    def transform_to_models(self) -> Tuple[List[Dict], List[Dict]]:
        """将解析的数据转换为数据库模型格式

        Returns:
            (教授数据列表, 评价数据列表)
        """
        professors = []
        evaluations = []

        for data in self.parsed_data:
            # 提取教授信息
            prof_info = data.get("professor_info", {})
            eval_info = data.get("evaluation_info", {})
            source_info = data.get("source_info", {})

            # 创建教授数据
            professor_data = {
                "name": prof_info.get("name", ""),
                "university": prof_info.get("university", ""),
                "department": prof_info.get("department"),
                "title": prof_info.get("title"),
                "research_fields": prof_info.get("research_fields", []),
            }

            # 创建评价数据（如果有）
            evaluation_data = None
            if eval_info:
                evaluation_data = {
                    "source": source_info.get("source", "excel"),
                    "personality_score": eval_info.get("personality_score"),
                    "group_atmosphere": eval_info.get("group_atmosphere"),
                    "student_comments": eval_info.get("student_comments"),
                    "evaluation_date": eval_info.get("evaluation_date"),
                }

            professors.append(professor_data)
            if evaluation_data:
                evaluations.append(evaluation_data)

        return professors, evaluations


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 示例：解析Excel文件
    parser = ExcelParser("path/to/your/excel_file.xlsx")
    if parser.load():
        # 获取数据摘要
        summary = parser.get_summary()
        print("数据摘要:", summary)

        # 解析所有数据
        data = parser.parse_all()
        print(f"解析到 {len(data)} 条数据")

        if data:
            # 转换为模型数据
            importer = ProfessorDataImporter(parser)
            professors, evaluations = importer.transform_to_models()
            print(f"教授数据: {len(professors)} 条")
            print(f"评价数据: {len(evaluations)} 条")