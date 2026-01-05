import os

# 官方的
# from langchain_deepseek import ChatDeepSeek
# from langchain_core.runnables import ConfigurableField
# 自己实现的
from smart_chain.chat_models import ChatDeepSeek
from smart_chain.runnables import ConfigurableField

api_key = os.getenv("OPENAI_API_KEY_DEEP")

llm = ChatDeepSeek(
    api_key=api_key, model="deepseek-chat", temperature=0.5
).configurable_fields(
    temperature=ConfigurableField(
        id="temperature",
        name="温度值",
        description="LLM 的采样温度参数，控制输出的多样性",
    )
)
# 打印说明信息，表示当前 temperature 配置为 1.0
print("\n默认值temperature=0.5：")
result1 = llm.invoke("你好，你怎么样？")
print(f"result1:{result1}")
# 打印说明信息，表示当前 temperature 配置为 1.0
print("\ntemperature=1.0：")
# 使用 llm.invoke 方法发送对话内容，并通过 config 参数传递 temperature=1.0 动态配置
result2 = llm.invoke("你好，你怎么样？", config={"configurable": {"temperature": 1.0}})
print(f"result2:{result2}")
