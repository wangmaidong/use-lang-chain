# 导入操作系统相关模块
import os

# 导入 openai 模块
import openai
from langchain_classic.chains.question_answering.map_reduce_prompt import messages

# 从 .messages 模块导入 AIMessage、HumanMessage 和 SystemMessage 类
from .messages import AIMessage,HumanMessage,SystemMessage
from .prompts import ChatPromptValue
# 定义与OpenAI聊天交互的类
class ChatOpenAI:
    # 初始化方法
    def __init__(self,model:str = "gpt-4o", **kwargs):
        # 初始化 ChatOpenAI 类
        """
        初始化 ChatOpenAI
        :param model: 模型名称，如 "gpt-4o"
        :param kwargs: 其他参数（如 temperature, max_tokens 等）
        """
        # 设置模型名
        self.model = model
        # 获取 api_key,优先从参数获取，没有则从环境变量获取
        self.api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
        # 如果没有提供 api_key 则抛出异常
        if not self.api_key:
            raise ValueError("需要提供 api_key 或设置 OPENAI_API_KEY 环境变量")
        # 保存除 api_key之外的其他参数，用于API调用
        self.model_kwargs = {k: v for k, v in kwargs.items() if k != "api_key"}
        # 创建OpenAi 客户端实例
        self.client = openai.OpenAI(api_key=self.api_key)

    # 调用模型生成回复的方法
    def invoke(self, input, **kwargs):
        # 调用模型生成回复
        """
        调用模型生成回复
        :param input: 输入内容，可以是字符串或消息列表
        :param kwargs: 额外的 API 参数
        :return: AI 的回复消息
        """
        # 将输入数据转换为消息格式
        messages = self._convert_input(input)
        # 构建 API 请求参数字典
        params = {
            "model": self.model,
            "messages": messages,
            **self.model_kwargs,
            **kwargs
        }
        # 使用 OpenAI 客户端发起 chat.completions.create 调用获取回复
        response = self.client.chat.completions.create(**params)
        # 取出返回结果中的第一个选项
        choice = response.choices[0]
        # 获取消息内容
        content = choice.message.content or ""
        # 返回一个 AIMessage 对象
        return AIMessage(content=content)
    def stream(self,input,**kwargs):
        # 流式调用模型生成回复
        """
        流式调用模型生成回复
        :param input: 输入内容，可以是字符串或消息列表
        :param kwargs: 额外的 API 参数
        Yields:
            AIMessage: AI 的回复消息块（每次产生部分内容）
        """
        # 将输入数据转换为消息格式
        messages = self._convert_input(input)
        # 构建API请求参数字典，启用流式输出
        params = {
            "model": self.model,
            "messages": messages,
            "stream": True,  # 启用流式输出
            **self.model_kwargs,
            **kwargs
        }
        # 使用OpenAI 客户端发起流式调用
        stream = self.client.chat.completions.create(**params)
        # 迭代流式响应
        for chunk in stream:
            # 检查是否有内容增量
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                # 检查 delta中是否有 content，如果有则发送
                if hasattr(delta, "content") and delta.content:
                    yield AIMessage(content=delta.content)


    # 内部方法，将输入转换为 OpenAI API 需要的消息格式
    def _convert_input(self, input):
        """
        将输入转换为 API 需要的消息格式

        Args:
            input: 字符串、消息列表或 ChatPromptValue

        Returns:
            list[dict]: API 格式的消息列表
        """
        # 如果输入是字符串，直接作为用户消息
        if isinstance(input, str):
            return [{"role": "user", "content": input}]
        # 如果输入的类型是列表
        elif isinstance(input, list):
            # 新建一个空的消息列表
            messages = []
            # 遍历输入列表中的每一个元素
            for msg in input:
                # 判断是否为字符串，是则作为用户消息加入
                if isinstance(msg, str):
                    messages.append({"role": "user", "content": msg})
                # 判断是否为 HumanMessage,AImessage或SystemMessage 实例
                elif isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
                    # 如果是 HumanMessage，将角色设为 user
                    if isinstance(msg, HumanMessage):
                        role = "user"
                    # 如果是 AIMessage，将角色设为 assistant
                    elif isinstance(msg, AIMessage):
                        role = "assistant"
                    # 如果是 SystemMessage，将角色设为 system
                    elif isinstance(msg, SystemMessage):
                        role = "system"
                    # 获取消息内容（有content属性则取content,否则转为字符串）
                    content = msg.content if hasattr(msg, content) else str(msg)
                    # 将角色和内容添加到消息列表
                    messages.append({"role": role, "content": content})
                # 如果元素本身为字典，直接添加进消息列表
                elif isinstance(msg, dict):
                    messages.append(dict)
                # 如果元素为长度为 2 的元组，将其解包为 role 和 content
                elif isinstance(msg, tuple) and len(msg) == 2:
                    # 将元组解包为role 和 content
                    role, content = msg
                    # 将角色和内容添加到消息列表
                    messages.append({"role": role, "content": content})
            return messages
        else:
            # 其他输入类型，转为字符串作为 user 消息
            return [{"role": "user", "content": str(input)}]

# 定义与 DeepSeek 聊天模型交互的类
class ChatDeepSeek:
   # 初始化方法
   # model: 模型名称，默认为 "deepseek-chat"
   # **kwargs: 其他可选参数（如 temperature, max_tokens 等）
   def __init__(self, model: str = "deepseek-chat", **kwargs):
       """
       初始化 ChatDeepSeek

       Args:
           model: 模型名称，如 "deepseek-chat"
           **kwargs: 其他参数（如 temperature, max_tokens 等）
       """
       # 设置模型名称
       self.model = model
       # 获取 api_key，优先从参数获取，否则从环境变量获取
       self.api_key = kwargs.get("api_key") or os.getenv("DEEPSEEK_API_KEY_DEEP")
       # 如果没有提供 api_key，则抛出异常
       if not self.api_key:
           raise ValueError("需要提供 api_key 或设置 DEEPSEEK_API_KEY_DEEP 环境变量")
       # 保存除 api_key 之外的其他参数，用于 API 调用
       self.model_kwargs = {k: v for k, v in kwargs.items() if k != "api_key"}
       # 获取 DeepSeek 的 base_url，默认为官方地址
       base_url = kwargs.get("base_url", "https://api.deepseek.com/v1")
       # 创建 OpenAI 兼容的客户端实例（DeepSeek 使用 OpenAI 兼容的 API）
       self.client = openai.OpenAI(api_key=self.api_key, base_url=base_url)

   # 调用模型生成回复的方法
   # input: 输入内容，可以是字符串或消息列表
   # **kwargs: 额外的 API 参数
   def invoke(self, input, **kwargs):
       """
       调用模型生成回复

       Args:
           input: 输入内容，可以是字符串或消息列表
           **kwargs: 额外的 API 参数

       Returns:
           AIMessage: AI 的回复消息
       """
       # 将输入数据转换为消息格式
       messages = self._convert_input(input)
       # 构建 API 请求参数字典
       params = {
           "model": self.model,
           "messages": messages,
           **self.model_kwargs,
           **kwargs
       }
       # 使用 OpenAI 兼容的客户端发起 chat.completions.create 调用获取回复
       response = self.client.chat.completions.create(**params)
       # 取出返回结果中的第一个选项
       choice = response.choices[0]
       # 获取消息内容
       content = choice.message.content or ""
       # 返回一个 AIMessage 对象
       return AIMessage(content=content)

   # 内部方法，将输入转换为 API 需要的消息格式
   # input: 字符串、消息列表或 ChatPromptValue
   def _convert_input(self, input):
       """
       将输入转换为 API 需要的消息格式

       Args:
           input: 字符串、消息列表或 ChatPromptValue

       Returns:
           list[dict]: API 格式的消息列表
       """
       # 如果输入是字符串，直接作为用户消息
       if isinstance(input,ChatPromptValue):
            input = input.to_messages()
       if isinstance(input, str):
           return [{"role": "user", "content": input}]
       # 如果输入的类型是列表
       elif isinstance(input, list):
           # 新建一个空的消息列表
           messages = []
           # 遍历输入列表中的每一个元素
           for msg in input:
               # 判断是否为字符串，是则作为用户消息加入
               if isinstance(msg, str):
                   messages.append({"role": "user", "content": msg})
               # 判断是否为 HumanMessage,AImessage或SystemMessage 实例
               elif isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
                   # 如果是 HumanMessage，将角色设为 user
                   if isinstance(msg, HumanMessage):
                       role = "user"
                   # 如果是 AIMessage，将角色设为 assistant
                   elif isinstance(msg, AIMessage):
                       role = "assistant"
                   # 如果是 SystemMessage，将角色设为 system
                   elif isinstance(msg, SystemMessage):
                       role = "system"
                   # 获取消息内容（有content属性则取content,否则转为字符串）
                   content = msg.content if hasattr(msg, "content") else str(msg)
                   # 将角色和内容添加到消息列表
                   messages.append({"role": role, "content": content})
               # 如果元素本身为字典，直接添加进消息列表
               elif isinstance(msg, dict):
                   messages.append(msg)
               # 如果元素为长度为 2 的元组，将其解包为 role 和 content
               elif isinstance(msg, tuple) and len(msg) == 2:
                   # 将元组解包为role 和 content
                   role, content = msg
                   # 将角色和内容添加到消息列表
                   messages.append({"role": role, "content": content})
           return messages
       else:
           # 其他输入类型，转为字符串作为 user 消息
           return [{"role": "user", "content": str(input)}]

   def stream(self, input, **kwargs):
       # 流式调用模型生成回复
       """
       流式调用模型生成回复
       :param input: 输入内容，可以是字符串或消息列表
       :param kwargs: 额外的 API 参数
       Yields:
           AIMessage: AI 的回复消息块（每次产生部分内容）
       """
       # 将输入数据转换为消息格式
       messages = self._convert_input(input)
       # 构建API请求参数字典，启用流式输出
       params = {
           "model": self.model,
           "messages": messages,
           "stream": True,  # 启用流式输出
           **self.model_kwargs,
           **kwargs
       }
       # 使用OpenAI 客户端发起流式调用
       stream = self.client.chat.completions.create(**params)
       # 迭代流式响应
       for chunk in stream:
           # 检查是否有内容增量
           if chunk.choices and len(chunk.choices) > 0:
               delta = chunk.choices[0].delta
               # 检查 delta中是否有 content，如果有则发送
               if hasattr(delta, "content") and delta.content:
                   yield AIMessage(content=delta.content)



# 定义与通义千问（Tongyi）聊天模型交互的类
class ChatTongyi:
   
   # 初始化方法
   # 初始化方法，设置模型名称和 API 相关参数
   def __init__(self, model: str = "qwen-max", **kwargs):
       """
       初始化 ChatTongyi
       
       Args:
           model: 模型名称，如 "qwen-max"
           **kwargs: 其他参数（如 temperature, max_tokens 等）
       """
       # 设置模型名称
       self.model = model
       # 获取 api_key，优先从参数获取，否则从环境变量获取
       self.api_key = kwargs.get("api_key") or os.getenv("DASHSCOPE_API_KEY")
       # 如果没有提供 api_key，则抛出异常
       if not self.api_key:
           raise ValueError("需要提供 api_key 或设置 DASHSCOPE_API_KEY 环境变量")
       # 保存除 api_key 之外的其他参数，用于 API 调用
       self.model_kwargs = {k: v for k, v in kwargs.items() if k != "api_key"}
       # 获取通义千问的 API base URL（使用 OpenAI 兼容模式），如果未指定则使用默认值
       base_url = kwargs.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
       # 创建 OpenAI 兼容的客户端实例（通义千问使用 OpenAI 兼容的 API）
       self.client = openai.OpenAI(api_key=self.api_key, base_url=base_url)
   
   # 调用模型生成回复的方法
   # 调用模型生成回复，返回 AIMessage 对象
   def invoke(self, input, **kwargs):
       """
       调用模型生成回复
       
       Args:
           input: 输入内容，可以是字符串或消息列表
           **kwargs: 额外的 API 参数
       
       Returns:
           AIMessage: AI 的回复消息
       """
       # 将输入数据转换为消息格式
       messages = self._convert_input(input)
       # 构建 API 请求参数字典，包含模型名、消息内容和其他参数
       params = {
           "model": self.model,
           "messages": messages,
           **self.model_kwargs,
           **kwargs
       }
       # 使用 OpenAI 兼容的客户端发起 chat.completions.create 调用以获取回复
       response = self.client.chat.completions.create(**params)
       # 取出返回结果中的第一个回复选项
       choice = response.choices[0]
       # 获取回复的消息内容，如果内容不存在则返回空字符串
       content = choice.message.content or ""
       # 构建并返回一个 AIMessage 对象
       return AIMessage(content=content)
   
   # 内部方法，将输入转换为 API 需要的消息格式
   # 支持字符串、消息列表等输入，统一包装为 OpenAI API 格式
   def _convert_input(self, input):
       """
       将输入转换为 API 需要的消息格式
       
       Args:
           input: 字符串、消息列表或 ChatPromptValue
       
       Returns:
           list[dict]: API 格式的消息列表
       """
       # 如果输入是字符串，直接包装为“用户”角色的消息
       if isinstance(input, str):
           return [{"role": "user", "content": input}]
       else:
           # 其他输入类型，转换为字符串作为“用户”消息内容
           return [{"role": "user", "content": str(input)}]            