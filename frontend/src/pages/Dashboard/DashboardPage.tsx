import React from 'react';
import { Card, Row, Col, Progress, Timeline, Table, Typography, Space, Tag } from 'antd';
import {
  UserOutlined,
  BookOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  RocketOutlined,
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

const DashboardPage: React.FC = () => {
  const timelineItems = [
    {
      color: 'green',
      children: (
        <div>
          <Text strong>个人资料完善</Text>
          <Paragraph type="secondary">已完成基本信息填写</Paragraph>
        </div>
      ),
    },
    {
      color: 'green',
      children: (
        <div>
          <Text strong>学术背景提交</Text>
          <Paragraph type="secondary">GPA、科研经历等已提交</Paragraph>
        </div>
      ),
    },
    {
      color: 'blue',
      children: (
        <div>
          <Text strong>导师搜索</Text>
          <Paragraph type="secondary">已搜索25位相关导师</Paragraph>
        </div>
      ),
    },
    {
      color: 'blue',
      children: (
        <div>
          <Text strong>匹配分析</Text>
          <Paragraph type="secondary">已完成8位导师的匹配分析</Paragraph>
        </div>
      ),
    },
    {
      color: 'gray',
      children: (
        <div>
          <Text strong>文书生成</Text>
          <Paragraph type="secondary">待生成申请文书</Paragraph>
        </div>
      ),
    },
    {
      color: 'gray',
      children: (
        <div>
          <Text strong>联系导师</Text>
          <Paragraph type="secondary">准备发送陶瓷邮件</Paragraph>
        </div>
      ),
    },
  ];

  const matchData = [
    { key: '1', professor: '张教授', university: '清华大学', score: 88, probability: '高' },
    { key: '2', professor: '李教授', university: '上海交通大学', score: 85, probability: '高' },
    { key: '3', professor: '王教授', university: '浙江大学', score: 78, probability: '中' },
    { key: '4', professor: '刘教授', university: '哈尔滨工业大学', score: 72, probability: '中' },
    { key: '5', professor: '陈教授', university: '北京航空航天大学', score: 65, probability: '低' },
  ];

  const columns = [
    {
      title: '导师',
      dataIndex: 'professor',
      key: 'professor',
    },
    {
      title: '学校',
      dataIndex: 'university',
      key: 'university',
    },
    {
      title: '匹配分数',
      dataIndex: 'score',
      key: 'score',
      render: (score: number) => (
        <Progress percent={score} size="small" strokeColor={score > 80 ? '#52c41a' : score > 70 ? '#faad14' : '#ff4d4f'} />
      ),
    },
    {
      title: '录取概率',
      dataIndex: 'probability',
      key: 'probability',
      render: (prob: string) => {
        const color = prob === '高' ? 'success' : prob === '中' ? 'warning' : 'error';
        return <Tag color={color}>{prob}</Tag>;
      },
    },
  ];

  return (
    <div className="p-4 md:p-6">
      <div className="mb-8">
        <Title level={2}>个人仪表板</Title>
        <Paragraph type="secondary">
          查看您的保研进度、匹配结果和个性化建议
        </Paragraph>
      </div>

      <Row gutter={[16, 16]} className="mb-8">
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Space direction="vertical" align="center" className="w-full">
              <UserOutlined className="text-3xl text-blue-500" />
              <Title level={3} className="!mb-0">85%</Title>
              <Text type="secondary">资料完整度</Text>
              <Progress percent={85} size="small" />
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Space direction="vertical" align="center" className="w-full">
              <BookOutlined className="text-3xl text-green-500" />
              <Title level={3} className="!mb-0">25</Title>
              <Text type="secondary">已搜索导师</Text>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Space direction="vertical" align="center" className="w-full">
              <FileTextOutlined className="text-3xl text-purple-500" />
              <Title level={3} className="!mb-0">3</Title>
              <Text type="secondary">已生成文书</Text>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Space direction="vertical" align="center" className="w-full">
              <RocketOutlined className="text-3xl text-orange-500" />
              <Title level={3} className="!mb-0">88</Title>
              <Text type="secondary">平均匹配分</Text>
            </Space>
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <Card title="保研进度" className="h-full">
            <Timeline items={timelineItems} />
            <div className="mt-4">
              <Paragraph>
                <CheckCircleOutlined className="text-green-500 mr-2" />
                已完成：个人信息收集、导师搜索
              </Paragraph>
              <Paragraph>
                <ClockCircleOutlined className="text-blue-500 mr-2" />
                进行中：匹配分析、文书准备
              </Paragraph>
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="近期匹配结果" className="h-full">
            <Table
              dataSource={matchData}
              columns={columns}
              pagination={false}
              size="small"
            />
            <Paragraph className="mt-4">
              建议：重点关注匹配分数85分以上的导师，优先联系。
            </Paragraph>
          </Card>
        </Col>
      </Row>

      <Card title="个性化建议" className="mt-8">
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Card size="small">
              <Title level={4}>📈 提升方向</Title>
              <Paragraph>
                • 补充科研项目经历<br />
                • 提高英语水平（托福/雅思）<br />
                • 学习相关专业课程<br />
                • 参加学术会议
              </Paragraph>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card size="small">
              <Title level={4}>🎯 申请策略</Title>
              <Paragraph>
                • 重点申请匹配度高的学校<br />
                • 准备个性化研究计划<br />
                • 提前联系心仪导师<br />
                • 准备面试模拟
              </Paragraph>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card size="small">
              <Title level={4}>📅 时间规划</Title>
              <Paragraph>
                • 3-4月：完善申请材料<br />
                • 5-6月：联系导师<br />
                • 7-8月：准备文书<br />
                • 9-10月：提交申请
              </Paragraph>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default DashboardPage;