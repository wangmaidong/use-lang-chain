
# 导入正则表达式模块，用于变量提取
import re

from pyexpat.errors import messages

# 导入消息类
from .messages import SystemMessage,HumanMessage,AIMessage
# 定义提示词模板类
class PromptTemplate:
    # 类说明文档，描述用途
    """提示词模板类，用于格式化字符串模板"""

    # 构造方法，初始化模板实例
    def __init__(self, template: str):
        # 保存模板字符串到实例属性
        self.template = template
        # 调用内部方法提取模板中的变量名列表
        input_variables = self._extract_variables(template)
        # 将变量名列表分配给实例属性
        self.input_variables = input_variables

    # 类方法：从模板字符串生成 PromptTemplate 实例
    @classmethod
    def from_template(cls, template: str):
        # 返回用 template 实例化的 PromptTemplate 对象
        return cls(template=template)

    # 格式化填充模板中的变量
    def format(self, **kwargs):
        # 计算模板中缺失但未传入的变量名集合
        missing_vars = set(self.input_variables) - set(kwargs.keys())
        # 如果存在缺失变量则抛出异常，提示哪些变量缺失
        if missing_vars:
            raise ValueError(f"缺少必需的变量: {missing_vars}")
        # 使用传入参数填充模板并返回格式化后的字符串
        return self.template.format(**kwargs)

    # 内部方法：从模板字符串中提取变量名
    def _extract_variables(self, template: str):
        # 定义正则表达式，匹配花括号中的变量名（冒号前的部分）
        pattern = r'\{([^}:]+)(?::[^}]+)?\}'
        # 查找所有符合 pattern 的变量名，返回匹配结果列表
        matches = re.findall(pattern, template)
        # 利用 dict 去重并保持顺序，最后转为列表返回
        return list(dict.fromkeys(matches))

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
                placeholder_messages = self._coerce_placeholder_value(
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
    def _coerce_placeholder_value(self, variable_name, value):
        if isinstance(value, list):
            messages = []
            for msg in value:
                # 如果是已有消息类型，直接返回
                if isinstance(msg, (SystemMessage, HumanMessage, AIMessage)):
                    messages.append(msg)
                # 有type 和 content属性，也有消息对象直接返回
                elif hasattr(msg, "type") and hasattr(msg, "content"):
                    messages.append(msg)
                # 字符串变为人类消息
                elif isinstance(msg, str):
                    messages.append(HumanMessage(content=msg))
                # 如果是元组(role,content)转为指定角色的消息
                elif isinstance(msg, tuple) and len(msg) == 2:
                    role, content = msg
                    # 根据role和content生成对应的消息对象
                    messages.append(self._create_message_from_role(role, content))
                # 字典，默认user角色
                elif isinstance(msg, dict):
                    # 获取role和content
                    role = msg.get("role", "user")
                    # 获取content
                    content = msg.get("content", "")
                    # 根据role和content生成对应的消息对象
                    messages.append(self._create_message_from_role(role, content))
                else:
                    # 其他无法识别类型，抛出异常
                    raise TypeError("无法将占位符内容转换为消息")
            return messages
        else:
            raise ValueError("variable history should be a list of base messages")
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