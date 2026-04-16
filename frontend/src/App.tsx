import React, { Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout, Spin, Watermark } from 'antd'
import { Helmet } from 'react-helmet-async'

import AppHeader from './components/layout/AppHeader'
import AppSidebar from './components/layout/AppSidebar'
import AppFooter from './components/layout/AppFooter'
import LoadingScreen from './components/common/LoadingScreen'
import { useAuthStore } from './store/authStore'

// 懒加载页面组件
const HomePage = React.lazy(() => import('@pages/Home/HomePage'))
const SearchPage = React.lazy(() => import('@pages/Search/SearchPage'))
const ProfessorDetailPage = React.lazy(() => import('@pages/ProfessorDetail/ProfessorDetailPage'))
const DashboardPage = React.lazy(() => import('@pages/Dashboard/DashboardPage'))
const DocumentsPage = React.lazy(() => import('@pages/Documents/DocumentsPage'))
const LoginPage = React.lazy(() => import('@pages/Auth/LoginPage'))
const SettingsPage = React.lazy(() => import('@pages/Settings/SettingsPage'))
const NotFoundPage = React.lazy(() => import('@pages/NotFound/NotFoundPage'))

const { Content } = Layout

const App: React.FC = () => {
  const { isAuthenticated, user } = useAuthStore()

  // 受保护路由组件
  const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />
    }
    return <>{children}</>
  }

  // 公共路由组件
  const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    if (isAuthenticated && window.location.pathname === '/login') {
      return <Navigate to="/" replace />
    }
    return <>{children}</>
  }

  return (
    <>
      <Helmet>
        <title>保研导师信息搜集网站</title>
        <meta name="description" content="智能匹配导师，生成个性化文书，助力保研成功" />
      </Helmet>

      <Watermark content="保研导师信息搜集网站" fontSize={12} gap={[100, 100]} opacity={0.05}>
        <Layout className="min-h-screen bg-gray-50">
          {isAuthenticated && <AppHeader />}

          <Layout>
            {isAuthenticated && <AppSidebar />}

            <Layout className="p-4 md:p-6">
              <Content className="bg-white rounded-lg shadow-sm p-4 md:p-6 min-h-[calc(100vh-200px)]">
                <Suspense fallback={<LoadingScreen />}>
                  <Routes>
                    {/* 公共路由 */}
                    <Route path="/login" element={
                      <PublicRoute>
                        <LoginPage />
                      </PublicRoute>
                    } />

                    {/* 受保护路由 */}
                    <Route path="/" element={
                      <ProtectedRoute>
                        <HomePage />
                      </ProtectedRoute>
                    } />

                    <Route path="/search" element={
                      <ProtectedRoute>
                        <SearchPage />
                      </ProtectedRoute>
                    } />

                    <Route path="/professor/:id" element={
                      <ProtectedRoute>
                        <ProfessorDetailPage />
                      </ProtectedRoute>
                    } />

                    <Route path="/dashboard" element={
                      <ProtectedRoute>
                        <DashboardPage />
                      </ProtectedRoute>
                    } />

                    <Route path="/documents" element={
                      <ProtectedRoute>
                        <DocumentsPage />
                      </ProtectedRoute>
                    } />

                    <Route path="/settings" element={
                      <ProtectedRoute>
                        <SettingsPage />
                      </ProtectedRoute>
                    } />

                    {/* 重定向 */}
                    <Route path="/home" element={<Navigate to="/" replace />} />
                    <Route path="/index" element={<Navigate to="/" replace />} />

                    {/* 404页面 */}
                    <Route path="*" element={<NotFoundPage />} />
                  </Routes>
                </Suspense>
              </Content>
            </Layout>
          </Layout>

          <AppFooter />
        </Layout>
      </Watermark>
    </>
  )
}

export default App