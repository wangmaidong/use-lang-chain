import os
# 官方的
# from langchain_deepseek import ChatDeepSeek
# from langchain.messages import HumanMessage,AIMessage,SystemMessage
# from langchain_core.prompts import (
#     PromptTemplate,ChatPromptTemplate,
#     SystemMessagePromptTemplate,
#     HumanMessagePromptTemplate,
#     AIMessagePromptTemplate,
#     MessagesPlaceholder
# )

# 自己的实现
from smart_chain.chat_models import ChatDeepSeek
from smart_chain.messages import  HumanMessage,AIMessage,SystemMessage
from smart_chain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    MessagesPlaceholder
)

# 初始对话模型客户端
api_key = os.getenv("OPENAI_API_KEY_DEEP")
llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key)

# 构建历史消息列表，模拟对话历史
history = [
    HumanMessage(content="你好"),
    AIMessage(content="你好，很高兴见到你")
]
template = ChatPromptTemplate([
    ('system', "你是一个乐于助人的AI助手"),
    MessagesPlaceholder("history"),
    ('human', "{question}")
])

prompt_messages = template.format_messages(
    history = history,
    question = "请介绍一下你自己"
)
print(prompt_messages)
response = llm.invoke(prompt_messages)

print(response.content)
