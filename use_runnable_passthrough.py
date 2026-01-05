# 官方实现
# from langchain_core.runnables import RunnableLambda, RunnablePassthrough
# 自己实现
from smart_chain.runnables import RunnableLambda, RunnablePassthrough


def process_text(text):
    return text.upper()


process_runnable = RunnableLambda(process_text)

pass_through = RunnablePassthrough()
result = pass_through.invoke("测试")
print(f"输入: '测试'")
print(f"输出: {result}")  # 输出：测试

batch_inputs = ["a", "b", "c"]
batch_results = pass_through.batch(batch_inputs)
print(f"批量输入: {batch_inputs}")
print(f"批量输出: {batch_results}")

print("流式输出...")
for chunk in pass_through.stream("stream-test"):
    print(f"  收到: {chunk}")

chain = RunnablePassthrough() | process_runnable
result = chain.invoke("hello")
print(f"输入: 'hello'")
print(f"输出: {result}")
