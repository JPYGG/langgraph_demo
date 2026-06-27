import os

from fastmcp import FastMCP
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier, RSAKeyPair
from fastmcp.server.dependencies import AccessToken, get_access_token

from zhipuai import ZhipuAI

# from agent.env_utils import ZHIPU_API_KEY


zhipuai_client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

# 1、 生成 RSA 密钥对
key_pair = RSAKeyPair.generate()

# 2. JWT 验证器（用公钥校验 token 签名）
jwt_verifier = JWTVerifier(
    public_key=key_pair.public_key,
    issuer='https://www.laoxiao.com',
    audience='my-dev-server',
)

# 3. 配置认证提供方
auth = RemoteAuthProvider(
    token_verifier=jwt_verifier,
    authorization_servers=['https://www.laoxiao.com'],
    base_url='http://127.0.0.1:8080',
    scopes_supported=['laoxiao', 'invoke_tools'],
)

# 4. 生成测试 token
token = key_pair.create_token(
    subject='dev_user',
    issuer='https://www.laoxiao.com',
    audience='my-dev-server',
    scopes=['laoxiao', 'invoke_tools'],
    expires_in_seconds=3600,
)

print(f"Test token: {token}")


server = FastMCP(
    name='lx_mcp',
    instructions='老肖的Python代码实现MCP服务器',
    auth=auth,
)


@server.tool(name='zhipuai_search')
def my_search(query: str) -> str:
    """搜索互联网上的内容,包括实时天气等"""
    try:
        print("执行我的Python中的工具，输入的参数为:", query)

        # 得到了验证通过之后的
        access_token: AccessToken = get_access_token()
        if access_token:
            print("<整个token:>", access_token)
            print(access_token.scopes)
        else:
            return '由于没有权限，所以不能搜索到任何内容！，请客户端传入有效token'

        response = zhipuai_client.web_search.web_search(
            search_engine="search_pro",
            search_query=query
        )
        if response.search_result:
            return "\n\n".join([d.content for d in response.search_result])
        return '没有搜索到任何内容！'
    except Exception as e:
        print(e)
        return '没有搜索到任何内容！'


@server.tool()
def say_hello(username: str) -> str:
    """给指定用户打个招呼"""
    return f"{username}， 你好，今天天气不错！"
