import os
from loguru import logger
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

def get_chat_model():
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        return ChatOpenAI(
            model='gpt-4o-mini',
            temperature=0.0,
        )

    except Exception as e:
        logger.error(f"Error while getting chat model: {e}")
        raise e


def get_embedding_model():
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        return OpenAIEmbeddings(
            model='text-embedding-ada-002',
        )
    except Exception as e:
        logger.error(f"Error while getting embedding model: {e}")
        raise e
