import os
import numpy as np
from abc import ABC, abstractmethod
import faiss
from openai import embeddings


# 计算一个向量与多个向量的余弦相似度
def cosine_similarity(from_vec, to_vecs):
    # 将from_vec转换为numpy数组并且强制类型为float
    from_vec = np.array(from_vec, dtype=float)
    to_vecs = np.array(to_vecs, dtype=float)
    # 计算from_vec模长
    norm1 = np.linalg.norm(from_vec)
    similarities = []
    for to_vec in to_vecs:
        dot_product = np.sum(from_vec * to_vec)
        norm_vec = np.linalg.norm(to_vec)
        similarity = dot_product / (norm1 * norm_vec)
        similarities.append(similarity)
    return np.array(similarities)


def mmr_select(query_vector, doc_vectors, k=3, lambda_mult=0.5):
    # 计算每个文档向量与查询向量(Query)的余弦相似度。这代表了文档的“相关性”。
    quer_similarities = cosine_similarity(query_vector, doc_vectors)
    # 选择与查询向量相似度最高的文档：文档 1。
    # 找到与查询向量最相关的文档的下标，作为初始的已选文档 S：选择的结果集=selected=[0]
    selected = [int(np.argmax(quer_similarities))]
    while len(selected) < k:
        # 存放每个候选文档的MMR分数
        mmr_scores = []
        for i in range(len(doc_vectors)):
            if i not in selected:
                # 相关性，指的是i对应的候选文档和查询文档这间的相似性
                relevance = quer_similarities[i]
                # 获取当前已选文档的向量集合
                selected_vecs = doc_vectors[selected]  # - S：选择的结果集
                # 计算当前文档与所有的已选文档的余弦相似度
                sims = cosine_similarity(doc_vectors[i], selected_vecs)
                # 获取对已选中的文档最最大相似度 最不多样性的那个
                # 与已选节点有最大相似度的那个就是最不具有多样性的节点
                max_sim = np.max(sims)
                mmr_score = lambda_mult * relevance - (1 - lambda_mult) * max_sim
                mmr_scores.append((i, mmr_score))
        # 选出MMR分数最高的文档索引
        best_idx, best_score = max(mmr_scores, key=lambda x: x[1])
        # 将选中的文档添加到已选文档中
        selected.append(best_idx)
    return selected
# 定义Document 文档对象类
class Document:
    """
    文档类，存储内容，元数据和嵌入向量
    """
    def __init__(self,page_content:str, metadata=None,embedding_value=None):
        # 初始化文档内容
        self.page_content = page_content
        # 初始化元数据，默认空字典
        self.metadata = metadata or {}
        # 初始化嵌入向量
        self.embedding_value = embedding_value

class VectorStore(ABC):
    # 向量存储抽象基类
    # 抽象方法
    @abstractmethod
    def add_texts(
            self,
            texts,
            metadatas = None
    ):
        pass
    # 抽象方法，最大边际相关性检索
    @abstractmethod
    def max_marginal_relevance_search(self,query:str,k:int=4,fetch_k:int=20):
        pass
    # 抽象类方法，从文本批量构建向量存储
    @classmethod
    @abstractmethod
    def from_texts(cls,texts,embeddings,metadatas=None):
        # 批量通过文本构建向量存储的抽象方法，由子类实现
        pass

# 定义FAISS向量存储类，继承自VectorStore
class FAISS(VectorStore):
    # FAISS向量存储实现
    def __init__(self,embeddings):
        # 保存嵌入模型
        self.embeddings = embeddings
        # 初始化FAISS索引为空
        self.index = None
        # 初始化文档字典，键为文档id，值为Document对象
        self.documents_by_id = {}

    # 添加文本到向量存储
    def add_texts(
            self,
            texts,
            metadatas = None
    ):
        """
        添加文本到向量存储
        :param texts: 文本
        :param metadatas: 元数据
        :return: None
        """
        # 如果未传入元数据，则使用空字典列表
        if metadatas is None:
            metadatas = [{}] * len(texts)
        # 利用嵌入模型生成文本的嵌入向量
        embedding_values = self.embeddings.embed_documents(texts)
        # 转换成float32类型的NumPy数组
        embedding_values = np.array(embedding_values, dtype=np.float32)
        # 若还未建立FAISS索引，则新建索引
        if self.index is None:
            dimension = len(embedding_values[0])
            self.index = faiss.IndexFlatL2(dimension)
        # 添加嵌入向量到FAISS索引库中
        self.index.add(embedding_values)
        # 获取已知的文档数量，用于新文档的编号
        start_index = len(self.documents_by_id)
        for i,(text, metadata,embedding_value) in enumerate(
            zip(texts, metadatas, embedding_values)
        ):
            # 构建文档ID
            doc_id = str(start_index + i)
            # 构建文档对象
            doc = Document(
                page_content=text,
                metadata=metadata,
                embedding_value=embedding_value
            )
            self.documents_by_id[doc_id] = doc
    @classmethod
    def from_texts(cls,texts,embeddings,metadatas=None):
        instance = cls(embeddings=embeddings)
        instance.add_texts(texts,metadatas=metadatas)
        return instance




