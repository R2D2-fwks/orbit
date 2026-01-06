from loguru import logger
def write_file(filepath: str, content: str) -> None:
    """Writes the given content to a file at the specified filepath."""
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