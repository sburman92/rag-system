"""FastAPI Main Application with LangChain Integration"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import logging
import os

from app.config import config
from app.modules.github_reader import GitHubReader
from app.modules.chunker import CodeChunker
from app.modules.embeddings import get_embeddings
from app.modules.vector_store import CodeVectorStore
from app.modules.llm import OllamaLLM

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Code RAG System",
    description="RAG system for understanding code repositories using LangChain",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
github_reader = GitHubReader(config.GITHUB_TOKEN)
chunker = CodeChunker(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
embeddings = get_embeddings()
vector_store = CodeVectorStore(persist_directory=config.CHROMA_DB_PATH)
llm = OllamaLLM()

# State
indexing_status = {
    "status": "idle",
    "progress": 0,
    "message": "",
}


# Pydantic Models
class IndexRequest(BaseModel):
    """Request to index a repository"""
    repo_url: str


class QueryRequest(BaseModel):
    """Request to query the RAG system"""
    query: str
    top_k: int = 5


class IndexResponse(BaseModel):
    """Response from indexing"""
    status: str
    message: str
    chunks_count: int


class QueryResponse(BaseModel):
    """Response from query"""
    answer: str
    sources: List[Dict]


# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Code RAG System is running"}


@app.get("/status")
async def get_status():
    """Get current indexing status"""
    return indexing_status


@app.post("/index", response_model=IndexResponse)
async def index_repository(request: IndexRequest, background_tasks: BackgroundTasks):
    """
    Index a GitHub repository using LangChain
    
    This endpoint:
    1. Reads files from GitHub repository
    2. Chunks the code using LangChain RecursiveCharacterTextSplitter
    3. Generates embeddings using Ollama via LangChain
    4. Stores in Chroma vector database
    """
    try:
        # Update status
        indexing_status["status"] = "indexing"
        indexing_status["progress"] = 0
        indexing_status["message"] = "Starting indexing process..."
        
        logger.info(f"Starting indexing for repository: {request.repo_url}")
        
        # Read repository
        indexing_status["message"] = "Reading GitHub repository..."
        files = github_reader.get_repository_files(request.repo_url)
        indexing_status["progress"] = 25
        
        if not files:
            raise ValueError("No code files found in repository")
        
        logger.info(f"Retrieved {len(files)} files")
        
        # Chunk files using LangChain
        indexing_status["message"] = "Chunking code files..."
        documents = chunker.chunk_files(files)
        indexing_status["progress"] = 50
        
        logger.info(f"Created {len(documents)} documents")
        
        # Add documents to vector store (LangChain handles embeddings internally)
        indexing_status["message"] = "Generating embeddings and storing..."
        vector_store.add_documents(documents, embeddings)
        indexing_status["progress"] = 100
        
        logger.info("Indexing completed successfully")
        
        # Update status
        indexing_status["status"] = "idle"
        indexing_status["message"] = "Indexing completed successfully"
        
        return IndexResponse(
            status="success",
            message="Repository indexed successfully",
            chunks_count=len(documents)
        )
    
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        indexing_status["status"] = "idle"
        indexing_status["message"] = f"Error: {str(e)}"
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_codebase(request: QueryRequest):
    """
    Query the indexed codebase with RAG using LangChain
    
    This endpoint:
    1. Searches similar documents using LangChain similarity search
    2. Retrieves relevant code chunks with metadata
    3. Sends context and query to LLM
    4. Returns the answer with sources
    """
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Search similar documents using LangChain
        search_results = vector_store.search(
            request.query, 
            embeddings,
            top_k=request.top_k
        )
        
        if not search_results:
            return QueryResponse(
                answer="No relevant code found in the repository.",
                sources=[]
            )
        
        # Build context from retrieved documents
        context_parts = []
        sources = []
        
        for result in search_results:
            metadata = result['metadata']
            file_path = metadata.get('file_path', 'unknown')
            
            # Add file path as section header
            context_parts.append(f"File: {file_path}")
            context_parts.append(f"Lines {metadata.get('start_line', '?')}-{metadata.get('end_line', '?')}:")
            context_parts.append(result['content'])
            context_parts.append("---")
            
            filename = os.path.basename(file_path)
            score = float(result.get('distance', 0.0))
            
            sources.append({
                'file_path': file_path,
                'filename': filename,
                'start_line': int(metadata.get('start_line', 0)),
                'end_line': int(metadata.get('end_line', 0)),
                'chunk_index': int(metadata.get('chunk_index', 0)),
                'score': score,
            })
        
        context = "\n".join(context_parts)
        
        # Generate response from LLM
        logger.info("Generating response from LLM...")
        answer = llm.generate_response(request.query, context)
        
        logger.info("Query processed successfully")
        
        return QueryResponse(
            answer=answer,
            sources=sources
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/collections")
async def get_collection_stats():
    """Get vector store statistics"""
    try:
        stats = vector_store.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear")
async def clear_vector_store():
    """Clear the vector store"""
    try:
        vector_store.clear(embeddings)
        return {"status": "success", "message": "Vector store cleared"}
    except Exception as e:
        logger.error(f"Error clearing vector store: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.API_PORT)
