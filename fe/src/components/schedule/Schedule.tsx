import React, { useEffect } from 'react';
import { 
  Card, 
  Typography, 
  Table, 
  Button, 
  Space, 
  Modal, 
  Form, 
  Input, 
  Select, 
  message 
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined 
} from '@ant-design/icons';
import { useAgentStore } from '../../store/agentStore';
import { useScheduleStore } from '../../store/scheduleStore';
import type { Agent } from '../../services/api';

const { Title } = Typography;
const { Option } = Select;

interface ScheduleItem {
  id: string;
  agentId: string;
  agentName: string;
  cronExpression: string;
  status: string;
  createdAt: string;
  updatedAt: string;
}

export const Schedule: React.FC = () => {
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();
  const { agents, fetchAgents } = useAgentStore();
  const { 
    schedules, 
    loading, 
    createModalVisible,
    editModalVisible,
    selectedSchedule, 
    fetchSchedules,
    setCreateModalVisible,
    setEditModalVisible,
    setSelectedSchedule,
    createSchedule,
    updateSchedule,
    deleteSchedule
  } = useScheduleStore();

  // Load data on component mount
  useEffect(() => {
    fetchAgents();
    fetchSchedules();
  }, [fetchAgents, fetchSchedules]);

  // Reset form when modal is opened
  useEffect(() => {
    if (createModalVisible) {
      form.resetFields();
    }
  }, [createModalVisible, form]);

  // Set edit form values when selected schedule changes
  useEffect(() => {
    if (selectedSchedule && editModalVisible) {
      editForm.setFieldsValue({
        agentId: selectedSchedule.agentId,
        cronExpression: selectedSchedule.cronExpression
      });
    }
  }, [selectedSchedule, editModalVisible, editForm]);

  // Handle create schedule form submission
  const handleCreateSchedule = async (values: { agentId: string; cronExpression: string }) => {
    await createSchedule(values);
    form.resetFields();
  };

  // Handle edit schedule
  const handleEditSchedule = (schedule: ScheduleItem) => {
    setSelectedSchedule(schedule);
    setEditModalVisible(true);
  };

  // Handle edit schedule form submission
  const handleUpdateSchedule = async (values: { agentId: string; cronExpression: string }) => {
    if (!selectedSchedule) return;
    
    await updateSchedule({
      ...selectedSchedule,
      agentId: values.agentId,
      cronExpression: values.cronExpression,
    });
    
    editForm.resetFields();
  };

  // Handle delete schedule with confirmation
  const handleDeleteScheduleWithConfirm = (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个调度任务吗？此操作不可逆。',
      okText: '确认',
      cancelText: '取消',
      onOk: () => deleteSchedule(id)
    });
  };

  // Table columns
  const columns = [
    {
      title: 'Agent名称',
      dataIndex: 'agentName',
      key: 'agentName',
      width: 150,
    },
    {
      title: 'Cron表达式',
      dataIndex: 'cronExpression',
      key: 'cronExpression',
      width: 200,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 150,
    },
    {
      title: '更新时间',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      width: 150,
    },
    {
      title: '操作',
      key: 'actions',
      fixed: 'right' as const,
      width: 120,
      render: (_: unknown, record: ScheduleItem) => (
        <Space>
          <Button 
            type="text" 
            icon={<EditOutlined />} 
            onClick={() => handleEditSchedule(record)} 
          />
          <Button 
            type="text" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDeleteScheduleWithConfirm(record.id)} 
          />
        </Space>
      ),
    },
  ];

  // Create schedule form
  const createScheduleForm = (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleCreateSchedule}
    >
      <Form.Item
        name="agentId"
        label="选择Agent"
        rules={[{ required: true, message: '请选择Agent' }]}
      >
        <Select placeholder="选择要调度的Agent">
          {agents.map((agent: Agent) => (
            <Option key={agent.id} value={agent.id}>{agent.display_name}</Option>
          ))}
        </Select>
      </Form.Item>
      
      <Form.Item
        name="cronExpression"
        label="Cron表达式"
        rules={[
          { required: true, message: '请输入Cron表达式' },
          { 
            pattern: /^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|\?|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|\?|([0-6])|\*\/([0-6]))$/,
            message: 'Cron表达式格式不正确'
          }
        ]}
        help="格式: 分 时 日 月 周 (例如: '0 8 ? * 1' 表示每周一上午8点，日字段必须为?)"
      >
        <Input placeholder="例如: 0 8 ? * 1" />
      </Form.Item>
    </Form>
  );

  // Edit schedule form
  const editScheduleForm = (
    <Form
      form={editForm}
      layout="vertical"
      onFinish={handleUpdateSchedule}
    >
      <Form.Item
        name="agentId"
        label="选择Agent"
        rules={[{ required: true, message: '请选择Agent' }]}
      >
        <Select placeholder="选择要调度的Agent">
          {agents.map((agent: Agent) => (
            <Option key={agent.id} value={agent.id}>{agent.display_name}</Option>
          ))}
        </Select>
      </Form.Item>
      
      <Form.Item
        name="cronExpression"
        label="Cron表达式"
        rules={[
          { required: true, message: '请输入Cron表达式' },
          { 
            pattern: /^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|\?|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|\?|([0-6])|\*\/([0-6]))$/,
            message: 'Cron表达式格式不正确'
          }
        ]}
        help="格式: 分 时 日 月 周 (例如: '0 8 ? * 1' 表示每周一上午8点，日字段必须为?)"
      >
        <Input placeholder="例如: 0 8 ? * 1" />
      </Form.Item>
    </Form>
  );

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <Title level={2}>Agent 调度管理</Title>
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={() => setCreateModalVisible(true)}
          >
            新增
          </Button>
        </div>
        
        <Table 
          columns={columns} 
          dataSource={schedules} 
          rowKey="id" 
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            defaultPageSize: 10,
            showSizeChanger: true,
            pageSizeOptions: ['10', '20', '50'],
            showTotal: (total) => `共 ${total} 条记录`
          }}
        />
        
        {/* Create Schedule Modal */}
        <Modal
          title="新增调度任务"
          open={createModalVisible}
          onCancel={() => setCreateModalVisible(false)}
          onOk={() => form.submit()}
          width={500}
          okText="创建"
          cancelText="取消"
        >
          {createScheduleForm}
        </Modal>
        
        {/* Edit Schedule Modal */}
        <Modal
          title="编辑调度任务"
          open={editModalVisible}
          onCancel={() => {
            setEditModalVisible(false);
            setSelectedSchedule(null);
          }}
          onOk={() => editForm.submit()}
          width={500}
          okText="保存"
          cancelText="取消"
        >
          {editScheduleForm}
        </Modal>
      </Card>
    </div>
  );
};
