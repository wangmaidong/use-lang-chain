import os
# 官方的
# from langchain_deepseek import ChatDeepSeek
# from langchain.messages import HumanMessage,AIMessage,SystemMessage
# from langchain_core.prompts import PromptTemplate,ChatPromptTemplate,SystemMessagePromptTemplate,HumanMessagePromptTemplate,AIMessagePromptTemplate
# 自己的实现
from smart_chain.chat_models import ChatDeepSeek
from smart_chain.messages import  HumanMessage,AIMessage,SystemMessage
from smart_chain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate,HumanMessagePromptTemplate,AIMessagePromptTemplate

# 初始对话模型客户端
api_key = os.getenv("OPENAI_API_KEY_DEEP")
llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key)

# template = ChatPromptTemplate(
#     [
#         ("system", "你是一个乐于助人的AI机器人，你的名字叫{name}"),
#         ("human", "你好，你最近怎么怎么样？"),
#         ("ai", "我很好，谢谢你的关心"),
#         ("human", "{user_input}")
#     ]
# )
#
# prompt_value = template.invoke({
#     "name":"小助",
#     "user_input":"你叫什么名字？"
# })
# print(prompt_value, type(prompt_value))
# print(prompt_value.to_string())
# print(prompt_value.to_messages())

template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("你是一个乐于助人的AI机器人，你的名字叫{name}"),
    HumanMessagePromptTemplate.from_template("你好，你最近怎么样？"),
    AIMessagePromptTemplate.from_template("我很好，谢谢你的关心！"),
    HumanMessagePromptTemplate.from_template("{user_input}")
])

prompt_messages = template.format_messages(name="小助",user_input="你叫什么名字？")
print(prompt_messages)
