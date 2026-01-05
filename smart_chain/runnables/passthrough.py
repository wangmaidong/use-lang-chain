from .runnable import Runnable


class RunnablePassthrough(Runnable):
    def invoke(self, input, config=None, **kwargs):
        return input

    def batch(self, inputs: list, config=None, **kwargs):
        return list(inputs)

    def stream(self, input, config=None, **kwargs):
        # 复用基类流式封装（对单值直接 yield）
        yield from super().stream(input, config=None, **kwargs)

    def __repr__(self):
        return f"RunnablePassthrough()"
