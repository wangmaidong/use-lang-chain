import os
import json

from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel, Field

# 官方的
from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser,
    PydanticOutputParser,
    BaseOutputParser,
)
from langchain_classic.output_parsers.fix import OutputFixingParser
from langchain_classic.output_parsers import RetryOutputParser
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import PromptTemplate
from langchain_core.prompt_values import StringPromptValue

# 自己实现的
# from smart_chain.output_parsers import (
#     StrOutputParser,
#     JsonOutputParser,
#     PydanticOutputParser,
#     OutputFixingParser,
#     RetryOutputParser,
# )
# from smart_chain.chat_models import ChatDeepSeek
# from smart_chain.prompts import PromptTemplate
# from smart_chain.prompt_values import StringPromptValue

api_key = os.getenv("OPENAI_API_KEY_DEEP")
llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key)


# 定义布尔值输出解析器类，继承自 BaseOutputParser
class BooleanOutputParser(BaseOutputParser):
    """
    布尔值输出解析器
    将文本解析为布尔值。支持多种表示方式：
    - YES/NO
    - TRUE/FALSE
    - 是/否
    - 1/0
    """

    # 初始化方法，可选指定代表True和False的字符串
    def __init__(self, true_val: str = "YES", false_val: str = "NO"):
        """
        初始化布尔值解析器
        :param true_val: 表示 True 的值（默认 "YES"）
        :param false_val: 表示 False 的值（默认 "NO"）
        """
        try:
            super().__init__()
        except TypeError:
            pass
        # 设置 true_val 属性，转换为大写
        object.__setattr__(self, "true_val", true_val.upper())
        object.__setattr__(self, "false_val", false_val.upper())

    # 定义解析方法，将文本转换为布尔值
    def parse(self, text: str) -> bool:
        """
        解析文本为布尔值
        :param text:要解析的文本
        :return:
            解析后的布尔值
        Raises:
            OutputParserException: 如果无法解析为布尔值
        """
        cleaned_text = text.strip()
        true_values = [self.true_val, "TRUE", "YES", "是", "1", "Y"]
        false_values = [self.false_val, "FALSE", "NO", "否", "0", "N"]
        if cleaned_text in true_values:
            return True
        elif cleaned_text in false_values:
            return False
        else:
            raise OutputParserException(
                f"BooleanOutputParser 无法解析 '{text}'。",
                f"期望的值：{true_values} 或 {false_values}",
            )

    # 告诉 LLM 应该输出什么样的格式，用于构造提示词的"格式说明"部分
    def get_format_instructions(self) -> str:
        # 返回格式说明，告知只输出 true_val 或 false_val
        return f"请输出 {self.true_val} 或 {self.false_val}（不区分大小写）"


bool_parser = BooleanOutputParser()

test_case = [
    "YES",
    "no",
    "true",
    "FALSE",
    "是",
    "否",
    "1",
    "0",
]
for test in test_case:
    try:
        result = bool_parser.parse(test)
        print(f"  '{test}' -> {result}")
    except Exception as e:
        print(f"解析测试案例出错{type(e).__name__}:e")

# 创建一个带有格式化说明的布尔判断提示模板
bool_prompt = PromptTemplate.from_template(
    """判断以下陈述是否正确。

    陈述：{statement}

    {format_instructions}

    请回答："""
)

# 定义要判断的陈述内容
statement = "Python 是一种编程语言"
# 用指定陈述和格式说明格式化 prompt
formatted = bool_prompt.format(
    statement=statement, format_instructions=bool_parser.get_format_instructions()
)

# 调用 LLM，获取结果
response = llm.invoke(formatted)
# 打印陈述和 LLM 输出内容
print(f"  陈述: {statement}")
print(f"  LLM 输出: {response.content}")

# 尝试用布尔解析器解析 LLM 输出内容
try:
    result = bool_parser.parse(response.content)
    print(f"  解析结果: {result}")
# 出现异常时打印错误信息
except Exception as e:
    print(f"  解析错误: {e}")
