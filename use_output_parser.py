import os

# 官方的
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek

api_key = os.getenv("OPENAI_API_KEY_DEEP")
llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key)
# 创建字符串输出解析器对象
parser = StrOutputParser()

# 调用模型生成一句话介绍python编程语言
response = llm.invoke("请用一句话介绍 Python 编程语言")
# 用字符串输出解析器对模型输出内容进行解析得到纯字符串
parser_output = parser.parse(response.content)
# 打印解析后的内容
print(f"返回的响应体：{response}")
print(f"解析后内容：{parser_output}")
print(f"解析后的类型：{type(parser_output)}")
