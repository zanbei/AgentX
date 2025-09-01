import React, { useEffect, useState } from 'react';
import { Flex, Space, Typography, Switch, Divider, Upload, message } from 'antd';
import { UserOutlined, UploadOutlined } from '@ant-design/icons';
import { Sender, Suggestion } from '@ant-design/x';
import { useStyles } from '../../styles';
import { useChatStore } from '../../store';
import { chatAPI, type Agent } from '../../services/api';

interface ChatInputProps {
  onSubmit: (text: string) => void;
  onCancel: () => void;
  loading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSubmit, onCancel, loading }) => {
  const { styles } = useStyles();
  const { 
    inputValue, 
    setInputValue, 
    agents, 
    selectedAgent, 
    chatRecordEnabled,
    setSelectedAgent, 
    setChatRecordEnabled,
    fetchAgents 
  } = useChatStore();
  
  // Fetch agents when component mounts
  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  const [fileContent, setFileContent] = useState<string>('');

  const handleSubmit = () => {
    if (!inputValue) return;
    
    // Check if agent is selected
    if (!selectedAgent) {
      message.warning('Please select an agent first');
      return;
    }
    
    onSubmit(inputValue);
    setInputValue('');
  };

  const handleFileUpload = async (file: File) => {
    try {
      // Check if agent is selected
      if (!selectedAgent) {
        message.warning('Please select an agent first');
        return false;
      }

      // Create form data for file upload
      const formData = new FormData();
      formData.append('file', file);

      // Upload file to get temporary path
      const response = await fetch('/api/agent/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('File upload failed');
      }

      const data = await response.json();
      console.log('Upload response:', data); // Debug log
      
      if (data.chat_id) {
        // Get file content using chat ID
        const content = await chatAPI.getFileContent(data.chat_id);
        setFileContent(content);
        
        // Set content to input value for user to edit
        setInputValue(`File content: ${content}`);
        
        // Notify user they can now edit and send the message
        message.success(`File "${file.name}" processed successfully. You can now edit and send the message.`);
      } else {
        // Fallback to original behavior if chat_id is not available
        setInputValue(`File uploaded to ${data.s3_path}`);
        message.success(`File "${file.name}" uploaded successfully. You can now edit and send the message.`);
      }
    } catch (error) {
      message.error('Failed to process file');
      console.error('File processing error:', error);
    }

    return false; // Prevent default upload behavior
  };
  
  // Handle agent selection from suggestion
  const handleAgentSelect = (agent: Agent) => {
    setSelectedAgent(agent);
    setInputValue("");
    // setInputValue(`[${agent.display_name}] `);
  };

  return (
    <div className={styles.sender}>
        {/* Input with Suggestion */}
        <Suggestion
          items={agents.map(agent => ({
            key: agent.id,
            label: agent.display_name,
            description: agent.description,
            value: agent.display_name,
            data: agent
          }))}
          onSelect={(value: string) => {
            // Find the agent by display name
            const agent = agents.find(a => a.display_name === value);
            if (agent) {
              handleAgentSelect(agent);
            }
          }}
        >
          {({ onTrigger, onKeyDown }) => (
            <Sender
              value={inputValue}
              autoSize={{ minRows: 3, maxRows: 6 }}
              header={
                selectedAgent && (
                  <Sender.Header
                    open={!!selectedAgent}
                    title={
                      <Space>
                        <UserOutlined />
                        <Typography.Text type="secondary">您已选择 [{selectedAgent.display_name}]</Typography.Text>
                      </Space>
                    }
                    onOpenChange={(open) => {
                      console.log(`onOpenChange: ${open}`);
                      if (!open) {
                        
                        setSelectedAgent(null);
                        setInputValue('');
                      }
                    }}
                  />
                )
              }
              onSubmit={handleSubmit}
              onChange={(value) => {
                if (value === '/') {
                  console.log(`sender onChange: value: ${value}`);
                  onTrigger();
                } else if (!value) {
                  onTrigger(false);
                }
                setInputValue(value);
              }}
              onKeyDown={onKeyDown}
              onCancel={onCancel}
              loading={loading}
              className={styles.sender}
              allowSpeech
              footer={({ components }) => {
                const { SendButton, LoadingButton, SpeechButton } = components;
                return (
                  <Flex justify="space-between" align="center">
                    <Flex gap="small" align="center">
                      <Space>
                        <UserOutlined />
                        Chat History
                        <Switch 
                          size="small" 
                          checked={chatRecordEnabled}
                          onChange={(checked) => {
                            setChatRecordEnabled(checked);
                          }}
                        />
                        <Upload
                          beforeUpload={handleFileUpload}
                          showUploadList={false}
                          accept=".txt,.csv,.docx,.pdf,.jpg,.jpeg,.png,.gif"
                        >
                          <Space>
                            <UploadOutlined />
                            Upload file
                          </Space>
                        </Upload>
                      </Space>
                    </Flex>
                    <Flex align="center">
                      <SpeechButton className={styles.speechButton} />
                      <Divider type="vertical" />
                      {loading ? <LoadingButton type="default" /> : <SendButton type="primary" />}
                    </Flex>
                  </Flex>
                );
              }}
              actions={false}
              placeholder="Ask or input / to select an agent"
            />
          )}
        </Suggestion>
      </div>
  );
};
