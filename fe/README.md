# AgentX Frontend

The frontend component of the AgentX platform, built with React, TypeScript, and Vite.

## 🌟 Features

- **Agent Management**: Create, configure, and manage AI agents
- **Chat Interface**: Interactive chat with agents
- **Schedule Management**: Create and manage scheduled agent tasks
- **MCP Integration**: Connect with Model Context Protocol servers
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

The frontend is organized using a component-based architecture:

- **src/components/**: UI components
  - **agent/**: Agent management components
  - **chat/**: Chat interface components
  - **layout/**: Layout components
  - **mcp/**: MCP integration components
  - **schedule/**: Schedule management components
  - **sidebar/**: Sidebar navigation components
- **src/store/**: State management using Zustand
- **src/services/**: API services
- **src/hooks/**: Custom React hooks
- **src/utils/**: Utility functions
- **src/styles/**: Global styles and themes

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ or Bun
- Backend server running

### Installation

1. Install dependencies:
   ```bash
   # Using npm
   npm install
   
   # Using Bun (recommended)
   bun install
   ```

2. Set up environment variables:
   Create a `.env` file with:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```

### Running the Application

For development:
```bash
# Using npm
npm run dev

# Using Bun
bun run dev
```

For production build:
```bash
# Using npm
npm run build

# Using Bun
bun run build
```

## 🧩 Components

### Agent Components

- **Agent.tsx**: Main agent management component
- **AgentForm.tsx**: Form for creating and editing agents
- **AgentList.tsx**: List of available agents
- **AgentDetail.tsx**: Detailed view of an agent

### Chat Components

- **Chat.tsx**: Main chat interface component
- **ChatList.tsx**: List of chat messages
- **ChatInput.tsx**: Input for sending messages to agents

### Schedule Components

- **Schedule.tsx**: Main schedule management component
- **ScheduleForm.tsx**: Form for creating and editing schedules
- **ScheduleList.tsx**: List of scheduled tasks

### MCP Components

- **MCP.tsx**: Main MCP management component
- **MCPForm.tsx**: Form for adding and configuring MCP servers

## 🔧 Configuration

The frontend can be configured through environment variables:

- `VITE_API_BASE_URL`: URL of the backend API
- `VITE_WS_BASE_URL`: WebSocket URL for chat streaming
- `VITE_DEFAULT_AGENT_ID`: Default agent ID to use (optional)

## 🛠️ Development

### Project Structure

```
fe/
├── public/
│   └── vite.svg
├── src/
│   ├── App.css
│   ├── App.tsx
│   ├── index.css
│   ├── main.tsx
│   ├── vite-env.d.ts
│   ├── assets/
│   ├── components/
│   │   ├── index.ts
│   │   ├── agent/
│   │   ├── chat/
│   │   ├── config/
│   │   ├── layout/
│   │   ├── mcp/
│   │   ├── schedule/
│   │   └── sidebar/
│   ├── constants/
│   ├── hooks/
│   ├── services/
│   ├── store/
│   ├── styles/
│   ├── types/
│   └── utils/
├── Dockerfile
├── eslint.config.js
├── index.html
├── package.json
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── README.md
```

### Code Style

This project uses ESLint for code linting. To run the linter:

```bash
# Using npm
npm run lint

# Using Bun
bun run lint
```

### Testing

Run tests with:

```bash
# Using npm
npm test

# Using Bun
bun test
```

## 📦 Deployment

For deployment instructions, see the [main deployment guide](../README-DEPLOYMENT.md).

## 🔗 Dependencies

- **React**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and development server
- **Ant Design**: UI component library
- **Zustand**: State management
- **Axios**: HTTP client
