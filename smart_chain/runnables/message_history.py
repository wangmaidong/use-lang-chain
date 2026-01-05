from requests import session

from ..messages import HumanMessage, AIMessage
from .runnable import Runnable
from ..config import ensure_config
from ..chat_history import InMemoryChatMessageHistory


class RunnableWithMessageHistory(Runnable):
    def __init__(
        self,
        runnable,  # 链条，要包装的Runnable实例
        get_session_history,  # 获取某个用户的历史记录,每个用户对应一个InMemoryChatMessageHistory实例
        *,  # 代表后面只能传关键字参数了，因为*可能匹配所有的位置 参数
        input_messages_key=None,  # 输入字典中存放用户问题的key
        history_messages_key=None,  # 历史消息键名
    ):
        self.runnable = runnable
        self.get_session_history = get_session_history
        self.input_messages_key = input_messages_key
        self.history_messages_key = history_messages_key

    # 带历史的invoke调用
    def invoke(self, input, config=None, **kwargs):
        # 确保config是存在的，并且格式是字典
        config = ensure_config(config)
        # 获取自定义配置部分
        configurable = config.get("configurable", {})
        session_id = configurable.get("session_id")
        if not session_id:
            raise ValueError("config['configurable']['session_id'] 必须提供")

        # 拉取此用户会话历史对象
        history: InMemoryChatMessageHistory = self.get_session_history(session_id)
        # 准备带历史消息的输入
        input[self.history_messages_key] = history.messages
        # 调用底层包装好的runnable
        output = self.runnable.invoke(input, config=config, **kwargs)
        # 添加用户消息
        history.add_user_message(
            HumanMessage(content=input.get(self.input_messages_key))
        )
        # 添加大模型的AI消息
        history.add_ai_message(output)
        return output

    def batch(self, inputs, config=None, **kwargs):
        return [self.invoke(input, config=config, **kwargs) for input in inputs]

    def stream(self, input, config=None, **kwargs):
        output = self.invoke(input, config=config, **kwargs)
        yield output

    def __repr__(self):
        return f"""RunnableWithMessageHistory(
        runnable={self.runnable},
        input_messages_key={self.input_messages_key},
        history_messages_key={self.history_messages_key},
        )"""
