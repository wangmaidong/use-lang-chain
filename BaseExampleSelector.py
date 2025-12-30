# 导入langchain_core的提示模板和few-shot提示模板
from typing import Any

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate

# 导入基础示例选择器基类
from langchain_core.example_selectors import BaseExampleSelector

# 导入 OpenAI的对话模型及嵌入模型
from langchain_deepseek import ChatDeepSeek

# 导入嵌入模型
from langchain_huggingface import HuggingFaceEmbeddings

import re
import jieba


# 定义自定义的基于关键词匹配的示例选择器
class KeywordBasedExampleSelector(BaseExampleSelector):
    """
    基于关键词匹配的自定义示例选择器
    这个选择器会根据输入中的关键词来选择最相关的示例
    计算输入和示例之间的关键词重叠度，选择重叠度最高的示例
    """

    # 构造函数，初始化参数
    def __init__(self, examples, k=3, input_key: str = "question", min_keyword_match=1):
        """
        初始化关键词选择器
        :param examples: 示例列表
        :param k: 选择的示例数量
        :param input_key: 用于匹配的输入键名
        :param min_keyword_match: 最少匹配的关键词数量
        """
        # 保存示例列表
        self.examples = examples
        # 需要返回的示例个数
        self.k = k
        # 指定比较的字段
        self.input_key = input_key
        # 匹配的最小关键词个数
        self.min_keyword_match = min_keyword_match

    def add_example(self, example: dict[str, str]) -> Any:
        pass

    # 私有方提取中文和英文关键词
    def _extract_keywords(self, text: str):
        """
        从文本提取关键词（中文和英文）
        :param text:输入文本
        :return:关键词集合
        """
        # 用集合存储关键词，防止重复
        keywords = set()
        # 使用jieba分词，支持中英文混合
        words = jieba.cut(text)
        for word in words:
            # 去除两端空白
            word = word.strip()
            # 跳过空字符串
            if not word:
                continue
            # 中文关键词：必须全是中文且长度大于1
            if re.match(r"^[\u4e00-\u9fa5]+$", word):
                if len(word) > 1:
                    keywords.add(word)
            # 英文关键词直接转小写加入
            elif re.match(r"^[a-zA-Z]+$", word):
                keywords.add(word.lower())

        return keywords

    # 私有方法，计算输入和示例文本的关键词重叠数量
    def _calculate_match_score(self, input_text: str, example_text: str) -> int:
        """
        计算输入文本和示例文本的匹配分数
        :param input_text: 输入文本
        :param example_text: 示例文本
        :return:
            int: 匹配分数（关键词重叠数量）
        """
        # 获取输入文本提取出的关键词集合
        input_keywords = self._extract_keywords(input_text)
        # 获取示例文本提取出的关键词集合
        example_keywords = self._extract_keywords(example_text)
        # 计算并返回交集（重叠关键词）的数量
        return len(input_keywords & example_keywords)

    # 主方法，根据输入选择最相关示例
    def select_examples(self, input_variables):
        """
        根据关键词匹配选择示例
        :param input_variables:输入变量字典
        :return:选中的示例列表
        """
        # 从输入变量中获取实际要比较的字段
        input_text = input_variables.get(self.input_key, "")
        # 如果输入内容为空，直接返回前k个示例
        if not input_text:
            return self.examples[: self.k]
        # 用列表存放所有达到匹配要求的（分数，示例）
        scored_examples = []
        for example in self.examples:
            # 取出当前示例的主要字段
            example_text = example.get(self.input_key, "")
            # 计算匹配分数
            score = self._calculate_match_score(input_text, example_text)
            # 如果分数满足最小关键词匹配数，收集该实例
            if score >= self.min_keyword_match:
                scored_examples.append((score, example))
            # 按分数从高到低排序
            # scored_examples.sort(key=lambda x:x[0], reverse=True)
            # 只取前K个高分示例
            selected = [example for _, example in scored_examples[: self.k]]
            if len(selected) < self.k:
                remaining = [ex for ex in self.examples if ex not in selected]
                selected.extend(remaining[: self.k - len(selected)])
            return selected


# 创建示例列表，每个包含'question'和'answer'
examples = [
    {"question": "今天天气怎么样？", "answer": "今天天气晴朗，适合出门活动。"},
    {
        "question": "怎么做西红柿炒鸡蛋？",
        "answer": "先把西红柿和鸡蛋切好，鸡蛋炒熟后盛出，再炒西红柿，最后把鸡蛋倒回去一起炒匀即可。",
    },
    {
        "question": "如何快速减肥？",
        "answer": "合理饮食结合锻炼，每天保持运动，避免高热量食物。",
    },
    {"question": "手机没电了怎么办？", "answer": "用充电器充电，或者借用移动电源。"},
    {"question": "头疼该怎么办？", "answer": "多休息，如果严重可以适当吃点止痛药。"},
    {"question": "怎样养护盆栽？", "answer": "定期浇水，保持阳光，不要积水。"},
    {
        "question": "想学英语怎么入门？",
        "answer": "可以先从背单词、学基础语法和多听多说开始。",
    },
    {
        "question": "晚上失眠怎么办？",
        "answer": "睡前放松，避免咖啡因，可以听点轻音乐帮助入睡。",
    },
    {
        "question": "烧水壶如何清理水垢？",
        "answer": "可以倒入一点醋和水煮几分钟，再用清水冲洗干净。",
    },
    {
        "question": "手机上怎么截图？",
        "answer": "可以同时按住电源键和音量减键进行截图，不同手机略有区别。",
    },
]

# 创建示例输出格式模板
example_prompt = PromptTemplate.from_template("问题：{question}\n答案：{answer}")

# 创建基于关键词的示例选择器
keyword_selector = KeywordBasedExampleSelector(
    examples=examples,
    k=3,
    input_key="question",
    min_keyword_match=1,
)

# 创建 FewShotPromptTemplate，其中 example_selector 使用自定义的 keyword_selector
few_shot_prompt = FewShotPromptTemplate(
    example_prompt=example_prompt,
    prefix="你是一个乐于助人的生活小助手。以下是一些建议示例：",
    suffix="问题：{question}\n答案：",
    example_selector=keyword_selector,  # 使用自定义选择器
)

# 用户输入的问题
user_question = "手机没信号怎么办？"
# 格式化出带有示例和用户问题的完整提示词
formatted = few_shot_prompt.format(question=user_question)
# 打印生成的提示词文本
print(formatted)
