
import json
def read_json_file(filepath: str) -> dict:
    """Reads the contents of a JSON file and returns it as a dictionary."""
    with open(filepath, 'r') as file:
        content = file.read()
        data = json.loads(content)
    return data