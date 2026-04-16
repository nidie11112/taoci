import React, { useState } from 'react';
import { Card, Form, Input, Button, Typography, Tabs, Select, Switch, Upload, message } from 'antd';
import { UserOutlined, MailOutlined, BookOutlined, SafetyOutlined, UploadOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../store/authStore';

const { Title, Paragraph, Text } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

const SettingsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const user = useAuthStore((state) => state.user);
  const updateUser = useAuthStore((state) => state.updateUser);

  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();

  const onProfileFinish = (values: any) => {
    setLoading(true);
    console.log('更新个人信息:', values);

    // 模拟API请求
    setTimeout(() => {
      updateUser(values);
      message.success('个人信息更新成功！');
      setLoading(false);
    }, 1000);
  };

  const onPasswordFinish = (values: any) => {
    setLoading(true);
    console.log('修改密码:', values);

    // 模拟API请求
    setTimeout(() => {
      if (values.newPassword !== values.confirmPassword) {
        message.error('两次输入的密码不一致');
        setLoading(false);
        return;
      }

      message.success('密码修改成功！');
      passwordForm.resetFields();
      setLoading(false);
    }, 1000);
  };

  const uploadProps = {
    beforeUpload: (file: File) => {
      const isImage = file.type.startsWith('image/');
      if (!isImage) {
        message.error('只能上传图片文件！');
      }

      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        message.error('图片大小不能超过2MB！');
      }

      return isImage && isLt2M;
    },
    onChange: (info: any) => {
      if (info.file.status === 'done') {
        message.success(`${info.file.name} 上传成功`);
      } else if (info.file.status === 'error') {
        message.error(`${info.file.name} 上传失败`);
      }
    },
  };

  return (
    <div className="p-4 md:p-6">
      <div className="mb-8">
        <Title level={2}>个人设置</Title>
        <Paragraph type="secondary">
          管理您的个人信息、账号安全和偏好设置
        </Paragraph>
      </div>

      <Tabs defaultActiveKey="1" type="card">
        <TabPane tab={<span><UserOutlined /> 个人信息</span>} key="1">
          <Card className="max-w-2xl">
            <Form
              form={form}
              layout="vertical"
              onFinish={onProfileFinish}
              initialValues={user}
            >
              <div className="mb-8">
                <Title level={4}>基本信息</Title>
                <Paragraph type="secondary">
                  更新您的个人资料信息
                </Paragraph>
              </div>

              <div className="flex flex-col md:flex-row gap-8 mb-8">
                <div className="md:w-1/3 text-center">
                  <div className="w-32 h-32 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                    {user?.avatar ? (
                      <img src={user.avatar} alt="头像" className="w-full h-full rounded-full object-cover" />
                    ) : (
                      <UserOutlined className="text-4xl text-gray-500" />
                    )}
                  </div>
                  <Upload {...uploadProps} showUploadList={false}>
                    <Button icon={<UploadOutlined />}>更换头像</Button>
                  </Upload>
                  <Paragraph type="secondary" className="mt-2">
                    支持 JPG、PNG 格式，大小不超过 2MB
                  </Paragraph>
                </div>

                <div className="md:w-2/3">
                  <Form.Item label="姓名" name="name" rules={[{ required: true, message: '请输入姓名' }]}>
                    <Input prefix={<UserOutlined />} placeholder="请输入姓名" size="large" />
                  </Form.Item>

                  <Form.Item label="邮箱" name="email" rules={[
                    { required: true, message: '请输入邮箱' },
                    { type: 'email', message: '邮箱格式不正确' },
                  ]}>
                    <Input prefix={<MailOutlined />} placeholder="请输入邮箱" size="large" />
                  </Form.Item>

                  <Form.Item label="学校" name="university">
                    <Input prefix={<BookOutlined />} placeholder="请输入学校" size="large" />
                  </Form.Item>

                  <Form.Item label="专业" name="major">
                    <Input placeholder="请输入专业" size="large" />
                  </Form.Item>
                </div>
              </div>

              <div className="flex justify-end">
                <Button type="primary" htmlType="submit" loading={loading} size="large">
                  保存更改
                </Button>
              </div>
            </Form>
          </Card>
        </TabPane>

        <TabPane tab={<span><SafetyOutlined /> 账号安全</span>} key="2">
          <Card className="max-w-2xl">
            <div className="mb-8">
              <Title level={4}>修改密码</Title>
              <Paragraph type="secondary">
                定期修改密码有助于保护账号安全
              </Paragraph>
            </div>

            <Form
              form={passwordForm}
              layout="vertical"
              onFinish={onPasswordFinish}
            >
              <Form.Item
                label="当前密码"
                name="currentPassword"
                rules={[{ required: true, message: '请输入当前密码' }]}
              >
                <Input.Password placeholder="请输入当前密码" size="large" />
              </Form.Item>

              <Form.Item
                label="新密码"
                name="newPassword"
                rules={[
                  { required: true, message: '请输入新密码' },
                  { min: 8, message: '密码至少8个字符' },
                ]}
              >
                <Input.Password placeholder="请输入新密码" size="large" />
              </Form.Item>

              <Form.Item
                label="确认新密码"
                name="confirmPassword"
                dependencies={['newPassword']}
                rules={[
                  { required: true, message: '请确认新密码' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('newPassword') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('两次输入的密码不一致'));
                    },
                  }),
                ]}
              >
                <Input.Password placeholder="请确认新密码" size="large" />
              </Form.Item>

              <div className="flex justify-end">
                <Button type="primary" htmlType="submit" loading={loading} size="large">
                  修改密码
                </Button>
              </div>
            </Form>

            <div className="mt-8 pt-8 border-t border-gray-200">
              <Title level={4}>安全设置</Title>
              <div className="space-y-4 mt-4">
                <div className="flex justify-between items-center">
                  <div>
                    <Text strong>双重认证</Text>
                    <Paragraph type="secondary" className="!mb-0">
                      启用后，登录时需要验证手机验证码
                    </Paragraph>
                  </div>
                  <Switch />
                </div>

                <div className="flex justify-between items-center">
                  <div>
                    <Text strong>登录通知</Text>
                    <Paragraph type="secondary" className="!mb-0">
                      当检测到新设备登录时发送邮件通知
                    </Paragraph>
                  </div>
                  <Switch defaultChecked />
                </div>

                <div className="flex justify-between items-center">
                  <div>
                    <Text strong>会话管理</Text>
                    <Paragraph type="secondary" className="!mb-0">
                      30天后自动退出登录
                    </Paragraph>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>
            </div>
          </Card>
        </TabPane>

        <TabPane tab="偏好设置" key="3">
          <Card className="max-w-2xl">
            <div className="mb-8">
              <Title level={4}>界面设置</Title>
              <Paragraph type="secondary">
                自定义您的使用体验
              </Paragraph>
            </div>

            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <Text strong>主题模式</Text>
                  <Paragraph type="secondary" className="!mb-0">
                    选择您偏好的界面主题
                  </Paragraph>
                </div>
                <Select defaultValue="light" style={{ width: 120 }}>
                  <Option value="light">浅色主题</Option>
                  <Option value="dark">深色主题</Option>
                  <Option value="auto">跟随系统</Option>
                </Select>
              </div>

              <div className="flex justify-between items-center">
                <div>
                  <Text strong>语言设置</Text>
                  <Paragraph type="secondary" className="!mb-0">
                    选择界面显示语言
                  </Paragraph>
                </div>
                <Select defaultValue="zh-CN" style={{ width: 120 }}>
                  <Option value="zh-CN">简体中文</Option>
                  <Option value="en-US">English</Option>
                </Select>
              </div>

              <div className="flex justify-between items-center">
                <div>
                  <Text strong>通知设置</Text>
                  <Paragraph type="secondary" className="!mb-0">
                    控制接收哪些类型的通知
                  </Paragraph>
                </div>
                <Select mode="multiple" defaultValue={['match', 'message']} style={{ width: 200 }}>
                  <Option value="match">匹配通知</Option>
                  <Option value="message">消息通知</Option>
                  <Option value="system">系统通知</Option>
                  <Option value="promotion">推广通知</Option>
                </Select>
              </div>

              <div className="flex justify-between items-center">
                <div>
                  <Text strong>自动保存</Text>
                  <Paragraph type="secondary" className="!mb-0">
                    编辑文书时自动保存草稿
                  </Paragraph>
                </div>
                <Switch defaultChecked />
              </div>

              <div className="flex justify-between items-center">
                <div>
                  <Text strong>数据备份</Text>
                  <Paragraph type="secondary" className="!mb-0">
                    每周自动备份数据到云端
                  </Paragraph>
                </div>
                <Switch defaultChecked />
              </div>
            </div>

            <div className="mt-8 flex justify-end">
              <Button type="primary" size="large">
                保存偏好设置
              </Button>
            </div>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default SettingsPage;