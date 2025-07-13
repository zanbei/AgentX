import React, { useEffect, useState } from 'react';
import { Layout as AntLayout, Menu } from 'antd';
import { 
  CommentOutlined, 
  SettingOutlined, 
  AppstoreOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  ScheduleOutlined
} from '@ant-design/icons';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { Chat } from '../chat/Chat';
import { AgentManager } from '../agent';
import { MCP } from '../mcp/MCP';
import { Schedule } from '../schedule';
// import { useChatStore } from '../../store';

const { Sider, Content } = AntLayout;

export const Layout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState('1');

  // Update message history when component mounts
  // useEffect(() => {
  //   updateMessageHistory();
  // }, [updateMessageHistory]);
  
  // Update selected key based on current path
  useEffect(() => {
    const path = window.location.pathname;
    if (path.includes('/chat')) {
      setSelectedKey('1');
    } else if (path.includes('/agent')) {
      setSelectedKey('2');
    } else if (path.includes('/mcp')) {
      setSelectedKey('3');
    } else if (path.includes('/schedule')) {
      setSelectedKey('4');
    }
  }, []);

  const menuItems = [
    {
      key: '1',
      icon: <CommentOutlined />,
      label: <Link to="/chat">Agent Chatbot</Link>,
    },
    {
      key: '2',
      icon: <SettingOutlined />,
      label: <Link to="/agent">Agent 管理</Link>,
    },
    {
      key: '3',
      icon: <AppstoreOutlined />,
      label: <Link to="/mcp">MCP 列表</Link>,
    },
    {
      key: '4',
      icon: <ScheduleOutlined />,
      label: <Link to="/schedule">Agent 调度</Link>,
    },
  ];

  return (
    <Router>
      <AntLayout style={{ minHeight: '100vh' }}>
        <Sider 
          collapsible 
          collapsed={collapsed} 
          onCollapse={setCollapsed}
          trigger={null}
          theme="light"
          style={{ 
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
            zIndex: 10
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', padding: '16px 0' }}>
            <div 
              style={{ 
                padding: '0 16px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
              onClick={() => setCollapsed(!collapsed)}
            >
              {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            </div>
            {!collapsed && <span style={{ fontWeight: 'bold' }}>Agent X</span>}
          </div>
          <Menu
            theme="light"
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onClick={e => setSelectedKey(e.key)}
          />
        </Sider>
        <Content style={{ background: '#fff' }}>
          <Routes>
            <Route path="/chat" element={<Chat />} />
            <Route path="/agent" element={<AgentManager />} />
            <Route path="/mcp" element={<MCP />} />
            <Route path="/schedule" element={<Schedule />} />
            <Route path="/" element={<Navigate to="/chat" replace />} />
          </Routes>
        </Content>
      </AntLayout>
    </Router>
  );
};
