/**
 * 学生相关类型定义
 */

// 科研经历
export interface ResearchExperience {
  project: string;
  role: string;
  duration: string;
  description: string;
  skillsUsed?: string[];
  outcomes?: string[];
}

// 竞赛获奖
export interface CompetitionAward {
  name: string;
  level: '国家级' | '省级' | '校级' | '其他';
  award: string;
  year: number;
  description?: string;
  organization?: string;
}

// 学生基础信息
export interface StudentBase {
  name: string;
  university: string;
  major?: string;
  gpa?: number;
  gpaRanking?: number;
  skills?: string[];
  resumePdfPath?: string;
}

// 创建学生请求
export interface StudentCreate extends StudentBase {
  researchExperience?: ResearchExperience[];
  competitionAwards?: CompetitionAward[];
}

// 更新学生请求
export interface StudentUpdate {
  name?: string;
  university?: string;
  major?: string;
  gpa?: number;
  gpaRanking?: number;
  skills?: string[];
  researchExperience?: ResearchExperience[];
  competitionAwards?: CompetitionAward[];
  resumePdfPath?: string;
}

// 学生响应数据
export interface StudentResponse extends StudentBase {
  id: number;
  uuid: string;
  researchExperience: ResearchExperience[];
  competitionAwards: CompetitionAward[];
  createdAt: string;
  updatedAt: string;
  deletedAt?: string;
}

// 学生列表响应
export interface StudentListResponse {
  total: number;
  page: number;
  pageSize: number;
  students: StudentResponse[];
}

// 学生匹配记录
export interface StudentMatchRecord {
  id: number;
  studentId: number;
  professorId: number;
  researchMatchScore: number;
  backgroundMatchScore: number;
  personalityMatchScore: number;
  overallScore: number;
  admissionProbability: number;
  matchReasons?: string;
  createdAt: string;
  professor?: {
    id: number;
    name: string;
    university: string;
    department?: string;
    title?: string;
    researchFields?: string[];
  };
}

// 学生简历上传响应
export interface ResumeUploadResponse {
  message: string;
  studentId: number;
  resumePath: string;
}