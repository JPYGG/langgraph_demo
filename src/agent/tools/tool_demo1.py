from langchain_core.tools import tool


@tool(return_direct=False)
def calculate1(a: float, b: float, operation: str) -> float:
    """工具函数：计算两个数字的运算结果"""
    print(f"调用 calculate 工具，第一个数字：{a}, 第二个数字：{b}, 运算类型：{operation}")

    result = 0.0
    match operation:
        case "add":
            result = a + b
        case "subtract":
            result = a - b
        case "multiply":
            result = a * b
        case "divide":
            if b != 0:
                result = a / b
            else:
                raise ValueError("除数不能为零")

    return result


# print(calculate1.name)
# print(calculate1.description)
# print(calculate1.args)
# print(calculate1.args_schema.model_json_schema())
# print(calculate1.return_direct)
