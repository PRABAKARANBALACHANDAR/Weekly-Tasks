from abc import ABC, abstractmethod

class Data(ABC):
    @abstractmethod
    def create(self): pass
    @abstractmethod
    def read(self): pass
    @abstractmethod
    def update(self, **kwargs): pass
    @abstractmethod
    def delete(self): pass
    @abstractmethod
    def to_dict(self): pass
