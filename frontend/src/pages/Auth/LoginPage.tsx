import React, { useState } from 'react';
import { Card, Form, Input, Button, Typography, Space, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../store/authStore';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      // 模拟登录请求
      console.log('登录信息:', values);

      // 模拟API请求延迟
      await new Promise(resolve => setTimeout(resolve, 1000));

      // 模拟用户数据
      const mockUser = {
        id: '1',
        name: values.username === 'admin' ? '管理员' : '吴凌钧',
        email: `${values.username}@example.com`,
        university: '清华大学',
        major: '工程力学',
      };

      login(mockUser);
      message.success('登录成功！');
      navigate('/dashboard');
    } catch (error) {
      message.error('登录失败，请检查用户名和密码');
      console.error('登录错误:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <UserOutlined className="text-3xl text-white" />
          </div>
          <Title level={2}>保研导师信息平台</Title>
          <Paragraph type="secondary">
            请输入您的账号信息登录系统
          </Paragraph>
        </div>

        <Form
          name="login"
          layout="vertical"
          onFinish={onFinish}
          autoComplete="off"
        >
          <Form.Item
            label="用户名"
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
            ]}
          >
            <Input
              prefix={<UserOutlined className="text-gray-400" />}
              placeholder="请输入用户名"
              size="large"
            />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined className="text-gray-400" />}
              placeholder="请输入密码"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
            >
              登录
            </Button>
          </Form.Item>
        </Form>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <Space direction="vertical" className="w-full">
            <Text type="secondary" className="text-center block">
              演示账号：admin / 123456
            </Text>
            <Text type="secondary" className="text-center block">
              学生账号：student / 123456
            </Text>
          </Space>
        </div>

        <div className="mt-8 text-center">
          <Paragraph type="secondary" className="text-sm">
            还没有账号？{' '}
            <Button type="link" className="!p-0" onClick={() => message.info('请联系管理员注册账号')}>
              联系管理员注册
            </Button>
          </Paragraph>
          <Paragraph type="secondary" className="text-xs mt-2">
            © 2026 保研导师信息平台 - 仅供学术研究使用
          </Paragraph>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;