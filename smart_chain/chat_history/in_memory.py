from .base import BaseChatMessageHistory


# 定义内存中的聊天消息历史实现类，继承自BaseChatMessageHistory
class InMemoryChatMessageHistory(BaseChatMessageHistory):
    """
    内存中的聊天消息历史实现

    将消息存储在内存列表中，适用于单进程应用。

    示例:
        python
        from smartchain.chat_history import InMemoryChatMessageHistory

        history = InMemoryChatMessageHistory()
        history.add_user_message("你好")
        history.add_ai_message("你好，有什么可以帮助你的吗？")

        # 获取所有消息
        messages = history.messages

        # 清空历史
        history.clear()
    """

    # 初始化方法，创建用于存储消息的私有列表
    def __init__(self):
        """
        初始化内存消息历史
        """
        # 使用列表存储消息
        self._messages = []

    # 实现messages属性，返回消息列表的副本，避免外部修改内部状态
    @property
    def messages(self):
        """
        获取所有消息列表
        Returns:
            消息列表的副本
        """
        return self._messages.copy()

    # 实现消息添加逻辑，将收到的消息追加到列表末尾
    def _add_message_impl(self, message):
        """
        实现添加消息的具体逻辑
        Args:
            message:BaseMessage 实例

        Returns:

        """
        self._messages.append(message)

    def clear(self):
        self._messages = []

    def __repr__(self):
        """返回对象的字符串表示"""
        return f"InMemoryChatMessageHistory(messages={len(self._messages)})"
