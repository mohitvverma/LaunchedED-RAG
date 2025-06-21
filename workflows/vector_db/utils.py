from typing import List, Union, Optional

from datetime import datetime
from loguru import logger

from workflows.utils import get_embedding_model
from workflows.vector_db.client import initialize_pinecone
from workflows.vector_db.models import PineconeConfig, PushToDatabaseResponseDto

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec, PineconeApiException

from workflows.handler import retry_with_custom_backoff


def handle_pinecone_push(
        texts: List,
        meta_datas: List,
        config: PineconeConfig,
        drop_namespace: bool=False
) -> PushToDatabaseResponseDto:
    if drop_namespace:
        pinecone_vs = initialize_pinecone()
        loaded_index = pinecone_vs.Index(config.index_name)

        if loaded_index is None:
            raise (f"Index {config.index_name} not found")

        namespaces = list(loaded_index.describe_index_stats()["namespaces"].keys())

        if config.namespace in namespaces:
            loaded_index.delete(delete_all=True, namespace=config.namespace)
            logger.info(f"Deleted namespace: {config.namespace} from index: {config.index_name}")

    PineconeVectorStore.from_texts(
        [t.page_content for t in texts],
        get_embedding_model(),
        meta_datas,
        index_name=config.index_name,
        namespace=config.namespace,
    )

    return PushToDatabaseResponseDto(
        status=True,
        message="Documents pushed successfully",
        document_ids=None,
        timestamp=datetime.now().isoformat(),
        index=config.index_name,
        namespace=config.namespace
    )


def push_to_database(
    texts: List,
    index_name: str = None,
    namespace: str = None,
) -> bool:
    try:
        config = PineconeConfig()
        config.index_name = index_name
        config.namespace = namespace

        meta_datas = [text.metadata for text in texts]
        handle_pinecone_push(
            texts=texts,
            meta_datas=meta_datas,
            config=config,
        )

        logger.info(f"Successfully pushed {len(texts)} documents to index: {index_name}")
        return True

    except Exception as e:
        logger.exception(f"Vector database operation failed: {str(e)}")
        return False


def load_index(
        index_name: str,
        namespace: str | None = None
) -> Union[PineconeVectorStore, None]:

    try:
        # load a pinecone index
        return PineconeVectorStore.from_existing_index(
            index_name=index_name,
            embedding=get_embedding_model(),
            namespace=namespace,
        )
    except Exception as e:
        logger.error(f"Failed to load index: {e}")
        return None


async def get_related_docs_with_score(
    index_name: str,
    namespace: str,
    question: str,
    total_docs_to_retrieve: int = 10,
) -> list[tuple[Document, float]]:
    try:
        docsearch = load_index(index_name=index_name)

        if not docsearch:
            raise ValueError("Document search object is None")

        related_docs_with_score = await docsearch.asimilarity_search_with_relevance_scores(
            query=question,
            namespace=namespace,
            k=total_docs_to_retrieve,
        )
        return related_docs_with_score

    except Exception as e:
        logger.error(f"Failed to get related docs without context: {e}")
        return []


def create_pinecone_index(pc: Pinecone, config: PineconeConfig) -> None:
    try:
        pc.create_index(
            name=config.index_name,
            dimension=config.dimension,
            metric=config.metric,
            spec=ServerlessSpec(cloud=config.cloud, region=config.region)
        )
        logger.info(f"Successfully created index: {config.index_name}")
    except (PineconeApiException, Exception) as e:
        logger.error(f"Failed to create index: {e}")
        raise


@retry_with_custom_backoff()
def validate_and_create_index(
        index_name: str,
        drop_index: bool = False
) -> bool:
    try:
        pc = initialize_pinecone()
        indexes = [index.get("name") for index in pc.list_indexes()]
        logger.info(f"Existing indexes: {indexes}")

        config = PineconeConfig(index_name=index_name)

        if index_name in indexes:
            if drop_index:
                try:
                    pc.delete_index(index_name)
                    create_pinecone_index(pc, config)
                except Exception as e:
                    logger.error(f"Failed to handle existing index: {e}")
                    return False
            return True

        create_pinecone_index(pc, config)
        return True

    except Exception as e:
        logger.error(f"Failed to validate and create index: {e}")
        return False