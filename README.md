# Strands Agentic - AgentX

AgentX is an agent management platform built on top of the Strands framework, allowing you to create, manage, and orchestrate AI agents with various tools and capabilities. It follows the principle:

**Agent = LLM Model + System Prompt + Tools + Environment**

## 🌟 Features

- **Agent Management**: Create, configure, and manage AI agents through a user-friendly interface
- **Multiple Model Support**: Use models from Bedrock, OpenAI, Anthropic, LiteLLM, Ollama, or custom providers
- **Extensive Tool Library**: Equip agents with tools for RAG, file operations, web interactions, image generation, and more
- **Agent Orchestration**: Create orchestrator agents that can coordinate with other agents
- **Scheduling**: Schedule agent tasks to run automatically at specified times
- **MCP Integration**: Extend agent capabilities with Model Context Protocol servers

## 🏗️ Architecture

The project consists of three main components:

### 🔙 Backend (be/)

A FastAPI-based API server that provides:
- RESTful APIs for agent management
- WebSocket endpoints for streaming chat with agents
- Integration with AWS services (DynamoDB, EventBridge, Lambda)

### 🖥️ Frontend (fe/)

A React/TypeScript application built with:
- Vite for fast development and optimized builds
- Ant Design for UI components
- Zustand for state management
- TypeScript for type safety

### 🔌 MCP Servers (mcp/)

Model Context Protocol servers that extend agent capabilities:
- **MySQL MCP**: Tools for interacting with MySQL databases
- **Redshift MCP**: Tools for interacting with Amazon Redshift

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Node.js 18+ and Bun
- Docker (for containerized deployment)
- AWS account (for AWS services)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/agentx.git
   cd agentx
   ```

2. **Set up the backend**:
   ```bash
   cd be
   uv sync
   uvicorn app.main:app --reload
   ```

3. **Set up the frontend**:
   ```bash
   cd fe
   bun install
   bun run dev
   ```

4. **Set up MCP servers** (optional):
   ```bash
   # For MySQL MCP
   cd mcp/mysql
   bun install
   bun run index.ts --transport http --port 3000
   
   # For Redshift MCP
   cd mcp/redshift
   uv sync
   python -m redshift_mcp_server --transport streamable-http --port 3001
   ```

## 📦 Deployment

For detailed deployment instructions, see [README-DEPLOYMENT.md](README-DEPLOYMENT.md).

## 📚 Documentation

- [Backend API Documentation](be/README.md)
- [Frontend Documentation](fe/README.md)
- [MySQL MCP Server Documentation](mcp/mysql/README.md)
- [Redshift MCP Server Documentation](mcp/redshift/README.md)

## 🛠️ Technologies

- **Backend**: FastAPI, Strands, Boto3, DynamoDB, EventBridge
- **Frontend**: React, TypeScript, Vite, Ant Design, Zustand
- **MCP Servers**: Python, Bun, MySQL, Redshift
- **Deployment**: Docker, AWS CDK, ECS, ECR

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
