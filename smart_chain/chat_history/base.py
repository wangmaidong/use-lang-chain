# 导入抽象基类ABC，以及抽象方法abstractmethod
from abc import ABC, abstractmethod

# 从当前包的messages模块导入基础消息类、人类消息类和AI消息类
from ..messages import BaseMessage, HumanMessage, AIMessage


# 定义聊天消息历史的抽象基类，继承自ABC
class BaseChatMessageHistory(ABC):
    """
    聊天消息历史的抽象基类

    定义了存储和管理聊天消息历史的标准接口。
    """

    # 定义抽象属性messages，要求子类实现
    @property
    @abstractmethod
    def messages(self):
        """
        获取所有消息列表
        Returns:
            消息列表
        """
        pass

    # 添加用户消息的便捷方法，可以接收HumanMessage实例或字符串
    def add_user_message(self, message):
        """
        添加用户消息的便捷方法
        Args:
            message:HumanMessage 实例或字符串

        Returns:

        """
        if isinstance(message, HumanMessage):
            self.add_message(message)
        else:
            self.add_message(HumanMessage(content=message))

    # 添加AI消息的便捷方法，可以接收AIMessage实例或字符串
    def add_ai_message(self, message):
        """
        添加 AI 消息的便捷方法
        Args:
            message: AIMessage 实例或字符串

        Returns:

        """
        # 如果参数是AIMessage实例，则直接添加
        if isinstance(message, AIMessage):
            self.add_message(message)
        else:
            self.add_message(AIMessage(content=message))

    # 添加单个消息，可以接收BaseMessage实例
    def add_message(self, message):
        """
        添加单个消息
        Args:
            message:BaseMessage 实例

        Returns:

        """
        self.add_messages([message])

    # 批量添加消息
    def add_messages(self, messages):
        """
        批量添加消息
        Args:
            messages:消息列表

        Returns:

        """
        # 遍历所有消息
        for message in messages:
            # 检查类型是否为BaseMessage的子类
            if not isinstance(message, BaseMessage):
                raise TypeError(
                    f"消息必须是 BaseMessage 实例，但得到了 {type(message)}"
                )
            # 调用子类实现的消息添加逻辑
            self._add_message_impl(message)

    # 定义抽象方法，子类需实现具体的单条消息添加逻辑
    @abstractmethod
    def _add_message_impl(self, message):
        """
        子类需要实现的添加消息的具体逻辑
        Args:
            message:

        Returns:

        """
        pass

    # 定义抽象方法，子类需实现清空历史的具体逻辑
    @abstractmethod
    def clear(self):
        """清空所有消息"""
        pass
