from fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent
import requests
from bs4 import BeautifulSoup

server = FastMCP(name='lx_mcp', instructions='老肖的Python代码实现MCP服务器')

# Bing 搜索的请求头
SEARCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def _bing_search(query: str, max_results: int = 5) -> list[dict]:
    """使用 Bing 搜索引擎抓取搜索结果"""
    resp = requests.get(
        "https://cn.bing.com/search?q=" + requests.utils.quote(query),
        headers=SEARCH_HEADERS,
        timeout=10,
    )
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    for item in soup.select("li.b_algo")[:max_results]:
        title_elem = item.select_one("h2 a")
        body_elem = item.select_one(".b_caption p")
        results.append({
            "title": title_elem.get_text(strip=True) if title_elem else "",
            "body": body_elem.get_text(strip=True) if body_elem else "",
            "href": title_elem.get("href", "") if title_elem else "",
        })
    return results


@server.tool(name='web_search')
def my_search(query: str) -> str:
    """搜索互联网上的内容,包括实时天气等"""
    try:
        print("执行搜索工具，输入的参数为:", query)

        results = _bing_search(query)

        if results:
            output = []
            for i, r in enumerate(results, 1):
                title = r["title"]
                body = r["body"]
                href = r["href"]
                output.append(f"{i}. {title}\n   {body}\n   {href}")
            return "\n\n".join(output)
        return '没有搜索到任何内容！'
    except Exception as e:
        print(f"搜索出错: {e}")
        return f'搜索出错: {e}'


@server.tool()
def say_hello(username: str) -> str:
    """给指定用户打个招呼"""
    return f"{username}， 你好，今天天气不错！"


@server.prompt
def ask_about_topic(topic: str) -> str:
    """生成请求解释特定主题的用户消息模板"""
    return f"能否请您解释一下'{topic}',这个概念？"


# 高级提示模板：返回结构化消息对象
@server.prompt
def generate_code_request(language: str, task_description: str) -> PromptMessage:
    """生成代码编写请求的用户消息模板"""
    content = f"请用{language}编写一个实现以下功能的函数：{task_description}"
    return PromptMessage(
        role="user",
        content=TextContent(type="text", text=content)
    )


# 结构化资源：自动序列化字典为JSON
@server.resource("resource://config")
def get_config() -> dict:
    """以JSON格式返回应用配置"""
    return {
        "theme": "dark",          # 界面主题配置
        "version": "1.2.0",       # 当前版本号
        "features": ["tools", "resources"],  # 已启用的功能模块
    }