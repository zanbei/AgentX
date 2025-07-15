import React, { useEffect } from 'react';
import { Flex, Space, Typography, Switch, Divider } from 'antd';
import { Sender, Suggestion } from '@ant-design/x';
import { UserOutlined } from '@ant-design/icons';
import { useStyles } from '../../styles';
import { useChatStore } from '../../store';
import type { Agent } from '../../services/api';

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
    agentSelectionEnabled, 
    // streamingEnabled,
    setSelectedAgent, 
    setAgentSelectionEnabled,
    // setStreamingEnabled,
    fetchAgents 
  } = useChatStore();
  
  // Fetch agents when component mounts
  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  const handleSubmit = () => {
    if (!inputValue) return;
    
    // Check if agent is selected when agent selection is enabled
    if (agentSelectionEnabled && !selectedAgent) {
      // message.warning('Please select an agent first');
      return;
    }
    
    onSubmit(inputValue);
    setInputValue('');

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
                if (value === '/' && agentSelectionEnabled) {
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
                        Agent
                        <Switch 
                          size="small" 
                          checked={agentSelectionEnabled}
                          onChange={(checked) => {
                            setAgentSelectionEnabled(checked);
                            if (!checked && selectedAgent) {
                              setSelectedAgent(null);
                            }
                          }}
                        />
                        <Divider type="vertical" />
                        {/* Streaming
                        <Switch 
                          size="small" 
                          checked={streamingEnabled}
                          onChange={(checked) => {
                            setStreamingEnabled(checked);
                          }}
                        /> */}
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
              placeholder={agentSelectionEnabled ? "Ask or input / to select an agent" : "Ask a question"}
            />
          )}
        </Suggestion>
      </div>
  );
};
