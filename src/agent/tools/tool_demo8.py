from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import tool



@tool
def get_user_info_by_name(config: RunnableConfig) -> float:
    """获取用户的所有信息，包括：性别，年龄等"""
    user_name = config['configurable'].get('user_name', 'zs')
    print(f"调用工具， 传入的用户名是: {user_name}")
    # 模拟
    return {'username': user_name, 'sex': '男', 'age': 18}


# print(calculate3.name)
# print(calculate3.description)
# print(calculate3.args)
# print(calculate3.args_schema.model_json_schema())
# print(calculate3.return_direct)

# print(calculate3.invoke({'a': 40, 'b': 2, 'operation': 'multiply'}))