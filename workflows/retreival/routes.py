from typing import Optional, List, Dict, Any

from langchain.chains.llm import LLMChain
from loguru import logger
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from workflows.vector_db.utils import get_related_docs_with_score
from workflows.retreival.prompt import get_response_generation_prompt
from workflows.utils import get_chat_model
from workflows.vector_db.models import PineconeConfig
from workflows.models import Message


async def get_response(
        question: str,
        language: str,
        chat_context: Optional[List[Message]] = None,
        namespace: Optional[str] = None,
        index_name: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        if question is None:
            raise ValueError("Question cannot be None")

        config = PineconeConfig()
        if index_name is None:
            config.index_name = index_name

        docs = await get_related_docs_with_score(
            question=question,
            index_name=config.index_name,
            namespace=namespace or config.namespace,
            total_docs_to_retrieve=10,
        )

        if not docs:
            return {
                "content": "I couldn't find any relevant information to answer your question.",
                "success": False,
                "error": "No relevant documents found"
            }

        chain = get_response_generation_prompt() | get_chat_model() | StrOutputParser()

        response = await chain.ainvoke(
            {
                "context": docs,
                "chat_history": chat_context or [],
                "question": question
            }
        )

        logger.debug(f"RAW LLM RESPONSE {response}")

        return {
            "content": response,
            "success": True,
            "error": None
        }

    except Exception as e:
        logger.error(f"Error in get_response: {e}")
        return {
            "content": "I'm sorry, but I encountered an error while processing your request.",
            "success": False,
            "error": str(e)
        }
