# 导入抽象类基类（ABC）和抽象方法（abstractmethod）
from abc import ABC, abstractmethod
import json
import re
import pydantic

from .prompts import PromptTemplate


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


# 定义Pydantic 输出解析器类，继承自JsonOutputParser


class PydanticOutputParser(JsonOutputParser):
    """
    Pydantic输出解析器
    将LLM的输出解析为Pydantic模型实例，
    先解析JSON，然后验证并转换为Pydantic模型
    主要用于：
    结构化数据验证
    类型安全的数据提取
    自动化数据验证和转换
    """

    def __init__(self, pydantic_object: type):
        super().__init__()
        self.pydantic_object = pydantic_object

    # 解析函数，将文本解析为 Pydantic 实例
    def parse(self, text: str):
        # 尝试解析并转换文本为 Pydantic 实例
        try:
            # 首先用父类方法将文本解析为 JSON 对象（如 dict）
            json_obj = super().parse(text)
            # 将 JSON 对象转为 Pydantic 模型实例
            return self._parse_obj(json_obj)
        except Exception as e:
            raise ValueError(f"无法解析为Pydantic 模型：{e}")

    def _parse_obj(self, obj: dict):
        # 如果模型有 model_validate 方法（Pydantic v2），优先使用
        if hasattr(self.pydantic_object, "model_validate"):
            return self.pydantic_object.model_validate(obj)
        # 如果模型有 parse_obj 方法（Pydantic v1），则使用
        elif hasattr(self.pydantic_object, "parse_obj"):
            return self.pydantic_object.parse_obj(obj)
        # 否则，尝试直接用 ** 解包初始化
        else:
            return self.pydantic_object(**obj)

    def _get_schema(self) -> dict:
        # 尝试获取 schema，支持 Pydantic v1 和 v2
        try:
            if hasattr(self.pydantic_object, "model_json_schema"):
                return self.pydantic_object.model_json_schema()
            elif hasattr(self.pydantic_object, "schema"):
                return self.pydantic_object.schema()
            else:
                return {}
        except Exception:
            return {}

    def get_format_instructions(self) -> str:
        # 获取Pydantic 模型schema
        schema = self._get_schema()
        # 拷贝一份schema进行编辑
        reduced_schema = dict(schema)
        # 删除 description 字段（如果有）
        if "description" in reduced_schema:
            del reduced_schema["description"]
        # 序列化 schema 为格式化字符串
        schema_str = json.dumps(reduced_schema, ensure_ascii=False, indent=2)
        # 返回格式说明字符串，内嵌 JSON Schema
        return f"""请以 JSON 格式输出你的回答,必须严格遵循以下的Schema

                    ```json
                    {schema_str}
                    ```

                    输出格式要求：
                    1. 必须完全符合上述的 Schema结构
                    2.所有的必需字段都必须提供
                    3.字段类型必须匹配(字符串、数字、布尔值等)
                    4.使用有效的JSON格式
                    5.可以使用markdown代码块包裹 ```json JSON字符串 ```

                    确保输出是有效的JSON，并且符合 schema定义
                """


# 输出修复解析器类，继承自 BaseOutputParser
class OutputFixingParser(BaseOutputParser):
    """
     输出修复解析器

    包装一个基础解析器，当解析失败时，使用 LLM 自动修复输出。
    这是一个非常有用的功能，可以处理 LLM 输出格式不正确的情况。

    工作原理：
    1. 首先尝试使用基础解析器解析输出
    2. 如果解析失败，将错误信息和原始输出发送给 LLM
    3. LLM 根据格式说明修复输出
    4. 再次尝试解析修复后的输出
    5. 可以设置最大重试次数
    """

    def __init__(self, parser: BaseOutputParser, retry_chain, max_retries: int = 1):
        """
        初始化 OutputFixingParser
        :param parser:基础解析器
        :param retry_chain:用于修复输出的链（通常是 Prompt -> LLM -> StrOutputParser）
        :param max_retries:最大重试次数
        """
        self.parser = parser
        self.retry_chain = retry_chain
        self.max_retries = max_retries

    # 从 LLM 创建 OutputFixingParser 的类方法
    @classmethod
    def from_llm(cls, llm, parser: BaseOutputParser, prompt=None, max_retries: int = 1):
        """
        从 LLM 创建 OutputFixingParser
        :param llm:用于修复输出的语言模型
        :param parser:基础解析器
        :param prompt:修复提示模板（可选，有默认模板）
        :param max_retries:最大重试次数
        :return:OutputFixingParser 实例
        """
        # 如果没有提供prompt,则使用默认的修复模板
        fix_template = """
        你是一个专门修复 LLM 输出格式的助手。
        原始输出：
        {completion}

        出现的错误：
        {error}

        输出应该遵循的格式：
        {instructions}

        请修复原始输出，使其符合要求的格式。
        只返回修复后的输出，不要添加任何解释。
        """
        # 利用模板生成PromptTemplate实例
        prompt = PromptTemplate.from_template(fix_template)
        # 创建修复链，使用 SimpleChain 连接 Prompt、LLM、StrOutputParser
        retry_chain = SimpleChain(prompt, llm, StrOutputParser())
        return cls(parser=parser, retry_chain=retry_chain, max_retries=max_retries)

    # 解析输出，如果失败则尝试自动修复
    def parse(self, completion: str):
        """
         解析输出，如果失败则尝试修复
        :param completion: LLM 的输出文本
        :return:解析后的结果
        """
        # 初始化重试次数
        retries = 0
        # 当重试次数未超过最大值时循环
        while retries <= self.max_retries:
            try:
                return self.parser.parse(completion)
            except (ValueError, OutputParserException, Exception) as e:
                # 如果已达到最大重试次数，抛出异常
                if retries >= self.max_retries:
                    raise OutputParserException(
                        f"解析失败， 已重试{retries} 次：{e}", llm_output=completion
                    )
                retries += 1
                print(f"第{retries}次尝试修复...")
                # 获取格式说明，通常来自基础解析器
                instructions = self.parser.get_format_instructions()
                # 利用retry_chain 调用LLM修复输出
                completion = self.retry_chain.invoke(
                    {
                        "instructions": instructions,
                        "completion": completion,
                        "error": str(e),
                    }
                )
        raise OutputParserException(
            f"解析失败,已重试了{retries}次:{e}", llm_output=completion
        )


# 输出解析异常类，继承自ValueError
class OutputParserException(ValueError):
    def __init__(self, message: str, llm_output: str = ""):
        super().__init__(message)
        self.llm_output = llm_output


# 简单的链式调用包装类
class SimpleChain:
    def __init__(self, prompt, llm, parser):
        self.prompt = prompt
        self.llm = llm
        self.parser = parser

    def invoke(self, input_dict: dict) -> str:
        # 格式化提示词
        formatted = self.prompt.format(**input_dict)
        # 通过 llm 调用生成响应
        response = self.llm.invoke(formatted)
        # 判断响应是否有 content 属性
        if hasattr(response, "content"):
            content = response.content
        else:
            content = str(response)
        return self.parser.parse(content)

    def run(self, **kwargs) -> str:
        return self.invoke(kwargs)


# 定义重试输出解析器
class RetryOutputParser(BaseOutputParser):
    """
    重试输出解析器
    包装一个基础解析器，当解析失败时，使用 LLM 重新生成输出。
    与 OutputFixingParser 的区别：
    - RetryOutputParser 需要原始 prompt 和 completion
    - 它使用 parse_with_prompt 方法而不是 parse 方法
    - 它将原始 prompt 和 completion 都传递给 LLM，让 LLM 重新生成

    工作原理：
    1. 首先尝试使用基础解析器解析 completion
    2. 如果解析失败，将原始 prompt 和 completion 发送给 LLM
    3. LLM 根据 prompt 的要求重新生成输出
    4. 再次尝试解析新生成的输出
    5. 可以设置最大重试次数

    """

    def __init__(self, parser: BaseOutputParser, retry_chain, max_retries: int = 1):
        """
        初始化RetryOutputParser
        :param parser:基础解析器
        :param retry_chain:用于重试的链（通常是 Prompt -> LLM -> StrOutputParser）
        :param max_retries:最大重试次数
        """
        self.parser = parser
        self.retry_chain = retry_chain
        self.max_retries = max_retries

    @classmethod
    def from_llm(
        cls, llm, parser: BaseOutputParser, prompt=None, max_retries: int = 1
    ) -> "RetryOutputParser":
        """
        从 LLM 创建 RetryOutputParser
        :param llm: 用于重试的语言模型
        :param parser: 基础解析器
        :param prompt: 重试提示模板（可选，有默认模板）
        :param max_retries: 最大重试次数
        :return:
            RetryOutputParser 实例
        """
        # 默认重试提示模板
        if prompt is None:
            retry_template = """
            Prompt:{prompt}
            Completion:{completion}
            上面的Completion并没有满足Prompt中的约束要求.
            请重新生成一个新的满足要求的输出
            """
            prompt = PromptTemplate.from_template(retry_template)
            # 创建重试链：Prompt --> LLM ---> StrOutputParser
        retry_chain = SimpleChain(prompt, llm, StrOutputParser())
        return cls(parser=parser, retry_chain=retry_chain, max_retries=max_retries)

    def parse_with_prompt(self, completion, prompt_value):
        # 初始化重试次数
        retries = 0
        while retries <= self.max_retries:
            try:
                return self.parser.parse(completion)
            except (ValueError, OutputParserException, Exception) as e:
                if retries > self.max_retries:
                    raise OutputParserException(
                        f"解析失败，已重试{retries}次：{e}", llm_output=completion
                    )
                retries += 1
                print(f"  第{retries}次尝试重试...")
                # 使用 LLM 重新生成输出
                try:
                    completion = self.retry_chain.invoke(
                        {"prompt": prompt_value.to_string(), "completion": completion}
                    )
                except Exception as retry_error:
                    raise OutputParserException(
                        f"重试输出时出错: {retry_error}", llm_output=completion
                    )
        raise OutputParserException(
            f"解析失败，已重试 {self.max_retries} 次", llm_output=completion
        )

    def parse(self, text):
        pass
