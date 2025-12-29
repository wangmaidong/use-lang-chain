import os
from openai import OpenAI
from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer
from langchain_huggingface import (
    HuggingFaceEmbeddings as LangchainHuggingfaceEmbeddings,
)
import requests


# 定义抽象基类Embedding
class Embedding(ABC):
    # 定义抽象方法，嵌入单个查询文本
    @abstractmethod
    def embed_query(self, text):
        pass

    # 定义抽象方法，嵌入多个文档文本
    @abstractmethod
    def embed_documents(self, texts):
        pass


# OpenAI 嵌入模型封装


class OpenAIEmbeddings(Embedding):
    # 初始化方法，支持自定义模型和参数
    def __init__(self, model="text-embedding-3-small", **kwargs):
        # 模型名称
        self.model = model
        # 获取API密钥，优先从参数中获取，否则从环境变量中获取
        self.api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY_DEEP")
        # 获取大模型地址
        self.base_url = kwargs.get("base_url", "https://api.deepseek.com/v1")
        # 如果没有提供api_key则报错
        if not self.api_key:
            raise ValueError(f"需要提供 api_key")
        # 过滤掉api_key后的其他embedding参数
        self.embedding_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["api_key", "base_url"]
        }
        # 初始化客户端
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    # 单条文本嵌入
    def embed_query(self, text):
        # 调用OpenAI嵌入接口，获取结果
        response = self.client.embeddings.create(
            model=self.model, input=text, **self.embedding_kwargs
        )
        # 返回第一个embedding向量
        return response.data[0].embedding

    # 多条文档批量嵌入
    def embed_documents(self, texts):
        # 调用OpenAI嵌入接口，支持批量输入
        response = self.client.embeddings.create(
            model=self.model, input=texts, **self.embedding_kwargs
        )
        return [item.embedding for item in response.data]


# HuggingFace嵌入模型封装
class HuggingfaceEmbeddings(Embedding):
    # 初始化方法，支持自定义模型和其他参数
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2", **kwargs):
        """
        初始化 HuggingFace 嵌入模型
        Args:
            model_name:HuggingFace 模型名称，默认为 "sentence-transformers/all-MiniLM-L6-v2"
            **kwargs: 传递给 langchain_huggingface.HuggingFaceEmbeddings 的其他参数
        """
        self.model_name = model_name
        self.embeddings = LangchainHuggingfaceEmbeddings(
            model_name=model_name, **kwargs
        )

    def embed_query(self, text):
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts):
        return self.embeddings.embed_documents(texts)


class SentenceTransFormerEmbeddings(Embedding):
    def __init__(self, model="all-MiniLM-L6-v2", **kwargs):
        self.model_name = model or "all-MiniLM-L6-v2"
        self.model = SentenceTransformer(self.model_name, **kwargs)
        # 可选：是否归一化嵌入向量
        self.normalize_embeddings = kwargs.get("normalize_embeddings", False)

    def embed_query(self, text):
        embedding = self.model.encode(
            text, normalize_embeddings=self.normalize_embeddings
        )
        return embedding.tolist() if hasattr(embedding, "tolist") else embedding

    def embed_documents(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self.model.encode(
            texts, normalize_embeddings=self.normalize_embeddings
        )
        if hasattr(embeddings, "tolist"):
            return embeddings.tolist()
        return embeddings
