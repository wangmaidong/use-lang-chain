import os
from sys import prefix

from torchgen.operator_versions.gen_mobile_upgraders import construct_operators

# 官方的
from langchain_deepseek import ChatDeepSeek
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    MessagesPlaceholder,
    FewShotPromptTemplate,
    load_prompt,
)
from langchain_core.example_selectors import (
    LengthBasedExampleSelector,
    MaxMarginalRelevanceExampleSelector,
    SemanticSimilarityExampleSelector,
)

# 自己的实现
# from smart_chain.chat_models import ChatDeepSeek
# from smart_chain.messages import HumanMessage, AIMessage, SystemMessage
# from smart_chain.prompts import (
#     PromptTemplate,
#     ChatPromptTemplate,
#     SystemMessagePromptTemplate,
#     HumanMessagePromptTemplate,
#     AIMessagePromptTemplate,
#     MessagesPlaceholder,
#     FewShotPromptTemplate,
#     load_prompt,
# )
# from smart_chain.example_selectors import (
#     LengthBasedExampleSelector,
#     MaxMarginalRelevanceExampleSelector,
# )
# from smart_chain.embeddings import HuggingFaceEmbeddings
# from smart_chain.vectorstores import FAISS

# 初始对话模型客户端
api_key = os.getenv("OPENAI_API_KEY_DEEP")
llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key)

# 定义10个围绕“怎样挑西瓜比较甜”等类似主题的中英文QA示例组成的列表
examples = [
    {
        "question": "如何挑选新鲜的水果？",
        "answer": "观察外皮是否光滑、色泽是否自然，还可以闻闻香味，挑选表皮无破损的新鲜水果。",
    },
    {
        "question": "西瓜挑选时要注意什么？",
        "answer": "应选择西瓜纹路清晰、瓜皮发亮，敲打有清脆声音，瓜蒂卷曲、瓜底发黄的通常比较甜。",
    },
    {
        "question": "西瓜怎么挑才甜？",
        "answer": "用手轻轻拍打西瓜，发出清脆、沉闷有弹性之音的西瓜比较甜",
    },
    {
        "question": "买水果有哪些小窍门？",
        "answer": "挑选时需观察颜色、闻气味、用手掂分量。对于瓜类可以敲一敲听声音来判断成熟度。",
    },
    {
        "question": "怎样判断水果是否熟透？",
        "answer": "可以轻捏表皮，成熟的水果通常较软，闻一闻是否有浓郁的水果香味，也可以看颜色是否均匀。",
    },
    {
        "question": "西瓜的黄底有什么意义？",
        "answer": "西瓜底部颜色越黄，通常说明在田里成熟时间长，甜度更高。",
    },
    {
        "question": "挑西瓜时候能用手敲吗？",
        "answer": "可以，声音清脆表示瓜比较熟，声音沉闷的可能不太熟。",
    },
    {
        "question": "吃西瓜对健康有哪些好处？",
        "answer": "西瓜含有丰富水分和多种维生素，夏季吃可补水解暑，有利于身体健康。",
    },
    {
        "question": "水果要怎么保存更久？",
        "answer": "可存放于阴凉处，易腐水果置于冰箱冷藏，有些水果如西瓜最好切块密封保存。",
    },
    {
        "question": "哪些水果适合夏天吃？",
        "answer": "西瓜、哈密瓜、桃子、李子等含水分高的水果特别适合夏天食用。",
    },
]
example_prompt = PromptTemplate.from_template("问题：{question}\n答案：{answer}")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
selector = SemanticSimilarityExampleSelector.from_examples(
    examples=examples, embeddings=embeddings, vectorstore_cls=FAISS, k=3
)
few_shot_prompt = FewShotPromptTemplate(
    example_prompt=example_prompt,
    prefix="你是一个乐于助人的生活小助手。以下是一些建议示例：",
    suffix="问题：{question}\n答案：",
    example_selector=selector,
)
user_question = "怎么样挑选西瓜"
formatted = few_shot_prompt.format(question=user_question)
print(formatted)
