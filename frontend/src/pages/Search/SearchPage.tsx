import React, { useState } from 'react';
import { Card, Input, Button, Select, Row, Col, Form, Tag, Space, Typography } from 'antd';
import { SearchOutlined, FilterOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { Option } = Select;
const { Search } = Input;

const SearchPage: React.FC = () => {
  const [loading, setLoading] = useState(false);

  const universities = [
    '清华大学', '北京大学', '上海交通大学', '复旦大学', '浙江大学',
    '南京大学', '中国科学技术大学', '哈尔滨工业大学', '西安交通大学',
    '同济大学', '华中科技大学', '武汉大学', '中山大学'
  ];

  const departments = [
    '力学', '机械工程', '航空航天', '材料科学与工程', '计算机科学',
    '电子工程', '土木工程', '化学工程', '生物医学工程', '数学'
  ];

  const researchFields = [
    '计算力学', '固体力学', '流体力学', '生物力学', '复合材料',
    '智能制造', '机器人学', '人工智能', '大数据', '机器学习'
  ];

  const handleSearch = (values: any) => {
    setLoading(true);
    console.log('搜索条件:', values);
    // 模拟搜索
    setTimeout(() => {
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="p-4 md:p-6">
      <div className="mb-8">
        <Title level={2}>导师智能搜索</Title>
        <Paragraph type="secondary">
          根据研究方向、学校、专业等多维度搜索适合的导师
        </Paragraph>
      </div>

      <Card className="mb-8">
        <Form layout="vertical" onFinish={handleSearch}>
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Form.Item label="关键词" name="keyword">
                <Search
                  placeholder="输入研究方向或导师姓名"
                  enterButton={<SearchOutlined />}
                  size="large"
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="学校" name="university">
                <Select
                  placeholder="选择学校"
                  size="large"
                  mode="multiple"
                  showSearch
                >
                  {universities.map(uni => (
                    <Option key={uni} value={uni}>{uni}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="院系" name="department">
                <Select
                  placeholder="选择院系"
                  size="large"
                  mode="multiple"
                >
                  {departments.map(dept => (
                    <Option key={dept} value={dept}>{dept}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="研究方向" name="researchField">
                <Select
                  placeholder="选择研究方向"
                  size="large"
                  mode="multiple"
                >
                  {researchFields.map(field => (
                    <Option key={field} value={field}>{field}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Space>
            <Button type="primary" htmlType="submit" loading={loading} icon={<SearchOutlined />}>
              搜索导师
            </Button>
            <Button icon={<FilterOutlined />}>高级筛选</Button>
          </Space>
        </Form>
      </Card>

      <Title level={3} className="mb-6">搜索建议</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={8}>
          <Card hoverable>
            <Title level={4}>计算力学方向</Title>
            <Paragraph>清华大学、上海交通大学、中国科学技术大学</Paragraph>
            <Space wrap>
              <Tag color="blue">有限元分析</Tag>
              <Tag color="blue">多尺度模拟</Tag>
              <Tag color="blue">高性能计算</Tag>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card hoverable>
            <Title level={4}>复合材料方向</Title>
            <Paragraph>哈尔滨工业大学、西北工业大学、北京航空航天大学</Paragraph>
            <Space wrap>
              <Tag color="green">碳纤维复合材料</Tag>
              <Tag color="green">功能梯度材料</Tag>
              <Tag color="green">智能材料</Tag>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card hoverable>
            <Title level={4}>生物力学方向</Title>
            <Paragraph>北京大学、复旦大学、浙江大学</Paragraph>
            <Space wrap>
              <Tag color="purple">组织工程</Tag>
              <Tag color="purple">生物材料</Tag>
              <Tag color="purple">医疗器械</Tag>
            </Space>
          </Card>
        </Col>
      </Row>

      <Card className="mt-8">
        <Title level={3}>搜索提示</Title>
        <Paragraph>
          1. 使用多个关键词组合搜索，结果更精确<br />
          2. 可以先选择学校范围，再细化研究方向<br />
          3. 关注导师近年发表论文和科研项目<br />
          4. 查看学生评价和实验室氛围<br />
          5. 使用智能匹配功能获得个性化推荐
        </Paragraph>
      </Card>
    </div>
  );
};

export default SearchPage;