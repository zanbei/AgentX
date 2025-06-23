# MySQL MCP Server

A Model Context Protocol (MCP) server for interacting with MySQL databases. This server provides dynamic resources for browsing databases and tables, as well as tools for executing SQL queries and retrieving database statistics.

## Features

- **Dynamic Resources**:
  - List all databases
  - List all tables in a database
  - View table DDL information

- **Tools**:
  - `execute_sql`: Execute SQL queries on MySQL databases
  - `get_table_count`: Get the number of tables in a database
  - `get_total_row_count`: Get the total number of rows across all tables
  - `get_topN_tables`: Get the top N largest tables in a database

- **Transport Types**:
  - STDIO for command-line integration
  - HTTP for network-based integration

## Installation

```bash
bun install
```

## Configuration

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
TRANSPORT_TYPE=stdio  # 'stdio' or 'http'
```

## Usage

### Start with STDIO transport (default)

```bash
bun run index.ts
```

### Start with HTTP transport

```bash
bun run index.ts --transport http --port 3000
```

### Command-line options

```
Options:
  -t, --transport <type>  Transport type (stdio or http) (default: "stdio")
  -p, --port <port>       HTTP server port (for http transport) (default: "3000")
  -h, --help              Display help for command
  -V, --version           Output the version number
```

## Development

This project was created using `bun init` in bun v1.1.34. [Bun](https://bun.sh) is a fast all-in-one JavaScript runtime.
