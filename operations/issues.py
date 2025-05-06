"""
GitHub issues operations module.
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


def list_issues(
    owner: str, 
    repo: str, 
    state: Optional[str] = None,
    sort: Optional[str] = None,
    direction: Optional[str] = None,
    page: int = 1,
    per_page: int = 30
) -> Dict[str, Any]:
    """
    List issues in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        state: Optional filter for issue state (open, closed, all)
        sort: Optional sorting field (created, updated, comments)
        direction: Optional sort direction (asc, desc)
        page: Page number
        per_page: Results per page
        
    Returns:
        List of issues with pagination info
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues"
    params = {
        "page": page,
        "per_page": per_page
    }
    
    if state:
        params["state"] = state
    
    if sort:
        params["sort"] = sort
    
    if direction:
        params["direction"] = direction
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    handle_github_response(response, f"Failed to list issues for {owner}/{repo}")
    
    issues = response.json()
    
    # Add pagination info
    pagination = {
        "page": page,
        "per_page": per_page
    }
    
    links = parse_link_header(response.headers.get("Link"))
    if links:
        pagination["links"] = links
    
    return {
        "items": issues,
        "pagination": pagination
    }


def get_issue(owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
    """
    Get a specific issue in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        
    Returns:
        Issue data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues/{issue_number}"
    
    response = requests.get(url, headers=HEADERS)
    
    handle_github_response(response, f"Failed to get issue #{issue_number}")
    
    return response.json()


def create_issue(owner: str, repo: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new issue in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        options: Issue options (title, body, etc.)
        
    Returns:
        Created issue data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues"
    
    response = requests.post(url, headers=HEADERS, json=options)
    
    handle_github_response(response, "Failed to create issue")
    
    return response.json()


def update_issue(owner: str, repo: str, issue_number: int, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing issue in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        options: Issue update options
        
    Returns:
        Updated issue data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues/{issue_number}"
    
    response = requests.patch(url, headers=HEADERS, json=options)
    
    handle_github_response(response, f"Failed to update issue #{issue_number}")
    
    return response.json()


def add_issue_comment(owner: str, repo: str, issue_number: int, body: str) -> Dict[str, Any]:
    """
    Add a comment to an issue.
    
    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        body: Comment text
        
    Returns:
        Created comment data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    
    data = {"body": body}
    
    response = requests.post(url, headers=HEADERS, json=data)
    
    handle_github_response(response, f"Failed to add comment to issue #{issue_number}")
    
    return response.json()


def list_issue_comments(owner: str, repo: str, issue_number: int) -> List[Dict[str, Any]]:
    """
    List comments on an issue.
    
    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        
    Returns:
        List of comments
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    
    response = requests.get(url, headers=HEADERS)
    
    handle_github_response(response, f"Failed to list comments for issue #{issue_number}")
    
    return response.json()
