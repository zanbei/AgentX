from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator, current_time,use_aws

model = OpenAIModel(
    client_args= {
        "api_key": "444b7a9e-f319-4310-9e5c-ee53504fc941",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3"
    },
    # model_id="doubao-seed-1-6-flash-250615"
    # model_id="doubao-seed-1-6-250615" 
    model_id="kimi-k2-250711"
)

agent = Agent(model=model, tools=[current_time, calculator, use_aws])
response = agent("帮我列出的us-west-2 region 中正在运行的EC2实例信息")
print(response)