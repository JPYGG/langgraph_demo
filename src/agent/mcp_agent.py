import asyncio
import concurrent.futures

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from agent.my_llm import llm


MCP_SERVER_URL = 'http://127.0.0.1:8080/streamable'


async def create_agent():
    """
    异步创建 agent。
    连接 MCP 服务器获取工具，连接失败时降级为无工具 agent。
    请确保 MCP 服务端 (tools_server.py) 先启动，监听 8080 端口。
    """
    mcp_client = MultiServerMCPClient({
        'python_mcp': {
            'url': MCP_SERVER_URL,
            'transport': 'streamable-http',
        }
    })

    print(f"正在连接 MCP 服务端: {MCP_SERVER_URL}")
    mcp_tools = await mcp_client.get_tools()
    print(mcp_tools)
    # p = await mcp_client.get_prompt(server_name='python_mcp', prompt_name='ask_about_topic', arguments={'topic': '深度学习'})
    # print(p)
    # data = await mcp_client.get_resources(server_name='python_mcp', uris='resource://config')
    # print(data[0])
    # print(data[0].data)  # json数据


    return create_react_agent(
        llm,
        tools=mcp_tools,
        prompt="你是一个智能助手，尽可能的调用工具回答用户的问题",
    )


def _init_agent():
    """
    在 LangGraph Server 已有事件循环的情况下安全初始化 agent。
    通过 ThreadPoolExecutor 在新线程中执行异步初始化。
    """
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, create_agent()).result()
    except RuntimeError:
        pass
    return asyncio.run(create_agent())


try:
    agent = _init_agent()
except BaseException as e:
    print(f"Agent 初始化异常 ({e})，创建基础 Agent 兜底，无 MCP 工具")
    agent = create_react_agent(
        llm,
        tools=[],
        prompt="你是一个智能助手，尽可能的调用工具回答用户的问题",
    )