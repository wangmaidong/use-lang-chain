# 定义基础消息类
class BaseMessage:
    """
    基础消息类
    """
    def __init__(self,content: str, **kwargs):
        """
        初始化消息
        :param content: 消息内容
        :param kwargs: 其他可选参数
        """
        self.content = content
        self.type = kwargs.get("type","base")
        for key,value in kwargs.items():
            if key != "type":
                setattr(self, key,value)

    def __str__(self):
        return self.content

    def __repr__(self):
        return f"{self.__class__.__name__}(content={self.content!r})"

# 定义用户消息类，继承自BaseMessage
class HumanMessage(BaseMessage):
    """
    用户消息
    """
    # 初始化方法，调用父类构造方法，并指定type为"human"
    def __init__(self,content:str,**kwargs):
        super().__init__(content, type="human", **kwargs)

# 定义AI消息类，继承子BaseMessage
class AIMessage(BaseMessage):
    """
    AI消息
    """
    # 初始化方法，调用父类构造方法，并指定type为"ai"
    def __init__(self,content:str,**kwargs):
        # 调用父类的构造方法，并固定type为ai
        super().__init__(content,type="ai",**kwargs)

# 定义系统消息类，继承自BaseMessage
class SystemMessage(BaseMessage):
    """
    系统消息
    """
    def __init__(self,content:str,**kwargs):
        # 调用父类的构造方法，并固定type为ai
        super().__init__(content,type="system",**kwargs)