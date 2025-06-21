from typing import Optional
from pydantic import BaseModel


class InjestRequestDto(BaseModel):
    pre_signed_url: str
    file_name: str
    original_file_name: str
    file_type: str
    namespace: Optional[str] = "dev"


class Message(BaseModel):
    type: str
    content: str