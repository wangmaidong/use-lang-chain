# 导入正则表达式模块
import re
from typing import List, Union

# 导入抽象基类相关
from abc import ABC, abstractmethod


# 定义 TextSplitter 抽象基类
class TextSplitter(ABC):
    """
    文本分割器的抽象基类。
    子类需要实现 split_text() 方法来定义具体的分割逻辑。
    """

    def __init__(
        self,
        chunk_size=4000,  # 每个块的最大字符数，默认为4000
        chunk_overlap=200,  # 块之间的重叠字符数，默认为200
        length_function=None,  # 计算文本长度的函数
        keep_separator=False,  # 是否保留分隔符，默认为False
        strip_whitespace=True,  # 是否去除首尾空白，默认为True
    ):
        """
        初始化文本分割器。
        Args:
            chunk_size: 每个块的最大字符数
            chunk_overlap: 块之间的重叠字符数
            length_function: 计算文本长度的函数，默认为 len
            keep_separator: 是否保留分隔符
            strip_whitespace: 是否去除首尾空白
        """
        # 检查 chunk_size 参数是否合法
        if chunk_size <= 0:
            raise ValueError(f"chunk_size 必须 > 0，当前值: {chunk_size}")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap 必须 >= 0，当前值: {chunk_overlap}")
        if chunk_overlap > chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) 不能大于 chunk_size ({chunk_size})"
            )
        # 保存参数到成员变量
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._length_function = length_function if length_function is not None else len
        self._keep_separator = keep_separator
        self._strip_whitespace = strip_whitespace

    # 抽象方法，子类必须实现此方法
    @abstractmethod
    def split_text(self, text):
        """
        将文本分割成多个块。
        Args:
            text: 要分割的文本

        Returns:
            文本块列表
        """
        # 强制子类必须实现 split_text 方法
        raise NotImplementedError("子类必须实现 split_text() 方法")

    # 合并分割后的文本块，控制结果块大小和重叠
    def _merge_splits(self, splits, separator):
        """
        将分割后的文本块合并，确保每个块不超过 chunk_size。
        Args:
            splits: 分割后的文本块列表
            separator: 用于连接文本块的分隔符

        Returns:

        """
        # 计算分隔符的长度
        separator_len = self._length_function(separator)
        # 定义用于存储最终文本块的列表
        docs = []
        # 正在构建的当前文档块
        current_doc = []
        # 当前文档块字符总长度
        total = 0
        # 遍历每个文本分块
        for d in splits:
            # 获取当前分块的长度
            len_ = self._length_function(d)
            # 计算如果加上当前块后，文档块的总长度
            total_with_sep = (
                total + len_ + (separator_len if len(current_doc) > 0 else 0)
            )
            # 如果添加当前块会超过设定的 chunk_size
            if total_with_sep > self._chunk_size:
                # 如果当前拼接块不为空，先拼接并记录
                if len(current_doc) > 0:
                    # 拼接当前文档块
                    doc = self._join_docs(current_doc, separator)
                    # 如果拼接结果不为空，则添加到结果列表
                    if doc is not None:
                        docs.append(doc)
                    if doc is None:
                        continue
                    # 处理重叠逻辑，只保留最后 chunk_overlap 个字符
                    # 需要保留的字符数
                    target_size = self._chunk_overlap
                    # 当前累计保留长度
                    current_size = 0
                    # 记录需要保留的分块
                    keep_docs = []
                    # 从后往前遍历当前文档块，直到累计长度达到重叠数
                    for i in range(len(current_doc) - 1, -1, -1):
                        # 取出每个子块
                        item = current_doc[i]
                        # 计算每个子块的长度
                        item_len = self._length_function(item)
                        # 计算分隔符的长度
                        sep_len = separator_len if len(keep_docs) > 0 else 0
                        # 如果累计长度加上子块长度和分隔符长度小于等于重叠字符数，则保留该分块
                        if current_size + item_len + sep_len <= target_size:
                            # 保留该分块，插入到 keep_docs 前面
                            keep_docs.insert(0, item)
                            current_size += item_len + sep_len
                        else:
                            # 一旦超过指定重叠字符数，则停止
                            break
                    # 更新当前文档块及总长度
                    current_doc = keep_docs
                    total = current_size
            # 把当前分块加入当前文档块
            current_doc.append(d)
            # 更新累计长度（已有分块需加分隔符长度）
            total += len_ + (separator_len if len(current_doc) > 1 else 0)
        # 合并处理最后剩余的一个文档块
        doc = self._join_docs(current_doc, separator)
        if doc is not None:
            docs.append(doc)
        # 返回处理后的所有文档块
        return docs

    def _join_docs(self, docs: List[str], separator: str) -> Union[str]:
        """
        使用分隔符连接文档块。
        Args:
            docs: 文档块列表
            separator: 分隔符

        Returns:
        """
        # 使用分隔符拼接各分块
        text = separator.join(docs)
        # 按需去除首尾空白符
        if self._strip_whitespace:
            text = text.strip()
        return text if text else None
