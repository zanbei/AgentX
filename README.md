# Strands Agentic - AgentX

AgentX is an agent management platform built on top of the Strands framework, allowing you to create, manage, and orchestrate AI agents with various tools and capabilities.

## Project Structure

The project is organized into three main components:

- **Backend (be/)**: FastAPI-based API server for agent management
- **Frontend (fe/)**: Bun-based TypeScript frontend (in development)
- **MCP Servers (mcp/)**: Model Context Protocol servers for extending agent capabilities
  - Redshift MCP: Provides tools for interacting with Amazon Redshift
  - MySQL MCP: Provides tools for interacting with MySQL databases

## Backend

The backend is built with FastAPI and provides APIs for:

- Creating agents
- Listing agents
- Getting agent details
- Deleting agents
- Streaming chat with agents

### Agent Types

- **Plain Agent**: Standard agent with tools
- **Orchestrator Agent**: Agent that can coordinate with other agents

### Model Providers

The system supports multiple model providers:
- Bedrock
- OpenAI
- Anthropic
- LiteLLM
- Ollama
- Custom

### Tools

Agents can be equipped with various tools:

- **RAG & Memory**: Knowledge retrieval and memory persistence
- **FileOps**: File reading, writing, and editing
- **Web & Network**: HTTP requests and Slack integration
- **Multi-modal**: Image processing and generation
- **AWS Services**: AWS service interactions
- **Utilities**: Calculations and time-related functions

## MCP Servers

### Redshift MCP Server

Provides tools for interacting with Amazon Redshift:
- Executing SQL queries
- Analyzing tables
- Getting execution plans
- Listing schemas and tables
- Getting table DDL and statistics

### MySQL MCP Server

Provides tools for interacting with MySQL databases (in development).

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd be
   ```
o
2. Install dependencies:
   ```
   uv sync
   ```

3. Run the FastAPI server:
   ```
   uvicorn app.main:app --reload
   or
   uv run fastapi --dev
   ```

### MCP Server Setup

#### Redshift MCP Server

1. Navigate to the Redshift MCP directory:
   ```
   cd mcp/redshift
   ```

2. Install dependencies:
   ```
   uv sync
   ```

3. Set up environment variables in a `.env` file:
   ```
   RS_HOST=your-redshift-host
   RS_PORT=5439
   RS_USER=your-username
   RS_PASSWORD=your-password
   RS_DATABASE=your-database
   RS_SCHEMA=public
   ```

4. Run the MCP server:
   ```
   python -m redshift_mcp_server --transport streamable-http --port 3000 --env_file .env
   or
   uv run redshift-mcp-server --port 3000 --transport streaming-http
   ```

## API Endpoints

- `GET /agent/list`: List all agents
- `GET /agent/get/{agent_id}`: Get agent details
- `DELETE /agent/delete/{agent_id}`: Delete an agent
- `POST /agent/create`: Create a new agent
- `POST /agent/stream_chat`: Stream chat with an agent

## Development

The project is under active development. The frontend is currently in early stages.

## Dependencies

- Python 3.13+
- FastAPI
- Strands Framework
- Boto3 (for AWS services)
- Redshift Connector
- Bun (for frontend)
