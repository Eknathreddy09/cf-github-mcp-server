"""
GitHub repository operations module.
"""
import os
import requests
from typing import Any, Dict, List, Optional

from common.errors import handle_github_response
from common.utils import parse_link_header

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# API headers
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}


def get_repository(owner: str, repo: str) -> Dict[str, Any]:
    """
    Get a GitHub repository by owner and name.
    
    Args:
        owner: Repository owner
        repo: Repository name
        
    Returns:
        Repository data as dict
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}"
    response = requests.get(url, headers=HEADERS)
    
    handle_github_response(response, f"Failed to get repository {owner}/{repo}")
    
    return response.json()


def search_repositories(query: str, page: int = 1, per_page: int = 30) -> Dict[str, Any]:
    """
    Search for GitHub repositories.
    
    Args:
        query: Search query
        page: Page number
        per_page: Results per page
        
    Returns:
        Search results with pagination info
    """
    url = f"{GITHUB_API_URL}/search/repositories"
    params = {
        "q": query,
        "page": page,
        "per_page": per_page
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    handle_github_response(response, "Repository search failed")
    
    results = response.json()
    
    # Add pagination info
    pagination = {
        "page": page,
        "per_page": per_page,
        "total_count": results.get("total_count", 0)
    }
    
    links = parse_link_header(response.headers.get("Link"))
    if links:
        pagination["links"] = links
    
    return {
        "items": results.get("items", []),
        "pagination": pagination
    }


def create_repository(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new GitHub repository.
    
    Args:
        options: Repository options
        
    Returns:
        Created repository data
    """
    url = f"{GITHUB_API_URL}/user/repos"
    
    response = requests.post(url, headers=HEADERS, json=options)
    
    handle_github_response(response, "Failed to create repository")
    
    return response.json()


def fork_repository(owner: str, repo: str, organization: Optional[str] = None) -> Dict[str, Any]:
    """
    Fork a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        organization: Optional organization to fork to
        
    Returns:
        Forked repository data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/forks"
    
    data = {}
    if organization:
        data["organization"] = organization
    
    response = requests.post(url, headers=HEADERS, json=data)
    
    handle_github_response(response, f"Failed to fork repository {owner}/{repo}")
    
    return response.json()
