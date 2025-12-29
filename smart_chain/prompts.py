
# 导入正则表达式模块，用于变量提取
import re

from langchain_classic.chains.qa_generation.prompt import templ

# 导入消息类
from .messages import SystemMessage,HumanMessage,AIMessage
# 导入解析json模块
import json
# 导入路径分析模块
from pathlib import Path
# 定义提示词模板类
class PromptTemplate:
    # 类说明文档，描述用途
    """提示词模板类，用于格式化字符串模板"""

    # 构造方法，初始化模板实例
    def __init__(self, template: str, partial_variables: dict = None):
        # 保存模板字符串到实例属性
        self.template = template
        # 保存部分变量（已预填充的变量）
        self.partial_variables = partial_variables or {}
        # 调用内部方法提取模板中的变量名列表
        input_variables = self._extract_variables(template)
        # 将变量名列表分配给实例属性
        # self.input_variables = input_variables
        self.input_variables = [v for v in input_variables if v not in self.partial_variables]
    # 类方法：从模板字符串生成 PromptTemplate 实例
    @classmethod
    def from_template(cls, template: str):
        # 返回用 template 实例化的 PromptTemplate 对象
        return cls(template=template)

    # 格式化填充模板中的变量
    def format(self, **kwargs):
        # 合并部分变量和用户提供的变量
        all_vars = {**self.partial_variables, **kwargs}
        # 计算模板中缺失但未传入的变量名集合
        missing_vars = set(self.input_variables) - set(kwargs.keys())
        # 如果存在缺失变量则抛出异常，提示哪些变量缺失
        if missing_vars:
            raise ValueError(f"缺少必需的变量: {missing_vars}")
        # 使用传入参数填充模板并返回格式化后的字符串
        return self.template.format(**all_vars)

    # 内部方法：从模板字符串中提取变量名
    def _extract_variables(self, template: str):
        # 定义正则表达式，匹配花括号中的变量名（冒号前的部分）
        pattern = r'\{([^}:]+)(?::[^}]+)?\}'
        # 查找所有符合 pattern 的变量名，返回匹配结果列表
        matches = re.findall(pattern, template)
        # 利用 dict 去重并保持顺序，最后转为列表返回
        return list(dict.fromkeys(matches))

    # 定义部分填充模板变量的方法，返回新的模板实例
    def partial(self, **kwargs):
        """
        部分填充模板变量，返回一个新的 PromptTemplate 实例
        **kwargs: 要部分填充的变量及其值
        Returns: 新的 PromptTemplate 实例，其中指定的变量已被填充
        """
        # 合并现有对象的部分变量（partial_variables）和本次要填充的新变量
        new_partial_variables = {**self.partial_variables, **kwargs}
        # 使用原模板字符串和更新后的部分变量，创建新的 PromptTemplate 实例
        new_template = PromptTemplate(
            template= self.template,
            partial_variables = new_partial_variables
        )
        return new_template

# 定义用于处理多轮对话消息模板的类
class ChatPromptTemplate:
    # 聊天提示词模板类，用于创建多轮对话的提示词
    """聊天提示词模板类，用于创建多轮对话的提示词"""
    def __init__(self,messages):
        # 保存消息模板/对象列表
        self.messages = messages
        # 提取所有输入变量并存入实际变量
        self.input_variables = self._extract_input_variables()

    # 定义一个类方法，用于通过消息对象列表创建 ChatPromptTemplate 实例
    @classmethod
    def from_messages(cls, messages):
        # 使用传入的 messages 参数创建并返回 ChatPromptTemplate 实例
        return cls(messages = messages)
    def format_messages(self, **kwargs):
        return self._format_all_messages(kwargs)
    def _extract_input_variables(self):
        # 用集合保存变量名，防止重复
        variables = set()
        # 遍历所有消息模板/对象
        for msg in self.messages:
            # 如果元素是（role,template_str）元组
            if isinstance(msg,tuple) and len(msg) == 2:
                _,template_str = msg
                # 用PromptTemplate对象提取变量
                prompt = PromptTemplate.from_template(template_str)
                # 合并到集合中
                variables.update(prompt.input_variables)
            elif isinstance(msg, BaseMessagePromptTemplate):
                variables.update(msg.prompt.input_variables)
            elif isinstance(msg, MessagesPlaceholder):
                variables.update(msg.variable_name)
        # 返回所有变量名组成的列表
        return list(variables)
    # 根据输入变量格式化所有消息模板，返回ChatPromptValue对象
    def invoke(self, input_variables):
        # 对消息模板进行实际变量填充
        formatted_messages = self._format_all_messages(input_variables)
        # 封装成ChatPromptValue对象返回
        return ChatPromptValue(messages = formatted_messages)

    def _format_all_messages(self,variables):
        # 新建列表保存格式化好的消息
        formatted_messages = []
        # 遍历每一个消息模板/对象
        for msg in self.messages:
            # 若是(role, template_str)元组
            if isinstance(msg, tuple) and len(msg) == 2:
                role, template_str = msg
                # 创建PromptTemplate模板并填充变量
                prompt = PromptTemplate.from_template(template_str)
                content = prompt.format(**variables)
                # 根据角色字符串生成对应的消息对象
                formatted_messages.append(self._create_message_from_role(role,content))
            # 如果是BaseMessagePromptTemplate的实例
            elif isinstance(msg,BaseMessagePromptTemplate):
                formatted_messages.append(msg.format(**variables))
            # 如果是占位符对象
            elif isinstance(msg,MessagesPlaceholder):
                placeholder_messages = self._get_placeholder_value(
                    msg.variable_name, variables.get(msg.variable_name)
                )
                formatted_messages.extend(placeholder_messages)
            else:
                formatted_messages.append(msg)
        return formatted_messages

    def _create_message_from_role(self, role, content):
        # 角色字符串转小写做归一化
        normalized_role = role.lower()
        if normalized_role == "system":
            return SystemMessage(content=content)
        elif normalized_role == "human":
            return HumanMessage(content=content)
        elif normalized_role == "ai":
            return AIMessage(content=content)
        # 如果角色未知，则抛出异常
        raise ValueError(f"未知的消息角色: {role}")
    def _get_placeholder_value(self, variable_name, value):
        if value is None:
            raise ValueError(f"MessagePlaceHolder {variable_name} 对应的值缺失")
        if isinstance(value, ChatPromptValue):
            return value.to_messages()
        elif isinstance(value,list):
            return [self._get_single_message(item) for item in value]
        else:
            return [self._get_single_message(value)]
    def _get_single_message(self, value):
        if isinstance(value,(SystemMessage, HumanMessage,AIMessage)):
            return value
        elif hasattr(value, "type") and hasattr(value, "content"):
            return value
        elif isinstance(value, str):
            return HumanMessage(content=value)
        elif isinstance(value, tuple):
            role, content = value
            return self._create_message_from_role(role,content)
        elif isinstance(value, dict):
            role = value.get("role", "user")
            content = value.get("content", "")
            return self._create_message_from_role(role,content)
        else:
            raise TypeError("无法将占位符的内容转化为消息")

# 定义一个用于存放格式化后的消息的类
class ChatPromptValue:
    # 聊天提示词值类，包含格式化后的消息列表
    """聊天提示词值类，包含格式化后的消息列表"""
    def __init__(self,messages):
        # 保存消息列表到实体变量
        self.messages = messages
    def to_string(self):
        # 新建一个用于存放字符串的列表
        parts = []
        for msg in self.messages:
            if hasattr(msg, "type") and hasattr(msg, "content"):
                role_map = {
                    "system": "System",
                    "human": "Human",
                    "ai": "AI"
                }
                # 获取对应的角色字符串，没有则首字母大写
                role = role_map.get(msg.type, msg.type.capitalize())
#               # 拼接角色和消息内容
                parts.append(f"{role}:{msg.content}")
            else:
                parts.append(str(msg))
        return "\n".join(parts)

    def to_messages(self):
        return self.messages
# 定义基础消息提示词模板类
class BaseMessagePromptTemplate:
    # 基础消息提示词模板类声明
    """基础消息提示词模板类"""
    # 构造函数，必须传入PromptTemplate实例
    def  __init__(self,prompt: PromptTemplate):
         # 将PromptTemplate实例保存在self.prompt属性中
         self.prompt = prompt

    # 工厂方法，利用模板字符串创建类实例
    @classmethod
    def from_template(cls, template: str):
        # 通过模板字符串创建PromptTemplate对象
        prompt = PromptTemplate.from_template(template)
        # 用生成的PromptTemplate 创建本类实体
        return cls(prompt=prompt)
    def format(self, **kwargs):
        # 使用PromptTemplate格式化内容，得到最终文本
        content = self.prompt.format(**kwargs)
        # 调用子类实现的方法将文本转换为对应消息的对象
        return self._create_message(content)
    # 抽象方法，子类必须实现，用于生成特定类型的消息对象
    def _create_message(self, content):
        raise NotImplementedError

# 系统消息提示词模板类，继承自BaseMessagePromptTemplate
class SystemMessagePromptTemplate(BaseMessagePromptTemplate):
    # 系统消息提示词模板说明
    """系统消息提示词模板"""
    # 实现父类的_create_message 方法，返回系统消息对象
    def _create_message(self, content):
        # 创建并返回SystemMessage对象，内容为content
        return SystemMessage(content = content)

# 系统消息提示词模板类，继承自BaseMessagePromptTemplate
class HumanMessagePromptTemplate(BaseMessagePromptTemplate):
    # 系统消息提示词模板说明
    """系统消息提示词模板"""
    # 实现父类的_create_message 方法，返回系统消息对象
    def _create_message(self, content):
        # 创建并返回SystemMessage对象，内容为content
        return HumanMessage(content = content)

# 系统消息提示词模板类，继承自BaseMessagePromptTemplate
class AIMessagePromptTemplate(BaseMessagePromptTemplate):
    # 系统消息提示词模板说明
    """系统消息提示词模板"""
    # 实现父类的_create_message 方法，返回系统消息对象
    def _create_message(self, content):
        # 创建并返回SystemMessage对象，内容为content
        return AIMessage(content = content)

# 定义动态消息列表占位符类
class MessagesPlaceholder:
    # 在聊天模板中插入动态消息列表的占位符
    """在聊天模板中插入动态消息列表的占位符"""
    def __init__(self,variable_name:str):
        self.variable_name = variable_name

class FewShotPromptTemplate:
    # 文档字符串：说明该类用于构造 few-shot 提示词的模板
    """用于构造few-shot 提示词模板"""
    # 构造方法，初始化类的各种属性
    def __init__(
            self,
            *,
            examples: list[dict] = None,
            example_prompt: PromptTemplate | str,
            prefix: str = "",
            suffix: str = "",
            example_separator: str = "\n\n",
            input_variables: list[str] | None = None,
            example_selector = None, # 示例选择器（可选）
    ):
        if examples is None and example_selector is None:
            raise ValueError(f"必须提供examples或example_selector中的一项")
        if example_selector is not None and examples is not None:
            raise ValueError(f"不能同时提供examples和example_selector，只能选择其中一个")
        # 如果未传入 examples，默认使用空列表
        self.examples = examples or []
        # 判断 example_prompt 是否为 PromptTemplate 类型
        if isinstance(example_prompt, PromptTemplate):
            # 如果是 PromptTemplate 直接赋值
            self.example_prompt = example_prompt
        else:
            self.example_prompt = PromptTemplate.from_template(example_prompt)
        # 保留前缀
        self.prefix = prefix
        # 保留后缀
        self.suffix = suffix
        # 保存示例分割符
        self.example_separator = example_separator
        # 保存示例选择实例
        self.example_selector = example_selector
        # 如果未指定输入变量，则自动根据前后缀推断变量名
        self.input_variables = input_variables or self._infer_input_variables()

    # 私有方法：推断前缀和后缀出现的模板变量名
    def _infer_input_variables(self) -> list[str]:
        # 新建一个集合用于保存变量名去重
        variables = set()
        # 提取 prefix 中引用的变量名
        variables.update(self._extract_vars(self.prefix))
        # 提取 suffix 中引用的变量名
        variables.update(self._extract_vars(self.suffix))
        # 转换为列表返回
        return list(variables)
    # 私有方法：提取文本中的所有花括号包裹的模板变量名
    def _extract_vars(self, text: str) -> list[str]:
        # 如果输入空字符床，直接返回空列表
        if not text:
            return []
        # 定义正则表达式，匹配 {变量名} 或 {变量名:格式}
        pattern = r"\{([^}:]+)(?::[^}]+)?\}"
        # 使用 re.findall 提取所有变量名
        matches = re.findall(pattern, text)
        # 去重并保持顺序返回变量名列表
        return list(dict.fromkeys(matches))
    # 格式化 few-shot 提示词， 返回完整字符串
    def format(self, **kwargs) -> str:
        """
        根据传入的变量生成完整的 few-shot 提示词文本
        **kwargs: 输入变量，可选，供示例选择
        """
        # 判断必需的变量是否全部传入，缺失时抛异常
        missing = set(self.input_variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"缺少必需的变量：{missing}")
        # 新建 parts 列表，用于拼接完整提示词的各部分内容
        parts: list[str] = []
        # 如果前缀不为空，格式化后加入parts
        if self.prefix:
            parts.append(self._format_text(self.prefix, **kwargs))
        # 如果存在示例选择实例
        if self.example_selector:
            example_block = self.example_separator.join(
                self._format_examples(input_variables=kwargs)
            )
        else:
            # 调用 format_examples 得到所有示例的字符串，并用分隔符拼接在一起
            example_block = self.example_separator.join(self._format_examples(kwargs))
        # 如果 example_block 不为空字符串，加入 parts
        if example_block:
            parts.append(example_block)
        # 如果后缀不为空，格式化后加入 parts
        if self.suffix:
            parts.append(self._format_text(self.suffix, **kwargs))
        # 用示例分隔符连接所有组成部分，过滤空字符串
        return self.example_separator.join(part for part in parts if part)

    # 私有方法：用 PromptTemplate 对 text 进行格式化
    def _format_text(self,text: str ,**kwargs):
        # 先创建 PromptTempalte 实例
        temp_prompt = PromptTemplate.from_template(text)
        # 用传入参数格式化
        return temp_prompt.format(**kwargs)
    # 格式化所有示例，返回字符串列表
    def _format_examples(self, input_variables: dict = None) -> list[str]:
        """返回格式化后的示例字符串列表"""
        if self.example_selector:
            selected_examples = self.example_selector.select_examples(input_variables)
        else:
            selected_examples = self.examples
        # 新建存放格式化后示例的列表
        formatted_examples = []
        # 遍历 every example 字典
        for example in selected_examples:
            # 用 example_propmt 对当前示例格式化
            formatted_examples.append(self.example_prompt.format(**example))
        return formatted_examples

# 定义一个从文件加载提示词模板的函数
def load_prompt(path:str | Path, encoding:str | None = None) ->PromptTemplate:
     # 将传入的路径参数转换为 Path 对象，方便后续进行文件操作
     file_path = Path(path)
     # 判断文件是否存在，如果不存在则抛出FileNotFoundError 异常
     if not file_path.exists():
         raise FileNotFoundError(f"提示词文件不存在: {path}")
     # 判断文件扩展名是否为 .json 如果不是则抛出ValueError错误
     if file_path.suffix != ".json":
         raise ValueError(f"只支持 .json 格式文件，当前文件: {file_path.suffix}")
     # 打开文件，使用指定编码（一般为 utf-8），并读取 JSON 配置信息到 config 变量
     with file_path.open(encoding=encoding) as f:
         config = json.load(f)
     config_type = config.get("type", "prompt")
     if config_type != "prompt":
         raise ValueError(f"不支持的提示词类型: {config_type}，当前只支持 'prompt'")
     template = config.get("template")
     if template is None:
         raise ValueError("配置文件中缺少 'template' 字段")
     return PromptTemplate.from_template(template)