import os
import streamlit as st
import tempfile
import asyncio
from typing import List, Dict, Any
import uuid
from dotenv import load_dotenv

load_dotenv()

from workflows.models import InjestRequestDto, Message
from workflows.injest.routes import injest_doc
from workflows.retreival.routes import get_response

# Set page configuration
st.set_page_config(
    page_title="Document Chat",
    page_icon="📄",
    layout="wide",
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "namespace" not in st.session_state:
    st.session_state.namespace = f"user_{uuid.uuid4().hex[:8]}"
if "documents" not in st.session_state:
    st.session_state.documents = []

# Function to run async functions in Streamlit
def run_async(func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(func(*args, **kwargs))
    loop.close()
    return result

# Title and description with improved styling
st.title("📄 Document Chat Assistant")
st.markdown("""
<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
    <h3 style="color: #0e1117;">Welcome to Document Chat!</h3>
    <p>Upload a document and chat with it! The system will use the document content to answer your questions.</p>
    <p><b>How to use:</b></p>
    <ol>
        <li>Upload your document using the sidebar on the left</li>
        <li>Click "Process Document" to analyze it</li>
        <li>Ask questions about your document in the chat below</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Sidebar for document upload
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx", "xlsx"])

    if uploaded_file is not None:
        file_details = {
            "FileName": uploaded_file.name,
            "FileType": uploaded_file.type,
            "FileSize": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.write("File Details:")
        st.json(file_details)

        # Process the uploaded file when the user clicks the button
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                # Save the uploaded file to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_file_path = tmp_file.name

                try:
                    # Determine file type
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    supported_extensions = {
                        "pdf": "pdf",
                        "txt": "txt",
                        "docx": "docx",
                        "xlsx": "xlsx"
                    }

                    if file_extension not in supported_extensions:
                        st.error(f"Unsupported file type: {file_extension}")
                    else:
                        # Create request object
                        request = InjestRequestDto(
                            pre_signed_url=temp_file_path,
                            file_name=uploaded_file.name,
                            original_file_name=uploaded_file.name,
                            file_type=supported_extensions[file_extension],
                            namespace='test'
                        )

                        # Process the document
                        result = run_async(injest_doc, request)

                        if result["success"]:
                            st.success(f"Document processed successfully! {result.get('chunks', 0)} chunks created.")
                            # Add to documents list
                            st.session_state.documents.append({
                                "name": uploaded_file.name,
                                "namespace": st.session_state.namespace
                            })
                        else:
                            st.error(f"Failed to process document: {result.get('message', 'Unknown error')}")
                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)

    # Display processed documents
    if st.session_state.documents:
        st.header("Processed Documents")
        for doc in st.session_state.documents:
            st.write(f"📄 {doc['name']}")

# Main chat interface
st.header("Chat with your documents")

# Display chat history in a more visually appealing way
st.subheader("Chat History")
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_history:
        # Display welcome message when there's no chat history
        # st.info("""
        # 👋 Welcome to Document Chat!
        #
        # Your conversation will appear here after you ask your first question.
        #
        # Upload a document using the sidebar, then ask questions about it below.
        # """)
        pass
    else:
        for message in st.session_state.chat_history:
            if message["type"] == "human":
                with st.chat_message("user", avatar="🧑‍💻"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(message["content"])

# Add a divider for better visual separation
st.markdown("---")

# Input area with improved styling
st.subheader("Ask a question")
col1, col2 = st.columns([4, 1])
with col1:
    # Input for new messages
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area("Your question:", key="user_input", height=100, 
                                placeholder="Type your question here...")
        col_a, col_b = st.columns([1, 1])
        with col_a:
            submitted = st.form_submit_button("Send", use_container_width=True)
        with col_b:
            clear_button = st.form_submit_button("Clear Chat", use_container_width=True)
            if clear_button:
                st.session_state.chat_history = []
                st.rerun()

if submitted and user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"type": "human", "content": user_input})

    # Convert chat history to Message objects
    messages = [Message(type=msg["type"], content=msg["content"]) for msg in st.session_state.chat_history]

    # Get response from the model
    with st.spinner("Thinking..."):
        response = run_async(
            get_response,
            question=user_input,
            language="en",
            chat_context=messages,
            namespace='test'
        )
        response_content = response.get("content", "I couldn't generate a response.")

    # Add assistant response to chat history
    st.session_state.chat_history.append({"type": "ai", "content": response_content})

    # Rerun to update the UI with the new messages
    st.rerun()

# Footer
st.markdown("---")
st.markdown("Document Chat System - Upload and chat with your documents")
