/**
 * 文书API服务
 */

import { api } from './client';
import {
  DocumentTemplateResponse,
  DocumentTemplateListResponse,
  DocumentTemplateCreate,
  DocumentTemplateUpdate,
  GeneratedDocumentResponse,
  GeneratedDocumentListResponse,
  GeneratedDocumentDetailResponse,
  GeneratedDocumentCreate,
  GeneratedDocumentUpdate,
  DocumentGenerationRequest,
  DocumentGenerationResponse,
} from '@/types/document';
import { ApiResponse, PaginationParams } from '@/types/common';

/**
 * 文书API服务
 */
export const documentApi = {
  // ==================== 文书模板相关 ====================

  /**
   * 获取文书模板列表
   */
  async getDocumentTemplates(
    params?: {
      category?: string;
      search?: string;
    } & PaginationParams
  ): Promise<ApiResponse<DocumentTemplateListResponse>> {
    const queryParams = {
      page: params?.page || 1,
      page_size: params?.pageSize || 20,
      category: params?.category,
      search: params?.search,
    };

    // 移除undefined参数
    Object.keys(queryParams).forEach(
      (key) =>
        queryParams[key as keyof typeof queryParams] === undefined &&
        delete queryParams[key as keyof typeof queryParams]
    );

    return api.get<DocumentTemplateListResponse>('/v1/documents/templates', {
      params: queryParams,
    });
  },

  /**
   * 获取单个文书模板
   */
  async getDocumentTemplate(
    templateId: number
  ): Promise<ApiResponse<DocumentTemplateResponse>> {
    return api.get<DocumentTemplateResponse>(`/v1/documents/templates/${templateId}`);
  },

  /**
   * 创建文书模板
   */
  async createDocumentTemplate(
    data: DocumentTemplateCreate
  ): Promise<ApiResponse<DocumentTemplateResponse>> {
    return api.post<DocumentTemplateResponse>('/v1/documents/templates', data);
  },

  /**
   * 更新文书模板
   */
  async updateDocumentTemplate(
    templateId: number,
    data: DocumentTemplateUpdate
  ): Promise<ApiResponse<DocumentTemplateResponse>> {
    return api.put<DocumentTemplateResponse>(
      `/v1/documents/templates/${templateId}`,
      data
    );
  },

  /**
   * 删除文书模板（软删除）
   */
  async deleteDocumentTemplate(templateId: number): Promise<ApiResponse<void>> {
    return api.delete<void>(`/v1/documents/templates/${templateId}`);
  },

  // ==================== 生成文书相关 ====================

  /**
   * 获取生成文书列表
   */
  async getGeneratedDocuments(
    params?: {
      studentId?: number;
      professorId?: number;
      documentType?: string;
    } & PaginationParams
  ): Promise<ApiResponse<GeneratedDocumentListResponse>> {
    const queryParams = {
      page: params?.page || 1,
      page_size: params?.pageSize || 20,
      student_id: params?.studentId,
      professor_id: params?.professorId,
      document_type: params?.documentType,
    };

    // 移除undefined参数
    Object.keys(queryParams).forEach(
      (key) =>
        queryParams[key as keyof typeof queryParams] === undefined &&
        delete queryParams[key as keyof typeof queryParams]
    );

    return api.get<GeneratedDocumentListResponse>('/v1/documents/generated', {
      params: queryParams,
    });
  },

  /**
   * 获取单个生成文书
   */
  async getGeneratedDocument(
    documentId: number
  ): Promise<ApiResponse<GeneratedDocumentDetailResponse>> {
    return api.get<GeneratedDocumentDetailResponse>(
      `/v1/documents/generated/${documentId}`
    );
  },

  /**
   * 创建生成文书
   */
  async createGeneratedDocument(
    data: GeneratedDocumentCreate
  ): Promise<ApiResponse<GeneratedDocumentResponse>> {
    return api.post<GeneratedDocumentResponse>('/v1/documents/generated', data);
  },

  /**
   * 更新生成文书
   */
  async updateGeneratedDocument(
    documentId: number,
    data: GeneratedDocumentUpdate
  ): Promise<ApiResponse<GeneratedDocumentResponse>> {
    return api.put<GeneratedDocumentResponse>(
      `/v1/documents/generated/${documentId}`,
      data
    );
  },

  /**
   * 删除生成文书
   */
  async deleteGeneratedDocument(documentId: number): Promise<ApiResponse<void>> {
    return api.delete<void>(`/v1/documents/generated/${documentId}`);
  },

  // ==================== 文书生成相关 ====================

  /**
   * 生成文书
   */
  async generateDocument(
    data: DocumentGenerationRequest
  ): Promise<ApiResponse<DocumentGenerationResponse>> {
    return api.post<DocumentGenerationResponse>('/v1/documents/generate', data);
  },

  /**
   * 生成套磁信
   */
  async generateCoverLetter(
    studentId: number,
    professorId?: number,
    templateId?: number,
    customVariables?: Record<string, string>
  ): Promise<ApiResponse<DocumentGenerationResponse>> {
    return this.generateDocument({
      studentId,
      professorId,
      templateId,
      documentType: '套磁信',
      customVariables,
    });
  },

  /**
   * 生成个人陈述
   */
  async generatePersonalStatement(
    studentId: number,
    targetUniversity?: string,
    targetMajor?: string,
    templateId?: number,
    customVariables?: Record<string, string>
  ): Promise<ApiResponse<DocumentGenerationResponse>> {
    const variables = {
      ...customVariables,
      target_university: targetUniversity,
      target_major: targetMajor,
    };

    return this.generateDocument({
      studentId,
      documentType: '个人陈述',
      templateId,
      customVariables: variables,
    });
  },

  /**
   * 生成推荐信
   */
  async generateRecommendationLetter(
    studentId: number,
    recommender: {
      name: string;
      title: string;
      university: string;
      department: string;
      relationship: string;
    },
    templateId?: number,
    customVariables?: Record<string, string>
  ): Promise<ApiResponse<DocumentGenerationResponse>> {
    const variables = {
      ...customVariables,
      recommender_name: recommender.name,
      recommender_title: recommender.title,
      recommender_university: recommender.university,
      recommender_department: recommender.department,
      recommender_relationship: recommender.relationship,
    };

    return this.generateDocument({
      studentId,
      documentType: '推荐信',
      templateId,
      customVariables: variables,
    });
  },

  /**
   * 获取学生的生成文书
   */
  async getStudentDocuments(
    studentId: number,
    documentType?: string,
    limit: number = 20
  ): Promise<ApiResponse<GeneratedDocumentResponse[]>> {
    return api.get<GeneratedDocumentResponse[]>(
      `/v1/documents/student/${studentId}/generated`,
      {
        params: {
          document_type: documentType,
          limit,
        },
      }
    );
  },

  /**
   * 获取导师相关的生成文书
   */
  async getProfessorDocuments(
    professorId: number,
    documentType?: string,
    limit: number = 20
  ): Promise<ApiResponse<GeneratedDocumentResponse[]>> {
    return api.get<GeneratedDocumentResponse[]>(
      `/v1/documents/professor/${professorId}/generated`,
      {
        params: {
          document_type: documentType,
          limit,
        },
      }
    );
  },

  /**
   * 获取文书统计信息
   */
  async getDocumentStats(): Promise<ApiResponse<any>> {
    return api.get<any>('/v1/documents/stats');
  },

  // ==================== 其他功能 ====================

  /**
   * 导出文书
   */
  async exportDocument(
    documentId: number,
    format: 'pdf' | 'docx' | 'txt' = 'pdf'
  ): Promise<ApiResponse<Blob>> {
    const response = await api.download(`/v1/documents/export/${documentId}`, {
      params: { format },
    });

    return {
      success: true,
      data: response,
    };
  },

  /**
   * 批量导出文书
   */
  async bulkExportDocuments(
    documentIds: number[],
    format: 'pdf' | 'docx' | 'txt' = 'pdf'
  ): Promise<ApiResponse<Blob>> {
    const response = await api.download('/v1/documents/export/bulk', {
      params: {
        document_ids: documentIds.join(','),
        format,
      },
    });

    return {
      success: true,
      data: response,
    };
  },

  /**
   * 复制文书
   */
  async duplicateDocument(
    documentId: number,
    newDocumentType?: string
  ): Promise<ApiResponse<GeneratedDocumentResponse>> {
    const document = await this.getGeneratedDocument(documentId);
    if (!document.success || !document.data) {
      throw new Error('获取文书失败');
    }

    const { data } = document;
    const newData: GeneratedDocumentCreate = {
      studentId: data.studentId,
      professorId: data.professorId,
      templateId: data.templateId,
      documentType: newDocumentType || data.documentType,
      content: data.content,
      filePath: undefined, // 新文书不复制文件路径
    };

    return this.createGeneratedDocument(newData);
  },

  /**
   * 获取推荐的模板
   */
  async getRecommendedTemplates(
    studentId: number,
    professorId?: number,
    documentType?: string
  ): Promise<ApiResponse<DocumentTemplateResponse[]>> {
    // 这里可以调用后端的推荐接口，暂时返回所有模板
    const templates = await this.getDocumentTemplates({ pageSize: 10 });
    if (!templates.success || !templates.data) {
      return templates;
    }

    // 简单过滤：如果有文档类型，过滤匹配类型
    let recommended = templates.data.templates;
    if (documentType) {
      // 根据文档类型推荐相应分类的模板
      const categoryMap: Record<string, string> = {
        套磁信: '力学',
        个人陈述: '通用',
        推荐信: '通用',
      };
      const preferredCategory = categoryMap[documentType] || '通用';
      recommended = recommended.filter(
        (t) => t.category === preferredCategory || t.category === '通用'
      );
    }

    return {
      success: true,
      data: recommended,
    };
  },

  /**
   * 搜索文书模板
   */
  async searchTemplates(
    query: string,
    category?: string
  ): Promise<ApiResponse<DocumentTemplateResponse[]>> {
    const response = await this.getDocumentTemplates({
      search: query,
      category,
      pageSize: 20,
    });

    if (!response.success || !response.data) {
      return response;
    }

    return {
      success: true,
      data: response.data.templates,
    };
  },
};

// 默认导出
export default documentApi;