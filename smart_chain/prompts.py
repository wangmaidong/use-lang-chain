
# 导入正则表达式模块，用于变量提取
import re

# 定义提示词模板类
class PromptTemplate:
    # 类说明文档，描述用途
    """提示词模板类，用于格式化字符串模板"""

    # 构造方法，初始化模板实例
    def __init__(self, template: str):
        # 保存模板字符串到实例属性
        self.template = template
        # 调用内部方法提取模板中的变量名列表
        input_variables = self._extract_variables(template)
        # 将变量名列表分配给实例属性
        self.input_variables = input_variables

    # 类方法：从模板字符串生成 PromptTemplate 实例
    @classmethod
    def from_template(cls, template: str):
        # 返回用 template 实例化的 PromptTemplate 对象
        return cls(template=template)

    # 格式化填充模板中的变量
    def format(self, **kwargs):
        # 计算模板中缺失但未传入的变量名集合
        missing_vars = set(self.input_variables) - set(kwargs.keys())
        # 如果存在缺失变量则抛出异常，提示哪些变量缺失
        if missing_vars:
            raise ValueError(f"缺少必需的变量: {missing_vars}")
        # 使用传入参数填充模板并返回格式化后的字符串
        return self.template.format(**kwargs)

    # 内部方法：从模板字符串中提取变量名
    def _extract_variables(self, template: str):
        # 定义正则表达式，匹配花括号中的变量名（冒号前的部分）
        pattern = r'\{([^}:]+)(?::[^}]+)?\}'
        # 查找所有符合 pattern 的变量名，返回匹配结果列表
        matches = re.findall(pattern, template)
        # 利用 dict 去重并保持顺序，最后转为列表返回
        return list(dict.fromkeys(matches))
