# Redshift MCP Server

A Model Context Protocol (MCP) server for Amazon Redshift that enables AI agents to interact with Redshift databases.

## 🌟 Features

- **Dynamic Resources**:
  - List all schemas in a database
  - List all tables in a schema
  - View table DDL information
  - Get table statistics

- **Powerful Tools**:
  - `execute_sql`: Execute SQL queries on Redshift databases
  - `analyze_table`: Analyze a table to collect statistics information
  - `get_execution_plan`: Get the execution plan for a SQL query

- **Multiple Transport Types**:
  - STDIO for command-line integration
  - HTTP for network-based integration

## 🏗️ Architecture

The Redshift MCP server follows the Model Context Protocol specification and provides:

- **Resources**: URI-addressable data sources
- **Tools**: Functions that can be called by AI agents
- **Transport Layer**: Communication methods (STDIO, HTTP)

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Amazon Redshift cluster
- Redshift credentials (host, port, username, password, database)

### Installation

```bash
# Install dependencies
uv sync
```

### Configuration

Create a `.env` file with your Redshift connection details:

```
# Redshift Configuration
RS_HOST=your-redshift-cluster.region.redshift.amazonaws.com
RS_PORT=5439
RS_USER=your_username
RS_PASSWORD=your_password
RS_DATABASE=your_database
RS_SCHEMA=public  # Optional, defaults to "public"

# Server Configuration
SERVER_PORT=3001
TRANSPORT_TYPE=streamable-http  # 'stdio' or 'streamable-http'
```

### Running the Server

```bash
# Using STDIO transport
python -m redshift_mcp_server

# Using HTTP transport
python -m redshift_mcp_server --transport streamable-http --port 3001
```

## 📚 Usage

### Resources

Access Redshift database information through these resource URIs:

- `rs:///schemas` - Lists all schemas in the database
- `rs:///{schema}/tables` - Lists all tables in a specific schema
- `rs:///{schema}/{table}/ddl` - Gets the DDL script for a specific table
- `rs:///{schema}/{table}/statistics` - Gets statistics for a specific table

### Tools

The server provides the following tools:

#### execute_sql

Execute SQL queries on Redshift databases.

```json
{
  "sql": "SELECT * FROM users LIMIT 10"
}
```

#### analyze_table

Analyze a table to collect statistics information.

```json
{
  "schema": "public",
  "table": "users"
}
```

#### get_execution_plan

Get the execution plan for a SQL query.

```json
{
  "sql": "SELECT * FROM users WHERE user_id = 123"
}
```

## 🔧 Command-line Options

```
Options:
  --transport TRANSPORT     Transport type (stdio or streamable-http) (default: stdio)
  --port PORT               HTTP server port (for streamable-http transport) (default: 3001)
  --env_file ENV_FILE       Path to .env file (default: .env)
  --help                    Show this help message and exit
```

## 🛠️ Development

### Project Structure

```
redshift/
├── redshift_mcp_server/
│   ├── __init__.py
│   ├── __main__.py
│   └── server.py
├── Dockerfile
├── pyproject.toml
├── pyrightconfig.json
└── README.md
```

### Adding New Tools

To add a new tool:

1. Edit `redshift_mcp_server/server.py`
2. Add a new tool definition
3. Implement the tool's functionality
4. Update the README with documentation

## 📦 Deployment

For deployment instructions, see the [main deployment guide](../../README-DEPLOYMENT.md).

## 🔗 Dependencies

- **mcp[cli]**: Model Context Protocol SDK
- **python-dotenv**: Environment variable management
- **redshift-connector**: Python connector for Amazon Redshift

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
