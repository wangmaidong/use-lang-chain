# 官方的
from langchain_text_splitters import CharacterTextSplitter

# 自己实现的
# from smart_chain.text_splitters import CharacterTextSplitter

text = (
    "LangChain 文本分割示例。"
    "CharacterTextSplitter 会按固定字符数切分，并可重叠。"
    "适合在构建向量索引前先做简单分片。"
)

splitter = CharacterTextSplitter(
    separator="。", chunk_size=40, chunk_overlap=5, keep_separator=True
)
chunks = splitter.split_text(text)
# 打印原始文本长度
print(f"原文本长度: {len(text)} 字符")
# 打印切分后获得了多少块
print(f"切分得到 {len(chunks)} 块：")
# 逐块打印每一个分片和该分片的字符数
for i, c in enumerate(chunks, 1):
    print(f"片段{i} ({len(c)} 字符): {c}")
