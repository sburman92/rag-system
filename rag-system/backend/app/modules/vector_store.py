"""Vector Store Module using LangChain + Chroma"""
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List, Dict
import logging
import os

logger = logging.getLogger(__name__)


class CodeVectorStore:
    """Vector store using LangChain Chroma for embeddings"""
    
    def __init__(self, persist_directory: str = "./chroma_db", 
                 collection_name: str = "code_embeddings"):
        """
        Initialize vector store
        
        Args:
            persist_directory: Directory to persist Chroma database
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        self.vector_store = None
        logger.info(f"Vector store initialized for path: {persist_directory}")
    
    def add_documents(self, documents: List[Document], embeddings):
        """
        Add documents with embeddings to the vector store
        
        Args:
            documents: List of LangChain Document objects
            embeddings: LangChain embeddings instance
        """
        if not documents:
            logger.warning("No documents to add")
            return
        
        try:
            # Create or update Chroma vector store
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
                collection_metadata={"hnsw:space": "cosine"}
            )
            
            # Persist to disk
            self.vector_store.persist()
            
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def search(self, query_text: str, embeddings, top_k: int = 5) -> List[Dict]:
        """
        Search similar documents using text query
        
        Args:
            query_text: Query text to search for
            embeddings: LangChain embeddings instance
            top_k: Number of top results to return
        
        Returns:
            List of search results with documents and metadata
        """
        if self.vector_store is None:
            # Load existing vector store
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
                embedding_function=embeddings
            )
        
        try:
            results = self.vector_store.similarity_search_with_score(
                query_text,
                k=top_k
            )
            
            search_results = []
            for doc, distance in results:
                result = {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'distance': float(distance),
                }
                search_results.append(result)
            
            logger.info(f"Search returned {len(search_results)} results")
            return search_results
        
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise
    
    def clear(self, embeddings):
        """
        Clear all documents from the vector store
        
        Args:
            embeddings: LangChain embeddings instance (needed to reinitialize)
        """
        try:
            # Delete existing data
            if self.vector_store is not None:
                import shutil
                chroma_path = os.path.join(self.persist_directory, self.collection_name)
                if os.path.exists(chroma_path):
                    shutil.rmtree(chroma_path)
            
            # Reinitialize
            self.vector_store = None
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store
        
        Returns:
            Dictionary with store statistics
        """
        try:
            if self.vector_store is None:
                return {'count': 0, 'name': self.collection_name}
            
            # Try to get collection count
            try:
                count = self.vector_store._collection.count()
            except:
                count = 0
            
            return {
                'count': count,
                'name': self.collection_name,
                'persist_directory': self.persist_directory,
            }
        except Exception as e:
            logger.error(f"Error getting vector store stats: {e}")
            return {'count': 0, 'name': self.collection_name, 'error': str(e)}
