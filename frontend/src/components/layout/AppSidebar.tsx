import React from 'react';
import { Layout, Menu } from 'antd';
import {
  HomeOutlined,
  SearchOutlined,
  UserOutlined,
  DashboardOutlined,
  FileTextOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useLocation, useNavigate } from 'react-router-dom';

const { Sider } = Layout;

const menuItems = [
  {
    key: '/',
    icon: <HomeOutlined />,
    label: '首页',
  },
  {
    key: '/search',
    icon: <SearchOutlined />,
    label: '导师搜索',
  },
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '个人仪表板',
  },
  {
    key: '/documents',
    icon: <FileTextOutlined />,
    label: '文书管理',
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: '设置',
  },
];

const AppSidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Sider
      width={220}
      className="bg-white border-r shadow-sm"
      breakpoint="lg"
      collapsedWidth="0"
    >
      <div className="p-4 border-b">
        <div className="text-lg font-semibold text-gray-800">导航菜单</div>
      </div>

      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        className="border-0"
      />
    </Sider>
  );
};

export default AppSidebar;