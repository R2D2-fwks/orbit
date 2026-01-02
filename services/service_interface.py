from abc import abstractmethod

class ServiceInterface:
    @abstractmethod
    def call_service(self, data: dict) -> dict:
        pass
    