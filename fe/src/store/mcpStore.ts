import { create } from 'zustand';
import { message } from 'antd';
import { mcpAPI } from '../services/api';
import type { MCPServer } from '../services/api';

interface MCPState {
  // Data
  mcpServers: MCPServer[];
  
  // UI State
  loading: boolean;
  createModalVisible: boolean;
  editModalVisible: boolean;
  detailModalVisible: boolean;
  deleteModalVisible: boolean;
  selectedServer: MCPServer | null;
  
  // Actions
  fetchMCPServers: () => Promise<void>;
  setCreateModalVisible: (visible: boolean) => void;
  setEditModalVisible: (visible: boolean) => void;
  setDetailModalVisible: (visible: boolean) => void;
  setDeleteModalVisible: (visible: boolean) => void;
  setSelectedServer: (server: MCPServer | null) => void;
  createMCPServer: (server: Omit<MCPServer, 'id'>) => Promise<void>;
  updateMCPServer: (server: MCPServer) => Promise<void>;
  deleteMCPServer: (id: string) => void;
  handleViewServer: (server: MCPServer) => void;
  handleEditServer: (server: MCPServer) => void;
  handleDeleteServer: (server: MCPServer) => void;
}

export const useMCPStore = create<MCPState>((set, get) => ({
  // Initial state
  mcpServers: [],
  loading: false,
  createModalVisible: false,
  editModalVisible: false,
  detailModalVisible: false,
  deleteModalVisible: false,
  selectedServer: null,
  
  // Actions
  fetchMCPServers: async () => {
    set({ loading: true });
    try {
      const data = await mcpAPI.getMCPServers();
      set({ mcpServers: data });
    } catch (error) {
      message.error('获取MCP服务器列表失败');
      console.error('Error fetching MCP servers:', error);
    } finally {
      set({ loading: false });
    }
  },
  
  setCreateModalVisible: (visible) => set({ createModalVisible: visible }),
  
  setEditModalVisible: (visible) => set({ editModalVisible: visible }),
  
  setDetailModalVisible: (visible) => set({ detailModalVisible: visible }),

  setDeleteModalVisible: (visible) => set({ deleteModalVisible: visible }),
  
  setSelectedServer: (server) => set({ selectedServer: server }),
  
  createMCPServer: async (server) => {
    try {
      await mcpAPI.createOrUpdateMCPServer(server);
      message.success('MCP服务器创建成功');
      set({ createModalVisible: false });
      get().fetchMCPServers(); // Refresh the list
    } catch (error) {
      message.error('创建MCP服务器失败');
      console.error('Error creating MCP server:', error);
    }
  },
  
  updateMCPServer: async (server) => {
    try {
      await mcpAPI.createOrUpdateMCPServer(server);
      message.success('MCP服务器更新成功');
      set({ editModalVisible: false });
      get().fetchMCPServers(); // Refresh the list
    } catch (error) {
      message.error('更新MCP服务器失败');
      console.error('Error updating MCP server:', error);
    }
  },
  
  deleteMCPServer: (id) => {
    try {
      // First update the UI immediately for better user experience
      const { mcpServers } = get();
      set({ mcpServers: mcpServers.filter(server => server.id !== id) });
      
      // Then call the API in the background
      mcpAPI.deleteMCPServer(id)
        .then(() => {
          message.success('MCP服务器删除成功');
          set({ deleteModalVisible: false });
          get().fetchMCPServers(); // Refresh the list
        })
        .catch((error) => {
          message.error('删除MCP服务器失败');
          console.error('Error deleting MCP server:', error);
          // Refresh the list to restore the server if API call failed
          get().fetchMCPServers();
        });
    } catch (error) {
      message.error('删除MCP服务器失败');
      console.error('Error deleting MCP server:', error);
    }
  },
  
  handleViewServer: (server) => {
    set({ 
      selectedServer: server,
      detailModalVisible: true
    });
  },
  
  handleEditServer: (server) => {
    set({ 
      selectedServer: server,
      editModalVisible: true
    });
  },
  handleDeleteServer: (server) => {
    set({ 
      selectedServer: server,
      deleteModalVisible: true
    });
  }

}));
