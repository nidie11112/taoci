/**
 * 通用类型定义
 */

// 基础API响应
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  code?: number;
}

// 分页参数
export interface PaginationParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// 分页元数据
export interface PaginationMeta {
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// 带分页的API响应
export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

// 错误响应
export interface ErrorResponse {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

// 文件上传响应
export interface FileUploadResponse {
  fileName: string;
  filePath: string;
  fileSize: number;
  mimeType: string;
  uploadedAt: string;
  url: string;
}

// 搜索参数
export interface SearchParams {
  q?: string;
  filters?: Record<string, any>;
  pagination?: PaginationParams;
}

// 下拉选项
export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
  children?: SelectOption[];
}

// 表格列定义
export interface TableColumn<T = any> {
  key: string;
  title: string;
  dataIndex?: keyof T;
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, record: T, index: number) => React.ReactNode;
  sorter?: (a: T, b: T) => number;
  filters?: { text: string; value: any }[];
  filterMode?: 'menu' | 'tree';
  filterSearch?: boolean;
  ellipsis?: boolean;
}

// 表单字段验证规则
export interface FormRule {
  required?: boolean;
  message?: string;
  validator?: (rule: any, value: any, callback: (error?: string) => void) => void;
  pattern?: RegExp;
  min?: number;
  max?: number;
  len?: number;
  type?: 'string' | 'number' | 'boolean' | 'method' | 'regexp' | 'integer' | 'float' | 'array' | 'object' | 'enum' | 'date' | 'url' | 'hex' | 'email';
  enum?: any[];
  transform?: (value: any) => any;
  whitespace?: boolean;
}

// 面包屑导航项
export interface BreadcrumbItem {
  title: string;
  href?: string;
  icon?: React.ReactNode;
}

// 菜单项
export interface MenuItem {
  key: string;
  label: React.ReactNode;
  icon?: React.ReactNode;
  children?: MenuItem[];
  disabled?: boolean;
  danger?: boolean;
  type?: 'group' | 'divider';
}

// 标签页
export interface TabItem {
  key: string;
  label: string;
  children: React.ReactNode;
  icon?: React.ReactNode;
  disabled?: boolean;
  closable?: boolean;
}

// 通知消息
export interface Notification {
  id: string;
  type: 'success' | 'info' | 'warning' | 'error';
  title: string;
  message: string;
  duration?: number;
  placement?: 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';
  showClose?: boolean;
  timestamp: string;
}

// 地理位置
export interface Location {
  latitude: number;
  longitude: number;
  address?: string;
  city?: string;
  province?: string;
  country?: string;
}

// 时间范围
export interface TimeRange {
  start: string;
  end: string;
}

// 颜色主题
export interface Theme {
  primaryColor: string;
  backgroundColor: string;
  textColor: string;
  borderColor: string;
  successColor: string;
  warningColor: string;
  errorColor: string;
  infoColor: string;
}