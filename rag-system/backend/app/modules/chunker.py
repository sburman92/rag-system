"""Data Chunking Module using LangChain"""
from typing import Dict, List, Optional
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
import logging
from app.config import config

logger = logging.getLogger(__name__)

# Mapping of file extensions to programming languages
EXTENSION_TO_LANGUAGE = {
    'py': Language.PYTHON,
    'js': Language.JS,
    'ts': Language.TS,  # TypeScript
    'jsx': Language.JS,
    'tsx': Language.TS,
    'java': Language.JAVA,
    'cpp': Language.CPP,
    'c': Language.C,
    'go': Language.GO,
    'rs': Language.RUST,
    'rb': Language.RUBY,
    'php': Language.PHP,
    'swift': Language.SWIFT,
    'kt': Language.KOTLIN,
    'scala': Language.SCALA,
    'html': Language.HTML,
    'md': Language.MARKDOWN,
    'lua': Language.LUA,
    'pl': Language.PERL,
    'sol': Language.SOL,
    'cs': Language.CSHARP,
}


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
        
        # Initialize default RecursiveCharacterTextSplitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
        )
        
        # Language-specific splitters (lazy loaded)
        self.language_splitters = {}
    
    def _get_language_from_file(self, file_path: str) -> Optional[Language]:
        """
        Detect programming language from file extension
        
        Args:
            file_path: Path to the file
        
        Returns:
            Language enum or None if not recognized
        """
        extension = file_path.split('.')[-1].lower()
        return EXTENSION_TO_LANGUAGE.get(extension)
    
    def _get_language_splitter(self, language: Language) -> RecursiveCharacterTextSplitter:
        """
        Get or create a language-specific splitter
        
        Args:
            language: Language enum
        
        Returns:
            Language-specific RecursiveCharacterTextSplitter
        """
        if language not in self.language_splitters:
            try:
                self.language_splitters[language] = RecursiveCharacterTextSplitter.from_language(
                    language=language,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                )
                logger.info(f"Created language-specific splitter for {language.value}")
            except Exception as e:
                logger.warning(f"Failed to create splitter for {language.value}: {e}. Using default splitter.")
                return self.splitter
        
        return self.language_splitters[language]
    
    def chunk_files(self, files_content: Dict[str, str]) -> List[Document]:
        """
        Chunk multiple files into LangChain Documents
        Uses language-specific splitting when possible
        
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
        Uses language-specific splitting based on file extension
        
        Args:
            file_path: Path to the file
            content: File content
        
        Returns:
            List of LangChain Document objects for this file
        """
        # Detect language and get appropriate splitter
        language = self._get_language_from_file(file_path)
        
        if language:
            splitter = self._get_language_splitter(language)
            logger.debug(f"Using {language.value} splitter for {file_path}")
        else:
            splitter = self.splitter
            logger.debug(f"Using default splitter for {file_path} (language not recognized)")
        
        # Split the content using appropriate splitter
        text_chunks = splitter.split_text(content)
        
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
                    'language': language.value if language else 'unknown',
                }
            )
            documents.append(doc)
        
        logger.debug(f"Chunked {file_path} into {len(documents)} documents (language: {language.value if language else 'unknown'})")
        return documents
    
    def chunk_file_by_language(self, file_path: str, content: str, language: Language) -> List[Document]:
        """
        Chunk a file using a specific programming language splitter
        Useful when you want to override auto-detection
        
        Args:
            file_path: Path to the file
            content: File content
            language: Language enum to use for splitting
        
        Returns:
            List of LangChain Document objects for this file
        """
        splitter = self._get_language_splitter(language)
        logger.debug(f"Using {language.value} splitter for {file_path} (explicitly specified)")
        
        text_chunks = splitter.split_text(content)
        
        documents = []
        current_line = 0
        
        for chunk_index, chunk_text in enumerate(text_chunks):
            start_line = current_line + 1
            chunk_lines = chunk_text.count('\n') + 1
            end_line = start_line + chunk_lines - 1
            current_line = end_line
            
            doc = Document(
                page_content=chunk_text,
                metadata={
                    'file_path': file_path,
                    'chunk_index': chunk_index,
                    'total_chunks': len(text_chunks),
                    'start_line': start_line,
                    'end_line': end_line,
                    'source': file_path,
                    'language': language.value,
                }
            )
            documents.append(doc)
        
        return documents
