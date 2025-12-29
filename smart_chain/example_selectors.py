from abc import ABC, abstractmethod
from .prompts import PromptTemplate
import re
import jieba
# 定义示例选择器的抽象基类
class BaseExampleSelector(ABC):
    """示例选择器的抽象基类"""
    @abstractmethod
    def select_examples(self, input_variables:dict) -> list[dict]:
        """根据输入变量选择示例"""
        pass

# 定义一个基于长度的示例选择器
class LengthBasedExampleSelector(BaseExampleSelector):
    """
    基于长度的示例选择器
    根据输入长度自动选择合适数量的示例，确保总长度不超过限制
    """
    def __init__(
            self,
            examples:list[dict], # 示例列表，每个元素为字典
            example_prompt: PromptTemplate | str, # 用于格式化示例的模板，可以是PromptTemplate或字符串
            max_length: int = 2048, # 提示词最大长度，默认为2048
            get_text_length = None  # 可选的文本长度计算函数
    ):
        """
            初始化 LengthBasedExampleSelector

            Args:
                examples: 示例列表，每个示例是一个字典
                example_prompt: 用于格式化示例的模板（PromptTemplate 或字符串）
                max_length: 提示词的最大长度（默认 2048）
                get_text_length: 计算文本长度的函数（默认按单词数计算）
        """
        # 保存所有示例到实例变量
        self.examples = examples
        # 如果example_prompt 是字符串，则构建为PromptTemplate对象
        if isinstance(example_prompt, str):
            self.example_prompt = PromptTemplate.from_template(example_prompt)
        else:
            self.example_prompt = example_prompt
        # 保存最大长度参数
        self.max_length = max_length
        # 设置文本长度计算函数，默认为内部定义的按单词数计算
        self.get_text_length = get_text_length or self._default_get_text_length
        # 计算并缓存每个示例（格式化后）的长度
        self.example_text_lengths = self._calculate_example_lengths()

    # 默认的长度计算方法，统计文本中的单词数
    def _default_get_text_length(self, text: str) -> int:
        """
        默认的长度计算函数：按单词数计算
        Args:
            text: 文本内容

        Returns:
            文本长度（单词数）
        """
        words = jieba.cut(text)
        list = [word for word in words if word.strip()]
        return len(list)
    # 计算并缓存每个示例（格式化后）的长度
    def _calculate_example_lengths(self) -> list[int]:
        lengths = []
        for example in self.examples:
            # 用模板对示例内容进行格式化
            formatted_example = self.example_prompt.format(**example)
            # 计算格式化后示例的长度
            length = self.get_text_length(formatted_example)
            # 记录到列表中
            lengths.append(length)
        # 返回长度列表
        return lengths

    # 根据输入内容长度，选择合适的示例列表
    def select_examples(self, input_variables:dict) -> list[dict]:
        """
        根据输入长度选择示例
        Args:
            input_variables: 输入变量字典

        Returns:
            选中的示例列表
        """
        # 将输入的所有变量拼成一个字符串
        input_text = " ".join(str(v) for v in input_variables.values())
        # 计算输入内容的长度
        input_length = self.get_text_length(input_text)
        # 计算剩余的可用的长度
        remaining_length = self.max_length - input_length
        selected_examples = []
        for i,example in enumerate(self.examples):
            if remaining_length <= 0:
                break
            example_length = self.example_text_lengths[i]
            if remaining_length - example_length < 0:
                break
            selected_examples.append(example)
            remaining_length -= example_length
        return selected_examples


