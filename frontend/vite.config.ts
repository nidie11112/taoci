import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

// 由于使用ES模块，需要获取__dirname的替代方案
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // 路径别名配置
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@pages': path.resolve(__dirname, 'src/pages'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@store': path.resolve(__dirname, 'src/store'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@types': path.resolve(__dirname, 'src/types'),
      '@styles': path.resolve(__dirname, 'src/styles'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@constants': path.resolve(__dirname, 'src/constants'),
      '@assets': path.resolve(__dirname, 'src/assets'),
    },
  },

  // 开发服务器配置
  server: {
    port: 3000,
    host: true, // 监听所有地址
    open: true, // 自动打开浏览器
    proxy: {
      // 代理API请求到后端
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1'),
      },
    },
  },

  // 构建配置
  build: {
    outDir: 'dist',
    sourcemap: process.env.NODE_ENV !== 'production',
    rollupOptions: {
      output: {
        // 代码分割配置
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['antd', '@ant-design/icons', '@ant-design/pro-components'],
          charts: ['echarts', 'echarts-for-react', 'recharts'],
          utils: ['axios', 'dayjs', 'lodash-es', 'clsx'],
        },
      },
    },
    // 块大小警告限制
    chunkSizeWarningLimit: 1000,
  },

  // 环境变量前缀
  envPrefix: 'VITE_',

  // CSS配置
  css: {
    // 预处理器配置（如果需要）
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@styles/variables.scss";`,
      },
      less: {
        javascriptEnabled: true,
        modifyVars: {
          // 自定义Ant Design主题变量
          'primary-color': '#1890ff',
          'border-radius-base': '4px',
        },
      },
    },
    // 启用CSS模块
    modules: {
      localsConvention: 'camelCase',
    },
  },

  // 测试配置
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/index.ts',
      ],
    },
  },
})