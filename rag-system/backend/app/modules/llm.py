"""LLM Module using Ollama"""
import requests
from typing import List
import logging
from app.config import config

logger = logging.getLogger(__name__)


class OllamaLLM:
    """Generate responses using Ollama"""
    
    def __init__(self, base_url: str = None, model: str = None):
        """
        Initialize Ollama LLM
        
        Args:
            base_url: Ollama server URL
            model: Model name to use
        """
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.model = model or config.OLLAMA_MODEL
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """
        Generate response from LLM
        
        Args:
            prompt: User question/prompt
            context: Relevant code context from retrieved chunks
        
        Returns:
            LLM response
        """
        # Build the full prompt with context
        if context:
            full_prompt = f"""You are a helpful code understanding assistant. 

Use the following code context to answer the question:

<context>
{context}
</context>

Question: {prompt}

Answer:"""
        else:
            full_prompt = prompt
        
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if 'response' in result:
                return result['response'].strip()
            else:
                raise ValueError("No response in result")
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            raise
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def generate_stream_response(self, prompt: str, context: str = ""):
        """
        Generate streaming response from LLM
        
        Args:
            prompt: User question/prompt
            context: Relevant code context from retrieved chunks
        
        Yields:
            Response chunks
        """
        # Build the full prompt with context
        if context:
            full_prompt = f"""You are a helpful code understanding assistant. 

Use the following code context to answer the question:

<context>
{context}
</context>

Question: {prompt}

Answer:"""
        else:
            full_prompt = prompt
        
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
        }
        
        try:
            response = requests.post(url, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if 'response' in data:
                        yield data['response']
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            raise
        except Exception as e:
            logger.error(f"Error generating stream response: {e}")
            raise
