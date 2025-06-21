import os
from loguru import logger
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

VECTOR_LEN = None

def get_chat_model():
    try:
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("OPENAI_API_KEY & AI21_API_KEY environment variable is not set")

        if os.getenv("GOOGLE_API_KEY"):
            logger.warning("GOOGLE_API_KEY is set, using Google Generative AI Model.")

            return ChatGoogleGenerativeAI(
                model='gemini-1.5-flash',
                temperature=0.0,
                max_tokens=2048,
            )

        return ChatOpenAI(
            model='gpt-4o-mini',
            temperature=0.0,
        )

    except Exception as e:
        logger.error(f"Error while getting chat model: {e}")
        raise e


def get_embedding_model():
    try:
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("OPENAI_API_KEY & GOOGLE_API_KEY environment variable is not set")

        if os.getenv("GOOGLE_API_KEY"):
            logger.warning("GOOGLE_API_KEY is set, using Google Generative AI Embeddings.")

            return GoogleGenerativeAIEmbeddings(
                model='models/embedding-001',
            )

        return OpenAIEmbeddings(
            model='text-embedding-ada-002',
        )
    except Exception as e:
        logger.error(f"Error while getting embedding model: {e}")
        raise e


try:
    vectors = get_embedding_model().embed_query(
        "This is a test to check if the embedding model is working correctly."
    )
    VECTOR_LEN = len(vectors)
except Exception as e:
    logger.error(f"Error while testing embedding model: {e}")