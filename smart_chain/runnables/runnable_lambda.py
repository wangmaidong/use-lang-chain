from gc import callbacks

from .runnable import Runnable
from ..config import ensure_config, _accept_config
import uuid as uuid_module


# 定义 RunnableLambda 类，用于将普通 Python 函数封装为 Runnable 对象
class RunnableLambda(Runnable):
    """
    RunnableLambda 将普通 Python 函数包装成 Runnable

    这使得普通函数可以在链式调用中使用，并支持统一的 invoke 接口。

    示例:
        python
        def add_one(x: int) -> int:
            return x + 1

        runnable = RunnableLambda(add_one)
        result = runnable.invoke(5)  # 返回 6
        results = runnable.batch([1, 2, 3])  # 返回 [2, 3, 4]
    """

    def __init__(self, func, name: str | None = None):
        """
        初始化RunnableLambda
        :param func: 要包装的函数
        :param name: Runnable的名称，可选，默认使用函数名
        """
        # 检查传入的func是否可为可调用对象
        if not callable(func):
            raise TypeError(f"func 必须是可调用对象，但得到了 {type(func)}")
        # 保存待封装的函数
        self.func = func
        # 如果传入了name，那么则使用
        if name is not None:
            self.name = name
        else:
            try:
                # 尽量用函数原名，如果是lambda就命名为lambda
                self.name = func.__name__ if func.__name__ != "<lambda>" else "lambda"
            except AttributeError:
                self.name = "runnable"

    # 实现 innvoke,同步调用底层函数
    def invoke(self, input, config=None, **kwargs):
        """
        调用包装的函数
        :param input: 输入值
        :param config: 可选的配置字典
        :param kwargs: 额外的关键字参数
        :return:
        """
        # 保证 config 不为 None，如为 None 则转为空字典
        config = ensure_config(config)
        # 从配置字典中获取回调对象
        callbacks = config.get("callbacks")
        # 初始化回调对象列表
        callback_list = []
        # 获取当前调用的唯一 ID(run_id)
        run_id = config.get("run_id")
        # 如果没有传入 run_id, 则自动生成一个新的uuid
        if run_id is None:
            run_id = uuid_module.uuid4()
        # 如果 callbacks 不为空
        if callbacks:
            # 如果 callbacks 已经是列表，则直接用，否则转为单元素列表
            if isinstance(callbacks, list):
                callback_list = callbacks
            else:
                callback_list = [callbacks]
        # 构造序列化信息，用于回调上报链条标识
        serialized = {"name": self.name, "type": "RunnableLambda"}
        # 遍历每个回调对象，触发其 on_chain_start 方法
        for callback in callback_list:
            # 只有回调对象有 on_chain_start 属性才调用
            if hasattr(callback, "on_chain_start"):
                try:
                    # 调用回调的 on_chain_start 方法，传入相关参数
                    callback.on_chain_start(
                        serialized=serialized,
                        inputs={"input": input},
                        run_id=run_id,
                        parent_run_id=None,
                        tags=config.get("tags"),
                        metadata=config.get("metadata"),
                        **kwargs,
                    )
                except Exception:
                    # 回调过程中如出现异常则忽略，确保主流程不会终止
                    pass
        # 检查被包装的函数是否能够接收config参数
        if _accept_config(self.func):
            kwargs["config"] = config
        try:
            # 正常调用被 包装的函数，将input作为第一个参数，kwargs作为关键字参数字典
            output = self.func(input, **kwargs)
        except Exception as e:
            if callback_list:
                for callback in callback_list:
                    if hasattr(callback, "on_chain_error"):
                        try:
                            callback.on_chain_error(
                                error=e,
                                run_id=run_id,
                                parent_run_id=None,
                                **kwargs,
                            )
                        except Exception:
                            pass
            raise
        if callback_list:
            for callback in callback_list:
                if hasattr(callback, "on_chain_end"):
                    try:
                        callback.on_chain_end(
                            outputs={"output": output},
                            run_id=run_id,
                            parent_run_id=None,
                            **kwargs,
                        )
                    except Exception:
                        pass
        return output

    # 批量调用内部依然使用invoke，保证与Runnable基本一致
    def batch(self, inputs: list, config=None, **kwargs) -> list:
        """
        批量调用包装的函数
        :param inputs:输入值列表
        :param kwargs:额外的关键字参数
        :return:
            输出值列表
        """
        # 调用 invoke 实现批量处理
        return [self.invoke(input_item, config=None, **kwargs) for input_item in inputs]

    # 流式调用：直接复用基类的流式封装
    def stream(self, input, config=None, **kwargs):
        """
        流式调用包装的函数
        :param input: 输入值
        :param kwargs:额外的参数列表
        :return:
        """
        yield from super().stream(input, config=None, **kwargs)

    def __repr__(self) -> str:
        """
        返回 RunnableLambda 的字符串表示
        :return:
        """
        return f"RunnableLambda(func={self.name})"
