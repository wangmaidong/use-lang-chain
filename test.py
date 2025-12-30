from smart_chain.embeddings import HuggingfaceEmbeddings,OpenAIEmbeddings

# huggingface = HuggingfaceEmbeddings()
# embedding_res = huggingface.embed_query('我在努力学习python')
# print(embedding_res)

openai = OpenAIEmbeddings()

print(openai.embed_query('我在努力学习python'))
