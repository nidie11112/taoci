/**
 * 文书相关类型定义
 */

// 文书模板变量定义
export interface TemplateVariable {
  [key: string]: string; // 变量名: 变量描述
}

// 文书模板基础信息
export interface DocumentTemplateBase {
  name: string;
  category: '通用' | '力学' | '机械' | '智能制造' | '其他';
  contentTemplate: string;
  variables?: TemplateVariable;
}

// 创建文书模板请求
export interface DocumentTemplateCreate extends DocumentTemplateBase {}

// 更新文书模板请求
export interface DocumentTemplateUpdate {
  name?: string;
  category?: '通用' | '力学' | '机械' | '智能制造' | '其他';
  contentTemplate?: string;
  variables?: TemplateVariable;
}

// 文书模板响应数据
export interface DocumentTemplateResponse extends DocumentTemplateBase {
  id: number;
  createdAt: string;
  updatedAt: string;
  deletedAt?: string;
}

// 文书模板列表响应
export interface DocumentTemplateListResponse {
  total: number;
  page: number;
  pageSize: number;
  templates: DocumentTemplateResponse[];
}

// 生成文书基础信息
export interface GeneratedDocumentBase {
  studentId: number;
  professorId?: number;
  templateId?: number;
  documentType: '套磁信' | '个人陈述' | '自我介绍' | '推荐信' | '其他';
  content: string;
  filePath?: string;
}

// 创建生成文书请求
export interface GeneratedDocumentCreate extends GeneratedDocumentBase {}

// 更新生成文书请求
export interface GeneratedDocumentUpdate {
  content?: string;
  filePath?: string;
}

// 生成文书响应数据
export interface GeneratedDocumentResponse extends GeneratedDocumentBase {
  id: number;
  generatedAt: string;
}

// 生成文书详情响应（包含学生、导师、模板信息）
export interface GeneratedDocumentDetailResponse extends GeneratedDocumentResponse {
  student?: {
    id: number;
    name: string;
    university: string;
    major?: string;
  };
  professor?: {
    id: number;
    name: string;
    university: string;
    department?: string;
    title?: string;
  };
  template?: {
    id: number;
    name: string;
    category: string;
  };
}

// 生成文书列表响应
export interface GeneratedDocumentListResponse {
  total: number;
  page: number;
  pageSize: number;
  documents: GeneratedDocumentResponse[];
}

// 文书生成请求
export interface DocumentGenerationRequest {
  studentId: number;
  professorId?: number;
  templateId?: number; // 如不提供，自动选择最合适的模板
  documentType: '套磁信' | '个人陈述' | '自我介绍' | '推荐信' | '其他';
  customVariables?: Record<string, string>;
}

// 文书生成响应
export interface DocumentGenerationResponse {
  success: boolean;
  documentId?: number;
  documentContent?: string;
  errorMessage?: string;
  warnings: string[];
}

// 文书导出选项
export interface DocumentExportOptions {
  format: 'pdf' | 'docx' | 'txt' | 'html';
  includeHeader?: boolean;
  includeFooter?: boolean;
  watermark?: string;
  fileName?: string;
}

// 文书编辑会话
export interface DocumentEditSession {
  documentId: number;
  content: string;
  variables: Record<string, string>;
  history: string[];
  lastSavedAt: string;
  autoSaveEnabled: boolean;
}