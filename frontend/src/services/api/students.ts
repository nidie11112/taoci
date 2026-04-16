/**
 * 学生API服务
 */

import { api } from './client';
import {
  StudentResponse,
  StudentListResponse,
  StudentCreate,
  StudentUpdate,
  StudentMatchRecord,
  ResumeUploadResponse,
} from '@/types/student';
import { ApiResponse, PaginationParams } from '@/types/common';

/**
 * 学生API服务
 */
export const studentApi = {
  /**
   * 获取学生列表
   */
  async getStudents(
    params?: {
      university?: string;
      major?: string;
    } & PaginationParams
  ): Promise<ApiResponse<StudentResponse[]>> {
    const queryParams = {
      page: params?.page || 1,
      page_size: params?.pageSize || 20,
      university: params?.university,
      major: params?.major,
    };

    // 移除undefined参数
    Object.keys(queryParams).forEach(
      (key) =>
        queryParams[key as keyof typeof queryParams] === undefined &&
        delete queryParams[key as keyof typeof queryParams]
    );

    return api.get<StudentResponse[]>('/v1/students/', {
      params: queryParams,
    });
  },

  /**
   * 获取单个学生信息
   */
  async getStudent(id: number): Promise<ApiResponse<StudentResponse>> {
    return api.get<StudentResponse>(`/v1/students/${id}`);
  },

  /**
   * 创建学生
   */
  async createStudent(
    data: StudentCreate
  ): Promise<ApiResponse<StudentResponse>> {
    return api.post<StudentResponse>('/v1/students/', data);
  },

  /**
   * 更新学生信息
   */
  async updateStudent(
    id: number,
    data: StudentUpdate
  ): Promise<ApiResponse<StudentResponse>> {
    return api.put<StudentResponse>(`/v1/students/${id}`, data);
  },

  /**
   * 删除学生（软删除）
   */
  async deleteStudent(id: number): Promise<ApiResponse<void>> {
    return api.delete<void>(`/v1/students/${id}`);
  },

  /**
   * 获取学生的匹配记录
   */
  async getStudentMatches(
    studentId: number
  ): Promise<ApiResponse<StudentMatchRecord[]>> {
    return api.get<StudentMatchRecord[]>(
      `/v1/students/${studentId}/matches`
    );
  },

  /**
   * 上传学生简历
   */
  async uploadStudentResume(
    studentId: number,
    file: File
  ): Promise<ApiResponse<ResumeUploadResponse>> {
    const formData = new FormData();
    formData.append('resume', file);

    return api.post<ResumeUploadResponse>(
      `/v1/students/${studentId}/upload-resume`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
  },

  /**
   * 获取当前登录学生信息
   */
  async getCurrentStudent(): Promise<ApiResponse<StudentResponse>> {
    // 假设后端有/me端点返回当前用户信息
    // 这里先实现为获取第一个学生（实际项目中应根据认证信息获取）
    const response = await this.getStudents({ pageSize: 1 });
    if (response.success && response.data && response.data.length > 0) {
      return {
        success: true,
        data: response.data[0],
      };
    }

    throw new Error('未找到学生信息');
  },

  /**
   * 批量导入学生数据
   */
  async importStudents(file: File): Promise<ApiResponse<{ count: number }>> {
    return api.upload<{ count: number }>('/v1/students/import', file);
  },

  /**
   * 导出学生数据
   */
  async exportStudents(
    studentIds?: number[]
  ): Promise<ApiResponse<Blob>> {
    const response = await api.download('/v1/students/export', {
      params: studentIds ? { ids: studentIds.join(',') } : undefined,
    });

    return {
      success: true,
      data: response,
    };
  },

  /**
   * 更新学生技能
   */
  async updateStudentSkills(
    studentId: number,
    skills: string[]
  ): Promise<ApiResponse<StudentResponse>> {
    return this.updateStudent(studentId, { skills });
  },

  /**
   * 添加科研经历
   */
  async addResearchExperience(
    studentId: number,
    experience: any // 简化类型，实际使用ResearchExperience类型
  ): Promise<ApiResponse<StudentResponse>> {
    const student = await this.getStudent(studentId);
    if (!student.success || !student.data) {
      throw new Error('获取学生信息失败');
    }

    const updatedExperiences = [
      ...(student.data.researchExperience || []),
      experience,
    ];

    return this.updateStudent(studentId, {
      researchExperience: updatedExperiences,
    });
  },

  /**
   * 添加竞赛获奖
   */
  async addCompetitionAward(
    studentId: number,
    award: any // 简化类型，实际使用CompetitionAward类型
  ): Promise<ApiResponse<StudentResponse>> {
    const student = await this.getStudent(studentId);
    if (!student.success || !student.data) {
      throw new Error('获取学生信息失败');
    }

    const updatedAwards = [
      ...(student.data.competitionAwards || []),
      award,
    ];

    return this.updateStudent(studentId, {
      competitionAwards: updatedAwards,
    });
  },
};

// 默认导出
export default studentApi;