import boto3, uuid
import importlib
import json

from boto3.dynamodb.conditions import Attr
from strands import Agent, tool

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel

AgentType  = Enum("AgentType", ("plain", "orchestrator"))
ModelProvider = Enum("ModelProvider", ("bedrock", "openai", "anthropic", "litellm", "ollama", "custom"))
AgentToolType = Enum("AgentToolType", ("strands", "mcp", "agent", "python"))

class Tools(Enum):

    retrieve = "RAG & Memory", "Retrive data from Amazon Bedrock Knowledge Base for RAG, memory, and other purpose"
    memory = "RAG & Memory", "Agent memory persistence in Amazon Bedrock Knowledge Bases"
    mem0_memory = "RAG & Memory", "Agent memory and personalization built on top of Mem0"

    editor = "FileOps", "File editing operations like line edits, search, and undo"
    file_read = "FileOps", "Read and parse files"
    file_write = "FileOps", "Create and modify files"

    http_request = "Web & Network", "Make API calls, fetch web data, and call local HTTP servers"
    slack = "Web & Network", "Slack integration with real-time events, API access, and message sending"

    image_reader = "Multi-modal", "Process and analyze images"
    generate_image = "Multi-modal", "Create AI generated images with Amazon Bedrock"
    nova_reels = "nova_reels", "Create AI generated videos with Nova Reels on Amazon Bedrock"
    speak = "nova_reels", "Generate speech from text using macOS say command or Amazon Polly"

    use_aws = "AWS Services", "Interact with AWS services"

    calculator = "Utilities", "Perform calculations and mathematical operations"
    current_time = "Utilities", "Get the current time and date"


    def __init__(self, category: str, desc: str):
        super().__init__()
        self._category = category
        self._desc = desc

    @property
    def desc(self):
        return self._desc

    @property
    def category(self):
        return self._category

    @classmethod
    def getToolByName(cls, name: str) -> Optional:
        for t in Tools:
            if t.name == name:
                return t
        return None

    def __repr__(self):
        return f"Tools(name={self.name}, category={self.category}, desc={self.desc})"


class HttpMCPSerer(object):
    def __init__(self, name: str, desc: str, url: str):
        self.name = name
        self.desc = desc
        self.url = url

    def __repr__(self):
        return f"HttpMCPSerer(name={self.name}, desc={self.desc}, url={self.url})"

class AgentTool(BaseModel):
    name: str
    catagory: str
    desc:str
    type: AgentToolType = AgentToolType.strands
    mcp_server_url: Optional[str] = None
    agent_id: Optional[str] = None

    def __repr__(self):
        return f"AgentTool(name={self.name}, category={self.catagory}, desc={self.desc}, type={self.type}, " \
               f"mcp_server_url={self.mcp_server_url}), agent_id={self.agent_id})"
    
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

    def __repr__(self):
        return f"AgentPO(name={self.name}, display_name={self.display_name} description={self.description}, " \
               f"agent_type={self.agent_type}, model_provider={self.model_provider}, " \
               f"model_id={self.model_id}, sys_prompt={self.sys_prompt}, tools={self.tools})"


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

    def build(self) -> AgentPO:
        return self._agent_po



class AgentPOService:
    """
    A service to manage AgentPO objects.It allows adding, retrieving, and listing agents from Amazon DynamoDB.
    """

    dynamodb_table_name = "AgentTable"

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        pass

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
        table.put_item(
            Item={
                'id': agent_po.id,
                'name': agent_po.name,
                'display_name': agent_po.display_name,
                'description': agent_po.description,
                'agent_type': agent_po.agent_type.value,
                'model_provider': agent_po.model_provider.value,
                'model_id': agent_po.model_id,
                'sys_prompt': agent_po.sys_prompt,
                'tools': [tool.model_dump_json() for tool in agent_po.tools]  # Convert tools to JSON string
            }
        )

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
    
    def stream_chat(self, agent_id: str, user_message: str):
        """
        Stream chat messages from an agent.

        :param agent_id: The ID of the agent to stream chat from.
        :param user_message: The user's message to send to the agent.
        :return: A generator that yields chat messages.
        """
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found.")
        
        agent_instance = None
        if agent.agent_type == AgentType.plain:
            agent_tools = []
            for tool in agent.tools:
                try:
                    module = importlib.import_module(f"strands_tools.{tool.name}")
                    func = getattr(module, tool.name)
                    agent_tools.append(func)
                except (ImportError, AttributeError) as e:
                    print(f"Error loading tool {tool.name}: {e}")
            agent_instance = Agent(
                system_prompt=agent.sys_prompt,
                model=agent.model_id,
                tools=agent_tools
            )

        # Create an Agent instance with the retrieved AgentPO
        agent_instance = Agent(
            system_prompt=agent.sys_prompt,
            model=agent.model_id,
            tools=agent.tools
        )

        # Stream the chat response
        for message in agent_instance.stream_chat(user_message):
            yield f"data: {message}\n\n"

    def build_strands_agent(self, agent: AgentPO, **kwargs) -> Agent:
        """
        Build a Strands agent from an AgentPO object.

        :param agent: The AgentPO object to build the Strands agent from.
        :return: A Strands Agent instance.
        """

        tools = []
        for t in agent.tools:
            if t.type == AgentToolType.strands:
                try:
                    module = importlib.import_module(f"strands_tools.{t.name}")
                    func = getattr(module, t.name)
                    tools.append(func)
                except (ImportError, AttributeError) as e:
                    print(f"Error loading tool {t.name}: {e}")
            elif t.type == AgentToolType.agent and t.agent_id:
                # If the tool is another agent, convert it to a Strands tool
                agent_po = self.get_agent(t.agent_id)
                tools.append(agent_as_tool(agent_po))

            elif t.type == AgentToolType.mcp:
                #TODO: Handle MCP tools
                pass
            else:
                print(f"Unsupported tool type: {t.type}")
        return Agent(
            system_prompt=agent.sys_prompt,
            model=agent.model_id,
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
            return AgentTool(name=tool_json['name'],
                             catagory=tool_json['catagory'],
                             desc=tool_json['desc'],
                             type=AgentToolType(tool_json['type']),
                             mcp_server_url=tool_json.get('mcp_server_url', None))
    
        return AgentPO(
            id=item['id'],
            name=item['name'],
            display_name=item['display_name'],
            description=item['description'],
            agent_type=AgentType(item['agent_type']),
            model_provider=ModelProvider(item['model_provider']),
            model_id=item['model_id'],
            sys_prompt=item['sys_prompt'],
            tools=[json_to_agent_tool(json.loads(tool)) for tool in item['tools'] ]
        )
    

def agent_as_tool(agent: AgentPO, **kwargs):

    if agent.agent_type != AgentType.plain:
        return

    @tool(name=agent.name, description=agent.description)
    def agent_tool(query: str):
        tools = []
        for t in agent.tools:
            if t.type == AgentToolType.strands:
                try:    
                    module = importlib.import_module(f"strands_tools.{t.name}")
                    func = getattr(module, t.name)
                    tools.append(func)
                except (ImportError, AttributeError) as e:
                    print(f"Error loading tool {t.name}: {e}")

        agent_instance = Agent(
            system_prompt=agent.sys_prompt,
            model=agent.model_id,
            tools= tools
        )
        agent_instance(query)

    return agent_tool

if __name__ == "__main__":
    # Example usage
    agent = AgentPOBuilder() \
        .set_id(uuid.uuid4().hex) \
        .set_name("utility_agent") \
        .set_display_name("测试Agent") \
        .set_description("You are an agent that can get do all kinds of calculation and get current time") \
        .set_agent_type(AgentType.plain) \
        .set_model_provider(ModelProvider.bedrock) \
        .set_model_id("us.anthropic.claude-3-7-sonnet-20250219-v1:0") \
        .set_sys_prompt("You are a helpful assistant.") \
        .set_tools([AgentTool(name="calculator", catagory="utilities", desc="Perform calculations and mathematical operations"),
                    AgentTool(name="current_time", catagory="utilities", desc="Get the current time and date")]) \
        .build()
    
    orchestrator = AgentPOBuilder() \
        .set_id(uuid.uuid4().hex) \
        .set_name("orchestrator_agent") \
        .set_display_name("Orchestrator Agent") \
        .set_description("An orchestrator agent") \
        .set_agent_type(AgentType.orchestrator) \
        .set_model_id("us.anthropic.claude-3-7-sonnet-20250219-v1:0") \
        .set_sys_prompt("You are an orchestrator agent, you can help me do many things.") \
        .set_tools([AgentTool(name="utilities_tools", catagory="utilities", desc="General utility tools that can do all kinds of calculation and get current time", type= AgentToolType.agent,agent_id="9b33d98d425c44249db926ce5015b28d")]) \
        .build()

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

    strands_agent = agent_service.build_strands_agent(orchestrator)
    strands_agent("北京是UTC+8 时区, 请问现在是什么时候?")
