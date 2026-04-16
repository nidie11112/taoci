import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import { ErrorBoundary } from 'react-error-boundary'
import { HelmetProvider } from 'react-helmet-async'
import zhCN from 'antd/locale/zh_CN'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

import App from './App'
import ErrorFallback from './components/common/ErrorFallback'
import './styles/global.css'

// 配置dayjs中文
dayjs.locale('zh-cn')

// 配置Ant Design主题
const theme = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    colorLink: '#1890ff',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  },
  components: {
    Button: {
      borderRadius: 6,
    },
    Card: {
      borderRadiusLG: 12,
    },
    Input: {
      borderRadius: 6,
    },
    Select: {
      borderRadius: 6,
    },
  },
}

// 全局错误处理
const onError = (error: Error, info: { componentStack: string }) => {
  // 可以在这里发送错误到监控服务
  console.error('应用错误:', error)
  console.error('组件堆栈:', info.componentStack)
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary FallbackComponent={ErrorFallback} onError={onError}>
      <HelmetProvider>
        <ConfigProvider locale={zhCN} theme={theme}>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ConfigProvider>
      </HelmetProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)