import os
# 官方的
from langchain_deepseek import ChatDeepSeek
from langchain.messages import HumanMessage,AIMessage,SystemMessage
from langchain_core.prompts import (
    PromptTemplate,ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    MessagesPlaceholder,
    FewShotPromptTemplate
)

# 自己的实现
# from smart_chain.chat_models import ChatDeepSeek
# from smart_chain.messages import  HumanMessage,AIMessage,SystemMessage
# from smart_chain.prompts import (
#     PromptTemplate,
#     ChatPromptTemplate,
#     SystemMessagePromptTemplate,
#     HumanMessagePromptTemplate,
#     AIMessagePromptTemplate,
#     MessagesPlaceholder
# )

# 初始对话模型客户端
api_key = os.getenv("OPENAI_API_KEY_DEEP")
llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key)

examples = [
    {"question": "1 plus 1 等于多少？", "answer": "答案是2"},
    {"question": "2 plus 2 等于多少？", "answer": "答案是4"}
]
example_prompt = PromptTemplate.from_template(
    "示例问题：{question}\n示例回答：{answer}"
)

# 构建 few-shot 提示词模板，包含前缀、示例、后缀和输入变量
few_shot_prompt = FewShotPromptTemplate(
    examples = examples,
    example_prompt= example_prompt,
    prefix="你是一个擅长算术的AI助手，以下是一些示例：",
    suffix="请回答用户问题：{user_question}\nAI",
    input_variables=["user_question"]
)

formatted_prompt = few_shot_prompt.format(user_question="3 plus 5等于多少？")
print(f"few-shot 提示词：\n {formatted_prompt}")

response = llm.invoke(formatted_prompt)
print("\n模型回答：")
print(response.content)