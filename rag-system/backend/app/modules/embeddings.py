"""Embeddings Module using LangChain"""
from langchain_community.embeddings import OllamaEmbeddings
import logging
from app.config import config

logger = logging.getLogger(__name__)


def get_embeddings():
    """
    Get LangChain OllamaEmbeddings instance
    
    Returns:
        OllamaEmbeddings instance configured for local Ollama
    """
    try:
        embeddings = OllamaEmbeddings(
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL
        )
        logger.info(f"Initialized OllamaEmbeddings with model: {config.OLLAMA_MODEL}")
        return embeddings
    except Exception as e:
        logger.error(f"Error initializing OllamaEmbeddings: {e}")
        raise
