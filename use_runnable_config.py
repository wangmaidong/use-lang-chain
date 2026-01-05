import uuid
from typing import Any
from uuid import UUID

# =============================
# 官方实现
# # 导入 RunnableLambda（用于将函数包装为可链式调用的 runnable）
# from langchain_core.runnables import RunnableLambda
# # 导入 RunnableConfig（runnable 的配置类型）
# from langchain_core.runnables.config import RunnableConfig
# # 导入回调处理器基类 BaseCallbackHandler
# from langchain_core.callbacks.stdout import BaseCallbackHandler
# ========================
# 自己的实现
from smart_chain.runnables import RunnableLambda


def to_upper(text, config={}):
    """将文本转换为大写"""
    print(f"[步骤1 - to_upper] 输入: {text}")
    print(f"  tags:{config.get('tags')}")
    print(f"  metadata:{config.get('metadata')}")
    print(f"  max_concurrency:{config.get('max_concurrency')}")
    print(f"  recursion_limit:{config.get('recursion_limit')}")
    print(f"  callbacks:{config.get('callbacks')}")
    print(f"  run_name:{config.get('run_name')}")
    print(f"  configurable:{config.get('configurable')}")
    result = text.upper()
    print(f"[步骤1 - to_upper] 输出: {result}")
    return result


# 定义第二个处理函数：为文本添加前缀
def add_prefix(text, config={}):
    """为文本添加前缀"""
    print("add_prefix=================")
    # 打印 config 的 tags 参数
    print(f"  tags: {config.get('tags')}")
    # 打印 config 的 metadata 参数
    print(f"  metadata: {config.get('metadata')}")
    # 打印 config 的 max_concurrency 参数
    print(f"  max_concurrency: {config.get('max_concurrency')}")
    # 打印 config 的 recursion_limit 参数
    print(f"  recursion_limit: {config.get('recursion_limit')}")
    # 打印 config 的 callbacks 参数
    print(f"  callbacks: {config.get('callbacks')}")
    print(f"  run_name:{config.get('run_name')}")
    # 打印 config 的 configurable 参数
    print(f"  configurable: {config.get('configurable')}")
    # 添加前缀字符串
    result = f"结果: {text}"
    # 输出添加前缀后的结果
    print(f"[步骤2 - add_prefix] 输出: {result}")
    # 返回结果
    return result


runnable1 = RunnableLambda(to_upper)
runnable2 = RunnableLambda(add_prefix)

# chain = runnable1 | runnable2

# run_name = "文本处理任务"
# config1 = {"run_name": run_name}
#
# result1 = chain.invoke("hello", config=config1)
#
# print(f"1.最终结果：{result1}")

# ===== 演示 2: run_id - 唯一标识符 =====
# 创建一个唯一的 uuid 作为 run_id
# run_id = uuid.uuid4()
# # 配置字典包含 run_id 和 run_name
# config2 = RunnableConfig(**{"run_id": run_id, "run_name": "带ID的任务"})
# # 处理字符串 "world" 并传递带 run_id 的 config
# result2 = chain.invoke("world", config=config2)
# # 打印结果及 run_id
# print(f"2. 最终结果: {result2}, run_id: {run_id}\n")

# 演示3： tags-标签（会传递给子调用）
# 配置字典添加tags片段

# config3 = {"tags": ["productions", "text-processing"], "run_name": "带标签的任务"}
#
# result3 = chain.invoke("test", config=config3)

# 演示4 元数据metadata

# config4 = {
#     "metadata": {"user_id": "12345", "session_id": "abc-def-ghi", "environment": "dev"}
# }
#
# result4 = chain.invoke("metadata", config=config4)
# print(f"4. 最终结果: {result4}, metadata: {config4['metadata']}\n")

#  案例5：max_concurrency 最大并发数

# config5 = {"max_concurrency": 2, "run_name": "批量处理任务"}
# inputs = ["a", "b", "c", "d"]
#
# results5 = chain.batch(inputs, config=RunnableConfig(**config5))
# # 打印输入列表
# print(f"输入: {inputs}")
# # 打印 batch 结果和最大并发设置
# print(f"5. 结果: {results5}, max_concurrency: {config5['max_concurrency']}\n")


# class MyCallbackHandler(BaseCallbackHandler):
#     def on_chain_start(
#         self, serialized: dict[str, Any], inputs: dict[str, Any], **kwargs
#     ) -> Any:
#         print(f"on_chain_start: {serialized}, {inputs}, {kwargs}")
#
#     def on_chain_end(
#         self,
#         outputs: dict[str, Any],
#         **kwargs: Any,
#     ) -> Any:
#         print(f"on_chain_end: {outputs}, {kwargs}")
#
#     def on_chain_error(
#         self,
#         error: BaseException,
#         **kwargs: Any,
#     ) -> Any:
#         print(f"on_chain_error: {error}, {kwargs}")
#
#     def on_llm_start(
#         self,
#         serialized: dict[str, Any],
#         prompts: list[str],
#         **kwargs: Any,
#     ) -> Any:
#         print(f"on_llm_start: {serialized}, {prompts}, {kwargs}")
#         # LLM 完成事件
#
#     def on_llm_end(self, response, **kwargs):
#         print(f"on_llm_end: {response}, {kwargs}")
#
#         # LLM 错误事件
#
#     def on_llm_error(self, error, **kwargs):
#         print(f"on_llm_error: {error}, {kwargs}")
#
#
# # 实例化回调处理器
# callback_handler = MyCallbackHandler()
# # 配置中添加自定义回调处理器
# config7 = {"callbacks": [callback_handler], "run_name": "带回调的任务"}
# # 传递带回调的配置测试
# result7 = chain.invoke("callback", config=config7)
# # 打印最终处理结果
# print(f"7. 最终结果: {result7}\n")

# ===== 演示 9: 组合使用多个配置项 =====
# 配置包含全部主要可配字段
# config9 = {
#     "run_id": uuid.uuid4(),
#     "run_name": "组合配置示例",
#     "tags": ["combined"],
#     "metadata": {"version": "1.0"},
#     "max_concurrency": 3,
#     "recursion_limit": 20,
#     "configurable": {"model": "gpt-4"},
# }
# # 综合测试各种配置传递
# result9 = chain.invoke("combined", config=config9)
# # 打印最终结果
# print(f"9. 最终结果: {result9}")
# # 用管道操作符 | 链接两个 runnable，形成处理链
chain = runnable1.with_config({"metadata": {"user_id": "001"}}) | runnable2.with_config(
    {"metadata": {"user_id": "002"}}
)
# 运行链式处理，并传递配置；输入字符串为 "hello"
result10 = chain.invoke("hello")
# 打印处理后的最终结果
print(f"10. 最终结果: {result10}\n")
