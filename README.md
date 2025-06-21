# LaunchedED-RAG

A document processing and retrieval system that allows users to upload documents, store them in a vector database, and chat with them using natural language.

## Features

- **Document Processing**: Upload and process various document types (PDF, TXT, DOCX, XLSX)
- **Vector Database Storage**: Store document chunks in Pinecone for efficient retrieval
- **Chat Interface**: Interact with your documents using natural language
- **Streamlit Web Application**: User-friendly interface for document upload and chat

## Prerequisites

- Python 3.8+
- OpenAI API Key
- Pinecone API Key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/LaunchedED-RAG.git
   cd LaunchedED-RAG
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   export OPENAI_API_KEY=your_openai_api_key
   export PINECONE_API_KEY=your_pinecone_api_key
   ```

## Usage

### Running the Streamlit Application

1. Start the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your browser and navigate to the URL displayed in the terminal (usually http://localhost:8501)

3. Use the sidebar to upload a document

4. Click "Process Document" to ingest the document into the system

5. Use the chat interface to ask questions about your document

### API Usage

The system can also be used programmatically:

#### Document Ingestion

```python
from workflows.models import InjestRequestDto
from workflows.injest.routes import injest_doc

# Create a request object
request = InjestRequestDto(
    pre_signed_url="path/to/your/file.pdf",
    file_name="file.pdf",
    original_file_name="file.pdf",
    file_type="pdf",
    namespace="your_namespace"
)

# Process the document
result = await injest_doc(request)
```

#### Document Retrieval

```python
from workflows.retreival.routes import get_response

# Get a response based on a question
response = await get_response(
    question="What is the main topic of the document?",
    language="en",
    namespace="your_namespace"
)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Streamlit Web Application                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Workflow Manager                         │
├─────────────────┬─────────────────────────────┬─────────────────┤
│                 │                             │                 │
▼                 ▼                             ▼                 ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ ┌─────────────┐
│  Document   │ │   Vector    │ │      Retrieval      │ │    Utils    │
│  Ingestion  │ │  Database   │ │                     │ │             │
└──────┬──────┘ └──────┬──────┘ └──────────┬──────────┘ └─────────────┘
       │               │                   │
       ▼               ▼                   ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐
│   Document   │ │   Pinecone   │ │   OpenAI Language    │
│   Loaders    │ │     API      │ │        Model         │
└──────────────┘ └──────────────┘ └──────────────────────┘
```

## Project Structure

- `app.py`: Streamlit web application
- `workflows/`: Core functionality
  - `injest/`: Document ingestion
  - `retreival/`: Document retrieval and chat
  - `vector_db/`: Vector database operations
  - `loader.py`: Document loading and processing
  - `utils.py`: Utility functions

## Supported File Types

- PDF (`.pdf`)
- Text (`.txt`)
- Word Documents (`.docx`)
- Excel Spreadsheets (`.xlsx`)

## License

This project is licensed under the terms of the license included in the repository.
