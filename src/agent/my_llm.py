import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 使用绝对路径加载 .env，避免 PyCharm 等 IDE 运行时工作目录不同导致找不到
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# 阻止 langchain-openai 覆盖自定义 http client
os.environ.setdefault("LANGCHAIN_OPENAI_TCP_KEEPALIVE", "0")


llm = ChatOpenAI(
    model='openai/gpt-oss-120b',
    temperature=0.8,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    openai_proxy="http://127.0.0.1:10808",
    # extra_body={'chat_template_kwargs': {'enable_thinking': False}},
)