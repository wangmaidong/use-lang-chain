# from langchain_core.runnables import RunnableLambda
from smart_chain.runnables import RunnableLambda

call_count = 0


def unstable_func(x):
    global call_count
    call_count += 1
    if call_count < 3:
        raise ValueError(f"第{call_count}次调用失败")
    return f"成功：{x}"


runnable = RunnableLambda(unstable_func)

retry_runnable = runnable.with_retry(
    retry_if_exception_type=(ValueError,),
    stop_after_attempt=3,
    wait_exponential_jitter=False,
)
# 调用带重试功能的 runnable（会自动重试直到成功）
print("调用带重试的 runnable:")
result = retry_runnable.invoke("测试")
# 输出最终返回的结果
print(f"结果: {result}")
# 输出总调用次数（用于验证重试确实执行了多次）
print(f"总调用次数: {call_count}")
# 重置计数器为0，准备演示批量调用场景
call_count = 0
print("\n批量调用（每个输入独立重试）:")
# 使用带重试功能的 runnable 进行 batch 调用（每个输入分别重试）
results = retry_runnable.batch(["A", "B"])
# 输出批量结果
print(f"结果: {results}")
# 输出所有调用的总次数
print(f"总调用次数: {call_count}")
