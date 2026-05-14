"""GitHub Repository Reader Module"""
import os
import tempfile
from typing import Dict, List
from github import Github
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class GitHubReader:
    """Reads files from GitHub repositories"""
    
    def __init__(self, github_token: str):
        """
        Initialize GitHub reader
        
        Args:
            github_token: GitHub API token
        """
        if not github_token:
            raise ValueError("GITHUB_TOKEN is not set. Add it to backend/.env before starting the API.")

        self.github = Github(github_token)
    
    def parse_repo_url(self, repo_url: str) -> tuple:
        """
        Parse GitHub repository URL
        
        Args:
            repo_url: Repository URL (e.g., https://github.com/user/repo)
        
        Returns:
            Tuple of (owner, repo_name)
        """
        # Remove .git suffix if present
        repo_url = repo_url.rstrip('/')
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        parts = repo_url.split('/')
        owner = parts[-2]
        repo_name = parts[-1]
        return owner, repo_name
    
    def get_repository_files(self, repo_url: str) -> Dict[str, str]:
        """
        Read all code files from a GitHub repository
        
        Args:
            repo_url: Repository URL
        
        Returns:
            Dictionary with file paths as keys and file contents as values
        """
        try:
            owner, repo_name = self.parse_repo_url(repo_url)
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            files_content = {}
            code_extensions = {
                '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
                '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt', '.scala',
                '.sql', '.html', '.css', '.json', '.yaml', '.yml', '.xml', '.md'
            }
            
            # Get all files from the repository
            self._get_files_recursive(repo, "", files_content, code_extensions)
            
            logger.info(f"Retrieved {len(files_content)} files from {repo_url}")
            return files_content
        
        except Exception as e:
            logger.error(f"Error reading repository: {e}")
            raise
    
    def _get_files_recursive(self, repo, path: str, files_content: Dict, 
                            code_extensions: set, max_depth: int = 10):
        """
        Recursively get files from repository
        
        Args:
            repo: GitHub repository object
            path: Current path in repository
            files_content: Dictionary to store file contents
            code_extensions: Set of file extensions to include
            max_depth: Maximum recursion depth
        """
        if max_depth == 0:
            return
        
        try:
            contents = repo.get_contents(path)
            
            for content in contents:
                # Skip hidden files and common non-essential directories
                if content.name.startswith('.') or content.name in ['node_modules', '__pycache__', '.git', 'dist', 'build']:
                    continue
                
                if content.type == "dir":
                    self._get_files_recursive(repo, content.path, files_content, code_extensions, max_depth - 1)
                else:
                    # Check file extension
                    file_ext = Path(content.name).suffix.lower()
                    if file_ext in code_extensions:
                        try:
                            file_content = content.decoded_content.decode('utf-8')
                            files_content[content.path] = file_content
                        except Exception as e:
                            logger.warning(f"Could not decode file {content.path}: {e}")
        
        except Exception as e:
            logger.warning(f"Error accessing path {path}: {e}")
