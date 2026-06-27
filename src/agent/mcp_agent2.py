import asyncio
import concurrent

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from agent.my_llm import llm


test_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJkZXZfdXNlciIsImlzcyI6Imh0dHBzOi8vd3d3Lmxhb3hpYW8uY29tIiwiaWF0IjoxNzgyNDg4Mzg5LCJleHAiOjE3ODI0OTE5ODksImF1ZCI6Im15LWRldi1zZXJ2ZXIiLCJzY29wZSI6Imxhb3hpYW8gaW52b2tlX3Rvb2xzIn0.ASK0ND-QWDng1aYNHGAf83LrwYTPKUYCRmwb_qBJYhYYs_Q1z_XEpd0GQuIcG0SpowY2yFQKQ8pTFizdfjIWbM9zq3ljXtgG-eKn8lLIuOFkvgP7wgM4PYFh8CpsHEWNzPe442pzrHCxrWh-7dH5VWgKMV4HG4WMWS9pzbMbv1aIZxTJHjA-oFrRfiTou6pLmbXK6yJmvNNb08_MeNJFVO_ADBJ7BoRiGIlb23ntUdZnZbesbuwGcS0ryARiNdjB0BZlW9VYfnNpR3Vt3C6cvFJkP4BeFeM6bT1Qqem86axy2x8Qc2tsbcCxH4tAgUQYODBtbsaqOufTT7xf5664yA"

# Python MCP 服务端的连接配置
python_mcp_server_config = {
    'url': 'http://127.0.0.1:8080/streamable',
    'transport': 'streamable_http',
    'headers': {
        'Authorization': f'Bearer {test_token}',
    }
    # 'url': 'http://127.0.0.1:8080/sse',
    # 'transport': 'sse',
}



# MCP的客户端
mcp_client = MultiServerMCPClient(
    {
        'python_mcp': python_mcp_server_config,
    }
)


async def create_agent():
    """创建 agent，只注册工具，不调用 LLM"""
    mcp_tools = await mcp_client.get_tools()
    print(mcp_tools)

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


if __name__ == '__main__':
    """直接运行时执行一次对话测试"""
    import sys
    sys.path.insert(0, 'src')

    async def main():
        mcp_tools = await mcp_client.get_tools()
        agent = create_react_agent(
            llm,
            tools=mcp_tools,
            prompt="你是一个智能助手，尽可能的调用工具回答用户的问题",
        )
        rest = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "今天，北京的天气怎么样？"}]}
        )
        print(rest['messages'])
        print(rest['messages'][-1].content)

    asyncio.run(main())



