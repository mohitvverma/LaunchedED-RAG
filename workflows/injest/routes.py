from typing import Dict, Any
from workflows.injest.utils import load_file_push_to_db
from workflows.models import InjestRequestDto
from loguru import logger


async def injest_doc(
        request: InjestRequestDto
) -> Dict[str, Any]:
    try:
        logger.info(f"Processing file: {request.file_name}")

        response = await load_file_push_to_db(request)

        if response["success"]:
            logger.info(f"Document ingestion successful: {response}")
            return response
        else:
            logger.error(f"Document ingestion failed: {response}")
            return response
    except Exception as e:
        logger.error(f"Error in document ingestion: {e}")
        return {
            "success": False,
            "message": f"Error in document ingestion: {str(e)}",
            "file_name": request.file_name
        }
