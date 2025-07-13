import { create } from 'zustand';
import { message } from 'antd';
import { agentAPI } from '../services/api';
import type { Agent, Tool } from '../services/api';

interface AgentState {
  // Data
  agents: Agent[];
  availableTools: Tool[];
  
  // UI State
  loading: boolean;
  createModalVisible: boolean;
  editModalVisible: boolean;
  toolDetailModalVisible: boolean;
  agentDetailModalVisible: boolean;
  deleteModalVisible: boolean;
  selectedTool: Tool | null;
  selectedAgent: Agent | null;
  
  // Actions
  fetchAgents: () => Promise<void>;
  fetchTools: () => Promise<void>;
  setCreateModalVisible: (visible: boolean) => void;
  setEditModalVisible: (visible: boolean) => void;
  setToolDetailModalVisible: (visible: boolean) => void;
  setAgentDetailModalVisible: (visible: boolean) => void;
  setDeleteModalVisible: (visible: boolean) => void;
  setSelectedTool: (tool: Tool | null) => void;
  setSelectedAgent: (agent: Agent | null) => void;
  createAgent: (agent: Omit<Agent, 'id'>) => Promise<void>;
  updateAgent: (agent: Agent) => Promise<void>;
  deleteAgent: (id: string) => void;
  handleToolClick: (tool: Tool) => void;
  handleViewAgent: (agent: Agent) => void;
  handleEditAgent: (agent: Agent) => void;
  handleDeleteAgent: (agent: Agent) => void;
}

export const useAgentStore = create<AgentState>((set, get) => ({
  // Initial state
  agents: [],
  availableTools: [],
  loading: false,
  createModalVisible: false,
  editModalVisible: false,
  toolDetailModalVisible: false,
  agentDetailModalVisible: false,
  deleteModalVisible: false,
  selectedTool: null,
  selectedAgent: null,
  
  // Actions
  fetchAgents: async () => {
    set({ loading: true });
    try {
      const data = await agentAPI.getAgents();
      set({ agents: data });
    } catch (error) {
      message.error('获取Agent列表失败');
      console.error('Error fetching agents:', error);
    } finally {
      set({ loading: false });
    }
  },
  
  fetchTools: async () => {
    try {
      const data = await agentAPI.getTools();
      set({ availableTools: data });
    } catch (error) {
      message.error('获取工具列表失败');
      console.error('Error fetching tools:', error);
    }
  },
  
  setCreateModalVisible: (visible) => set({ createModalVisible: visible }),
  
  setEditModalVisible: (visible) => set({ editModalVisible: visible }),
  
  setToolDetailModalVisible: (visible) => set({ toolDetailModalVisible: visible }),
  
  setAgentDetailModalVisible: (visible) => set({ agentDetailModalVisible: visible }),

  setDeleteModalVisible: (visible) => set({ deleteModalVisible: visible }),
  
  setSelectedTool: (tool) => set({ selectedTool: tool }),
  
  setSelectedAgent: (agent) => set({ selectedAgent: agent }),
  
  createAgent: async (agent) => {
    try {
      await agentAPI.createOrUpdateAgent(agent);
      message.success('Agent创建成功');
      set({ createModalVisible: false });
      get().fetchAgents(); // Refresh the list
    } catch (error) {
      message.error('创建Agent失败');
      console.error('Error creating agent:', error);
    }
  },
  
  updateAgent: async (agent) => {
    try {
      await agentAPI.createOrUpdateAgent(agent);
      message.success('Agent更新成功');
      set({ editModalVisible: false });
      get().fetchAgents(); // Refresh the list
    } catch (error) {
      message.error('更新Agent失败');
      console.error('Error updating agent:', error);
    }
  },
  
  deleteAgent: async (id) => {
    const { agents } = get();
    // In a real app, you would call an API to delete the agent
    set({ agents: agents.filter(agent => agent.id !== id) });
    await agentAPI.deleteAgent(id);
    message.success('Agent删除成功');
    set({ deleteModalVisible: false });
    get().fetchAgents(); 
  },
  
  handleToolClick: (tool) => {
    set({ 
      selectedTool: tool,
      toolDetailModalVisible: true
    });
  },
  
  handleViewAgent: (agent) => {
    set({ 
      selectedAgent: agent,
      agentDetailModalVisible: true
    });
  },
  
  handleEditAgent: (agent) => {
    set({ 
      selectedAgent: agent,
      editModalVisible: true
    });
  },
  handleDeleteAgent: (agent) => {
    set({ 
      selectedAgent: agent,
      deleteModalVisible: true
    });
  }

}));
