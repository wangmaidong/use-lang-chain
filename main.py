from openai import OpenAI
from pprint import pprint
import os

client = OpenAI(
    api_key= os.getenv("OPENAI_API_KEY_DEEP"),
    base_url= "https://api.deepseek.com"
)
response = client.chat.completions.create(
    model="deepseek-chat",
    messages= [
        {
            "role":"user",
            "content":"1+1=?"
        }
    ],
    max_tokens=500,
    temperature=0.7
)
# 提取回复内容
# response.choices[0] 表示第一个选择（通常只有一个）
# .message.content 是消息内容
reply = response.choices[0].message.content

# 打印回复
print("ChatGPT 的回复：")
print(reply)
