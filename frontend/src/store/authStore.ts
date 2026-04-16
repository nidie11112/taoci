import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  university?: string;
  major?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (userData: User) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}

// 模拟用户数据
const mockUser: User = {
  id: '1',
  name: '吴凌钧',
  email: 'wulingjun@example.com',
  university: '清华大学',
  major: '工程力学',
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: mockUser,
      isAuthenticated: true, // 开发环境默认已登录
      login: (userData: User) => {
        set({ user: userData, isAuthenticated: true });
      },
      logout: () => {
        set({ user: null, isAuthenticated: false });
        // 实际应用中这里可能还需要清理token等
      },
      updateUser: (updates: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ user: { ...currentUser, ...updates } });
        }
      },
    }),
    {
      name: 'auth-storage', // localStorage key
      // 可以配置部分持久化
      // partialize: (state) => ({ user: state.user }),
    }
  )
);