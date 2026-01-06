import os
from pathlib import Path

# 官方实现
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    WebBaseLoader,
    CSVLoader,
)

# 自己实现
from smart_chain.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    WebBaseLoader,
    CSVLoader,
)

# file_path = "example_file/example.docx"
#
# print(f"文件路径{file_path}是否存在：{os.path.exists(file_path)}")
# loader = Docx2txtLoader(file_path)
#
# docs = loader.load()
#
# # 打印加载成功的文件路径
# print(f"成功加载文件: {file_path}")
#
# # 打印加载到的 Document 数量
# print(f"共 {len(docs)} 个 Document\n")
#
# for i, doc in enumerate(docs, 1):
#     # 打印 Document 的编号
#     print(f"--- Document {i} ---")
#     # 打印内容预览提示
#     print("内容预览:")
#     preview = doc.page_content[:300]
#     # 如果有内容则输出内容预览，否则输出“空内容”
#     print(preview if preview else "(空内容)")
#     # 打印元数据提示
#     print("\n元数据:")
#     # 输出 Document 的元数据信息
#     print(doc.metadata)


# url = "https://study.renshengtech.com/"
#
# docs = WebBaseLoader(web_paths=[url]).load()
# # 打印当前加载网页的 URL 以及所获得 Document 的总数
# print(f"加载 {url}，共 {len(docs)} 个 Document")
#
# # 遍历所有加载得到的 Document 对象
# for i, doc in enumerate(docs, 1):
#     # 打印每个文档内容的前 120 个字符，以及该文档的元数据信息
#     print(f"{doc.page_content[:120]} \n元数据:{doc.metadata}\n")

# file_path = "example_file/example.csv"
# docs = CSVLoader(file_path=file_path, encoding="utf-8").load()
# print(f"共 {len(docs)} 个 Document")
# for i, doc in enumerate(docs, 1):
#     print(f"--- 文档 {i} ---\n{doc.page_content}\n元数据:{doc.metadata}\n")
#
# docs_custom = CSVLoader(
#     file_path=file_path, encoding="utf-8", csv_args={"delimiter": ",", "quotechar": '"'}
# ).load()
# print(f"自定义参数: {len(docs_custom)} 个 Document")
# for i, doc in enumerate(docs_custom[:2], 1):
#     print(f"--- 文档 {i} ---\n{doc.page_content[:100]}...\n元数据:{doc.metadata}\n")
