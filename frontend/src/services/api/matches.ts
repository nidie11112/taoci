/**
 * 匹配API服务
 */

import { api } from './client';
import {
  MatchResponse,
  MatchListResponse,
  MatchDetailResponse,
  MatchCreate,
  MatchUpdate,
  MatchSearchParams,
  MatchCalculateResponse,
  MatchCalculateRequest,
} from '@/types/match';
import { ApiResponse, PaginationParams } from '@/types/common';

/**
 * 匹配API服务
 */
export const matchApi = {
  /**
   * 获取匹配列表
   */
  async getMatches(
    params?: MatchSearchParams & PaginationParams
  ): Promise<ApiResponse<MatchListResponse>> {
    const queryParams = {
      page: params?.page || 1,
      page_size: params?.pageSize || 20,
      student_id: params?.studentId,
      professor_id: params?.professorId,
      min_score: params?.minScore,
      min_probability: params?.minProbability,
    };

    // 移除undefined参数
    Object.keys(queryParams).forEach(
      (key) =>
        queryParams[key as keyof typeof queryParams] === undefined &&
        delete queryParams[key as keyof typeof queryParams]
    );

    return api.get<MatchListResponse>('/v1/matches/', {
      params: queryParams,
    });
  },

  /**
   * 获取单个匹配信息
   */
  async getMatch(id: number): Promise<ApiResponse<MatchDetailResponse>> {
    return api.get<MatchDetailResponse>(`/v1/matches/${id}`);
  },

  /**
   * 创建匹配记录
   */
  async createMatch(
    data: MatchCreate
  ): Promise<ApiResponse<MatchResponse>> {
    return api.post<MatchResponse>('/v1/matches/', data);
  },

  /**
   * 更新匹配信息
   */
  async updateMatch(
    id: number,
    data: MatchUpdate
  ): Promise<ApiResponse<MatchResponse>> {
    return api.put<MatchResponse>(`/v1/matches/${id}`, data);
  },

  /**
   * 删除匹配记录
   */
  async deleteMatch(id: number): Promise<ApiResponse<void>> {
    return api.delete<void>(`/v1/matches/${id}`);
  },

  /**
   * 获取学生推荐导师
   */
  async getStudentRecommendations(
    studentId: number,
    limit: number = 10
  ): Promise<ApiResponse<any[]>> {
    return api.get<any[]>(`/v1/matches/student/${studentId}/recommendations`, {
      params: { limit },
    });
  },

  /**
   * 获取导师推荐学生
   */
  async getProfessorRecommendations(
    professorId: number,
    limit: number = 10
  ): Promise<ApiResponse<any[]>> {
    return api.get<any[]>(`/v1/matches/professor/${professorId}/recommendations`, {
      params: { limit },
    });
  },

  /**
   * 计算学生和导师的匹配度
   */
  async calculateMatch(
    data: MatchCalculateRequest
  ): Promise<ApiResponse<MatchCalculateResponse>> {
    const { studentId, professorId, includeDetails = true } = data;

    return api.post<MatchCalculateResponse>('/v1/matches/calculate', {
      student_id: studentId,
      professor_id: professorId,
      include_details: includeDetails,
    });
  },

  /**
   * 快速计算匹配度（简化参数）
   */
  async quickCalculateMatch(
    studentId: number,
    professorId: number
  ): Promise<ApiResponse<MatchCalculateResponse>> {
    return this.calculateMatch({ studentId, professorId, includeDetails: false });
  },

  /**
   * 获取匹配统计信息
   */
  async getMatchStats(): Promise<ApiResponse<any>> {
    return api.get<any>('/v1/matches/stats/overall');
  },

  /**
   * 批量创建匹配记录
   */
  async bulkCreateMatches(
    matches: MatchCreate[]
  ): Promise<ApiResponse<{ successCount: number; failedCount: number; errors: any[] }>> {
    const results = {
      successCount: 0,
      failedCount: 0,
      errors: [] as any[],
    };

    // 逐个创建匹配记录
    for (const match of matches) {
      try {
        await this.createMatch(match);
        results.successCount++;
      } catch (error) {
        results.failedCount++;
        results.errors.push({
          match,
          error: error instanceof Error ? error.message : '未知错误',
        });
      }
    }

    return {
      success: results.failedCount === 0,
      data: results,
      message: results.failedCount === 0
        ? '批量创建成功'
        : `${results.successCount}条成功，${results.failedCount}条失败`,
    };
  },

  /**
   * 获取学生的所有匹配记录
   */
  async getStudentMatches(
    studentId: number,
    params?: PaginationParams
  ): Promise<ApiResponse<MatchListResponse>> {
    return this.getMatches({
      studentId,
      page: params?.page,
      pageSize: params?.pageSize,
    });
  },

  /**
   * 获取导师的所有匹配记录
   */
  async getProfessorMatches(
    professorId: number,
    params?: PaginationParams
  ): Promise<ApiResponse<MatchListResponse>> {
    return this.getMatches({
      professorId,
      page: params?.page,
      pageSize: params?.pageSize,
    });
  },

  /**
   * 获取高分匹配（匹配度>=0.8）
   */
  async getHighScoreMatches(
    params?: PaginationParams
  ): Promise<ApiResponse<MatchListResponse>> {
    return this.getMatches({
      minScore: 0.8,
      page: params?.page,
      pageSize: params?.pageSize,
    });
  },

  /**
   * 获取高录取概率匹配（概率>=0.7）
   */
  async getHighProbabilityMatches(
    params?: PaginationParams
  ): Promise<ApiResponse<MatchListResponse>> {
    return this.getMatches({
      minProbability: 0.7,
      page: params?.page,
      pageSize: params?.pageSize,
    });
  },

  /**
   * 导出匹配数据
   */
  async exportMatches(
    params?: MatchSearchParams
  ): Promise<ApiResponse<Blob>> {
    const response = await api.download('/v1/matches/export', {
      params,
    });

    return {
      success: true,
      data: response,
    };
  },
};

// 默认导出
export default matchApi;