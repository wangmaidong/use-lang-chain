import random
import time
from abc import ABC, abstractmethod
import inspect
import uuid as uuid_module
from ..config import ensure_config, _accept_config, _merge_configs


class Runnable(ABC):
    """
    Runnable 抽象基类

    所有可运行组件的基础接口，定义了统一的调用方法。
    """

    # 抽象方法，子类必须实现，用于同步调用
    @abstractmethod
    def invoke(self, input, config=None, **kwargs):
        """
        同步调用 Runnable
        :param input: 输入值
        :param config: 可选的配置字典
        :param kwargs: 额外的关键字参数
        :return:
        """

    def stream(self, input, config=None, **kwargs):
        """
        流式调用 Runnable

        默认实现：先调用 invoke，若返回可迭代且不是字符串/字节/字典，则逐项 yield；
        否则直接 yield 单值。
        :param input:
        :param config: 可选的配置字典
        :param kwargs:
        :return:
        """
        result = self.invoke(input, config=config, **kwargs)
        # 字符串/字节/字典不视为可迭代，直接返回单值
        if hasattr(result, "__iter__") and not isinstance(result, (str, dict, bytes)):
            for item in result:
                yield item
        else:
            yield result

    # 定义批量调用方法，默认实现为遍历输入逐个调用 invoke
    def batch(self, inputs: list, config=None, **kwargs):
        """
        批量调用 Runnable
        :param inputs: 输入值列表
        config: 可选的配置字典
        :param kwargs: 额外的关键字参数
        :return:
            输出值列表
        """
        return [
            self.invoke(input_item, config=config, **kwargs) for input_item in inputs
        ]

    #  定义管道操作每个子任务的cofig的配置
    def with_config(self, config=None, **kwargs):
        """
        绑定配置到 Runnable，返回一个新的 Runnable
        :param config:
        :param kwargs:
        :return:
        """
        merged_config = {}
        if config:
            merged_config.update(config)
        if kwargs:
            merged_config.update(kwargs)

        return RunnableBinding(bound=self, config=merged_config)

    # 管道操作符，便于链式拼接
    def __or__(self, other):
        if not isinstance(other, Runnable):
            raise TypeError("管道右侧必须是Runnable实例")
        return RunnableSequence([self, other])

    def __repr__(self):
        return

    def with_retry(
        self,
        retry_if_exception_type=(Exception,),
        stop_after_attempt=3,
        wait_exponential_jitter=True,
        exponential_jitter_params=None,
    ):
        return RunnableRetry(
            bound=self,
            retry_if_exception_type=retry_if_exception_type,
            stop_after_attempt=stop_after_attempt,
            wait_exponential_jitter=wait_exponential_jitter,
            exponential_jitter_params=exponential_jitter_params,
        )


# 定义 RunnableSequence 类，用于实现可运行对象的链式组合（A | B | C 的效果）
class RunnableSequence(Runnable):
    # 初始化方法，接收一个 Runnable 对象的列表
    def __init__(self, runnables: list[Runnable]):
        # 检查传入的 runnables 列表不能为空
        if not runnables:
            raise ValueError("runnables 不能为空")
        # 校验每一个元素都必须是 Runnable 实例
        for r in runnables:
            if not isinstance(r, Runnable):
                raise TypeError("runnables 需全部为 Runnable 实例")
        self.runnables = runnables

    # 实现管道操作符 |，使链式拼接成立
    def __or__(self, other):
        # 右侧对象必须也是 Runnable 实例
        if not isinstance(other, Runnable):
            raise TypeError(f"管道右侧必须是一个Runnable实例")
        return RunnableSequence(self.runnables[other])

    # 调用链的同步调用，将输入依次传过所有组件
    def invoke(self, input, config=None, **kwargs):
        """
        逐个执行链条：上一步输出作为下一步输入。
        :param input:
        :param kwargs:
        :return:
        """
        # 确保config存在
        config = ensure_config(config)
        # 处理回调如果有callbacks则触发链的开始回调
        callbacks = config.get("callbacks")
        callbacks_list = []
        run_id = config.get("run_id")
        if run_id is None:
            run_id = uuid_module.uuid4()
        if callbacks:
            # 如果 callbacks 是列表，则直接赋值给 callback_list
            if isinstance(callbacks, list):
                callbacks_list = callbacks
            else:
                callbacks_list = [callbacks]
        # 序列化信息，用于回调上报链条标识
        serialized = {"name": "RunnableSequence", "type": "chain"}
        # 遍历每个回调对象，触发其 on_chain_start 方法
        for callback in callbacks_list:
            # 只有回调对象有on_chain_start 属性才调用
            if hasattr(callback, "on_chain_start"):
                try:
                    # 调用回调的 on_chain_start 方法，传入相关参数
                    callback.on_chain_start(
                        serialized,
                        {"input": input},
                        run_id=run_id,
                        parent_run_id=None,
                        tags=config.get("tags"),
                        metadata=config.get("metadata"),
                        **kwargs,
                    )
                except Exception:
                    pass
        # 初始化 value 为 input
        value = input
        try:
            # 依次调用每个 runnable 的 invoke，并传递最新的 value
            for runnable in self.runnables:
                child_config = config.copy()
                child_run_id = uuid_module.uuid4()
                child_config["run_id"] = child_run_id
                child_config["parent_run_id"] = run_id
                value = runnable.invoke(value, config=child_config, **kwargs)
        except Exception as e:
            # 若捕获到异常，则对所有回调触发 on_chain_error 并继续抛出异常
            if callbacks_list:
                for callback in callbacks_list:
                    if hasattr(callback, "on_chain_error"):
                        try:
                            callback.on_chain_error(
                                e, run_id=run_id, parent_run_id=None, **kwargs
                            )
                        except Exception:
                            pass
            raise
        else:
            # 如果没有异常执行，顺序触发所有回调的on_chain_end方法
            if callbacks_list:
                for callback in callbacks_list:
                    if hasattr(callback, "on_chain_end"):
                        try:
                            callback.on_chain_end(
                                outputs={"output": value},
                                run_id=run_id,
                                parent_run_id=None,
                                **kwargs,
                            )
                        except Exception:
                            pass
        return value

    # 批量调用，输入为多个 input，结果为每个 input 执行完整链条的输出
    def batch(self, inputs: list, config=None, **kwargs):
        """对输入列表逐项执行同一条链。"""
        # 逐项调用invoke,收集所有
        return [self.invoke(item, config=None, **kwargs) for item in inputs]

    # 流式调用，默认复用基类逻辑
    def stream(self, input, config=None, **kwargs):
        """
        流式执行：沿用基类逻辑，对最终结果做流式分发。
        :param input:
        :param kwargs:
        :return:
        """
        yield from super().stream(input, config=None, **kwargs)

    # 定义字符串表示，便于调试，输出链路结构
    def __repr__(self) -> str:
        names = " | ".join(
            getattr(r, "name", r.__class__.__name__) for r in self.runnables
        )


class RunnableRetry(Runnable):
    def __init__(
        self,
        bound,
        retry_if_exception_type=(Exception,),
        stop_after_attempt=3,
        wait_exponential_jitter=True,
        exponential_jitter_params=None,
    ):
        self.bound = bound
        self.retry_if_exception_type = retry_if_exception_type
        self.stop_after_attempt = stop_after_attempt
        self.wait_exponential_jitter = wait_exponential_jitter
        self.exponential_jitter_params = exponential_jitter_params or {}

    def invoke(self, input, config=None, **kwargs):
        # 记录最后一次抛出异常
        last_exception = None
        # 初始延迟
        initial = self.exponential_jitter_params.get("initial", 0)
        # 最大延迟
        max_wait = self.exponential_jitter_params.get("max_wait", 10.0)
        # 幂指数基数
        exp_base = self.exponential_jitter_params.get("exp_base", 2.0)
        # 抖动范围
        jitter = self.exponential_jitter_params.get("jitter", 0.0)

        for attempt in range(1, self.stop_after_attempt, 1):
            try:
                return self.bound.invoke(input, config=None, **kwargs)
            except self.retry_if_exception_type as error:
                # 保存本次捕获的异常
                last_exception = error
                # 如果还没有到达最大重试次数
                if attempt < self.stop_after_attempt:
                    # 如果要启动指数回退
                    if self.wait_exponential_jitter:
                        # 计算当前的延迟时间
                        delay = min(max_wait, initial * (exp_base ** (attempt - 1)))
                        # 如果配置了jitter,叠加一个随即抖动，jitter的中文含义就是抖动
                        if jitter > 0:
                            delay = random.uniform(0, jitter)
                    else:
                        delay = initial
                        time.sleep(delay)
                        # 如果抛出的是不会重试范围内的异常，则直接抛出
            except Exception:
                raise
        raise last_exception


class RunnableBinding(Runnable):
    """
    Runnable 绑定包装器
    用于将配置绑定到 Runnable，返回一个新的 Runnable 实例。
    当调用绑定的 Runnable 时，会自动合并绑定的配置和传入的配置。
    """

    def __init__(self, bound, config=None, kwargs=None):
        """
        初始化 RunnableBinding
        :param bound:要绑定的底层 Runnable 实例
        :param config:要绑定的配置字典
        :param kwargs:
        """
        if not isinstance(bound, Runnable):
            raise TypeError(f" {bound} 必须是 Runnable 实例")
        self.bound = bound
        self.config = config
        self.kwargs = kwargs or {}

    def invoke(self, input, config=None, **kwargs):
        """
        调用绑定的 Runnable，合并配置
        :param input: 输入值
        :param config: 可选的配置字典，会与绑定的配置合并
        :param kwargs: 额外的关键字参数
        :return:
        """
        merged_config = _merge_configs(self.config, config)
        merged_kwargs = {**self.kwargs, **kwargs}
        return self.bound.invoke(input, config=merged_config, **merged_kwargs)

    def batch(self, inputs, config=None, **kwargs):
        """
        批量调用绑定的 Runnable，合并配置

        Args:
            inputs: 输入值列表
            config: 可选的配置字典，会与绑定的配置合并
            **kwargs: 额外的关键字参数
        Returns:
            输出值列表
        """
        # 合并绑定的配置和传入的配置
        merged_config = _merge_configs(self.config, config)
        # 合并关键字参数
        merged_kwargs = {**self.kwargs, **kwargs}
        # 调用底层 Runnable
        return self.bound.batch(inputs, config=merged_config, **merged_kwargs)

    def stream(self, input, config=None, **kwargs):
        """
        流式调用绑定的 Runnable，合并配置
        Args:
            input: 输入值
            config: 可选的配置字典，会与绑定的配置合并
            **kwargs: 额外的关键字参数
        Yields:
            底层 Runnable 的流式输出
        """
        # 合并绑定的配置和传入的配置
        merged_config = _merge_configs(self.config, config)
        # 合并关键字参数
        merged_kwargs = {**self.kwargs, **kwargs}
        # 调用底层 Runnable
        yield from self.bound.stream(input, config=merged_config, **merged_kwargs)

    def __repr__(self):
        """返回对象的字符串表示"""
        return f"RunnableBinding(bound={self.bound}, config={self.config})"
