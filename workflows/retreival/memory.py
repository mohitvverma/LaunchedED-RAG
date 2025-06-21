from loguru import logger

from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from workflows.models import Message


def initialise_memory_from_chat_context(chat_context, input_key: str = None):
    return __load_chat_context(chat_context, input_key)


def __load_chat_context(chat_context, input_key: str = None):
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=10,
        input_key=input_key or "question",
        chat_memory=ChatMessageHistory()
    )

    if not chat_context:
        return memory

    logger.info("Loading context from chat context")
    for message_dict in chat_context:
        # Convert dict to Message object if needed
        message = (
            message_dict if isinstance(message_dict, Message)
            else Message(**message_dict)
        )

        # Add messages to memory
        if message.type == "human":
            memory.chat_memory.add_message(HumanMessage(content=message.content))
        elif message.type == "ai":
            memory.chat_memory.add_message(AIMessage(content=message.content))

    return memory