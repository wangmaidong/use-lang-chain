# 官方实现
# from langchain_core.runnables import RunnableLambda, RunnableSequence


# 自己的实现
from smart_chain.runnables import RunnableLambda


# 定义多个处理函数
def add_one(x):
    return x + 1


def multiple_two(x):
    return x * 2


def add_prefix(x):
    return f"结果：{x}"


add_one_runnable = RunnableLambda(add_one)
multiply_two_runnable = RunnableLambda(multiple_two)
add_prefix_runnable = RunnableLambda(add_prefix)

chain = add_one_runnable | multiply_two_runnable | add_prefix_runnable

result = chain.invoke(5)

print(f"输入：5")
print(f"输出：{result}")

inputs = [1, 2, 3, 4]
batch_results = chain.batch((inputs))
print(f"批量输入：{inputs}")
print(f"批量输出：{batch_results}")

print("流式输出")
for chunk in chain.stream(7):
    print(f"收到：{chunk}")
