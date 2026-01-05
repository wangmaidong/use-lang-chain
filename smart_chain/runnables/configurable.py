from ..config import ensure_config
from collections import namedtuple
from .runnable import Runnable

# id 字段的唯一标识 在config["configurable"]中使用
# name 字段的显示名称 可选
# description 字段的描述
# annotation 注释 可选
# is_shared 字段是否共享 可选
ConfigurableField = namedtuple(
    "ConfigurableField",
    ["id", "name", "description", "annotation", "is_shared"],
    defaults=(None, None, None, False),
)


class RunnableConfigurableFields(Runnable):
    def __init__(self, default, fields):
        self.default = default
        self.fields = fields

    def _prepare(self, config=None):
        # 规范化config字典
        config = ensure_config(config)
        # 从config中取出configurable配置
        configurable = config.get("configurable", {})
        # 收集需要修改的字段的值
        updates = {}
        # 收集需要修改的字段和值
        for field_name, field_spec in self.fields.items():
            if isinstance(field_spec, ConfigurableField):
                config_value = configurable.get(field_spec.id)
                if config_value is not None:
                    updates[field_name] = config_value
        # 如果有更新内容，需要创建新的实例
        if updates:
            # 获取默认实例的类型ChatOpenAI
            default_class = type(self.default)
            # 获取类型名
            class_name = default_class.__name__
            if class_name in ("ChatOpenAI", "ChatDeepSeek", "ChatTongyi"):
                init_params = {"model": self.default.model}
                if hasattr(self.default, "model_kwargs"):
                    init_params.update(self.default.model_kwargs.copy())
                # 增加本次需要更新的参数
                init_params.update(updates)
                if hasattr(self.default, "api_key"):
                    init_params["api_key"] = self.default.api_key
                if hasattr(self.default, "base_url"):
                    init_params["base_url"] = self.default.base_url
                # 使用合并后的参数创建新的实例
                new_instance = default_class(**init_params)
                return new_instance, config

    def invoke(self, input, config=None, **kwargs):
        if config is None:
            return self.default.invoke(input, **kwargs)
        # 获取动态配置后的runnable实例和合并后配置
        runnable, merged_config = self._prepare(config)
        if isinstance(runnable, Runnable):
            return runnable.invoke(input, config=merged_config, **kwargs)
        else:
            # 非runnable实例的话直接调用 初始参数已经生效
            return runnable.invoke(input, **kwargs)


class RunnableConfigurableAlternatives(Runnable):
    def __init__(self, selector_field, default_key, alternatives):
        self.selector_field = selector_field
        self.default_key = default_key
        self.alternatives = alternatives

    def _select(self, config=None):
        config = ensure_config(config)
        configurable = config.get("configurable", {})
        key = configurable.get(self.selector_field.id, self.default_key)
        if key not in self.alternatives:
            raise ValueError(f"未找到可用的分支")
        return self.alternatives[key], config

    def invoke(self, input, config=None, **kwargs):
        selected, merged_config = self._select(config)
        if isinstance(selected, Runnable):
            return selected.invoke(input, config=merged_config, **kwargs)
        else:
            # 非runnable实例的话直接调用 初始参数已经生效
            return selected.invoke(input, **kwargs)
