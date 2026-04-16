/**
 * 认证相关类型定义
 */

// 用户角色
export type UserRole = 'student' | 'admin' | 'guest';

// 用户基础信息
export interface UserBase {
  username: string;
  email: string;
  fullName?: string;
  avatar?: string;
  role: UserRole;
}

// 登录请求
export interface LoginRequest {
  username: string;
  password: string;
  rememberMe?: boolean;
}

// 注册请求
export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  fullName?: string;
  role?: UserRole;
}

// 认证响应
export interface AuthResponse {
  accessToken: string;
  refreshToken?: string;
  tokenType: string;
  expiresIn: number;
  user: UserResponse;
}

// 用户响应数据
export interface UserResponse extends UserBase {
  id: number;
  uuid: string;
  createdAt: string;
  updatedAt: string;
  lastLoginAt?: string;
  isActive: boolean;
}

// 刷新令牌请求
export interface RefreshTokenRequest {
  refreshToken: string;
}

// 密码重置请求
export interface PasswordResetRequest {
  email: string;
}

// 密码重置确认请求
export interface PasswordResetConfirmRequest {
  token: string;
  newPassword: string;
  confirmPassword: string;
}

// 认证状态
export interface AuthState {
  isAuthenticated: boolean;
  user: UserResponse | null;
  loading: boolean;
  error: string | null;
  accessToken: string | null;
  refreshToken: string | null;
}

// 权限
export interface Permission {
  resource: string;
  action: 'create' | 'read' | 'update' | 'delete' | 'manage';
  allowed: boolean;
}

// 用户权限
export interface UserPermissions {
  userId: number;
  permissions: Permission[];
}