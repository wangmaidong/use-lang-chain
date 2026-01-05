from abc import ABC, abstractmethod


class PromptValue(ABC):
    @abstractmethod
    def to_string(self) -> str:
        """Return prompt value as string."""


class StringPromptValue(PromptValue):
    """String prompt value."""

    def __init__(self, text: str):
        self.text = text

    def to_string(self) -> str:
        """返回提示词字符串"""
        return self.text
