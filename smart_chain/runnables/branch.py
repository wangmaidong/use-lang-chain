from .runnable import Runnable


class RunnableBranch(Runnable):
    def __init__(self, *branches):
        # branches里面本身是个元组，但是在我们这里需要转成一个列表
        if len(branches) < 2:
            raise ValueError(f"至少需要有一个条件分支和一个默认分支")
        branches_list = list(branches)
        # 最后一个位置参数为默认分支
        default_branch = branches_list.pop()
        # 校验每个分支
        validated_branches = []
        # 遍历每个分支
        for branch in branches_list:
            # 解包条件函数和runnable
            condition, runnable = branch
            if not callable(condition):
                raise TypeError("分支条件必须是可调用对象")
            if not isinstance(runnable, Runnable):
                raise TypeError("runnable必须是Runnable实例")
            validated_branches.append((condition, runnable))
        if not isinstance(default_branch, Runnable):
            raise TypeError("默认runnable必须是Runnable实例")
        self.branches = validated_branches
        self.default_branch = default_branch

    def invoke(self, input, config=None, **kwargs):
        # 遍历所有的分支，遇到条件命中则执行对应的runnable
        for condition, runnable in self.branches:
            if condition(input, **kwargs):
                return runnable.invoke(input, config=None, **kwargs)
        # 如果所有的分支条件都没有匹配上，则执行默认的default_branch
        if self.default_branch is not None:
            return self.default_branch.invoke(input, config=None, **kwargs)
        raise ValueError("未匹配到任何分支，也没有提供默认分支")

    def batch(self, inputs: list, config=None, **kwargs):
        return [self.invoke(input, config=None, **kwargs) for input in inputs]

    def stream(self, input, config=None, **kwargs):
        yield from super().stream(input, config=None, **kwargs)

    def __repr__(self):
        parts = [
            f"branch{idx} {condition.__name__} {repr(runnable)}"
            for idx, (condition, runnable) in enumerate(self.branches)
        ]
        if self.default_branch:
            parts.append("default")
        return f"RunnableBranch(branches=[{', '.join(parts)}])"
