import React from 'react';
import { Spin, Typography, Space } from 'antd';

const { Text } = Typography;

const LoadingScreen: React.FC = () => {
  return (
    <div className="min-h-[400px] flex items-center justify-center">
      <Space direction="vertical" align="center" size="large">
        <Spin size="large" />
        <Text type="secondary">加载中，请稍候...</Text>
      </Space>
    </div>
  );
};

export default LoadingScreen;