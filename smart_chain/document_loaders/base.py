from abc import ABC, abstractmethod


class BaseLoader(ABC):
    def load(self):
        return list(self.lazy_load())

    @abstractmethod
    def lazy_load(self):
        msg = f"{self.__class__.__name__} 必须实现lazy_load方法"
        raise NotImplementedError(msg)
