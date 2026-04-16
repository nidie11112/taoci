import React from 'react';
import { Layout, Typography, Space } from 'antd';

const { Footer } = Layout;
const { Text, Link } = Typography;

const AppFooter: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <Footer className="bg-gray-50 border-t py-4 px-6 text-center">
      <Space direction="vertical" size="small">
        <Text type="secondary" className="text-sm">
          © {currentYear} 保研导师信息搜集网站. 版权所有.
        </Text>
        <Text type="secondary" className="text-xs">
          本网站旨在帮助大学生在保研过程中智能化搜索、匹配导师，并生成个性化申请文书。
        </Text>
        <Space size="middle">
          <Link href="/privacy" className="text-xs">隐私政策</Link>
          <Link href="/terms" className="text-xs">使用条款</Link>
          <Link href="/contact" className="text-xs">联系我们</Link>
          <Link href="https://github.com/your-username/taoci-web" target="_blank" className="text-xs">GitHub</Link>
        </Space>
      </Space>
    </Footer>
  );
};

export default AppFooter;