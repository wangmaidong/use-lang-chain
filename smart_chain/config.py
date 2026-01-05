"""配置相关的类型定义和工具函数"""

import inspect
from typing import Union

# 导入 uuid 库，主要用于 run_id 的唯一标识
import uuid

# Callbacks = Any  # 可以是 BaseCallbackHandler 或 Handler 列表

# RunnableConfig 是普通 dict，可包含如下可选字段:
#   - tags: list[str]                # 标签列表
#   - metadata: dict[str, Any]       # 元数据字典
#   - callbacks: Callbacks           # 回调对象或回调对象列表
#   - run_name: str                  # 运行名称
#   - max_concurrency: int | None    # 批量时最大并发数
#   - recursion_limit: int           # 最大递归层数限制
#   - configurable: dict[str, Any]   # 可配置参数字典
#   - run_id: uuid.UUID | None       # 唯一运行 ID
# 默认的递归层数限制
DEFAULT_RECURSION_LIMIT = 25


# 工具函数：确保传入的 config 参数不是 None，并返回字典副本
def ensure_config(config: Union[dict] = None):
    """
    确保配置字典存在，如果为 None 则返回空字典。
    :param config: 可选的配置字典
    :return: 配置字典（如果为 None 则返回空字典）
    """
    if config is None:
        return {}
    # 如果已经是 dict，则返回其副本，否则将其转为字典
    return config.copy() if isinstance(config, dict) else dict(config)


def _accept_config(func):
    try:
        sig = inspect.signature(func)
        return "config" in sig.parameters
    except (ValueError, TypeError):
        return False


def _merge_configs(*configs):
    """
    合并多个配置字典
    :param configs:
    :return:
    """
    result = {}
    for config in configs:
        if config:
            for key, value in config.items():
                if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    result[key] = {**result[key], **value}
                else:
                    result[key] = value
    return result
