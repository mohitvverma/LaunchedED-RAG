from dataclasses import dataclass
from pydantic import BaseModel, Field

from typing import Optional, List


class PushToDatabaseResponseDto(BaseModel):
    """Response DTO for pushing data to the database."""
    status: bool = False
    message: Optional[str] = None
    document_ids: Optional[List[str]] = None
    timestamp: Optional[str] = None
    index: Optional[str] = None
    namespace: Optional[str] = None


@dataclass
class PineconeConfig:
    index_name: str = "test"
    namespace: str = "default"
    dimension: int = 1536
    metric: str = "cosine"
    cloud: str = "aws"
    region: str = "us-east-1"
