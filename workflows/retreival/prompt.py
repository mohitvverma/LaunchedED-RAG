from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

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


# RESPONSE_GENERATION_PROMPT="""
# You are a helpful assistant. Answer the user's question based on the provided context and chat history.
#
# Context:
# Document(metadata={'producer': 'WeasyPrint 65.1', 'creator': 'ChatGPT', 'source': 'Launched', 'file_path': '/Users/mohitverma/Downloads/AI-Powered Conversational Chatbot for Mental Health Assessment.pdf', 'total_pages': 51, 'format': 'PDF 1.7', 'title': 'AI-Powered Conversational Chatbot for Mental Health Assessment', 'author': 'ChatGPT Deep Research', 'page': 0, 'original_file_name': 'test.pdf', 'file_name': 'test.pdf', 'file_type': 'pdf'}, page_content='AI-Powered Conversational Chatbot for Mental\nHealth Assessment\nIntroduction\nDeveloping an AI-driven mental health assessment chatbot requires an extensive knowledge base of\npsychiatric conditions, a robust symptom mapping system, and a carefully designed dialogue and\narchitecture. This report presents a comprehensive overview of major mental health disorders and their\ncharacteristics, a framework mapping symptoms to possible diagnoses, example use cases for the')
#
# Chat History:
# [{'user':'', 'ai'}]
#
# User Question:
# what is stress
# RESPONSE:
# """



def get_response_generation_prompt():
    return PromptTemplate(
        input_variables=['context', 'chat_history', 'question'],
        template=RESPONSE_GENERATION_PROMPT,
        output_parser=StrOutputParser(),
    )
