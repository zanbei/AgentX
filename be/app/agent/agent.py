import boto3, uuid
import importlib
import json
import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"
from boto3.dynamodb.conditions import Attr
from strands import Agent, tool
from strands.models import BedrockModel
from strands.models.bedrock import BotocoreConfig
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from ..mcp.mcp import MCPService
from .event_serializer import EventSerializer
from ..utils.aws_config import get_aws_region

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel

AgentType  = Enum("AgentType", ("plain", "orchestrator"))
ModelProvider = Enum("ModelProvider", ("bedrock", "openai", "anthropic", "litellm", "ollama", "custom"))
AgentToolType = Enum("AgentToolType", ("strands", "mcp", "agent", "python"))

class Tools(Enum):

    retrieve = "RAG & Memory","retrieve", "Retrive data from Amazon Bedrock Knowledge Base for RAG, memory, and other purpose"
    memory = "RAG & Memory", "memory", "Agent memory persistence in Amazon Bedrock Knowledge Bases"
    mem0_memory = "RAG & Memory", "mem0_memory", "Agent memory and personalization built on top of Mem0"

    editor = "FileOps", "editor", "File editing operations like line edits, search, and undo"
    file_read = "FileOps", "file_read", "Read and parse files"
    file_write = "FileOps", "file_write", "Create and modify files"

    http_request = "Web & Network", "http_request", "Make API calls, fetch web data, and call local HTTP servers"
    slack = "Web & Network", "slack", "Slack integration with real-time events, API access, and message sending"

    image_reader = "Multi-modal", "image_reader", "Process and analyze images"
    generate_image = "Multi-modal", "generate_image", "Create AI generated images with Amazon Bedrock"
    nova_reels = "nova_reels", "nova_reels", "Create AI generated videos with Nova Reels on Amazon Bedrock"
    speak = "nova_reels", "speak", "Generate speech from text using macOS say command or Amazon Polly"

    use_aws = "AWS Services", "use_aws","Interact with AWS services"

    calculator = "Utilities", "calculator","Perform calculations and mathematical operations"
    current_time = "Utilities", "current_time", "Get the current time and date"
    
    agentCoreBrowser = "Browser", "browser.AgentCoreBrowser.browser","Interact with web browsers, take screenshots, and perform web automation"
    agentCodeInterpreter = "Code", "code_interpreter.AgentCoreCodeInterpreter.code_interpreter","Perform code execution, data analysis, and file operations using the Code Interpreter tool"


    def __init__(self, category: str, identify:str, desc: str):
        super().__init__()
        self._category = category
        self._desc = desc
        self._identify = identify

    @property
    def desc(self):
        return self._desc

    @property
    def category(self):
        return self._category
    
    @property
    def identify(self):
        return self._identify

    @classmethod
    def getToolByName(cls, name: str) -> Optional:
        for t in Tools:
            if t.name == name:
                return t
        return None

    def __repr__(self):
        return f"Tools(name={self.name}, category={self.category}, identify = {self.identify}, desc={self.desc})"


class HttpMCPSerer(object):
    def __init__(self, name: str, desc: str, url: str):
        self.name = name
        self.desc = desc
        self.url = url

    def __repr__(self):
        return f"HttpMCPSerer(name={self.name}, desc={self.desc}, url={self.url})"

class AgentTool(BaseModel):
    name: str
    display_name: Optional[str] = None
    category: str
    desc:str
    type: AgentToolType = AgentToolType.strands
    mcp_server_url: Optional[str] = None
    agent_id: Optional[str] = None
    extra: Optional[dict] = None

    def __repr__(self):
        return f"AgentTool(name={self.name}, display_name={self.display_name} ,category={self.category},  " \
               f"desc={self.desc}, type={self.type}, mcp_server_url={self.mcp_server_url}, "\
               f"agent_id={self.agent_id}, extra={self.extra})"
    
class AgentPO(BaseModel):
    id: str
    name: str
    display_name: str
    description: str
    agent_type: AgentType = AgentType.plain
    model_provider: ModelProvider = ModelProvider.bedrock
    model_id: str = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    sys_prompt: str = "You are a helpful assistant."
    tools: List[AgentTool] = []
    envs: str = ""
    extras: Optional[dict] = None

    def __repr__(self):
        return f"AgentPO(name={self.name}, display_name={self.display_name} description={self.description}, " \
               f"agent_type={self.agent_type}, model_provider={self.model_provider}, " \
               f"model_id={self.model_id}, sys_prompt={self.sys_prompt}, tools={self.tools}, envs={self.envs})"


class AgentPOBuilder:
    def __init__(self):
        self._agent_po = AgentPO(id="", name="", display_name="", description="")

    def set_id(self, id: str):
        self._agent_po.id = id
        return self

    def set_name(self, name: str):
        self._agent_po.name = name
        return self

    def set_display_name(self, display_name: str):
        self._agent_po.display_name = display_name
        return self

    def set_description(self, description: str):
        self._agent_po.description = description
        return self

    def set_agent_type(self, agent_type: AgentType):
        self._agent_po.agent_type = agent_type
        return self

    def set_model_provider(self, model_provider: ModelProvider):
        self._agent_po.model_provider = model_provider
        return self

    def set_model_id(self, model_id: str):
        self._agent_po.model_id = model_id
        return self

    def set_sys_prompt(self, sys_prompt: str):
        self._agent_po.sys_prompt = sys_prompt
        return self

    def set_tools(self, tools: List[AgentTool]):
        self._agent_po.tools = tools
        return self
        
    def set_envs(self, envs: str):
        self._agent_po.envs = envs
        return self

    def build(self) -> AgentPO:
        return self._agent_po



class AgentPOService:
    """
    A service to manage AgentPO objects.It allows adding, retrieving, and listing agents from Amazon DynamoDB.
    """

    dynamodb_table_name = "AgentTable"

    def __init__(self):
        aws_region = get_aws_region()
        self.dynamodb = boto3.resource('dynamodb', region_name=aws_region)

    def add_agent(self, agent_po: AgentPO):
        """
        Add an AgentPO object to Amazon DynamoDB

        :param agent_po: The AgentPO object to add.
        :raises ValueError: If an agent with the same name already exists.
        :return: None
        """
        if not isinstance(agent_po, AgentPO):
            raise TypeError("agent_po must be an instance of AgentPO")

        # write to DynamoDB
        table = self.dynamodb.Table(self.dynamodb_table_name)
        item = {
            'id': agent_po.id,
            'name': agent_po.name,
            'display_name': agent_po.display_name,
            'description': agent_po.description,
            'agent_type': agent_po.agent_type.value,
            'model_provider': agent_po.model_provider.value,
            'model_id': agent_po.model_id,
            'sys_prompt': agent_po.sys_prompt,
            'tools': [tool.model_dump_json() for tool in agent_po.tools],  # Convert tools to JSON string
            'envs': agent_po.envs
        }
        
        # Add extras if it exists
        if agent_po.extras:
            item['extras'] = agent_po.extras
            
        table.put_item(Item=item)

    def get_agent(self, id: str) -> Optional[AgentPO]:
        """
        Retrieve an AgentPO object by its ID from Amazon DynamoDB.

        :param id: The ID of the agent to retrieve.
        :return: An AgentPO object if found, otherwise None.
        """
        table = self.dynamodb.Table(self.dynamodb_table_name)
        response = table.get_item(Key={'id': id})

        if 'Item' in response:
            item = response['Item']
            return self._map_agent_item(item)
        return None

    def query_agent_by_name(self, name: str, limit: int = 5) -> Optional[List[AgentPO]]:
        """
        Retrieve an AgentPO object by its name from Amazon DynamoDB.

        :param name: The name of the agent to retrieve.
        :return: An AgentPO object if found, otherwise None.
        """
        table = self.dynamodb.Table(self.dynamodb_table_name)
        response = table.scan(FilterExpression=Attr('name').eq(name),
                              Limit = limit)

        items = response.get('Items', [])
        if items:
            return [self._map_agent_item(item) for item in items]
        return None

    def list_agents(self) -> List[AgentPO]:
        """
        List all AgentPO objects from Amazon DynamoDB.
        :return: A list of AgentPO objects.
        """
        table = self.dynamodb.Table(self.dynamodb_table_name)
        response = table.scan()
        items = response.get('Items', [])
        if items:
            return [ self._map_agent_item(item) for item in items]
        return []

    def delete_agent(self, id: str) -> bool:
        """
        Delete an AgentPO object by its ID from Amazon DynamoDB.

        :param id: The ID of the agent to delete.
        :return: True if deletion was successful, False otherwise.
        """
        table = self.dynamodb.Table(self.dynamodb_table_name)
        response = table.delete_item(Key={'id': id})

        # Check if the item was deleted successfully
        return response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200
    
    async def stream_chat(self, agent_id: str, user_message: str):
        """
        Stream chat messages from an agent.

        :param agent_id: The ID of the agent to stream chat from.
        :param user_message: The user's message to send to the agent.
        :return: A generator that yields complete event information.
        """
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found.")
    
        agent_instance = self.build_strands_agent(agent)

        # Stream the chat response
        async for message in agent_instance.stream_async(user_message):
            # print(f"Received message: {message}")
            msg = EventSerializer.prepare_event_for_serialization(message)
            # print(f"Received message: {msg}")
            # Return the complete event information instead of just the data field
            yield message

    def get_all_available_tools(self) -> List[AgentTool]:
        """
        Get all available tools from the AgentPOService.

        :return: A list of AgentTool objects.
        """
        tools = []
        for tool in Tools:
            tools.append(AgentTool(name=tool.identify, display_name=tool.name, category=tool.category, desc=tool.desc))
        
        # Add Agent tools(Only plain agents)
        for agent in self.list_agents():
            if agent.agent_type == AgentType.plain:
                tools.append(AgentTool(name=agent.name, display_name=agent.name, category="Agent", desc=agent.description, type=AgentToolType.agent, agent_id=agent.id))

        # Add MCP tools
        mcpService = MCPService()
        for mcp in mcpService.list_mcp_servers():
            tools.append(AgentTool(name=mcp.name, display_name=mcp.name, category="Mcp", desc=mcp.desc, type=AgentToolType.mcp, mcp_server_url=mcp.host))
        
        return tools

    def build_strands_agent(self, agent: AgentPO, **kwargs) -> Agent:
        """
        Build a Strands agent from an AgentPO object.

        :param agent: The AgentPO object to build the Strands agent from.
        :return: A Strands Agent instance.
        """
        # Parse and set environment variables if they exist
        if agent.envs:
            for line in agent.envs.strip().split('\n'):
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        print(f"Setting environment variable: {key}")
                        import os
                        os.environ[key] = value
        # Load tools based on their type
        tools = []
        for t in agent.tools:
            if t.type == AgentToolType.strands:
                try:
                    print(f"tool.name: {t.name}")
                    name_segs = t.name.split(".")
                    if len(name_segs) ==1:
                        # If the tool name is just a single name, it is a module in strands_tools
                        module = importlib.import_module(f"strands_tools.{t.name}")
                        tools.append(module)
                    elif len(name_segs) >= 3:
                        # module.class.method pattern
                        module_name = f"strands_tools.{'.'.join(name_segs[:-2])}"
                        class_name = name_segs[-2]
                        method_name = name_segs[-1]
                        module = importlib.import_module(module_name)
                        cls = getattr(module, class_name)
                        obj = cls()
                        method = getattr(obj, method_name)
                        tools.append(method)
                    else:
                        raise AttributeError(f"Invalid tool name format: {t.name}. Expected format: module.class.method or module.")
                except (ImportError, AttributeError) as e:
                    print(f"Error loading tool {t.name}: {e}")
            elif t.type == AgentToolType.agent and t.agent_id:
                # If the tool is another agent, convert it to a Strands tool
                agent_po = self.get_agent(t.agent_id)
                tools.append(agent_as_tool(agent_po))
            elif t.type == AgentToolType.mcp and t.mcp_server_url:
                try:
                    # If the tool is an MCP server, create a Strands MCP client with increased timeout
                    print(f"Initializing MCP client for server: {t.mcp_server_url}")
                    streamable_http_mcp_client = MCPClient(
                        lambda: streamablehttp_client(t.mcp_server_url),
                        startup_timeout=60  # Increase timeout to 60 seconds
                    )
                    streamable_http_mcp_client = streamable_http_mcp_client.start()
                    mcp_tools = streamable_http_mcp_client.list_tools_sync()
                    print(f"Successfully loaded {len(mcp_tools)} tools from MCP server")
                    tools.extend(mcp_tools)
                except Exception as e:
                    print(f"Error initializing MCP client for {t.mcp_server_url}: {str(e)}")
                    # Continue without the MCP tools rather than failing completely
                    continue
            else:
                print(f"Unsupported tool type: {t.type}")
        

        # Choose the appropriate model based on the provider
        if agent.model_provider == ModelProvider.bedrock:
            boto_config = BotocoreConfig(
                retries={"max_attempts": kwargs['max_attempts'] if 'max_attempts' in kwargs else 10, "mode": "standard"},
                connect_timeout=kwargs['connect_timeout'] if 'connect_timeout' in kwargs else 10,
                read_timeout=kwargs['read_timeout'] if 'read_timeout' in kwargs else 900
            )

            model = BedrockModel(
                model_id=agent.model_id,
                boto_client_config=boto_config,
            )
        elif agent.model_provider == ModelProvider.openai:
            # For OpenAI, use the extras field to get base_url and api_key
            from strands.models.openai import OpenAIModel
            
            base_url = None
            api_key = None
            
            if agent.extras:
                base_url = agent.extras.get('base_url')
                api_key = agent.extras.get('api_key')
            
            model = OpenAIModel(
                client_args={
                    "api_key": api_key,
                    "base_url": base_url
                },
                model_id=agent.model_id,
            )
        else:
            # Default to Bedrock for now
            boto_config = BotocoreConfig(
                retries={"max_attempts": kwargs['max_attempts'] if 'max_attempts' in kwargs else 10, "mode": "standard"},
                connect_timeout=kwargs['connect_timeout'] if 'connect_timeout' in kwargs else 10,
                read_timeout=kwargs['read_timeout'] if 'read_timeout' in kwargs else 900
            )

            model = BedrockModel(
                model_id=agent.model_id,
                boto_client_config=boto_config,
            )

        return Agent(
            system_prompt=agent.sys_prompt,
            model=model,
            tools=tools
        )

    def _map_agent_item(self, item: dict) -> AgentPO:
        """
        Map a DynamoDB item to an AgentPO object.

        :param item: The DynamoDB item to map.
        :return: An AgentPO object.
        """
        def json_to_agent_tool(tool_json: dict) -> AgentTool:
            """
            Convert a JSON string to an AgentTool object.
            """
            return AgentTool(
                             name=tool_json['name'],
                             display_name= tool_json.get('display_name', tool_json['name']),
                             category=tool_json['category'],
                             desc=tool_json['desc'],
                             type=AgentToolType(tool_json['type']),
                             mcp_server_url=tool_json.get('mcp_server_url', None),
                             agent_id= tool_json.get('agent_id', None))
    
        return AgentPO(
            id=item['id'],
            name=item['name'],
            display_name=item['display_name'],
            description=item['description'],
            agent_type=AgentType(item['agent_type']),
            model_provider=ModelProvider(item['model_provider']),
            model_id=item['model_id'],
            sys_prompt=item['sys_prompt'],
            tools=[json_to_agent_tool(json.loads(tool)) for tool in item['tools'] ],
            envs=item.get('envs', ''),
            extras=item.get('extras')
        )
    

def agent_as_tool(agent: AgentPO, **kwargs):

    if agent.agent_type != AgentType.plain:
        return

    @tool(name=agent.name, description=agent.description)
    def agent_tool(query: str) -> str:
        # Parse and set environment variables if they exist
        if agent.envs:
            for line in agent.envs.strip().split('\n'):
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        print(f"Setting environment variable: {key}")
                        import os
                        os.environ[key] = value
                        
        tools = []
        for t in agent.tools:
            if t.type == AgentToolType.strands:
                try:    
                    module = importlib.import_module(f"strands_tools.{t.name}")
                    tools.append(module)
                except (ImportError, AttributeError) as e:
                    print(f"Error loading tool {t.name}: {e}")

        # Choose the appropriate model based on the provider
        if agent.model_provider == ModelProvider.bedrock:
            boto_config = BotocoreConfig(
                retries={"max_attempts": kwargs['max_attempts'] if 'max_attempts' in kwargs else 10, "mode": "standard"},
                connect_timeout=kwargs['connect_timeout'] if 'connect_timeout' in kwargs else 10,
                read_timeout=kwargs['read_timeout'] if 'read_timeout' in kwargs else 900
            )

            model = BedrockModel(
                model_id=agent.model_id,
                boto_client_config=boto_config,
            )
        elif agent.model_provider == ModelProvider.openai:
            # For OpenAI, use the extras field to get base_url and api_key
            from strands.models import OpenAIModel
            
            base_url = None
            api_key = None
            
            if agent.extras:
                base_url = agent.extras.get('base_url')
                api_key = agent.extras.get('api_key')
            
            model = OpenAIModel(
                model_id=agent.model_id,
                api_key=api_key,
                base_url=base_url
            )
        else:
            # Default to Bedrock for now
            boto_config = BotocoreConfig(
                retries={"max_attempts": kwargs['max_attempts'] if 'max_attempts' in kwargs else 10, "mode": "standard"},
                connect_timeout=kwargs['connect_timeout'] if 'connect_timeout' in kwargs else 10,
                read_timeout=kwargs['read_timeout'] if 'read_timeout' in kwargs else 900
            )

            model = BedrockModel(
                model_id=agent.model_id,
                boto_client_config=boto_config,
            )

        agent_instance = Agent(
            system_prompt=agent.sys_prompt,
            model=model,
            tools= tools
        )

        resp = agent_instance(query)
        return str(resp)

    return agent_tool

# Agent Chat Records
class ChatRecord(BaseModel):
    id: str
    agent_id: str
    user_message: str
    create_time: str

# Agent Chat Responses
class ChatResponse(BaseModel):
    chat_id: str
    resp_no: int
    content: str
    create_time: str


class ChatRecordService:
    """
    A service to manage chat records and responses.It allows adding, retrieving, and listing chat records and responses from Amazon DynamoDB.
    """

    chat_record_table_name = "ChatRecordTable"
    chat_response_table_name = "ChatResponseTable"

    def __init__(self):
        aws_region = get_aws_region()
        self.dynamodb = boto3.resource('dynamodb', region_name=aws_region)

    def add_chat_record(self, record: ChatRecord):
        """
        Add a chat record to Amazon DynamoDB.

        :param record: The ChatRecord object to add.
        :raises ValueError: If a chat record with the same ID already exists.
        :return: None
        
        """
        if (not record.id):
            record.id = uuid.uuid4().hex
        
        table = self.dynamodb.Table(self.chat_record_table_name)
        try:
            table.put_item(
                Item={
                    'id': record.id,
                    'agent_id': record.agent_id,
                    'user_message': record.user_message,
                    'create_time': record.create_time
                }   
            )
            # print(f"Successfully wrote chat record to DynamoDB. {self.chat_record_table_name} ID: {record.id}")
        except Exception as e:
            print(f"Error writing chat record to DynamoDB. ID: {record.id}")
            print(f"Error details: {str(e)}")
            raise
    
    def get_chat_record(self, id: str) -> ChatRecord:
        """
        Retrieve a chat record by its ID from Amazon DynamoDB.

        :param id: The ID of the chat record to retrieve.
        :return: A ChatRecord object if found, otherwise None.
        
        """
        table = self.dynamodb.Table(self.chat_record_table_name)
        response = table.get_item(Key={'id': id})

        if 'Item' in response:
            item = response['Item']
            return ChatRecord(id=item['id'], agent_id=item['agent_id'], user_message=item['user_message'], create_time=item['create_time'])
        return None

    
    def get_chat_records(self) -> List[ChatRecord]:
        """
        Retrieve all chat records from Amazon DynamoDB.

        :return: A list of ChatRecord objects.
        """
        table = self.dynamodb.Table(self.chat_record_table_name)
        response = table.scan(Limit=100)
        items = response.get('Items', [])
        if items:
            return [ChatRecord(id=item['id'], agent_id=item['agent_id'], user_message=item['user_message'], create_time=item['create_time']) for item in items]
        return []
    
    def add_chat_response(self, response: ChatResponse):
        """
        Add a chat response to Amazon DynamoDB.

        :param response: The ChatResponse object to add.
        """
        table = self.dynamodb.Table(self.chat_response_table_name)
        try:
            table.put_item(
                Item={
                    'id': response.chat_id,
                    'resp_no': response.resp_no,
                    'content': response.content,
                    'create_time': response.create_time
                }
            )
            print(f"Successfully wrote chat response to DynamoDB. Chat ID: {response.chat_id}, Response No: {response.resp_no}")
        except Exception as e:
            print(f"Error writing chat response to DynamoDB. Chat ID: {response.chat_id}, Response No: {response.resp_no}")
            print(f"Error details: {str(e)}")
            raise

    def get_all_chat_responses(self, chat_id: str) -> List[ChatResponse]:
        """
        Retrieve all chat responses for a given chat ID from Amazon DynamoDB.

        :param chat_id: The ID of the chat to retrieve responses for.
        :return: A list of ChatResponse objects.
        """
        table = self.dynamodb.Table(self.chat_response_table_name)
        response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key('id').eq(chat_id))
        items = response.get('Items', [])
        if items:
            return [ChatResponse(chat_id=item['id'], resp_no=item['resp_no'], content=item['content'], create_time=item['create_time']) for item in items]
        return []
    
    def del_chat(self, id: str):
        """
        Delete Chat Record and Chat Responses by its ID from Amazon DynamoDB.

        :param id: The ID of the agent to delete.
        """
        table = self.dynamodb.Table(self.chat_record_table_name)
        table.delete_item(Key={'id': id})

        table = self.dynamodb.Table(self.chat_response_table_name)
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('id').eq(id)
        )
        
        items = response['Items']
        deleted_count = 0
        
        # 批量删除项目
        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(
                    Key={
                        'id': item['id'],
                        'resp_no': item['resp_no']
                    }
                )
                deleted_count += 1
        print(f"delete chat:{id}, count:{deleted_count}")
    


if __name__ == "__main__":
    # Example usage
    # agent = AgentPOBuilder() \
    #     .set_id(uuid.uuid4().hex) \
    #     .set_name("utility_agent") \
    #     .set_display_name("测试Agent") \
    #     .set_description("You are an agent that can get do all kinds of calculation and get current time") \
    #     .set_agent_type(AgentType.plain) \
    #     .set_model_provider(ModelProvider.bedrock) \
    #     .set_model_id("us.anthropic.claude-3-7-sonnet-20250219-v1:0") \
    #     .set_sys_prompt("You are a helpful assistant.") \
    #     .set_tools([AgentTool(name="calculator", catagory="utilities", desc="Perform calculations and mathematical operations"),
    #                 AgentTool(name="current_time", catagory="utilities", desc="Get the current time and date")]) \
    #     .build()
    
    # agent_with_mcp_tool = AgentPOBuilder() \
    #     .set_id(uuid.uuid4().hex) \
    #     .set_name("rds_agent") \
    #     .set_display_name("AWs RDS Agent") \
    #     .set_description("An Agent with RDS MySQL MCP Server") \
    #     .set_agent_type(AgentType.plain) \
    #     .set_model_provider(ModelProvider.bedrock) \
    #     .set_model_id("us.anthropic.claude-3-7-sonnet-20250219-v1:0") \
    #     .set_sys_prompt("You are an senior MySQL expert and are proficient at SQL and MySQL operation") \
    #     .set_tools([AgentTool(name="", catagory="mysql", desc="MySQL MCP Server that can execute sql and get database and table statistics ", 
    #                           type=AgentToolType.mcp, mcp_server_url="http://localhost:3000/mcp") ]) \
    #     .build()
    
    # orchestrator = AgentPOBuilder() \
    #     .set_id(uuid.uuid4().hex) \
    #     .set_name("orchestrator_agent") \
    #     .set_display_name("Orchestrator Agent") \
    #     .set_description("An orchestrator agent") \
    #     .set_agent_type(AgentType.orchestrator) \
    #     .set_model_id("us.anthropic.claude-3-7-sonnet-20250219-v1:0") \
    #     .set_sys_prompt("You are an orchestrator agent, you can help me do many things.") \
    #     .set_tools([AgentTool(name="utilities_tools", catagory="utilities", desc="General utility tools that can do all kinds of calculation and get current time", type= AgentToolType.agent,agent_id="9b33d98d425c44249db926ce5015b28d")]) \
    #     .build()

    # orchestrator = Agent(
    #     system_prompt="You are an orchestrator agent, you can help me do many things.",
    #     model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    #     tools=[agent_as_tool(agent)]
    # )

    # orchestrator("100+100 等于多少")

    # print(agent)

    agent_service = AgentPOService()
    # agent_service.add_agent(agent)

    # query_ret = agent_service.get_agent("9b33d98d425c44249db926ce5015b28d")
    # print("Query Result:")
    # print(query_ret)

    # print("List of Agents:")
    # print(agent_service.list_agents())

    # strands_agent = agent_service.build_strands_agent(orchestrator)
    # strands_agent("100*300 等于多少")

    # strands_agent_with_mcp_tool = agent_service.build_strands_agent(agent_with_mcp_tool)
    # strands_agent_with_mcp_tool("mydata 数据库中一共有多少张表? 一共有多少行数据?")

    agentPO = agent_service.get_agent(id= "0de59ed3181c417f9ede8472386bcd4a")
    strands_agent = agent_service.build_strands_agent(agentPO)
    strands_agent("Help me inspect the RDS cluster and all EC2 instances in us-west-2 region on 2025-07-13")
