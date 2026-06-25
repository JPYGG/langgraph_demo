from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.postgres import PostgresStore

from agent.graph import search_tool
from agent.my_llm import llm
from agent.tools.tool_demo6 import runnable_tool

# checkpointer = InMemorySaver()  # 短期记忆，保持到内存中

# pip install langgraph-checkpoint-sqlite
# conn = sqlite3.connect("chat_history.db", check_same_thread=False)
# checkpointer = SqliteSaver(conn)

DB_URI = 'postgresql://postgres:123456@localhost:5432/langgraph_db'

with (
    PostgresStore.from_conn_string(DB_URI) as store,
    PostgresSaver.from_conn_string(DB_URI) as checkpointer,
):
    # checkpointer.setup()
    # store.setup()
    agent = create_react_agent(
        llm,
        tools=[runnable_tool, search_tool],
        prompt="你是一个智能助手，尽可能的调用工具回答用户的问题",
        checkpointer=checkpointer,
        store=store,
    )

    config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    rest = list(agent.get_state(config))  # 从短期存储中，返回所有当前会话的上下文

    rest = list(agent.get_state_history(config))  # 从长期存储中，返回所有当前会话的上下文

    print(rest)

    resp1 = agent.invoke(
        {"messages": [{"role": "user", "content": "给我一个关于相声的报幕词？"}]},
        config,
    )

    print(resp1['messages'][-1].content)

    resp2 = agent.invoke(
        {"messages": [{"role": "user", "content": "再给我关于流行歌曲<<忐忑>>的"}]},
        config,
    )

    print(resp2['messages'][-1].content)