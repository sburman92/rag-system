"""Data Chunking Module using LangChain"""
from typing import Dict, List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
from app.config import config

logger = logging.getLogger(__name__)


class CodeChunker:
    """Chunks code files using LangChain while preserving context"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize chunker
        
        Args:
            chunk_size: Number of characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
        
        # Initialize RecursiveCharacterTextSplitter for better code splitting
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],  # Try to split at meaningful boundaries
            length_function=len,
        )
    
    def chunk_files(self, files_content: Dict[str, str]) -> List[Document]:
        """
        Chunk multiple files into LangChain Documents
        
        Args:
            files_content: Dictionary with file paths and contents
        
        Returns:
            List of LangChain Document objects with metadata
        """
        documents = []
        
        for file_path, content in files_content.items():
            file_docs = self.chunk_file(file_path, content)
            documents.extend(file_docs)
        
        logger.info(f"Created {len(documents)} documents from {len(files_content)} files")
        return documents
    
    def chunk_file(self, file_path: str, content: str) -> List[Document]:
        """
        Chunk a single file into LangChain Documents
        
        Args:
            file_path: Path to the file
            content: File content
        
        Returns:
            List of LangChain Document objects for this file
        """
        # Split the content using LangChain's splitter
        text_chunks = self.splitter.split_text(content)
        
        documents = []
        lines = content.split('\n')
        
        current_line = 0
        for chunk_index, chunk_text in enumerate(text_chunks):
            # Calculate line numbers
            start_line = current_line + 1
            chunk_lines = chunk_text.count('\n') + 1
            end_line = start_line + chunk_lines - 1
            
            # Update current line for next iteration
            current_line = end_line
            
            # Create Document with metadata
            doc = Document(
                page_content=chunk_text,
                metadata={
                    'file_path': file_path,
                    'chunk_index': chunk_index,
                    'total_chunks': len(text_chunks),
                    'start_line': start_line,
                    'end_line': end_line,
                    'source': file_path,  # LangChain standard field
                }
            )
            documents.append(doc)
        
        logger.debug(f"Chunked {file_path} into {len(documents)} documents")
        return documents
