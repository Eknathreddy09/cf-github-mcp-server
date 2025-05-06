"""
GitHub commits operations module.
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


def list_commits(
    owner: str, 
    repo: str, 
    page: int = 1, 
    per_page: int = 30, 
    sha: Optional[str] = None
) -> Dict[str, Any]:
    """
    List commits in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        page: Page number
        per_page: Results per page
        sha: Optional filter by SHA or branch name
        
    Returns:
        List of commits with pagination info
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits"
    params = {
        "page": page,
        "per_page": per_page
    }
    
    if sha:
        params["sha"] = sha
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    handle_github_response(response, f"Failed to list commits for {owner}/{repo}")
    
    commits = response.json()
    
    # Add pagination info
    pagination = {
        "page": page,
        "per_page": per_page
    }
    
    links = parse_link_header(response.headers.get("Link"))
    if links:
        pagination["links"] = links
    
    return {
        "items": commits,
        "pagination": pagination
    }


def get_commit(owner: str, repo: str, sha: str) -> Dict[str, Any]:
    """
    Get a specific commit in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        sha: Commit SHA
        
    Returns:
        Commit data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits/{sha}"
    
    response = requests.get(url, headers=HEADERS)
    
    handle_github_response(response, f"Failed to get commit {sha}")
    
    return response.json()


def compare_commits(
    owner: str, 
    repo: str, 
    base: str, 
    head: str
) -> Dict[str, Any]:
    """
    Compare two commits in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        base: Base commit SHA or branch
        head: Head commit SHA or branch
        
    Returns:
        Comparison data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/compare/{base}...{head}"
    
    response = requests.get(url, headers=HEADERS)
    
    handle_github_response(response, f"Failed to compare {base} and {head}")
    
    return response.json()


def get_commit_comments(owner: str, repo: str, sha: str) -> List[Dict[str, Any]]:
    """
    Get comments on a commit.
    
    Args:
        owner: Repository owner
        repo: Repository name
        sha: Commit SHA
        
    Returns:
        List of comments
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits/{sha}/comments"
    
    response = requests.get(url, headers=HEADERS)
    
    handle_github_response(response, f"Failed to get comments for commit {sha}")
    
    return response.json()


def add_commit_comment(owner: str, repo: str, sha: str, body: str, path: Optional[str] = None, position: Optional[int] = None) -> Dict[str, Any]:
    """
    Add a comment to a commit.
    
    Args:
        owner: Repository owner
        repo: Repository name
        sha: Commit SHA
        body: Comment text
        path: Optional file path for specific file comments
        position: Optional line position for file comments
        
    Returns:
        Created comment data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits/{sha}/comments"
    
    data = {"body": body}
    
    if path:
        data["path"] = path
    
    if position is not None:
        data["position"] = position
    
    response = requests.post(url, headers=HEADERS, json=data)
    
    handle_github_response(response, f"Failed to add comment to commit {sha}")
    
    return response.json()
