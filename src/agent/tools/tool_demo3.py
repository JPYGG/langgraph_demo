from typing import Annotated

from langchain_core.runnables import Runnable
from langchain_core.tools import tool
from pydantic import BaseModel, Field



@tool('calculate')
def calculate3(
        x: Annotated[float, '第一个需要输入的数字,必须要传入。'],
        y: Annotated[float, '第二个需要输入的数字,必须要传入。'],
        operation: Annotated[str, '运算类型，只能是add、subtract、multiply和divide中的任意一个,必须要传入。']) -> float:
    """工具函数：计算两个数字的运算结果"""
    print(f"调用 calculate 工具，第一个数字：{x}, 第二个数字：{y}, 运算类型：{operation}")

    result = 0.0
    match operation:
        case "add":
            result = x + y
        case "subtract":
            result = x - y
        case "multiply":
            result = x * y
        case "divide":
            if y != 0:
                result = x / y
            else:
                raise ValueError("除数不能为零")

    return result


print(calculate3.name)
print(calculate3.description)
print(calculate3.args)
print(calculate3.args_schema.model_json_schema())
print(calculate3.return_direct)

print(calculate3.invoke({'x': 40, 'y': 2, 'operation': 'multiply'}))