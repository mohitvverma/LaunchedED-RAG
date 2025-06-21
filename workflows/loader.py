import requests
from os import remove
from os.path import expanduser, isfile
from pathlib import Path
from loguru import logger
from urllib.parse import urlparse
from tempfile import NamedTemporaryFile
from typing import Any, List, Optional, Dict, Union

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    PyMuPDFLoader,
    UnstructuredCSVLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader
)

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
    """Split documents into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(text)


class UnifiedLoader:
    """Handles loading files from both local paths and URLs"""
    def __init__(
            self,
            base_loader_cls,
            file_path: Union[str, Path],
            headers: Optional[Dict[str, Any]] = None,
            **unstructured_kwargs: Any,
    ):
        self._temp_file = None
        self.headers = headers or {}
        self.file_path = self._setup_file_path(file_path)
        self.loader = base_loader_cls(
            file_path=str(self.file_path),
            **unstructured_kwargs
        )

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        parsed = urlparse(url)
        return bool(parsed.scheme) and bool(parsed.netloc)

    def _setup_file_path(self, file_path: Union[str, Path]) -> Path:
        """Set up file path from URL or local path"""
        if isinstance(file_path, str) and self._is_valid_url(file_path):
            self._temp_file = NamedTemporaryFile(delete=False)
            try:
                resp = requests.get(file_path, headers=self.headers)
                resp.raise_for_status()
                self._temp_file.write(resp.content)
                self._temp_file.flush()
                return Path(self._temp_file.name)
            except Exception:
                if self._temp_file:
                    self._temp_file.close()
                    remove(self._temp_file.name)
                raise

        path = Path(file_path)
        if "~" in str(path):
            path = Path(expanduser(str(path)))
        if isfile(str(path)):
            return path

        raise ValueError(f"File path {file_path!r} is not a valid file or URL")

    def load(self) -> List[Document]:
        """Load documents from file"""
        documents = self.loader.load()
        if not documents:
            raise ValueError(f"No documents loaded from {self.file_path}")
        return documents

    def __del__(self) -> None:
        """Clean up temporary files"""
        if hasattr(self, "_temp_file") and self._temp_file:
            self._temp_file.close()
            remove(self._temp_file.name)


class FileLoader(BaseLoader):
    """Maps file types to appropriate loaders"""
    LOADER_MAP = {
        "txt": TextLoader,
        "pdf": PyMuPDFLoader,
        "docx": UnstructuredWordDocumentLoader,
        "xlsx": UnstructuredExcelLoader,
        "csv": UnstructuredCSVLoader
    }

    def __init__(self, file_path: Union[str, Path], file_type: str = "txt", headers: Optional[Dict[str, Any]] = None):
        self.file_path = str(file_path) if hasattr(file_path, '__fspath__') else file_path
        self.file_type = file_type.lower()
        self.headers = headers or {}

        if self.file_type not in self.LOADER_MAP:
            raise ValueError(f"Unsupported file type: {self.file_type}. Supported types: {', '.join(self.LOADER_MAP.keys())}")

    def load(self) -> List[Document]:
        """Load documents using appropriate loader"""
        loader_cls = self.LOADER_MAP.get(self.file_type)
        loader = UnifiedLoader(loader_cls, file_path=self.file_path, headers=self.headers)
        return loader.load()


def file_loader(
        file_path: str,
        file_name: str,
        original_file_name: str,
        file_type: str,
        metadata: List[Dict[str, str]] = None,
) -> List[Document]:
    """Load, split and enrich documents with metadata"""

    FILE_TYPE = [
        'pdf','docx','txt','xlsx'
    ]
    if file_type not in FILE_TYPE:
        raise ValueError(f"Unsupported file type: {file_type}. Supported types: {', '.join(FILE_TYPE)}")

    # Load documents
    loader = FileLoader(file_path=file_path, file_type=file_type)
    loaded_documents = loader.load()

    # Split into chunks
    parsed_documents = split_text(
        text=loaded_documents,
        chunk_size=1000,
        chunk_overlap=200,
    )

    # Prepare metadata
    additional_metadata = {
        "original_file_name": original_file_name,
        "file_name": file_name,
        "file_type": file_type,
    }

    if metadata:
        for meta_dict in metadata:
            additional_metadata.update(meta_dict)

    # Add metadata to documents
    for document in parsed_documents:
        document.metadata |= additional_metadata | {
            "title": document.metadata.get("title") or original_file_name
        }
        document.metadata = {k: v for k, v in document.metadata.items() if v != ""}

    return parsed_documents
