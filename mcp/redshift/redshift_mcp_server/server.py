from collections.abc import AsyncIterator
import logging
import os
import asyncio
import anyio
import redshift_connector
import click

from redshift_connector import Connection
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import Resource, ResourceTemplate, Tool, TextContent
from pydantic import AnyUrl

# init logger
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers= [
        logging.FileHandler('redshift_mcp_log.out')
    ]
)
logger = logging.getLogger('redshift-mcp-server')

rs_scheme = "rs://"
mime_txt = "text/plain"

# Init MCP Server
server = Server("redshift-mcp-server")
server.version = "0.1.0"

def get_redshift_config()-> dict[str, str]:
    """Get database configuration from environment variables."""
    config = {
        "host": os.getenv("RS_HOST", "localhost"),
        "port": os.getenv("RS_PORT", "5439"),
        "user": os.getenv("RS_USER", "awsuser"),
        "password": os.getenv("RS_PASSWORD"),
        "database": os.getenv("RS_DATABASE", "dev"),
        "schema": os.getenv("RS_SCHEMA", "public")
    }

    return config

@server.list_resources()
async def list_resources() -> list[Resource]:
    """List basic Redshift resources."""
    return [
        Resource(
            uri = AnyUrl(f"{rs_scheme}/schemas"),
            name = "All Schemas in Databases",
            description="List all schemas in Redshift database",
            mimeType = mime_txt
        )
    ]

@server.list_resource_templates()
async def list_resource_templates() -> list[ResourceTemplate]:
    """Tables/DDL/statistic Resource Templates"""
    return [
        ResourceTemplate(
            uriTemplate= f"{rs_scheme}/{{schema}}/tables",
            name = "Schema Tables",
            description="List all tables in a schema",
            mimeType= mime_txt
        ),
        ResourceTemplate(
            uriTemplate= f"{rs_scheme}/{{schema}}/{{table}}/ddl",
            name = "Table DDL",
            description="Get a table's DDL script",
            mimeType= mime_txt
        ),
        ResourceTemplate(
            uriTemplate= f"{rs_scheme}/{{schema}}/{{table}}/statistic",
            name = "Table Statistic",
            description="Get statistic of a table",
            mimeType= mime_txt
        )
    ]

@server.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Get resource content based on URI."""
    config = get_redshift_config()
    uri_str = str(uri)

    if not (uri_str.startswith(rs_scheme)):
      raise ValueError(f"Invalid URI schema: {uri}")

    try:
        conn = redshift_connector.connect(
            host=config['host'],
            port=int(config['port']),
            user=config['user'],
            password=config['password'],
            database=config['database'],
        )
        conn.autocommit = True
        # split rs:/// URI path
        path_parts = uri_str[6:].split('/')

        if path_parts[0] == 'schemas':
            # list all schemas
            return _get_schemas(conn)
        elif len(path_parts) == 2 and path_parts[1] == "tables":
            # list all tables
            return _get_tables(conn, path_parts[0])
        elif len(path_parts) == 3 and path_parts[2] == "ddl":
            # get table dll
            schema, table  = path_parts[0], path_parts[1]
            return _get_table_ddl(conn, schema, table)
        elif len(path_parts) == 3 and path_parts[2] == "statistic":
            # get table dll
            schema, table  = path_parts[0], path_parts[1]
            return _get_table_statistic(conn, schema, table)

    except Exception as e:
        raise RuntimeError(f"Redshift Error: {str(e)}")
    finally:
        conn.close()

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Redsfhit tools"""
    logger.info("List available tools...")

    return [
        Tool(
            name="execute_sql",
            description="Execute a SQL Query on the Redshift cluster",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL to Execute"
                    }
                },
                "required": ["sql"]
            }
        ),
        Tool(
            name="analyze_table",
            description="Analyze table to collect statistics information",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema": {
                        "type": "string",
                        "description": "Schema name"
                    },
                    "table": {
                        "type": "string",
                        "description": "Table name"
                    }
                },
                "required": ["schema", "table"]
            }
        ),
        Tool(
            name="get_execution_plan",
            description="Get actual execution plan with runtime statistics for a SQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to analyze"
                    }
                },
                "required": ["sql"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, args: dict) -> list[TextContent]:
    """Execute SQL"""
    config=get_redshift_config()
    sql = ''

    if name == "execute_sql":
        sql = args.get("sql")
        if not sql:
            raise ValueError("sql parameter is required when calling execute_sql tool")
    elif name == "analyze_table":
        schema = args.get("schema")
        table = args.get("table")
        if not all([schema, table]):
            raise ValueError("'schema' and 'table' parameters are required when calling analyze_table tool")
        sql = f"ANALYZE {schema}.{table}"
    elif name == "get_execution_plan":
        sql = args.get("sql")
        if not sql:
            raise ValueError("sql parameter is required when calling get_query_plan tool")
        sql = f"EXPLAIN {sql}"

    try:
        conn = redshift_connector.connect(
            host=config['host'],
            port=int(config['port']),
            user=config['user'],
            password=config['password'],
            database=config['database'],
        )
        conn.autocommit = True

        with conn.cursor() as cursor:
            cursor.execute(sql)
            if name == "analyze_table":
                return [TextContent(type="text", text=f"Successfully analyzed table {schema}.{table}")]

            if cursor.description is None:
                return [TextContent(type="text", text=f"Successfully execute sql {sql}")]

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [",".join(map(str, row)) for row in rows]
            return [TextContent(type="text", text="\n".join([",".join(columns)] +  result ))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing query: {str(e)}")]
    finally:
        conn.close()


def _get_schemas(conn: Connection ) -> str:
   """Get all schemas from redshift database"""
   sql = """
        SELECT nspname AS schema_name
        FROM pg_namespace
        WHERE nspname NOT LIKE 'pg_%'
            AND nspname != 'information_schema'
            AND nspname != 'catalog_history'
        ORDER BY schema_name
   """
   with conn.cursor() as cursor:
       cursor.execute(sql)
       rows = cursor.fetchall()
       schemas = [row[0] for row in rows]
       return "\n".join(schemas)

def _get_tables(conn: Connection, schema: str) -> str:
   """Get all tables in a schema from redshift database."""
   sql = f"""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = '{schema}'
        GROUP BY table_name
        ORDER BY table_name
   """
   with conn.cursor() as cursor:
       cursor.execute(sql)
       rows = cursor.fetchall()
       tables = [row[0] for row in rows]
       return "\n".join(tables)

def _get_table_ddl(conn: Connection, schema: str, table: str) -> str:
   """Get DDL for a table from redshift database."""
   with conn.cursor() as cursor:
       cursor.execute(f"show table {schema}.{table}")
       ddl = cursor.fetchone()
       return ddl[0] if ddl and ddl[0] else f"No DDL found for {schema}.{table}"

def _get_table_statistic(conn: Connection, schema: str, table: str) -> str:
   """Get statistic for a table from redshift database."""
   with conn.cursor() as cursor:
       cursor.execute(f"ANALYZE {schema}.{table};")
       return f"ANALYZE {schema}.{table} command executed"

@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    help="Transport type",
)
@click.option("--port", default=3000, help="Port to listen on for HTTP")
@click.option("--env_file", default=".env", help="Redshift MCP env file path")
def run(transport: str, port: int, env_file: str) -> int:

    if transport == 'stdio':
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as (read_stream, write_stream):
                try:
                    logger.info("start to init Redshift MCP Server")
                    await server.run(
                        read_stream,
                        write_stream,
                        server.create_initialization_options()
                    )
                except Exception as e:
                    logger.warn(f"MCP Server Error: {str(e)}")
                    raise

        anyio.run(arun)
    elif transport == 'http':
        session_manager = StreamableHTTPSessionManager(
            app = server,
            json_response = True
        )
        from starlette.applications import Starlette
        from starlette.types import Receive, Scope, Send
        from starlette.routing import Mount, Route
        from starlette.responses import JSONResponse
        from dotenv import load_dotenv
        import contextlib

        load_dotenv(dotenv_path = env_file)

        async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
            await session_manager.handle_request(scope, receive, send)

        async def health(request):
            return JSONResponse({'hello': 'world'})

        @contextlib.asynccontextmanager
        async def lifespan(app: Starlette) -> AsyncIterator[None]:
            """Context Manager for Session Manager"""
            async with session_manager.run():
                logger.info("Application started with StreamableHTTP session manager!")
                try:
                    yield
                finally:
                    logger.info("Application shutting down...")

        starlette_app = Starlette(
            routes=[
                Mount("/rs_mcp", app= handle_streamable_http),
                Route("/health", health, methods=["GET"])
            ],
            lifespan= lifespan
        )

        import uvicorn

        uvicorn.run(starlette_app, host="0.0.0.0", port = port)

    return 0

if __name__ == "__main__":
    asyncio.run(run())
