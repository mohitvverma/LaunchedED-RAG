from workflows.models import InjestRequestDto
from typing import Dict, Any

from loguru import logger
from workflows.loader import file_loader
from workflows.vector_db.utils import push_to_database
from workflows.vector_db.models import PineconeConfig


async def load_file_push_to_db(
        request: InjestRequestDto
) -> Dict[str, Any]:
    try:
        logger.debug(f"load_file_push_to_db(): Attempting to load file from {request.pre_signed_url}")

        chunked_documents = file_loader(
            file_path=request.pre_signed_url,
            file_name=request.file_name,
            original_file_name=request.original_file_name,
            file_type=request.file_type,
        )
        logger.info(f"Successfully loaded file from {request.pre_signed_url} and total chunks: {len(chunked_documents)}")

        config = PineconeConfig()
        push_status = push_to_database(
            texts=chunked_documents,
            index_name=config.index_name,
            namespace=request.namespace
        )

        if not push_status:
            return {
                "success": False,
                "message": "Failed to push documents to database",
                "file_name": request.file_name
            }

        logger.info("Processing completed successfully")
        return {
            "success": True,
            "message": "File processed and stored successfully",
            "file_name": request.file_name,
            "namespace": request.namespace,
            "chunks": len(chunked_documents)
        }

    except Exception as e:
        logger.error(f"Failed to load file from {request.pre_signed_url} and error is {e}")
        return {
            "success": False,
            "message": f"Error processing file: {str(e)}",
            "file_name": request.file_name
        }
