"""
GitHub branches operations module.
"""
import os
import requests
from typing import Any, Dict, List, Optional

from common.errors import handle_github_response

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# API headers
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}


def list_branches(owner: str, repo: str, protected: Optional[bool] = None) -> List[Dict[str, Any]]:
    """
    List branches in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        protected: Optional filter for protected branches
        
    Returns:
        List of branches
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches"
    params = {}
    
    if protected is not None:
        params["protected"] = "true" if protected else "false"
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    handle_github_response(response, f"Failed to list branches for {owner}/{repo}")
    
    return response.json()


def get_branch(owner: str, repo: str, branch: str) -> Dict[str, Any]:
    """
    Get a specific branch in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch name
        
    Returns:
        Branch data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches/{branch}"
    
    response = requests.get(url, headers=HEADERS)
    
    handle_github_response(response, f"Failed to get branch {branch}")
    
    return response.json()


def create_branch_from_ref(owner: str, repo: str, branch: str, from_branch: str) -> Dict[str, Any]:
    """
    Create a new branch from a reference branch.
    
    Args:
        owner: Repository owner
        repo: Repository name
        branch: New branch name
        from_branch: Source branch name
        
    Returns:
        Created branch data
    """
    # Get the SHA of the reference branch
    ref_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/refs/heads/{from_branch}"
    ref_response = requests.get(ref_url, headers=HEADERS)
    
    handle_github_response(ref_response, f"Failed to get reference for branch {from_branch}")
    
    ref_data = ref_response.json()
    sha = ref_data["object"]["sha"]
    
    # Create new branch
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/refs"
    data = {
        "ref": f"refs/heads/{branch}",
        "sha": sha
    }
    
    response = requests.post(url, headers=HEADERS, json=data)
    
    handle_github_response(response, f"Failed to create branch {branch}")
    
    # Return formatted result
    return {
        "name": branch,
        "ref": f"refs/heads/{branch}",
        "sha": sha,
        "from_branch": from_branch,
        "url": response.json().get("url")
    }


def get_branch_protection(owner: str, repo: str, branch: str) -> Dict[str, Any]:
    """
    Get branch protection settings.
    
    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch name
        
    Returns:
        Branch protection settings
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches/{branch}/protection"
    
    # Use the specific media type for branch protection
    custom_headers = HEADERS.copy()
    custom_headers["Accept"] = "application/vnd.github.v3+json"
    
    response = requests.get(url, headers=custom_headers)
    
    handle_github_response(response, f"Failed to get protection for branch {branch}")
    
    return response.json()
