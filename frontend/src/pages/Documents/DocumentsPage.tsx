import React, { useState } from 'react';
import { Card, Row, Col, List, Button, Typography, Space, Tag, Modal, Form, Input, Select } from 'antd';
import {
  FileTextOutlined,
  EditOutlined,
  DeleteOutlined,
  DownloadOutlined,
  PlusOutlined,
  EyeOutlined,
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const DocumentsPage: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);

  const documents = [
    {
      id: '1',
      title: '清华大学张教授-个人陈述',
      professor: '张教授',
      university: '清华大学',
      type: '个人陈述',
      status: '已完成',
      createdAt: '2026-03-15',
      wordCount: 1250,
    },
    {
      id: '2',
      title: '上海交通大学李教授-研究计划',
      professor: '李教授',
      university: '上海交通大学',
      type: '研究计划',
      status: '草稿',
      createdAt: '2026-03-10',
      wordCount: 850,
    },
    {
      id: '3',
      title: '浙江大学王教授-推荐信',
      professor: '王教授',
      university: '浙江大学',
      type: '推荐信',
      status: '待完善',
      createdAt: '2026-03-05',
      wordCount: 720,
    },
    {
      id: '4',
      title: '哈尔滨工业大学刘教授-个人简历',
      professor: '刘教授',
      university: '哈尔滨工业大学',
      type: '个人简历',
      status: '已完成',
      createdAt: '2026-02-28',
      wordCount: 950,
    },
  ];

  const documentTypes = [
    '个人陈述',
    '研究计划',
    '推荐信',
    '个人简历',
    '动机信',
    '学术论文',
  ];

  const showCreateModal = () => {
    setIsModalVisible(true);
  };

  const handleCreate = (values: any) => {
    console.log('创建文书:', values);
    setIsModalVisible(false);
  };

  return (
    <div className="p-4 md:p-6">
      <div className="mb-8">
        <Title level={2}>文书管理</Title>
        <Paragraph type="secondary">
          管理您的申请文书，支持智能生成、编辑和导出
        </Paragraph>
      </div>

      <Row gutter={[16, 16]} className="mb-8">
        <Col xs={24} md={12} lg={8}>
          <Card className="text-center h-full">
            <FileTextOutlined className="text-4xl text-blue-500 mb-4" />
            <Title level={3}>{documents.length}</Title>
            <Text type="secondary">文书总数</Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={8}>
          <Card className="text-center h-full">
            <EditOutlined className="text-4xl text-green-500 mb-4" />
            <Title level={3}>{documents.filter(d => d.status === '已完成').length}</Title>
            <Text type="secondary">已完成</Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={8}>
          <Card className="text-center h-full">
            <PlusOutlined className="text-4xl text-purple-500 mb-4" />
            <Button type="primary" size="large" icon={<PlusOutlined />} onClick={showCreateModal}>
              新建文书
            </Button>
          </Card>
        </Col>
      </Row>

      <Card
        title="我的文书"
        extra={
          <Space>
            <Button icon={<DownloadOutlined />}>批量导出</Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={showCreateModal}>
              新建
            </Button>
          </Space>
        }
      >
        <List
          dataSource={documents}
          renderItem={(doc) => (
            <List.Item
              actions={[
                <Button key="view" type="text" icon={<EyeOutlined />}>查看</Button>,
                <Button key="edit" type="text" icon={<EditOutlined />}>编辑</Button>,
                <Button key="download" type="text" icon={<DownloadOutlined />}>下载</Button>,
                <Button key="delete" type="text" danger icon={<DeleteOutlined />}>删除</Button>,
              ]}
            >
              <List.Item.Meta
                avatar={<FileTextOutlined className="text-2xl" />}
                title={
                  <Space>
                    <Text strong>{doc.title}</Text>
                    <Tag color={doc.status === '已完成' ? 'success' : doc.status === '草稿' ? 'warning' : 'error'}>
                      {doc.status}
                    </Tag>
                  </Space>
                }
                description={
                  <Space direction="vertical" size="small">
                    <Text type="secondary">
                      {doc.professor} · {doc.university} · {doc.type}
                    </Text>
                    <Text type="secondary">
                      创建时间：{doc.createdAt} · 字数：{doc.wordCount}字
                    </Text>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      <Card title="文书模板" className="mt-8">
        <Row gutter={[16, 16]}>
          {documentTypes.map((type, index) => (
            <Col xs={24} sm={12} md={8} lg={6} key={index}>
              <Card
                hoverable
                className="text-center h-full"
                onClick={() => console.log('选择模板:', type)}
              >
                <FileTextOutlined className="text-3xl text-blue-500 mb-3" />
                <Title level={4} className="!mb-2">{type}</Title>
                <Paragraph type="secondary">智能生成{type}模板</Paragraph>
                <Button type="link">使用模板</Button>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      <Modal
        title="新建文书"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        <Form layout="vertical" onFinish={handleCreate}>
          <Form.Item
            label="文书类型"
            name="type"
            rules={[{ required: true, message: '请选择文书类型' }]}
          >
            <Select placeholder="选择文书类型">
              {documentTypes.map(type => (
                <Option key={type} value={type}>{type}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="目标导师"
            name="professor"
            rules={[{ required: true, message: '请输入导师姓名' }]}
          >
            <Input placeholder="例如：张教授" />
          </Form.Item>

          <Form.Item
            label="目标学校"
            name="university"
            rules={[{ required: true, message: '请输入学校名称' }]}
          >
            <Input placeholder="例如：清华大学" />
          </Form.Item>

          <Form.Item
            label="文书标题"
            name="title"
            rules={[{ required: true, message: '请输入文书标题' }]}
          >
            <Input placeholder="例如：个人陈述-清华大学-张教授" />
          </Form.Item>

          <Form.Item>
            <Space className="w-full justify-end">
              <Button onClick={() => setIsModalVisible(false)}>取消</Button>
              <Button type="primary" htmlType="submit">创建文书</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default DocumentsPage;