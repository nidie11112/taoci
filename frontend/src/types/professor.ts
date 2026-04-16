/**
 * 导师相关类型定义
 */

// 导师基础信息
export interface ProfessorBase {
  name: string;
  university: string;
  department?: string;
  title?: string;
  researchFields?: string[];
  personalPageUrl?: string;
  email?: string;
  phone?: string;
}

// 创建导师请求
export interface ProfessorCreate extends ProfessorBase {}

// 更新导师请求
export interface ProfessorUpdate {
  name?: string;
  university?: string;
  department?: string;
  title?: string;
  researchFields?: string[];
  personalPageUrl?: string;
  email?: string;
  phone?: string;
}

// 导师响应数据
export interface ProfessorResponse extends ProfessorBase {
  id: number;
  uuid: string;
  createdAt: string;
  updatedAt: string;
  deletedAt?: string;
}

// 导师列表响应
export interface ProfessorListResponse {
  total: number;
  page: number;
  pageSize: number;
  professors: ProfessorResponse[];
}

// 导师搜索参数
export interface ProfessorSearchParams {
  university?: string;
  department?: string;
  title?: string;
  researchField?: string;
  page?: number;
  pageSize?: number;
}

// 导师评价
export interface ProfessorEvaluation {
  id?: number;
  professorId: number;
  source: 'excel' | 'github' | 'manual';
  personalityScore?: number; // 1-5
  groupAtmosphere?: string;
  studentComments?: string;
  evaluationDate?: string;
  createdAt?: string;
}

// 导师论文
export interface AcademicPaper {
  id?: number;
  professorId: number;
  title: string;
  authors?: string[];
  publicationVenue?: string;
  publicationYear?: number;
  abstract?: string;
  keywords?: string[];
  pdfUrl?: string;
  citations?: number;
  createdAt?: string;
}

// 导师统计信息
export interface ProfessorStats {
  professorId: number;
  totalEvaluations: number;
  avgPersonalityScore: number;
  paperCount: number;
  matchCount: number;
  profileCompleteness: number;
}

// 搜索建议项
export interface ProfessorSuggestion {
  id: number;
  name: string;
  university: string;
  department: string;
  title: string;
  researchFields: string[];
}