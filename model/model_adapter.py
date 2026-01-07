from model.model_interface import ModelInterface


class ModelAdapter(ModelInterface):
    def __init__(self, model: ModelInterface):
        super().__init__()
        self.model = model

    def generate(self, prompt: str,instruction: str) -> str:
        return self.model.generate(prompt, instruction)

    def getModel(self) -> ModelInterface:
        return self.model
    
    def get_latest_thread(self) -> str:
        return self.model.get_latest_thread()
    
    def delete_thread(self, thread_id: str) -> bool:
        return self.model.delete_thread(thread_id)