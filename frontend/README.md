# 保研导师信息搜集网站 - 前端

## 项目概述
基于React + TypeScript的前端应用，提供导师搜索、匹配分析、文书生成等功能的用户界面。

## 技术栈
- React 18
- TypeScript 5
- Vite (构建工具)
- Ant Design / Material-UI (UI组件库)
- Zustand (状态管理)
- React Router v6 (路由)
- Axios (HTTP客户端)
- ECharts / Recharts (数据可视化)

## 开发环境设置

### 1. 安装依赖
```bash
npm install
# 或
yarn install
```

### 2. 运行开发服务器
```bash
npm run dev
# 或
yarn dev
```

### 3. 构建生产版本
```bash
npm run build
# 或
yarn build
```

### 4. 代码质量检查
```bash
npm run lint
npm run type-check
```

## 项目结构
```
frontend/
├── public/              # 静态资源
├── src/
│   ├── components/     # 可复用组件
│   │   ├── common/    # 通用组件
│   │   ├── professor/ # 导师相关组件
│   │   ├── matching/  # 匹配相关组件
│   │   ├── documents/ # 文书相关组件
│   │   └── dashboard/ # 仪表板组件
│   ├── pages/         # 页面组件
│   ├── services/      # API服务
│   ├── store/         # 状态管理
│   ├── utils/         # 工具函数
│   ├── types/         # TypeScript类型定义
│   ├── styles/        # 全局样式
│   ├── hooks/         # 自定义Hook
│   ├── constants/     # 常量定义
│   ├── App.tsx       # 根组件
│   └── index.tsx     # 入口文件
├── package.json
├── tsconfig.json
├── vite.config.ts
└── ...
```

## 环境变量
创建 `.env` 文件并配置：
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=保研导师信息搜集网站
VITE_DEBUG=true
```

## 开发规范
1. **组件设计**：使用函数组件和Hooks，避免类组件
2. **类型安全**：所有组件和函数必须有明确的TypeScript类型
3. **状态管理**：局部状态使用useState，全局状态使用Zustand
4. **代码分割**：路由级代码分割，优化加载性能
5. **错误处理**：统一错误处理，友好的用户反馈

## 与后端API集成
前端通过 `services/api` 模块与后端通信，所有API调用需要：
1. 错误处理
2. 加载状态管理
3. 数据缓存（可选）

## 测试
```bash
# 单元测试
npm run test

# E2E测试（如果配置）
npm run test:e2e
```

## 构建与部署
```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview

# 部署到静态托管服务
# 如：Netlify, Vercel, GitHub Pages
```

## 注意事项
- 移动端响应式设计必须
- 用户数据本地存储需加密
- 遵循无障碍设计原则
- 性能优化（图片懒加载、代码分割等）