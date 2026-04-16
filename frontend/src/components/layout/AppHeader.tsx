import React from 'react';
import { Layout, Avatar, Dropdown, Space, Typography } from 'antd';
import { UserOutlined, LogoutOutlined, SettingOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../store/authStore';

const { Header } = Layout;
const { Text } = Typography;

const AppHeader: React.FC = () => {
  const { user, logout } = useAuthStore();

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: () => logout(),
    },
  ];

  return (
    <Header className="bg-white shadow-sm border-b px-4 md:px-6 flex items-center justify-between">
      <div className="flex items-center">
        <div className="text-xl font-bold text-blue-600">保研导师信息搜集网站</div>
      </div>

      <div className="flex items-center gap-4">
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <Space className="cursor-pointer hover:bg-gray-100 px-3 py-1 rounded">
            <Avatar size="small" icon={<UserOutlined />} />
            <Text>{user?.name || '用户'}</Text>
          </Space>
        </Dropdown>
      </div>
    </Header>
  );
};

export default AppHeader;