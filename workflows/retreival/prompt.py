from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


RESPONSE_GENERATION_PROMPT="""
You are a helpful assistant. Answer the user's question based on the provided context and chat history.

Context:
{context}

Chat History:
{chat_history}

User Question:
{question}

RESPONSE: 
"""


def get_response_generation_prompt():
    return PromptTemplate(
        input_variables=['context', 'chat_history', 'question'],
        template=RESPONSE_GENERATION_PROMPT,
    )
