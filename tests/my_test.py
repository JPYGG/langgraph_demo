from langgraph_sdk import get_sync_client

client = get_sync_client(url="http://localhost:2024")

for chunk in client.runs.stream(
    None,  # Threadless run
    "agent", # Name of assistant. Defined in langgraph.json.
    input={
        "messages": [{
            "role": "human",
            "content": "告诉我当前用户的年龄？",
            # "content": "计算一下(3 + 5) x 12的结果",
        }],

    },
    stream_mode="messages-tuple",
    # stream_mode="messages",
    # stream_mode="updates",
    config={"configurable": {"user_name": "user_123"}}
):
    # print(f"Receiving new event of type: {chunk.event}...")
    # print(chunk.data)
    if isinstance(chunk.data, list) and 'type' in chunk.data[0] and chunk.data[0]['type'] == 'AIMessageChunk':
        print(chunk.data[0]['content'], end='|')

