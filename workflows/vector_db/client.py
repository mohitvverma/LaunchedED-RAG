import os
from loguru import logger
from pinecone import Pinecone, ServerlessSpec


def initialize_pinecone() -> Pinecone:
    try:
        pc = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY"),
        )
        logger.info("Successfully connected to Pinecone")
        return pc
    except Exception as e:
        logger.error(f"Error connecting to Pinecone: {e}")
        raise e
