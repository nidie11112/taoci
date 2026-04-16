/**
 * 匹配相关类型定义
 */

// 匹配基础信息
export interface MatchBase {
  studentId: number;
  professorId: number;
  researchMatchScore?: number; // 0-1
  backgroundMatchScore?: number; // 0-1
  personalityMatchScore?: number; // 0-1
  overallScore?: number; // 0-1
  admissionProbability?: number; // 0-1
  matchReasons?: string;
}

// 创建匹配请求
export interface MatchCreate extends MatchBase {}

// 更新匹配请求
export interface MatchUpdate {
  researchMatchScore?: number;
  backgroundMatchScore?: number;
  personalityMatchScore?: number;
  overallScore?: number;
  admissionProbability?: number;
  matchReasons?: string;
}

// 匹配响应数据
export interface MatchResponse extends MatchBase {
  id: number;
  createdAt: string;
}

// 匹配详情响应（包含学生和导师信息）
export interface MatchDetailResponse extends MatchResponse {
  student: {
    id: number;
    name: string;
    university: string;
    major?: string;
    gpa?: number;
  };
  professor: {
    id: number;
    name: string;
    university: string;
    department?: string;
    title?: string;
    researchFields?: string[];
  };
}

// 匹配列表响应
export interface MatchListResponse {
  total: number;
  page: number;
  pageSize: number;
  matches: MatchResponse[];
}

// 匹配搜索参数
export interface MatchSearchParams {
  studentId?: number;
  professorId?: number;
  minScore?: number; // 0-1
  minProbability?: number; // 0-1
  page?: number;
  pageSize?: number;
}

// 匹配计算请求
export interface MatchCalculateRequest {
  studentId: number;
  professorId: number;
  includeDetails?: boolean;
}

// 匹配计算响应
export interface MatchCalculateResponse {
  success: boolean;
  data?: {
    researchMatchScore: number;
    backgroundMatchScore: number;
    personalityMatchScore: number;
    overallScore: number;
    admissionProbability: number;
    matchReasons: string[];
    detailedAnalysis?: string;
  };
  message?: string;
  error?: string;
}

// 匹配分数分析
export interface MatchScoreAnalysis {
  dimension: string;
  score: number;
  weight: number;
  description: string;
  factors: string[];
}

// 录取概率分析
export interface AdmissionProbabilityAnalysis {
  probability: number;
  confidence: number;
  factors: {
    positive: string[];
    negative: string[];
    neutral: string[];
  };
  recommendations: string[];
}