"""
匹配服务

实现导师与学生智能匹配的核心算法
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba
import jieba.analyse

# 尝试导入sentence-transformers，如果未安装则使用TF-IDF作为备选
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False
    print("警告: sentence-transformers 未安装，将使用TF-IDF进行文本相似度计算")


@dataclass
class MatchResult:
    """匹配结果"""
    research_match_score: float
    background_match_score: float
    personality_match_score: float
    overall_score: float
    admission_probability: float
    match_reasons: str
    details: Dict[str, Any]


class MatchingService:
    """匹配服务类"""

    def __init__(self):
        """初始化匹配服务"""
        self.vectorizer = TfidfVectorizer(max_features=1000)

        # 初始化中文分词器
        jieba.initialize()

        # 加载sentence-transformers模型（如果可用）
        self.sentence_model = None
        if SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                self.sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            except Exception as e:
                print(f"警告: 无法加载sentence-transformers模型: {e}")
                self.sentence_model = None

        # 院校层级映射（简化版）
        self.university_tiers = {
            "清华大学": 1, "北京大学": 1,
            "上海交通大学": 2, "复旦大学": 2, "浙江大学": 2, "南京大学": 2,
            "西安交通大学": 2, "哈尔滨工业大学": 2, "华中科技大学": 2,
            # 其他985院校
            "同济大学": 3, "武汉大学": 3, "中山大学": 3, "四川大学": 3,
            # 211院校
            "北京航空航天大学": 4, "北京理工大学": 4, "南开大学": 4,
            # 普通一本
            "default": 5
        }

        # 研究方向关键词映射
        self.research_keywords = {
            "力学": ["力学", "固体力学", "流体力学", "材料力学", "结构力学", "计算力学", "实验力学"],
            "机械": ["机械", "机械工程", "机械设计", "制造", "自动化", "机器人", "机电"],
            "材料": ["材料", "复合材料", "智能材料", "功能材料", "纳米材料", "高分子", "金属材料"],
            "智能制造": ["智能制造", "数字化", "工业4.0", "智能工厂", "物联网", "大数据", "人工智能"],
            "航空航天": ["航空航天", "飞行器", "航空发动机", "航天器", "空气动力学"],
            "土木": ["土木", "结构工程", "桥梁", "隧道", "岩土工程", "建筑工程"],
            "能源": ["能源", "动力工程", "热能", "新能源", "可再生能源", "储能"],
        }

    def calculate_research_similarity(
        self,
        student_interests: List[str],
        professor_fields: List[str],
        professor_papers: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        """计算研究方向相似度

        Args:
            student_interests: 学生研究方向列表
            professor_fields: 导师研究方向列表
            professor_papers: 导师论文列表（可选）

        Returns:
            相似度得分 (0-1)
        """
        if not student_interests or not professor_fields:
            return 0.0

        # 1. 关键词匹配（精确匹配）
        student_keywords = self._extract_keywords(student_interests)
        professor_keywords = self._extract_keywords(professor_fields)

        # 计算Jaccard相似度
        if not student_keywords or not professor_keywords:
            keyword_similarity = 0.0
        else:
            intersection = set(student_keywords) & set(professor_keywords)
            union = set(student_keywords) | set(professor_keywords)
            keyword_similarity = len(intersection) / len(union) if union else 0.0

        # 2. 文本相似度（基于论文摘要）
        text_similarity = 0.0
        if professor_papers and self.sentence_model:
            # 使用sentence-transformers计算文本相似度
            paper_abstracts = []
            for paper in professor_papers:
                if paper.get("abstract"):
                    # 清理摘要文本
                    abstract = self._clean_text(paper["abstract"])
                    if abstract:
                        paper_abstracts.append(abstract)

            if paper_abstracts and student_interests:
                # 将学生兴趣连接为文本
                student_text = " ".join(student_interests)
                student_text = self._clean_text(student_text)

                if student_text and paper_abstracts:
                    # 计算平均相似度
                    try:
                        # 编码文本
                        student_embedding = self.sentence_model.encode([student_text])
                        paper_embeddings = self.sentence_model.encode(paper_abstracts)

                        # 计算余弦相似度
                        similarities = cosine_similarity(student_embedding, paper_embeddings)
                        text_similarity = float(np.max(similarities))  # 取最高相似度
                    except Exception as e:
                        print(f"文本相似度计算错误: {e}")
                        text_similarity = 0.0
        elif professor_papers:
            # 使用TF-IDF作为备选
            text_similarity = self._calculate_tfidf_similarity(student_interests, professor_papers)

        # 3. 综合得分（加权平均）
        # 关键词匹配权重60%，文本相似度权重40%
        similarity_score = 0.6 * keyword_similarity + 0.4 * text_similarity

        # 确保得分在0-1范围内
        return max(0.0, min(1.0, similarity_score))

    def calculate_background_similarity(
        self,
        student: Dict[str, Any],
        professor: Dict[str, Any]
    ) -> float:
        """计算背景匹配度

        Args:
            student: 学生信息字典
            professor: 导师信息字典

        Returns:
            背景匹配度得分 (0-1)
        """
        scores = []

        # 1. 院校层级匹配（权重40%）
        university_score = self._calculate_university_score(student, professor)
        scores.append(("university", university_score, 0.4))

        # 2. 成绩匹配（权重30%）
        gpa_score = self._calculate_gpa_score(student)
        scores.append(("gpa", gpa_score, 0.3))

        # 3. 科研经历匹配（权重20%）
        research_exp_score = self._calculate_research_experience_score(student, professor)
        scores.append(("research_exp", research_exp_score, 0.2))

        # 4. 竞赛获奖匹配（权重10%）
        competition_score = self._calculate_competition_score(student)
        scores.append(("competition", competition_score, 0.1))

        # 计算加权平均
        total_score = 0.0
        total_weight = 0.0
        for name, score, weight in scores:
            total_score += score * weight
            total_weight += weight

        background_score = total_score / total_weight if total_weight > 0 else 0.0

        return max(0.0, min(1.0, background_score))

    def calculate_personality_similarity(
        self,
        student_personality: Optional[Dict[str, Any]],
        professor_evaluations: Optional[List[Dict[str, Any]]]
    ) -> float:
        """计算性格/课题组文化匹配度

        Args:
            student_personality: 学生性格描述（可选）
            professor_evaluations: 导师评价列表（可选）

        Returns:
            性格匹配度得分 (0-1)
        """
        # 如果没有评价数据，返回默认值
        if not professor_evaluations:
            return 0.5  # 中等匹配度

        # 计算平均人品得分
        total_score = 0.0
        valid_count = 0

        for evaluation in professor_evaluations:
            score = evaluation.get("personality_score")
            if score is not None:
                total_score += score
                valid_count += 1

        if valid_count == 0:
            avg_personality_score = 3.0  # 默认中等分数
        else:
            avg_personality_score = total_score / valid_count

        # 将1-5分转换为0-1分
        personality_score = (avg_personality_score - 1) / 4

        # 如果有学生性格描述，可以进行更复杂的匹配
        # 这里简化处理
        if student_personality:
            # 简化的性格匹配逻辑
            # 实际应用中可以使用更复杂的NLP分析
            pass

        return max(0.0, min(1.0, personality_score))

    def calculate_overall_score(
        self,
        research_score: float,
        background_score: float,
        personality_score: float,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """计算综合匹配度

        Args:
            research_score: 研究方向匹配度
            background_score: 背景匹配度
            personality_score: 性格匹配度
            weights: 各维度权重（可选）

        Returns:
            综合匹配度得分 (0-1)
        """
        if weights is None:
            # 默认权重：研究方向40%，背景30%，性格30%
            weights = {
                "research": 0.4,
                "background": 0.3,
                "personality": 0.3
            }

        total_score = (
            research_score * weights["research"] +
            background_score * weights["background"] +
            personality_score * weights["personality"]
        )

        return max(0.0, min(1.0, total_score))

    def predict_admission_probability(
        self,
        student: Dict[str, Any],
        professor: Dict[str, Any],
        match_scores: Dict[str, float],
        historical_data: Optional[Dict[str, Any]] = None
    ) -> float:
        """预测录取概率

        Args:
            student: 学生信息
            professor: 导师信息
            match_scores: 匹配度分数
            historical_data: 历史录取数据（可选）

        Returns:
            录取概率 (0-1)
        """
        # 基础概率（基于综合匹配度）
        base_probability = match_scores.get("overall_score", 0.5)

        # 调整因子
        adjustment_factors = []

        # 1. 院校层级差异调整
        university_adjustment = self._calculate_university_adjustment(student, professor)
        adjustment_factors.append(("university", university_adjustment, 0.3))

        # 2. 成绩调整
        gpa_adjustment = self._calculate_gpa_adjustment(student)
        adjustment_factors.append(("gpa", gpa_adjustment, 0.2))

        # 3. 科研经历调整
        research_adjustment = self._calculate_research_adjustment(student, professor)
        adjustment_factors.append(("research", research_adjustment, 0.25))

        # 4. 导师热门程度调整（简化：基于评价数量）
        professor_adjustment = self._calculate_professor_adjustment(professor)
        adjustment_factors.append(("professor", professor_adjustment, 0.25))

        # 计算加权调整
        total_adjustment = 0.0
        total_weight = 0.0
        for name, adjustment, weight in adjustment_factors:
            total_adjustment += adjustment * weight
            total_weight += weight

        if total_weight > 0:
            average_adjustment = total_adjustment / total_weight
        else:
            average_adjustment = 0.0

        # 应用调整
        probability = base_probability * (1 + average_adjustment)

        # 使用历史数据微调（如果有）
        if historical_data:
            probability = self._adjust_with_historical_data(probability, historical_data)

        # 确保概率在0-1范围内
        return max(0.0, min(1.0, probability))

    def generate_match_reasons(
        self,
        student: Dict[str, Any],
        professor: Dict[str, Any],
        match_scores: Dict[str, float]
    ) -> str:
        """生成匹配原因分析

        Args:
            student: 学生信息
            professor: 导师信息
            match_scores: 匹配度分数

        Returns:
            匹配原因分析文本
        """
        reasons = []

        # 研究方向匹配原因
        research_score = match_scores.get("research_match_score", 0)
        if research_score >= 0.8:
            reasons.append("研究方向高度匹配")
        elif research_score >= 0.6:
            reasons.append("研究方向有一定重合")
        else:
            reasons.append("研究方向匹配度一般")

        # 背景匹配原因
        background_score = match_scores.get("background_match_score", 0)
        if background_score >= 0.8:
            reasons.append("背景契合度高")
        elif background_score >= 0.6:
            reasons.append("背景基本相符")
        else:
            reasons.append("背景匹配度有待提升")

        # 性格匹配原因
        personality_score = match_scores.get("personality_match_score", 0)
        if personality_score >= 0.8:
            reasons.append("性格/课题组文化匹配良好")
        elif personality_score >= 0.6:
            reasons.append("性格匹配度中等")
        else:
            reasons.append("性格匹配度需进一步了解")

        # 具体分析
        details = []

        # 院校分析
        student_university = student.get("university", "")
        professor_university = professor.get("university", "")
        if student_university and professor_university:
            if student_university == professor_university:
                details.append("同校背景可能增加录取机会")
            elif self._get_university_tier(student_university) <= self._get_university_tier(professor_university) + 1:
                details.append("院校层级差异在合理范围内")
            else:
                details.append("院校层级差异较大，需突出个人优势")

        # 研究方向具体匹配点
        student_interests = student.get("research_interests", []) or student.get("skills", [])
        professor_fields = professor.get("research_fields", [])
        if student_interests and professor_fields:
            common_interests = set(student_interests) & set(professor_fields)
            if common_interests:
                details.append(f"共同研究方向: {', '.join(list(common_interests)[:3])}")

        # 构建最终文本
        if reasons:
            main_reason = "；".join(reasons) + "。"
        else:
            main_reason = "匹配度分析完成。"

        if details:
            detail_text = "具体分析：" + "；".join(details) + "。"
        else:
            detail_text = ""

        return main_reason + detail_text

    def match_student_professor(
        self,
        student: Dict[str, Any],
        professor: Dict[str, Any],
        professor_papers: Optional[List[Dict[str, Any]]] = None,
        professor_evaluations: Optional[List[Dict[str, Any]]] = None
    ) -> MatchResult:
        """匹配学生和导师

        Args:
            student: 学生信息
            professor: 导师信息
            professor_papers: 导师论文列表（可选）
            professor_evaluations: 导师评价列表（可选）

        Returns:
            匹配结果
        """
        # 提取学生研究方向
        student_interests = []
        if student.get("research_interests"):
            student_interests.extend(student["research_interests"])
        if student.get("skills"):
            student_interests.extend(student["skills"])

        # 1. 计算研究方向匹配度
        research_score = self.calculate_research_similarity(
            student_interests=student_interests,
            professor_fields=professor.get("research_fields", []),
            professor_papers=professor_papers
        )

        # 2. 计算背景匹配度
        background_score = self.calculate_background_similarity(student, professor)

        # 3. 计算性格匹配度
        personality_score = self.calculate_personality_similarity(
            student_personality=student.get("personality"),
            professor_evaluations=professor_evaluations
        )

        # 4. 计算综合匹配度
        overall_score = self.calculate_overall_score(research_score, background_score, personality_score)

        # 5. 预测录取概率
        match_scores = {
            "research_match_score": research_score,
            "background_match_score": background_score,
            "personality_match_score": personality_score,
            "overall_score": overall_score
        }

        admission_probability = self.predict_admission_probability(
            student=student,
            professor=professor,
            match_scores=match_scores
        )

        # 6. 生成匹配原因
        match_reasons = self.generate_match_reasons(student, professor, match_scores)

        # 7. 构建结果
        return MatchResult(
            research_match_score=research_score,
            background_match_score=background_score,
            personality_match_score=personality_score,
            overall_score=overall_score,
            admission_probability=admission_probability,
            match_reasons=match_reasons,
            details={
                "student_interests": student_interests,
                "professor_fields": professor.get("research_fields", []),
                "university_comparison": self._compare_universities(
                    student.get("university"), professor.get("university")
                ),
                "score_breakdown": {
                    "research": research_score,
                    "background": background_score,
                    "personality": personality_score,
                    "overall": overall_score
                }
            }
        )

    # ==================== 私有方法 ====================

    def _extract_keywords(self, texts: List[str]) -> List[str]:
        """从文本列表中提取关键词"""
        keywords = []
        for text in texts:
            if not text:
                continue

            # 使用jieba提取关键词
            try:
                # 提取前5个关键词
                extracted = jieba.analyse.extract_tags(text, topK=5)
                keywords.extend(extracted)
            except Exception:
                # 如果jieba失败，使用简单分割
                words = re.findall(r'[\w\u4e00-\u9fff]+', text)
                keywords.extend(words)

        # 去重
        return list(set(keywords))

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""

        # 移除特殊字符和多余空格
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\u4e00-\u9fff\s]', ' ', text)
        return text.strip()

    def _calculate_tfidf_similarity(
        self,
        student_interests: List[str],
        professor_papers: List[Dict[str, Any]]
    ) -> float:
        """使用TF-IDF计算文本相似度"""
        try:
            # 准备文本
            texts = []
            for paper in professor_papers:
                if paper.get("abstract"):
                    texts.append(self._clean_text(paper["abstract"]))

            if not texts or not student_interests:
                return 0.0

            # 学生兴趣作为查询文本
            query_text = " ".join(student_interests)
            query_text = self._clean_text(query_text)

            # 将所有文本合并
            all_texts = texts + [query_text]

            # 计算TF-IDF
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)

            # 计算查询文本与所有论文的相似度
            query_vector = tfidf_matrix[-1]
            paper_vectors = tfidf_matrix[:-1]

            similarities = cosine_similarity(query_vector, paper_vectors)
            max_similarity = float(np.max(similarities))

            return max_similarity
        except Exception as e:
            print(f"TF-IDF相似度计算错误: {e}")
            return 0.0

    def _calculate_university_score(
        self,
        student: Dict[str, Any],
        professor: Dict[str, Any]
    ) -> float:
        """计算院校层级匹配分数"""
        student_university = student.get("university", "")
        professor_university = professor.get("university", "")

        if not student_university or not professor_university:
            return 0.5

        student_tier = self._get_university_tier(student_university)
        professor_tier = self._get_university_tier(professor_university)

        # 计算层级差异
        tier_diff = professor_tier - student_tier

        # 转换为分数：差异越小，分数越高
        if tier_diff <= 0:  # 学生院校更好或同级
            return 1.0
        elif tier_diff == 1:
            return 0.8
        elif tier_diff == 2:
            return 0.6
        elif tier_diff == 3:
            return 0.4
        else:
            return 0.2

    def _get_university_tier(self, university_name: str) -> int:
        """获取院校层级"""
        # 尝试精确匹配
        for name, tier in self.university_tiers.items():
            if name in university_name:
                return tier

        # 尝试模糊匹配
        for name, tier in self.university_tiers.items():
            if name[:2] in university_name:
                return tier

        # 默认层级
        return self.university_tiers.get("default", 5)

    def _calculate_gpa_score(self, student: Dict[str, Any]) -> float:
        """计算GPA分数"""
        gpa = student.get("gpa")
        if gpa is None:
            return 0.5

        # 将GPA转换为0-1分数（假设4.0满分）
        if gpa >= 3.8:
            return 1.0
        elif gpa >= 3.5:
            return 0.8
        elif gpa >= 3.2:
            return 0.6
        elif gpa >= 3.0:
            return 0.4
        else:
            return 0.2

    def _calculate_research_experience_score(
        self,
        student: Dict[str, Any],
        professor: Dict[str, Any]
    ) -> float:
        """计算科研经历匹配分数"""
        research_experience = student.get("research_experience", [])
        if not research_experience:
            return 0.3

        # 检查研究方向相关性
        professor_fields = professor.get("research_fields", [])
        if not professor_fields:
            return 0.5

        # 简化计算：有科研经历即给基础分，研究方向相关则加分
        base_score = 0.5
        relevance_bonus = 0.0

        # 检查学生科研经历是否与导师研究方向相关
        for exp in research_experience:
            if isinstance(exp, dict):
                project = exp.get("project", "")
                if project:
                    # 简单关键词匹配
                    for field in professor_fields:
                        if field in project:
                            relevance_bonus += 0.1

        # 限制加分上限
        relevance_bonus = min(relevance_bonus, 0.5)

        return min(1.0, base_score + relevance_bonus)

    def _calculate_competition_score(self, student: Dict[str, Any]) -> float:
        """计算竞赛获奖分数"""
        competitions = student.get("competition_awards", [])
        if not competitions:
            return 0.3

        # 计算获奖级别分数
        total_score = 0.0
        for comp in competitions:
            if isinstance(comp, dict):
                level = comp.get("level", "")
                award = comp.get("award", "")

                # 国家级奖项
                if "国家" in level or "全国" in level:
                    if "一等奖" in award:
                        total_score += 1.0
                    elif "二等奖" in award:
                        total_score += 0.8
                    elif "三等奖" in award:
                        total_score += 0.6
                # 省级奖项
                elif "省" in level:
                    if "一等奖" in award:
                        total_score += 0.7
                    elif "二等奖" in award:
                        total_score += 0.5
                    elif "三等奖" in award:
                        total_score += 0.3
                # 校级奖项
                elif "校" in level:
                    total_score += 0.2

        # 归一化到0-1
        avg_score = total_score / len(competitions) if competitions else 0
        return min(1.0, avg_score)

    def _calculate_university_adjustment(
        self,
        student: Dict[str, Any],
        professor: Dict[str, Any]
    ) -> float:
        """计算院校层级调整因子"""
        student_university = student.get("university", "")
        professor_university = professor.get("university", "")

        if not student_university or not professor_university:
            return 0.0

        student_tier = self._get_university_tier(student_university)
        professor_tier = self._get_university_tier(professor_university)

        # 调整因子：学生院校比导师院校每高一级，概率增加10%
        # 每低一级，概率减少10%（但最多减少30%）
        tier_diff = professor_tier - student_tier

        if tier_diff < 0:  # 学生院校更好
            return min(0.3, abs(tier_diff) * 0.1)
        elif tier_diff > 0:  # 学生院校较差
            return max(-0.3, -tier_diff * 0.1)
        else:  # 同级
            return 0.0

    def _calculate_gpa_adjustment(self, student: Dict[str, Any]) -> float:
        """计算GPA调整因子"""
        gpa = student.get("gpa")
        if gpa is None:
            return 0.0

        # GPA调整：3.8以上+20%，3.5-3.8+10%，3.0-3.5+0%，3.0以下-10%
        if gpa >= 3.8:
            return 0.2
        elif gpa >= 3.5:
            return 0.1
        elif gpa >= 3.0:
            return 0.0
        else:
            return -0.1

    def _calculate_research_adjustment(
        self,
        student: Dict[str, Any],
        professor: Dict[str, Any]
    ) -> float:
        """计算科研经历调整因子"""
        research_experience = student.get("research_experience", [])
        if not research_experience:
            return -0.1  # 无科研经历，略微降低概率

        # 检查相关性
        professor_fields = professor.get("research_fields", [])
        if not professor_fields:
            return 0.0

        # 计算相关科研经历数量
        relevant_count = 0
        for exp in research_experience:
            if isinstance(exp, dict):
                project = exp.get("project", "")
                if project:
                    for field in professor_fields:
                        if field in project:
                            relevant_count += 1
                            break

        # 调整：每项相关经历+5%，最多+20%
        adjustment = min(0.2, relevant_count * 0.05)
        return adjustment

    def _calculate_professor_adjustment(self, professor: Dict[str, Any]) -> float:
        """计算导师热门程度调整因子"""
        # 简化：基于导师是否热门（这里假设所有导师同等）
        # 实际可以根据评价数量、论文数量等判断
        return 0.0

    def _adjust_with_historical_data(
        self,
        probability: float,
        historical_data: Dict[str, Any]
    ) -> float:
        """使用历史数据调整概率"""
        # 简化实现：基于历史成功率调整
        historical_success_rate = historical_data.get("success_rate", 0.5)

        # 如果历史成功率与当前概率差异较大，向历史数据靠拢（权重0.3）
        adjusted = probability * 0.7 + historical_success_rate * 0.3

        return adjusted

    def _compare_universities(
        self,
        student_university: Optional[str],
        professor_university: Optional[str]
    ) -> Dict[str, Any]:
        """比较学生和导师的院校"""
        if not student_university or not professor_university:
            return {"comparison": "无法比较", "tier_diff": 0}

        student_tier = self._get_university_tier(student_university)
        professor_tier = self._get_university_tier(professor_university)
        tier_diff = professor_tier - student_tier

        if tier_diff < 0:
            comparison = f"学生院校({student_university})优于导师院校({professor_university})"
        elif tier_diff > 0:
            comparison = f"导师院校({professor_university})优于学生院校({student_university})"
        else:
            comparison = f"学生院校({student_university})与导师院校({professor_university})同级"

        return {
            "comparison": comparison,
            "tier_diff": tier_diff,
            "student_tier": student_tier,
            "professor_tier": professor_tier
        }