import React from 'react';
import { Button, Result, Typography, Space } from 'antd';
import { HomeOutlined, ReloadOutlined, FrownOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph } = Typography;

const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center p-4">
      <div className="text-center max-w-2xl">
        <Result
          icon={<FrownOutlined className="text-6xl text-gray-400" />}
          title={
            <Title level={1} className="!text-6xl !font-bold !mb-4">
              404
            </Title>
          }
          subTitle={
            <div>
              <Title level={3} className="!mb-4">
                页面未找到
              </Title>
              <Paragraph type="secondary" className="text-lg">
                抱歉，您访问的页面不存在或已被移除
              </Paragraph>
            </div>
          }
          extra={
            <Space direction="vertical" size="middle" className="w-full">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button
                  type="primary"
                  size="large"
                  icon={<HomeOutlined />}
                  onClick={() => navigate('/')}
                  className="min-w-[180px]"
                >
                  返回首页
                </Button>
                <Button
                  size="large"
                  icon={<ReloadOutlined />}
                  onClick={() => window.location.reload()}
                  className="min-w-[180px]"
                >
                  刷新页面
                </Button>
              </div>
            </Space>
          }
        />

        <div className="mt-12 p-8 bg-white rounded-2xl shadow-lg border border-gray-200">
          <Title level={4} className="!mb-6">
            您可以尝试以下操作：
          </Title>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl text-blue-500">1</span>
              </div>
              <Title level={5} className="!mb-2">检查网址</Title>
              <Paragraph type="secondary">
                确认您输入的网址是否正确，可能存在拼写错误
              </Paragraph>
            </div>

            <div className="p-4 bg-green-50 rounded-lg">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl text-green-500">2</span>
              </div>
              <Title level={5} className="!mb-2">使用导航</Title>
              <Paragraph type="secondary">
                通过顶部导航栏或侧边栏访问其他页面
              </Paragraph>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl text-purple-500">3</span>
              </div>
              <Title level={5} className="!mb-2">联系支持</Title>
              <Paragraph type="secondary">
                如果问题持续存在，请联系技术支持
              </Paragraph>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <Paragraph type="secondary">
            或者回到我们最受欢迎的页面：
          </Paragraph>
          <Space wrap className="mt-4">
            <Button onClick={() => navigate('/dashboard')}>个人仪表板</Button>
            <Button onClick={() => navigate('/search')}>导师搜索</Button>
            <Button onClick={() => navigate('/professors')}>导师列表</Button>
            <Button onClick={() => navigate('/documents')}>文书管理</Button>
          </Space>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-300">
          <Paragraph type="secondary" className="text-sm">
            <strong>技术信息：</strong> 如果您是网站管理员，请检查路由配置和页面组件是否正确导入。
          </Paragraph>
          <Paragraph type="secondary" className="text-xs mt-2">
            © 2026 保研导师信息平台 - 错误页面
          </Paragraph>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;