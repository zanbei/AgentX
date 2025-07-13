# AgentX Backend

The backend component of the AgentX platform, built with FastAPI and the Strands framework.

## 🌟 Features

- **Agent Management**: Create, list, get, and delete agents
- **Chat Interface**: Stream chat with agents using WebSockets
- **Schedule Management**: Create and manage scheduled agent tasks
- **MCP Integration**: Connect with Model Context Protocol servers
- **AWS Integration**: Interact with AWS services (DynamoDB, EventBridge, Lambda)

## 🏗️ Architecture

The backend is organized into the following modules:

- **app/main.py**: Main FastAPI application entry point
- **app/agent/**: Agent management and interaction logic
- **app/routers/**: API route definitions
- **app/mcp/**: Model Context Protocol integration
- **app/schedule/**: Scheduling service for agent tasks

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- uv (Python package manager)
- AWS credentials (for AWS services)

### Installation

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables:
   ```bash
   # AWS credentials
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-west-2
   ```

### Running the Server

For development:
```bash
uvicorn app.main:app --reload
```

For production:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Agent Management

- `GET /agent/list`: List all agents
- `GET /agent/get/{agent_id}`: Get agent details
- `POST /agent/create`: Create a new agent
- `DELETE /agent/delete/{agent_id}`: Delete an agent
- `POST /agent/stream_chat`: Stream chat with an agent

#### Schedule Management

- `GET /schedule/list`: List all schedules
- `POST /schedule/create`: Create a new schedule
- `PUT /schedule/update/{schedule_id}`: Update a schedule
- `DELETE /schedule/delete/{schedule_id}`: Delete a schedule

#### MCP Management

- `GET /mcp/list`: List all MCP servers
- `POST /mcp/add`: Add a new MCP server
- `DELETE /mcp/delete/{mcp_id}`: Delete an MCP server

## 🧩 Agent Types

### Plain Agent

Standard agent with tools:
- RAG & Memory tools
- FileOps tools
- Web & Network tools
- Multi-modal tools
- AWS Services tools
- Utility tools

### Orchestrator Agent

Agent that can coordinate with other agents:
- Can use other agents as tools
- Can delegate tasks to specialized agents
- Can aggregate results from multiple agents

## 🔧 Configuration

The backend can be configured through environment variables:

- `AWS_REGION`: AWS region for services (default: us-west-2)
- `DYNAMODB_ENDPOINT`: Custom DynamoDB endpoint (optional)
- `EVENTBRIDGE_ENDPOINT`: Custom EventBridge endpoint (optional)
- `LAMBDA_FUNCTION_ARN`: ARN for the Lambda function (for scheduling)
- `SCHEDULE_ROLE_ARN`: ARN for the EventBridge scheduler role

## 🛠️ Development

### Project Structure

```
be/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── event_models.py
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── mcp.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── chat_record.py
│   │   ├── mcp.py
│   │   └── schedule.py
│   └── schedule/
│       ├── __init__.py
│       ├── models.py
│       └── service.py
├── Dockerfile
├── pyproject.toml
└── README.md
```

### Testing

Run tests with:
```bash
pytest
```

## 📦 Deployment

For deployment instructions, see the [main deployment guide](../README-DEPLOYMENT.md).

## 🔗 Dependencies

- **FastAPI**: Web framework for building APIs
- **Strands**: Framework for building AI agents
- **Boto3**: AWS SDK for Python
- **Pydantic**: Data validation and settings management
- **WebSockets**: For streaming chat responses
