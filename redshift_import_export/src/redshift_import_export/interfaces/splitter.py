from abc import ABC, abstractmethod


class Splitter(ABC):

    @abstractmethod
    def split(self):
        pass