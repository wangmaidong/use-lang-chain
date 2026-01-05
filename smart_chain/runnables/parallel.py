from .runnable import Runnable


class RunnableParallel(Runnable):
    """并行执行多个 Runnable，返回字典结果。"""

    # 构造方法，接收若干个可运行对象作为关键字参数
    def __init__(self, **runnables):
        # 如果未传递任何 runnable，则报错
        if not runnables:
            raise ValueError("至少需要提供一个Runnable")
        # 检查每个传入的值是否为 Runnable 实例
        for name, runnable in runnables.items():
            if not isinstance(runnable, Runnable):
                raise TypeError(f"键{name}必须是Runnable的实例")
        # 保存所有传入的 runnable 到实例属性
        self.runnables = runnables

    # 同步调用，将相同输入传递给所有子 runnable，并收集结果为字典
    def invoke(self, input, config=None, **kwargs):
        """
        同一输入传给所有子 runnable，收集结果为字典。
        :param input:
        :param config:
        :param kwargs:
        :return:
        """
        # 遍历每个 runnable，调用其 invoke，结果收集为 {name: 返回值}
        return {
            name: r.invoke(input, config=None, **kwargs)
            for name, r in self.runnables.items()
        }

    # 批量调用，对输入列表每一项都运行 invoke，返回结果字典的列表
    def batch(self, inputs: list, config=None, **kwargs):
        """
        对输入列表逐项并行处理，返回字典列表。
        :param inputs:
        :param config:
        :param kwargs:
        :return:
        """
        return [self.invoke(item, config=None, **kwargs) for item in inputs]

    # 流式调用，直接调用父类的流式实现
    def stream(self, input, config=None, **kwargs):
        """
        对单次输入执行并返回一个字典，流式单次产出。
        :param input:
        :param config:
        :param kwargs:
        :return:
        """
        for name, runnable in self.runnables.items():
            yield {name: runnable.invoke(input, config=None, **kwargs)}

    # 返回对象的字符串表示（列出包含的所有子 runnable 的键名）
    def __repr__(self):
        keys = ", ".join(self.runnables.keys())
        return f"RunnableParallel({keys})"
