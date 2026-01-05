# 官方的
# from langchain_core.runnables import RunnableLambda, RunnableBranch
# 自定义的
from smart_chain.runnables import RunnableLambda, RunnableBranch


# 定义处理正数的函数，输入为正数时返回描述字符串
def handle_positive(x):  # 正数
    return f"{x} 是正数"


# 定义处理负数的函数，输入为负数时返回描述字符串
def handle_negative(x):  # 负数
    return f"{x} 是负数"


# 定义处理零的函数，输入为零时返回描述字符串
def handle_zero(x):  # 零
    return "0 是零"


# 将处理正数的函数封装为 RunnableLambda
pos = RunnableLambda(handle_positive)

# 将处理负数的函数封装为 RunnableLambda
neg = RunnableLambda(handle_negative)

# 将处理零的函数封装为 RunnableLambda
zero = RunnableLambda(handle_zero)

branch = RunnableBranch((lambda v: v > 0, pos), (lambda v: v < 0, neg), zero)
for value in [3, -2, 0]:
    print(f"输入{value} -> {branch.invoke(value)}")

values = [5, 0, -1]
print("batch:", branch.batch(values))

# 演示流式 stream 用法（本例每次只产出一个结果）
print("stream 结果:")
for chunk in branch.stream(-7):
    # 逐个输出流式返回的结果
    print("  ", chunk)
