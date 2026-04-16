/**
 * 导师API服务
 */

import { api } from './client';
import {
  ProfessorResponse,
  ProfessorListResponse,
  ProfessorCreate,
  ProfessorUpdate,
  ProfessorSearchParams,
  ProfessorEvaluation,
  AcademicPaper,
  ProfessorStats,
  ProfessorSuggestion,
} from '@/types/professor';
import { ApiResponse, PaginationParams } from '@/types/common';

/**
 * 导师API服务
 */
export const professorApi = {
  /**
   * 获取导师列表
   */
  async getProfessors(
    params?: ProfessorSearchParams & PaginationParams
  ): Promise<ApiResponse<ProfessorListResponse>> {
    const queryParams = {
      page: params?.page || 1,
      page_size: params?.pageSize || 20,
      university: params?.university,
      department: params?.department,
      title: params?.title,
      research_field: params?.researchField,
    };

    // 移除undefined参数
    Object.keys(queryParams).forEach(
      (key) =>
        queryParams[key as keyof typeof queryParams] === undefined &&
        delete queryParams[key as keyof typeof queryParams]
    );

    return api.get<ProfessorListResponse>('/v1/professors/', {
      params: queryParams,
    });
  },

  /**
   * 获取单个导师信息
   */
  async getProfessor(id: number): Promise<ApiResponse<ProfessorResponse>> {
    return api.get<ProfessorResponse>(`/v1/professors/${id}`);
  },

  /**
   * 创建导师
   */
  async createProfessor(
    data: ProfessorCreate
  ): Promise<ApiResponse<ProfessorResponse>> {
    return api.post<ProfessorResponse>('/v1/professors/', data);
  },

  /**
   * 更新导师信息
   */
  async updateProfessor(
    id: number,
    data: ProfessorUpdate
  ): Promise<ApiResponse<ProfessorResponse>> {
    return api.put<ProfessorResponse>(`/v1/professors/${id}`, data);
  },

  /**
   * 删除导师（软删除）
   */
  async deleteProfessor(id: number): Promise<ApiResponse<void>> {
    return api.delete<void>(`/v1/professors/${id}`);
  },

  /**
   * 获取导师评价列表
   */
  async getProfessorEvaluations(
    professorId: number
  ): Promise<ApiResponse<ProfessorEvaluation[]>> {
    return api.get<ProfessorEvaluation[]>(
      `/v1/professors/${professorId}/evaluations`
    );
  },

  /**
   * 获取导师论文列表
   */
  async getProfessorPapers(
    professorId: number
  ): Promise<ApiResponse<AcademicPaper[]>> {
    return api.get<AcademicPaper[]>(`/v1/professors/${professorId}/papers`);
  },

  /**
   * 搜索建议
   */
  async searchSuggestions(
    query: string
  ): Promise<ApiResponse<ProfessorSuggestion[]>> {
    return api.get<ProfessorSuggestion[]>('/v1/professors/search/suggest', {
      params: { q: query },
    });
  },

  /**
   * 添加导师评价
   */
  async addProfessorEvaluation(
    professorId: number,
    evaluation: Omit<ProfessorEvaluation, 'id' | 'createdAt' | 'professorId'>
  ): Promise<ApiResponse<{ evaluationId: number; professorId: number }>> {
    return api.post<{ evaluationId: number; professorId: number }>(
      `/v1/professors/${professorId}/add-evaluation`,
      evaluation
    );
  },

  /**
   * 获取导师统计信息
   */
  async getProfessorStats(
    professorId: number
  ): Promise<ApiResponse<ProfessorStats>> {
    return api.get<ProfessorStats>(`/v1/professors/${professorId}/stats`);
  },

  /**
   * 批量获取导师信息
   */
  async getProfessorsByIds(ids: number[]): Promise<ApiResponse<ProfessorResponse[]>> {
    // 如果ID数量少，可以逐个获取，但更好的做法是后端提供批量接口
    // 这里先实现为逐个获取（实际项目中应使用批量接口）
    const promises = ids.map((id) => this.getProfessor(id));
    const results = await Promise.all(promises);

    return {
      success: results.every((r) => r.success),
      data: results.map((r) => r.data!).filter(Boolean),
      message: results.every((r) => r.success)
        ? '批量获取成功'
        : '部分导师信息获取失败',
    };
  },

  /**
   * 导出导师数据
   */
  async exportProfessors(
    params?: ProfessorSearchParams
  ): Promise<ApiResponse<Blob>> {
    const response = await api.download('/v1/professors/export', {
      params,
    });

    return {
      success: true,
      data: response,
    };
  },

  /**
   * 导入导师数据
   */
  async importProfessors(file: File): Promise<ApiResponse<{ count: number }>> {
    return api.upload<{ count: number }>('/v1/professors/import', file);
  },
};

// 默认导出
export default professorApi;