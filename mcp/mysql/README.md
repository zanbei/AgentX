# MySQL MCP Server

A Model Context Protocol (MCP) server for MySQL databases that enables AI agents to interact with MySQL databases.

## 🌟 Features

- **Dynamic Resources**:
  - List all databases
  - List all tables in a database
  - View table DDL information
  - Get table statistics

- **Powerful Tools**:
  - `execute_sql`: Execute SQL queries on MySQL databases
  - `get_table_count`: Get the number of tables in a database
  - `get_total_row_count`: Get the total number of rows across all tables
  - `get_topN_tables`: Get the top N largest tables in a database

- **Multiple Transport Types**:
  - STDIO for command-line integration
  - HTTP for network-based integration

## 🏗️ Architecture

The MySQL MCP server follows the Model Context Protocol specification and provides:

- **Resources**: URI-addressable data sources
- **Tools**: Functions that can be called by AI agents
- **Transport Layer**: Communication methods (STDIO, HTTP)

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ or Bun
- MySQL database
- MySQL credentials (host, port, username, password, database)

### Installation

```bash
# Using npm
npm install

# Using Bun (recommended)
bun install
```

### Configuration

Create a `.env` file based on the provided `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file to configure your MySQL connection:

```
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=your_database_here

# Server Configuration
SERVER_PORT=3000
TRANSPORT_TYPE=http  # 'stdio' or 'http'
```

### Running the Server

```bash
# Using STDIO transport
bun run index.ts

# Using HTTP transport
bun run index.ts --transport http --port 3000
```

## 📚 Usage

### Resources

Access MySQL database information through these resource URIs:

- `mysql:///databases` - Lists all databases
- `mysql:///{database}/tables` - Lists all tables in a specific database
- `mysql:///{database}/{table}/ddl` - Gets the DDL script for a specific table
- `mysql:///{database}/{table}/statistics` - Gets statistics for a specific table

### Tools

The server provides the following tools:

#### execute_sql

Execute SQL queries on MySQL databases.

```json
{
  "sql": "SELECT * FROM users LIMIT 10",
  "database": "mydb"  // Optional, uses default if not specified
}
```

#### get_table_count

Get the number of tables in a database.

```json
{
  "database": "mydb"  // Optional, uses default if not specified
}
```

#### get_total_row_count

Get the total number of rows across all tables in a database.

```json
{
  "database": "mydb"  // Optional, uses default if not specified
}
```

#### get_topN_tables

Get the top N largest tables in a database.

```json
{
  "database": "mydb",  // Optional, uses default if not specified
  "limit": 5  // Optional, defaults to 10
}
```

## 🔧 Command-line Options

```
Options:
  -t, --transport <type>  Transport type (stdio or http) (default: "stdio")
  -p, --port <port>       HTTP server port (for http transport) (default: "3000")
  -h, --help              Display help for command
  -V, --version           Output the version number
```

## 🛠️ Development

### Project Structure

```
mysql/
├── src/
│   ├── config.ts
│   ├── index.ts
│   ├── db/
│   │   ├── connection-test.ts
│   │   └── mysql-connection.ts
│   └── mcp/
│       └── server.ts
├── Dockerfile
├── package.json
├── tsconfig.json
└── README.md
```

### Adding New Tools

To add a new tool:

1. Edit `src/mcp/server.ts`
2. Add a new tool definition
3. Implement the tool's functionality
4. Update the README with documentation

## 📦 Deployment

For deployment instructions, see the [main deployment guide](../../README-DEPLOYMENT.md).

## 🔗 Dependencies

- **mcp**: Model Context Protocol SDK
- **mysql2**: MySQL client for Node.js
- **dotenv**: Environment variable management
- **commander**: Command-line interface
