"""ReAct agent implemented with LangGraph StateGraph.

Uses ChatOpenAI with a weather tool in a manual ReAct loop.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Sequence

from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
import httpx
proxy_async_client = httpx.AsyncClient(proxy="http://127.0.0.1:10808")


llm = ChatOpenAI(
    model='openai/gpt-oss-120b',
    temperature=0.8,
    api_key='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',
    base_url="https://integrate.api.nvidia.com/v1",
    # extra_body={'chat_template_kwargs': {'enable_thinking': False}},
    http_async_client=proxy_async_client
)


@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


class State(TypedDict):
    """Input state for the ReAct agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


tools = [get_weather]
llm_with_tools = llm.bind_tools(tools)


# def call_model(state: State) -> Dict[str, Any]:
#     """Call the LLM with the current conversation messages."""
#     response = llm_with_tools.invoke(state["messages"])
#     return {"messages": [response]}

# 配置日志输出到标准输出，方便在终端或 Studio 中直接查看
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def call_model(state: State) -> Dict[str, Any]:
    """Call the LLM with the current conversation messages."""
    logger.info("--- 开始调用 call_model 节点 ---")
    logger.info(f"当前 State 中的消息流长度: {len(state['messages'])}")
    logger.info(f"最后一条输入消息: {state['messages'][-1].content}")

    try:
        # 尝试调用模型
        response = llm_with_tools.invoke(state["messages"])
        logger.info("--- LLM 调用成功 ---")
        logger.info(f"LLM 响应内容: {response.content}")
        return {"messages": [response]}

    except Exception as e:
        # 捕捉异常并打印完整的堆栈信息，暴露出到底是哪个 URL 报的 503
        logger.error("🚨 LLM 调用发生崩溃！详细错误信息如下：", exc_info=True)

        # 打印当前 LLM 对象的配置参数，检查 base_url 是否符合预期
        if hasattr(llm_with_tools, 'kwarg') or hasattr(llm, 'client'):
            logger.error(f"当前 LLM 实例配置详情: {getattr(llm, 'model_name', '未知模型')}")

        # 重新抛出以便 LangGraph 记录
        raise e


def call_tool(state: State) -> Dict[str, Any]:
    """Execute tool calls from the last AI message."""
    last_message = state["messages"][-1]
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_result = get_weather.invoke(tool_call)
        tool_messages.append(tool_result)
    return {"messages": tool_messages}


def should_continue(state: State) -> str:
    """Determine whether to continue the tool loop or end."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "call_tool"
    return "__end__"


# Define the graph
graph = (
    StateGraph(State)
    .add_node(call_model)
    .add_node(call_tool)
    .add_edge("__start__", "call_model")
    .add_conditional_edges(
        "call_model",
        should_continue,
        {"call_tool": "call_tool", "__end__": "__end__"},
    )
    .add_edge("call_tool", "call_model")
    .compile(name="ReAct Agent")
)
