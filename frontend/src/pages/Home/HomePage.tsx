import React from 'react';
import { Card, Row, Col, Statistic, Button, Typography, Space } from 'antd';
import {
  UserOutlined,
  SearchOutlined,
  FileTextOutlined,
  RocketOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph } = Typography;

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: '导师智能搜索',
      description: '基于研究方向、学校、专业等多维度搜索合适导师',
      icon: <SearchOutlined className="text-2xl text-blue-500" />,
      action: () => navigate('/search'),
    },
    {
      title: '智能匹配分析',
      description: '根据您的背景和兴趣，智能匹配最适合的导师',
      icon: <UserOutlined className="text-2xl text-green-500" />,
      action: () => navigate('/dashboard'),
    },
    {
      title: '文书自动生成',
      description: '基于匹配结果，自动生成个性化的申请文书',
      icon: <FileTextOutlined className="text-2xl text-purple-500" />,
      action: () => navigate('/documents'),
    },
    {
      title: '保研进度跟踪',
      description: '全程跟踪保研进度，提供申请建议和时间规划',
      icon: <RocketOutlined className="text-2xl text-orange-500" />,
      action: () => navigate('/dashboard'),
    },
  ];

  return (
    <div className="p-4 md:p-6">
      <div className="mb-8">
        <Title level={2}>欢迎使用保研导师信息搜集网站</Title>
        <Paragraph type="secondary" className="text-lg">
          智能匹配导师，生成个性化文书，助力您的保研之路
        </Paragraph>
      </div>

      <Row gutter={[16, 16]} className="mb-8">
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已收录导师"
              value={1258}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="成功匹配案例"
              value={347}
              prefix={<RocketOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="文书生成数量"
              value={892}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均匹配分数"
              value={86.5}
              suffix="分"
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      <Title level={3} className="mb-6">核心功能</Title>
      <Row gutter={[24, 24]}>
        {features.map((feature, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card
              hoverable
              className="h-full"
              onClick={feature.action}
            >
              <Space direction="vertical" size="middle" className="text-center">
                <div className="flex justify-center">{feature.icon}</div>
                <Title level={4} className="!mb-2">{feature.title}</Title>
                <Paragraph type="secondary">{feature.description}</Paragraph>
                <Button type="primary" onClick={feature.action}>
                  开始使用
                </Button>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      <Card className="mt-8">
        <Title level={3}>快速开始</Title>
        <Paragraph>
          1. 完善您的个人资料和学术背景<br />
          2. 使用智能搜索功能查找心仪导师<br />
          3. 查看匹配分析报告和录取概率<br />
          4. 生成个性化申请文书<br />
          5. 跟踪申请进度并及时调整策略
        </Paragraph>
        <Button type="primary" size="large" onClick={() => navigate('/dashboard')}>
          立即开始
        </Button>
      </Card>
    </div>
  );
};

export default HomePage;