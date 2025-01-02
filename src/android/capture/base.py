from abc import ABC, abstractmethod


class Capturer(ABC):
    @abstractmethod
    def capture(self):
        pass

    @abstractmethod
    def init_env(self):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    def __del__(self):
        self.clear()