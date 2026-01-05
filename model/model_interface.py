from abc import abstractmethod


class ModelInterface:
    @abstractmethod
    def generate(self, prompt: str,instruction: str) -> str:
        pass