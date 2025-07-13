
import uuid
import boto3
from pydantic import BaseModel
from ..utils.aws_config import get_aws_region

class HttpMCPServer(BaseModel):
   id: str | None = None
   name: str
   desc: str
   host: str


class MCPService:

    dynamodb_table_name = "HttpMCPTable"

    def __init__(self):
        aws_region = get_aws_region()
        self.dynamodb = boto3.resource('dynamodb', region_name=aws_region)

    def add_mcp_server(self, server: HttpMCPServer):
        if not server.id:
            server.id = uuid.uuid4().hex
        self.dynamodb.Table(self.dynamodb_table_name).put_item(
            Item={
                'id': server.id,
                'name': server.name,
                'desc': server.desc,
                'host': server.host
            }
        )

    def list_mcp_servers(self) -> list[HttpMCPServer]:
        response = self.dynamodb.Table(self.dynamodb_table_name).scan()
        items = response.get('Items', [])
        self.mcp_servers = [HttpMCPServer.model_validate(item) for item in items]
        return self.mcp_servers
        

    def get_mcp_server(self, id: str) -> HttpMCPServer | None:
        response = self.dynamodb.Table(self.dynamodb_table_name).get_item(
            Key={'id': id}
        )
        item = response.get('Item')
        if item:
            return HttpMCPServer.model_validate(item)
        return None
        

    def delete_mcp_server(self, id: str) -> bool:
        response = self.dynamodb.Table(self.dynamodb_table_name).delete_item(
            Key={'id': id}
        )
        return response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200
