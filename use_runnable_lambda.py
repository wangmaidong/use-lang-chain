# 官方实现
# from langchain_core.runnables import RunnableLambda
# 自己的实现
from smart_chain.runnables import RunnableLambda

add_one_runnable = RunnableLambda(lambda x: x + 1)
print(f"add_one_runnable:{add_one_runnable}")
result = add_one_runnable.invoke(3)
print(result)

results = add_one_runnable.batch([1, 2, 3, 4, 5])
print(results)

mul_runnable = RunnableLambda(lambda x: x * 2)
square_runnable = RunnableLambda(lambda x: x**2)

input_value = 3

step1 = add_one_runnable.invoke(input_value)
step2 = mul_runnable.invoke(step1)
step3 = square_runnable.invoke(step2)

print(f"step3:{step3}")


def process_text(text: str):
    words = text.split()
    print(words)
    for word in words:
        yield word


stream_runnable = RunnableLambda(process_text)

input_text = "你好 世界 python"

for chunk in stream_runnable.stream(input_text):
    print(chunk)
