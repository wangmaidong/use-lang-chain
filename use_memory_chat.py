import os

# from langchain_deepseek import ChatDeepSeek
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.chat_history import InMemoryChatMessageHistory
# from langchain_core.messages import HumanMessage
# from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda

# 自己实现的
from smart_chain.chat_models import ChatDeepSeek
from smart_chain.chat_history import InMemoryChatMessageHistory
from smart_chain.prompts import ChatPromptTemplate, MessagesPlaceholder
from smart_chain.messages import HumanMessage
from smart_chain.runnables import RunnableWithMessageHistory, RunnableLambda

api_key = os.getenv("OPENAI_API_KEY_DEEP")
llm = ChatDeepSeek(api_key=api_key, model="deepseek-chat", temperature=0.7)
"""
# 创建一个内存版的对话历史对象
history = InMemoryChatMessageHistory()
template = ChatPromptTemplate(
    [
        # 系统指令，设定 AI 的身份和风格
        ("system", "你是一个友好的AI助手"),
        # 历史消息占位
        MessagesPlaceholder("history"),
        # 用户输入，将在调用函数是被格式化
        ("human", "{question}"),
    ]
)


def chat(question: str):
    history_message = history.messages
    prompt_messages = template.format_messages(
        history=history_message, question=question
    )
    response = llm.invoke(prompt_messages)
    history.add_user_message(question)
    history.add_ai_message(response.content)

    return response.content


# ============以下用于演示多轮对话功能=============

# 第一轮对话
print("【第一轮】")
print("用户：我叫小明")
print(f"AI：{chat('我叫小明')}\n")

# 第二轮对话
print("【第二轮】")
print("用户：我的名字是什么？")
print(f"AI：{chat('我的名字是什么？')}\n")

# 第三轮对话
print("【第三轮】")
print("用户：请介绍一下我")
print(f"AI：{chat('请介绍一下我')}\n")

# ============显示完整历史记录===============

# 打印分隔线
print("=" * 50)
# 打印标题
print("历史记录：")
# 遍历历史中的所有消息，逐条输出
for i, msg in enumerate(history.messages, 1):
    # 判断消息类型，用户消息显示“用户”，否则为 AI
    role = "用户" if isinstance(msg, HumanMessage) else "AI"
    # 打印第 i 条历史消息
    print(f"{i}. [{role}] {msg.content}")
"""

store = {}


def get_by_session_id(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个友好的 AI 助手。"),
        MessagesPlaceholder(variable_name="history"),  # 消息占位符，用于插入历史消息
        ("human", "{question}"),
    ]
)


def chain_func(input_dict):
    """链式函数：先格式化 prompt，再调用 llm"""
    prompt_value = prompt.invoke(input_dict)
    return llm.invoke(prompt_value.messages)


chain = RunnableLambda(chain_func)

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_by_session_id,
    input_messages_key="question",
    history_messages_key="history",
)
# 演示多轮对话
print("【第一轮】")
response1 = chain_with_history.invoke(
    {"question": "我叫小明"}, config={"configurable": {"session_id": "session-1"}}
)
print(f"用户：我叫小明")
print(f"AI：{response1.content}\n")
print("【第二轮】")
response2 = chain_with_history.invoke(
    {"question": "我的名字是什么？"},
    config={"configurable": {"session_id": "session-1"}},
)
print(f"用户：我的名字是什么？")
print(f"AI：{response2.content}\n")

# 显示历史记录
print("=" * 50)
print("历史记录：")
for i, msg in enumerate(store["session-1"].messages, 1):
    role = "用户" if msg.type == "human" else "AI"
    print(f"{i}. [{role}] {msg.content}")
