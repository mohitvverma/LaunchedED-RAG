from workflows.vector_db.utils import validate_and_create_index
from loguru import logger


def start_injestion():
    validate_and_create_index(
        index_name='test'
    )


try:
    start_injestion()
except Exception as e:
    logger.error(f"Error occurred during injestion: {e}")