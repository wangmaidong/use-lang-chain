# 官方的
from langchain_core.runnables import RunnableLambda, RunnableParallel


# 定义多个处理函数
def add_one(x):
    """加1"""
    return x + 1


def multiply_two(x):
    """乘以2"""
    return x * 2


def square(x):
    """平方"""
    return x**2


add_one_runnable = RunnableLambda(add_one)
multiply_two_runnable = RunnableLambda(multiply_two)
square_runnable = RunnableLambda(square)

parallel = RunnableParallel(
    added=add_one_runnable, multiplied=multiply_two_runnable, squared=square_runnable
)

input_val = 5
result = parallel.invoke(input_val)

# 打印结果
print(f"输入: {input_val}")
print(f"输出: {result}")

# 批量调用：对多个输入同时并行计算，返回结果列表
batch_inputs = [1, 2, 3]
batch_results = parallel.batch(batch_inputs)
print(f"批量输入: {batch_inputs}")
print(f"批量输出: {batch_results}")

# 流式调用：对单个输入流式获取并行结果
print("流式输出:")
for chunk in parallel.stream(4):
    print(f"  收到: {chunk}")
