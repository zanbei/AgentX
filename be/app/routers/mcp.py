
from fastapi import APIRouter, Request

from ..mcp.mcp import HttpMCPServer, MCPService


mcp_service = MCPService()

router = APIRouter(
    prefix="/mcp",
    tags=["mcp"],
    responses={404: {"description": "Not found"}}
)


@router.get("/list")
def list_mcp_servers() -> list[HttpMCPServer]:
    """
    List all MCP servers.
    :return: A list of MCP servers.
    """
    return mcp_service.list_mcp_servers()

@router.get("/get/{server_id}")
def get_mcp_server(server_id: str) -> HttpMCPServer | None:
    """
    Get a specific MCP server by ID.
    :param server_id: The ID of the MCP server to retrieve.
    :return: Details of the specified MCP server.
    """
    return mcp_service.get_mcp_server(server_id)

@router.delete("/delete/{server_id}")
def delete_mcp_server(server_id: str) -> bool:
    """
    Delete a specific MCP server by ID.
    :param server_id: The ID of the MCP server to delete.
    :return: True if deletion was successful, False otherwise.
    """
    return mcp_service.delete_mcp_server(server_id)

@router.post("/createOrUpdate")
async def create_mcp_server(server: Request) -> HttpMCPServer:
    """
    Create or update an MCP server.
    :param server: The MCP server data to create or update.
    :return: Confirmation of MCP server creation or update.
    """
    server_data = await server.json()
    server = HttpMCPServer(
        id=server_data.get("id"),
        name=server_data.get("name"),
        desc=server_data.get("desc"),
        host=server_data.get("host")
    )
    mcp_service.add_mcp_server(server)
    return server