import os
import json

# 官方的
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import PromptTemplate

# 自己实现的
# from smart_chain.output_parsers import StrOutputParser, JsonOutputParser
# from smart_chain.chat_models import ChatDeepSeek
# from smart_chain.prompts import PromptTemplate

api_key = os.getenv("OPENAI_API_KEY_DEEP")
llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key)
parser = JsonOutputParser()

# 定义不同测试用的 JSON 格式数据
test_cases = [
    # 第一种：纯 JSON 格式的字符串
    '{"name": "张三", "age": 25, "city": "北京"}',
    # 第二种：包裹在 Markdown 代码块里的 JSON
    '``json\n noise {"product": "手机", "price": 3999, "in_stock": true}\n``',
    # 第三种：JSON 数组
    '["苹果", "香蕉", "橙子"]',
]

# 遍历每个测试用例，解析并输出解析结果
for i, test_input in enumerate(test_cases, 1):
    # 使用解析器解析输入字符串
    result = parser.parse(test_input, True)
    # 输出解析成功后的结果，以及数据类型
    print(
        f"解析成功：{json.dumps(result, ensure_ascii=False, indent=2)} , {type(result)}"
    )
# 创建提示模板，要求LLM按照JSON格式输出结构化数据
# prompt = PromptTemplate.from_template(
#     """你是一个数据提取助手。请从以下文本中提取信息，并以 JSON 格式输出。
#     文本：{text}
#
#     {format_instructions}
#
#     请提取以下信息：
#     - name: 姓名
#     - age: 年龄
#     - location: 地点
#     - interests: 兴趣列表（数组）
#
#     JSON 输出：
#     """
# )
# # 获取JSON格式输出的格式说明
# format_instructions = parser.get_format_instructions()
#
# ## 输出提示信息，表示即将提取结构化数据
# print(f"\n使用 JsonOutputParser 提取结构化数据：")
#
# text_texts = [
#     "我叫李四，今年30岁，住在上海。我喜欢编程、阅读和旅行。",
#     "王五，28岁，来自深圳。爱好包括音乐、电影和摄影。",
# ]
#
# for i, text in enumerate(text_texts):
#     formatted_prompt = prompt.format(text=text, format_instructions=format_instructions)
#     # 调用大模型，根据提示生成回复
#     response = llm.invoke(formatted_prompt)
#     print(response.content)
#     # 解析模型回复中的JSON数据
#     result = parser.parse(response.content)
#     print(json.dumps(result, ensure_ascii=False, indent=2))
#     print(f"数据类型：{type(result).__name__}")
#     # 如果解析结果是字典（结构化数据），则访问具体字段并逐项打印
#     if isinstance(result, dict):
#         print(f"\n访问数据：")
#         print(f"  姓名：{result.get('name', 'N/A')}")
#         print(f"  年龄：{result.get('age', 'N/A')}")
#         print(f"  地点：{result.get('location', 'N/A')}")
#         print(f"  兴趣：{result.get('interests', [])}")
