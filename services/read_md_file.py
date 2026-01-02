from loguru import logger
def read_md_file(filepath: str) -> str:
    """Reads the contents of a Markdown file and returns it as a string."""
    try:
        logger.info(f"Reading Markdown file from: {filepath}")
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