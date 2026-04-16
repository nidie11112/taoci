import React from 'react';
import { Card, Row, Col, Typography, Descriptions, Tag, Space, Button, Progress } from 'antd';
import { UserOutlined, MailOutlined, PhoneOutlined, BookOutlined, TeamOutlined } from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

const ProfessorDetailPage: React.FC = () => {
  // 模拟导师数据
  const professor = {
    id: '1',
    name: '张教授',
    title: '教授、博士生导师',
    university: '清华大学',
    department: '工程力学系',
    researchFields: ['计算力学', '复合材料', '多尺度模拟'],
    email: 'zhang.prof@tsinghua.edu.cn',
    phone: '(010) 6278-XXXX',
    personalPage: 'http://mech.tsinghua.edu.cn/zhang',
    education: [
      '博士 - 斯坦福大学 (2010)',
      '硕士 - 清华大学 (2005)',
      '学士 - 清华大学 (2002)'
    ],
    researchDirection: '主要从事计算力学、复合材料多尺度模拟、高性能计算等方面的研究。',
    publications: 125,
    projects: 18,
    students: 32,
    matchScore: 88,
    admissionProbability: 75,
  };

  return (
    <div className="p-4 md:p-6">
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={16}>
          <Card className="mb-6">
            <Row gutter={[24, 24]}>
              <Col xs={24} md={8} className="text-center">
                <div className="w-32 h-32 bg-gray-200 rounded-full mx-auto flex items-center justify-center mb-4">
                  <UserOutlined className="text-4xl text-gray-500" />
                </div>
                <Title level={3}>{professor.name}</Title>
                <Text type="secondary">{professor.title}</Text>
              </Col>
              <Col xs={24} md={16}>
                <Descriptions column={1}>
                  <Descriptions.Item label="学校">{professor.university}</Descriptions.Item>
                  <Descriptions.Item label="院系">{professor.department}</Descriptions.Item>
                  <Descriptions.Item label="邮箱">
                    <Space>
                      <MailOutlined />
                      <Text copyable>{professor.email}</Text>
                    </Space>
                  </Descriptions.Item>
                  <Descriptions.Item label="电话">
                    <Space>
                      <PhoneOutlined />
                      {professor.phone}
                    </Space>
                  </Descriptions.Item>
                  <Descriptions.Item label="个人主页">
                    <a href={professor.personalPage} target="_blank" rel="noopener noreferrer">
                      {professor.personalPage}
                    </a>
                  </Descriptions.Item>
                </Descriptions>
              </Col>
            </Row>
          </Card>

          <Card title="研究方向" className="mb-6">
            <Space wrap>
              {professor.researchFields.map((field, index) => (
                <Tag key={index} color="blue" style={{ fontSize: '14px', padding: '4px 12px' }}>
                  {field}
                </Tag>
              ))}
            </Space>
            <Paragraph className="mt-4">{professor.researchDirection}</Paragraph>
          </Card>

          <Card title="教育背景" className="mb-6">
            <ul className="list-disc pl-5">
              {professor.education.map((edu, index) => (
                <li key={index} className="mb-2">
                  <Text>{edu}</Text>
                </li>
              ))}
            </ul>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="匹配分析" className="mb-6">
            <div className="text-center mb-6">
              <Progress
                type="circle"
                percent={professor.matchScore}
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
                size={150}
                format={percent => (
                  <div>
                    <div className="text-3xl font-bold">{percent}分</div>
                    <div className="text-gray-500">匹配分数</div>
                  </div>
                )}
              />
            </div>

            <div className="mb-4">
              <div className="flex justify-between mb-2">
                <Text>录取概率</Text>
                <Text strong>{professor.admissionProbability}%</Text>
              </div>
              <Progress percent={professor.admissionProbability} />
            </div>

            <Space direction="vertical" size="middle" className="w-full">
              <Button type="primary" block size="large">
                生成匹配报告
              </Button>
              <Button block size="large">
                添加到收藏
              </Button>
              <Button block size="large">
                联系导师
              </Button>
            </Space>
          </Card>

          <Card title="研究统计" className="mb-6">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <div className="text-center">
                  <BookOutlined className="text-2xl text-blue-500 mb-2" />
                  <div className="text-2xl font-bold">{professor.publications}</div>
                  <Text type="secondary">发表论文</Text>
                </div>
              </Col>
              <Col span={12}>
                <div className="text-center">
                  <TeamOutlined className="text-2xl text-green-500 mb-2" />
                  <div className="text-2xl font-bold">{professor.projects}</div>
                  <Text type="secondary">科研项目</Text>
                </div>
              </Col>
              <Col span={12}>
                <div className="text-center">
                  <UserOutlined className="text-2xl text-purple-500 mb-2" />
                  <div className="text-2xl font-bold">{professor.students}</div>
                  <Text type="secondary">指导学生</Text>
                </div>
              </Col>
              <Col span={12}>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-500 mb-2">A+</div>
                  <div className="text-2xl font-bold">4.8</div>
                  <Text type="secondary">学生评价</Text>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ProfessorDetailPage;