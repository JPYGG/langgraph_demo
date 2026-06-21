from langgraph_sdk import get_client
import asyncio


# 调用agent发布的API接口


client = get_client(url="http://localhost:2024")  # 接口地址

async def main():
    async for chunk in client.runs.stream(
        None,  # Threadless run
        "agent", # Name of assistant. Defined in langgraph.json.
        input={
        "messages": [{
            "role": "human",
            "content": "给当前用户一个祝福语",
            }],
        },
        config={"configurable": {"user_name": "老肖"}}
    ):
        print(f"Receiving new event of type: {chunk.event}...")
        print(chunk.data)
        print("\n\n")


if __name__ == '__main__':
    asyncio.run(main())