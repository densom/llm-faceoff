from abc import ABC, abstractmethod

class LLMAdapterInterface(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_response(self, topic: str, context: str) -> str:
        pass
