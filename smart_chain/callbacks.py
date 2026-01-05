from abc import ABC


class BaseCallbackHandler(ABC):
    """
    回调处理器基类

    用于在 Runnable 执行过程中接收各种事件通知。
    子类可以重写感兴趣的方法来处理特定事件。
    """

    # 链开始执行时会调用此方法
    def on_chain_start(self, serialized, inputs, **kwargs):
        """
        当链开始执行时调用

        Args:
            serialized: 序列化的链信息
            inputs: 输入数据
            **kwargs: 其他关键字参数
        """
        # 默认实现为空，子类可重写
        pass

    # 链执行完成时会调用此方法
    def on_chain_end(self, outputs, **kwargs):
        """
        当链执行完成时调用
        :param outputs:输出数据
        :param kwargs:其他关键字参数
        :return:
        """
        pass

    # 链执行出错时会调用此方法
    def on_chain_error(self, error, **kwargs):
        """
        当链执行出错时调用
        :param error: 错误对象
        :param kwargs: 其他关键字参数
        :return:
        """
        pass

    # LLM 开始执行时会调用此方法
    def on_llm_start(self, serialized, prompts, **kwargs):
        """
        当 LLM 开始执行时调用

        Args:
            serialized: 序列化的 LLM 信息
            prompts: 提示词列表
            **kwargs: 其他关键字参数
        """
        # 默认实现为空，子类可重写
        pass

    # LLM 执行完成时会调用此方法
    def on_llm_end(self, response, **kwargs):
        """
        当 LLM 执行完成时调用
        Args:
            response: LLM 的响应
            **kwargs: 其他关键字参数
        """
        # 默认实现为空，子类可重写
        pass

    # LLM 执行出错时会调用此方法
    def on_llm_error(self, error, **kwargs):
        """
        当 LLM 执行出错时调用
        Args:
            error: 错误对象
            **kwargs: 其他关键字参数
        """
        # 默认实现为空，子类可重写
        pass
