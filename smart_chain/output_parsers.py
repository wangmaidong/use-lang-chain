# 导入抽象类基类（ABC）和抽象方法（abstractmethod）
from abc import ABC, abstractmethod
import json
import re


# 定义输出解析器的抽象基类
class BaseOutputParser(ABC):
    """输出解析器的抽象基类"""

    # 定义抽象方法 parse，需要子类实现具体的解析逻辑
    @abstractmethod
    def parse(self, text):
        """
        解析输出文本

        Args:
            text: 要解析的文本

        Returns:
            解析后的结果
        """
        pass


# 定义字符串输出解析器类，继承自 BaseOutputParser
class StrOutputParser(BaseOutputParser):
    """
    字符串输出解析器
    将 LLM 的输出解析为字符串。这是最简单的输出解析器，
    它不会修改输入内容，只是确保输出是字符串类型。
    主要用于：
    - 确保 LLM 输出是字符串类型
    - 在链式调用中统一输出格式
    - 简化输出处理流程
    """

    # 实现 parse 方法，将输入内容原样返回为字符串
    def parse(self, text) -> str:
        """
        解析输出文本（实际上只是返回原文本）
        Args:
            text:输入文本（应该是字符串）

        Returns:
            str: 原样返回输入文本
        """
        # 如果输入不是字符串，则将其转换为字符串类型
        if not isinstance(text, str):
            return str(text)
        return text

    # 定义 __repr__ 方法，返回该解析器的字符串表示
    def __repr__(self):
        """返回解析器的字符串表示"""
        return "StrOutputParser()"


def parse_json(text):
    text = text.strip()
    json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    # 如果找到markdown格式的json字符串
    if json_match:
        # 提取代码块中的JSON字符串并去除首尾空格
        text = json_match.group(1).strip()
    # 再次匹配文本中的
    json_match = re.search(r"(\{.*\}|\ [.*\ ])", text, re.DOTALL)
    if json_match:
        text = json_match.group(1).strip()
    return json.loads(text)


# 定义一个 JSON 输出解析器类，继承自 BaseOutputParser
class JsonOutputParser(BaseOutputParser):
    """
    JSON 输出解析器
    将 LLM 的输出解析为 JSON 对象。支持：
    - 纯 JSON 字符串
    - Markdown 代码块中的 JSON（``json ... ``）
    - 包含 JSON 的文本（自动提取）
    主要用于：
    - 结构化数据提取
    - API 响应解析
    - 数据格式化
    """

    # 解析输入文本为JSON对象
    def parse(self, input):
        """
        解析JSON文本输出
        Args:
            input: 包含JSON的文本

        Returns:解析后的 JSON 对象（字典、列表等）

        """
        try:
            parsed = parse_json(input)
            return parsed
        except json.JSONDecodeError as e:
            raise ValueError(f"无法解析JSON输出:{input[:100]},错误原因:{str(e)}")
        except Exception as e:
            raise ValueError(f"解析JSON时出错")

    def get_format_instructions(self):
        return """请以 JSON 格式输出你的回答。
        输出格式要求：
        1. 使用有效的 JSON 格式
        2. 可以使用 markdown 代码块包裹：```json ... ```
        3. 确保所有字符串都用双引号
        4. 确保 JSON 格式正确且完整

        示例格式：
        ```json
        {
        "key": "value",
        "number": 123
        }
       ```
       """
