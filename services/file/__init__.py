from loguru import logger
import json 

class FileService:

    def read_file(self,filepath: str) -> str:
        try:
            content = ""
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            logger.error(f"Error: The file '{filepath}' was not found.")
            raise FileNotFoundError(f"The file '{filepath}' was not found.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e
        
    def read_json_file(self, filepath: str) -> dict:
        with open(filepath, 'r') as file:
            content = file.read()
            data = json.loads(content)
        return data
    
    def write_file(self,filepath: str, content: str) -> None:
        try:
            logger.info(f"Writing to file at: {filepath}")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            logger.error(f"Error: The file '{filepath}' was not found.")
            raise FileNotFoundError(f"The file '{filepath}' was not found.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e
    
    def append_file(self,filepath: str, content: str) -> None:
        try:
            logger.info(f"Writing to file at: {filepath}")
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(content)
        except FileNotFoundError:
            logger.error(f"Error: The file '{filepath}' was not found.")
            raise FileNotFoundError(f"The file '{filepath}' was not found.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e 