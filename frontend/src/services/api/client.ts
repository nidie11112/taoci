/**
 * API客户端配置
 */

import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
} from 'axios';
import { ApiResponse, ErrorResponse } from '@/types/common';

// API基础URL
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// 请求超时时间
const REQUEST_TIMEOUT = 30000; // 30秒

// 创建axios实例
const createAxiosInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: API_BASE_URL,
    timeout: REQUEST_TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    withCredentials: true, // 允许跨域携带cookie
  });

  // 请求拦截器
  instance.interceptors.request.use(
    (config) => {
      // 添加认证token
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      // 添加请求ID用于追踪
      config.headers['X-Request-ID'] = crypto.randomUUID();

      // 如果是GET请求，添加时间戳防止缓存
      if (config.method?.toLowerCase() === 'get') {
        config.params = {
          ...config.params,
          _t: Date.now(),
        };
      }

      console.debug(`API请求: ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      });

      return config;
    },
    (error) => {
      console.error('请求配置错误:', error);
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      console.debug(
        `API响应: ${response.config.method?.toUpperCase()} ${response.config.url}`,
        {
          status: response.status,
          data: response.data,
        }
      );

      // 直接返回数据部分（根据后端API结构调整）
      return response.data;
    },
    async (error: AxiosError) => {
      const originalRequest = error.config;

      // 处理网络错误
      if (!error.response) {
        console.error('网络错误，请检查网络连接');
        return Promise.reject({
          success: false,
          error: 'network_error',
          message: '网络连接失败，请检查网络设置',
        });
      }

      const { status, data } = error.response;

      // 记录错误日志
      console.error(`API错误 ${status}:`, {
        url: originalRequest?.url,
        method: originalRequest?.method,
        data: originalRequest?.data,
        response: data,
      });

      // 处理特定状态码
      switch (status) {
        case 400:
          console.error('请求参数错误:', data);
          break;
        case 401:
          console.error('未授权访问');
          // 清除本地token
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          // 跳转到登录页
          window.location.href = '/login';
          break;
        case 403:
          console.error('权限不足');
          break;
        case 404:
          console.error('资源不存在');
          break;
        case 429:
          console.error('请求过于频繁，请稍后重试');
          break;
        case 500:
        case 502:
        case 503:
          console.error('服务器错误，请稍后重试');
          break;
        default:
          console.error(`未知错误 ${status}`);
      }

      // 统一错误格式
      const errorResponse: ApiResponse = {
        success: false,
        error: data?.error || `http_${status}`,
        message:
          data?.message ||
          data?.detail ||
          data?.error ||
          `请求失败 (${status})`,
        code: status,
      };

      return Promise.reject(errorResponse);
    }
  );

  return instance;
};

// 创建API客户端实例
const apiClient = createAxiosInstance();

// API客户端方法封装
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = apiClient;
  }

  // 通用请求方法
  async request<T = any>(config: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.request<ApiResponse<T>>(config);
      return response;
    } catch (error) {
      // 错误已经在拦截器中处理，这里直接抛出
      throw error;
    }
  }

  // GET请求
  async get<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'GET', url });
  }

  // POST请求
  async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'POST', url, data });
  }

  // PUT请求
  async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'PUT', url, data });
  }

  // PATCH请求
  async patch<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'PATCH', url, data });
  }

  // DELETE请求
  async delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'DELETE', url });
  }

  // 上传文件
  async upload<T = any>(
    url: string,
    file: File,
    fieldName = 'file',
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append(fieldName, file);

    const uploadConfig: AxiosRequestConfig = {
      ...config,
      headers: {
        ...config?.headers,
        'Content-Type': 'multipart/form-data',
      },
    };

    return this.post<T>(url, formData, uploadConfig);
  }

  // 下载文件
  async download(url: string, config?: AxiosRequestConfig): Promise<Blob> {
    const response = await this.client.request<Blob>({
      ...config,
      method: 'GET',
      url,
      responseType: 'blob',
    });
    return response;
  }

  // 设置认证token
  setAuthToken(token: string | null): void {
    if (token) {
      localStorage.setItem('access_token', token);
      this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      localStorage.removeItem('access_token');
      delete this.client.defaults.headers.common['Authorization'];
    }
  }

  // 获取当前token
  getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }

  // 清除认证信息
  clearAuth(): void {
    this.setAuthToken(null);
    localStorage.removeItem('refresh_token');
  }
}

// 创建单例实例
export const api = new ApiClient();

// 默认导出
export default api;