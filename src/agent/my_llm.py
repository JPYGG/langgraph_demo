import os

import httpx
from langchain_openai import ChatOpenAI
proxy_async_client = httpx.AsyncClient(proxy="http://127.0.0.1:10808")


llm = ChatOpenAI(
    model='openai/gpt-oss-120b',
    temperature=0.8,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    # extra_body={'chat_template_kwargs': {'enable_thinking': False}},
    http_async_client=proxy_async_client
)