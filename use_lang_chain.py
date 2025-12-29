import os
from sys import prefix

# 官方的
# from langchain_deepseek import ChatDeepSeek
# from langchain.messages import HumanMessage,AIMessage,SystemMessage
# from langchain_core.prompts import (
#     PromptTemplate,
#     ChatPromptTemplate,
#     SystemMessagePromptTemplate,
#     HumanMessagePromptTemplate,
#     AIMessagePromptTemplate,
#     MessagesPlaceholder,
#     FewShotPromptTemplate,
#     load_prompt
# )
# from langchain_core.example_selectors import LengthBasedExampleSelector
# 自己的实现
from smart_chain.chat_models import ChatDeepSeek
from smart_chain.messages import  HumanMessage,AIMessage,SystemMessage
from smart_chain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    MessagesPlaceholder,
    FewShotPromptTemplate,
    load_prompt
)
from smart_chain.example_selectors import LengthBasedExampleSelector

# 初始对话模型客户端
api_key = os.getenv("OPENAI_API_KEY_DEEP")
llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key)

# 定义一个包含多个问答对的列表，每个元素是一个字典，表示一个示例
examples = [
    {"question": "1 plus 1等于多少？", "answer": "答案是2"},
    {"question": "2 plus 2等于多少？", "answer": "答案是4"},
    {"question": "3 plus 3等于多少？", "answer": "答案是6"},
    {"question": "4 plus 4等于多少？", "answer": "答案是8"},
    {"question": "5 plus 5等于多少？", "answer": "答案是10"},
]

# 定义示例展示的格式模板，通过 from_template 方法快速构建
example_prompt = PromptTemplate.from_template(
    "问题：{question}\n答案：{answer}"
)
# 创建 LengthBasedExampleSelector，用于按照总长度自动选择若干示例
# max_length 设置为较小值（15），方便演示输入长度不同对示例数目的影响
selector = LengthBasedExampleSelector(
    examples=examples,
    example_prompt=example_prompt,
    max_length=50
)

# 构造两个用于测试的不同长度的输入，用于观察选择器行为
test_inputs = [
    # 短输入：可以选取较多示例
    {"user_question": "6 plus 6等于多少？"},
    # 长输入：只能选取少量示例
    {"user_question": "这是一个非常长的问题，用来测试当输入很长时，示例选择器会选择更少的示例，因为剩余的长度更少了。"},
]

few_shot_prompt = FewShotPromptTemplate(
    example_prompt=example_prompt,
    prefix="你是一个数学助手。以下是一些示例：",
    suffix="问题：{user_question}\n答案：",
    example_selector=selector
)
# 使用 FewShotPromptTemplate 格式化文本，实际填充示例和用户输入
formatted = few_shot_prompt.format(user_question="6 plus 6等于多少？")

# 打印出格式化好的 prompt，方便检查示例引用和输入拼接效果
print(formatted)