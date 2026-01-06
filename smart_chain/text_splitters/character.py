"""文本分割器模块，提供文本分割功能。"""

# 导入正则表达式模块
import re
from .base import TextSplitter


# 定义按字符数处理的文本分割器
class CharacterTextSplitter(TextSplitter):
    """
    字符文本分割器：按字符数分割文本。
    可以指定分隔符，先按分隔符分割，然后再合并成指定大小的块。
    """

    # 构造函数，初始化字符型文本分割器
    def __init__(
        self,
        separator="\n\n",  # 分隔符，默认双换行
        is_separator_regex=False,  # 分隔符是否为正则表达式
        **kwargs,  # 其它参数传递给父类
    ):
        """
        初始化字符文本分割器。

        Args:
            separator: 分隔符，默认为双换行符 "\n\n"
            is_separator_regex: 分隔符是否为正则表达式
            **kwargs: 传递给父类的其他参数（chunk_size, chunk_overlap 等）
        """
        # 初始化父类参数
        super().__init__(**kwargs)
        # 保存分隔符
        self._separator = separator
        # 保存分隔符是否为正则表达式
        self._is_separator_regex = is_separator_regex

    # 重写文本分割方法
    def split_text(self, text):
        """
        将文本分割成多个块。

        Args:
            text: 要分割的文本

        Returns:
            文本块列表
        """
        # 判断分隔符是否为正则表达式
        if self._is_separator_regex:
            # 直接使用正则表达式
            sep_pattern = self._separator
        else:
            # 普通字符要转义用于正则分割
            sep_pattern = re.escape(self._separator)

        # 使用分隔符（正则）分割文本
        splits = self._split_text_with_regex(text, sep_pattern)

        # 根据 self._keep_separator 决定合并分块时是否加分隔符
        merge_sep = self._separator if self._keep_separator else ""

        # 对分割结果做合并处理，返回
        return self._merge_splits(splits, merge_sep)

    # 使用正则表达式分割文本块
    def _split_text_with_regex(self, text, separator):
        """
        使用正则表达式分割文本。

        Args:
            text: 要分割的文本
            separator: 分隔符（正则表达式）

        Returns:
            分割后的文本块列表（过滤掉空字符串）
        """
        # 如果分隔符不为空
        if separator:
            # 利用正则分割输入文本
            splits = re.split(separator, text)
        else:
            # 若分隔符为空，则将文本每个字符拆为一个子块
            splits = list(text)

        # 过滤掉空字符串，仅返回非空的块
        return [s for s in splits if s]
