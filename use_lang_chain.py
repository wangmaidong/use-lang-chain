import os
官方的
from langchain_deepseek import ChatDeepSeek
from langchain.messages import HumanMessage,AIMessage,SystemMessage
from langchain_core.prompts import PromptTemplate
# 自己的实现
# from smart_chain.chat_models import ChatDeepSeek
# from smart_chain.messages import  HumanMessage,AIMessage,SystemMessage
# from smart_chain.prompts import PromptTemplate
api_key = os.getenv("OPENAI_API_KEY_DEEP")
llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key)

# messages = [
#     SystemMessage(content="你是一个AI助手，请回答用户的问题"),
#     "你好，我叫张三，你是谁？",
#     AIMessage(content="我是deepseek,一个AI助手"),
#     {"role": "user", "content": "你知道我叫什么吗？"},
#     ("assistant","你的名字是张三")
# ]
prompt_template = PromptTemplate("你好，我叫{name},你是谁")
print(prompt_template)
filled_prompt = prompt_template.format(name="张三")
print(filled_prompt)
# result = llm.invoke(messages)
# print(result.content, type(result))