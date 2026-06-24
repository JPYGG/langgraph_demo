from typing import Any, Type, Optional
import urllib.parse
import httpx
from bs4 import BeautifulSoup
import asyncio

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class SearchArgs(BaseModel):
    query: str = Field(description="需要进行网络搜索的信息。")

# 网络搜索的工具
class MySearchTool(BaseTool):
    # 工具名字
    name: str = "search_tool"

    description: str = '搜索互联网上公开内容的工具'

    return_direct: bool = False

    args_schema: Type[BaseModel] = SearchArgs

    def _get_search_results(self, query: str) -> str:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        url = f"https://cn.bing.com/search?q={urllib.parse.quote(query)}"
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            for li in soup.find_all('li', class_='b_algo'):
                title_tag = li.find('h2')
                snippet_tag = li.find('div', class_='b_caption') or li.find('p')
                
                if title_tag and snippet_tag:
                    title = title_tag.get_text(strip=True)
                    snippet = snippet_tag.get_text(strip=True)
                    results.append(f"标题: {title}\n内容: {snippet}")
                
                if len(results) >= 5:
                    break
                    
            if results:
                return "\n\n".join(results)
            return '没有搜索到任何内容！'

    def _run(self, query: str) -> str:
        try:
            return self._get_search_results(query)
        except Exception as e:
            print(f"搜索出错: {e}")
            return f'搜索出错，没有搜索到内容！错误: {e}'

    async def _arun(self, query: str) -> str:
        try:
            # 使用 asyncio.to_thread 防止阻塞异步事件循环
            return await asyncio.to_thread(self._get_search_results, query)
        except Exception as e:
            print(f"异步搜索出错: {e}")
            return f'搜索出错，没有搜索到内容！错误: {e}'



# my_tool = MySearchTool()
# print(my_tool.name)
# print(my_tool.description)
# print(my_tool.args_schema.model_json_schema())