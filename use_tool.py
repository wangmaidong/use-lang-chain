from typing import Any

from pydantic import BaseModel, Field

# 官方的
from langchain_core.tools import BaseTool


# 定义加法输入的数据模型，继承自BaseModel
class AddInput(BaseModel):
    """加法输入参数"""

    a: int = Field(..., description="被加数")
    b: int = Field(..., description="加数")


class AddTool(BaseTool):
    """继承 BaseTool，声明 name/description/args_schema 并实现 _run/_arun"""

    # 工具名称，字符串类型
    name: str = "add"
    # 工具描述，字符串类型
    description: str = "计算两个数的和"
    # 参数模式，类型为BaseModel,此处为AddInput
    args_schema: type[BaseModel] = AddInput

    # 实现同步运行方法，计算两个整数的和
    def _run(self, a: int, b: int, **kwargs) -> int:
        return a + b

    async def _arun(self, a: int, b: int, **kwargs) -> int:
        return self._run(a, b, **kwargs)


# 主程序入口
if __name__ == "__main__":
    # 实例化加法工具
    tool = AddTool()
    # 打印工具名称
    print("工具名称:", tool.name)
    # 打印工具描述
    print("工具描述:", tool.description)
    # 打印参数模式的JSON属性
    print("参数模式:", tool.args_schema.model_json_schema()["properties"])
    # 同步调用invoke方法，传入字典参数，打印调用结果
    print("调用结果:", tool.invoke({"a": 3, "b": 5}))
