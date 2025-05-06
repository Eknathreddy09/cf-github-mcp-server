"""
GitHub pull requests operations module.
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


def list_pull_requests(
    owner: str, 
    repo: str, 
    state: Optional[str] = None,
    head: Optional[str] = None,
    base: Optional[str] = None,
    sort: Optional[str] = None,
    direction: Optional[str] = None,
    page: int = 1,
    per_page: int = 30
) -> Dict[str, Any]:
    """
    List pull requests in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        state: Optional filter for PR state (open, closed, all)
        head: Optional filter by head user/repo
        base: Optional filter by base branch
        sort: Optional sorting field (created, updated, popularity, long-running)
        direction: Optional sort direction (asc, desc)
        page: Page number
        per_page: Results per page
        
    Returns:
        List of PRs with pagination info
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls"
    params = {
        "page": page,
        "per_page": per_page
    }
    
    if state:
        params["state"] = state
    
    if head:
        params["head"] = head
    
    if base:
        params["base"] = base
    
    if sort:
        params["sort"] = sort
    
    if direction:
        params["direction"] = direction
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    handle_github_response(response, f"Failed to list pull requests for {owner}/{repo}")
    
    pulls = response.json()
    
    # Add pagination info
    pagination = {
        "page": page,
        "per_page": per_page
    }
    
    links = parse_link_header(response.headers.get("Link"))
    if links:
        pagination["links"] = links
    
    return {
        "items": pulls,
        "pagination": pagination
    }


def get_pull_request(owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
    """
    Get a specific pull request in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        Pull request data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}"
    
    response = requests.get(url, headers=HEADERS)
    
    handle_github_response(response, f"Failed to get pull request #{pull_number}")
    
    return response.json()


def create_pull_request(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new pull request in a GitHub repository.
    
    Args:
        options: Pull request options (owner, repo, title, head, base, body, etc.)
        
    Returns:
        Created pull request data
    """
    owner = options.pop("owner")
    repo = options.pop("repo")
    
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls"
    
    response = requests.post(url, headers=HEADERS, json=options)
    
    handle_github_response(response, "Failed to create pull request")
    
    return response.json()


def get_pull_request_files(owner: str, repo: str, pull_number: int) -> List[Dict[str, Any]]:
    """
    Get files changed in a pull request.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        List of files
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}/files"
    
    response = requests.get(url, headers=HEADERS)
    
    handle_github_response(response, f"Failed to get files for PR #{pull_number}")
    
    return response.json()


def create_pull_request_review(
    owner: str, 
    repo: str, 
    pull_number: int,
    options: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a review on a pull request.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number
        options: Review options (event, body, comments, etc.)
        
    Returns:
        Created review data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
    
    response = requests.post(url, headers=HEADERS, json=options)
    
    handle_github_response(response, f"Failed to create review for PR #{pull_number}")
    
    return response.json()


def get_pull_request_reviews(owner: str, repo: str, pull_number: int) -> List[Dict[str, Any]]:
    """
    Get reviews on a pull request.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        List of reviews
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
    
    response = requests.get(url, headers=HEADERS)
    
    handle_github_response(response, f"Failed to get reviews for PR #{pull_number}")
    
    return response.json()


def get_pull_request_comments(owner: str, repo: str, pull_number: int) -> List[Dict[str, Any]]:
    """
    Get review comments on a pull request.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        List of comments
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}/comments"
    
    response = requests.get(url, headers=HEADERS)
    
    handle_github_response(response, f"Failed to get comments for PR #{pull_number}")
    
    return response.json()


def get_pull_request_status(owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
    """
    Get the combined status of all status checks for a pull request.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        Combined status data
    """
    # First, get the pull request to get the head SHA
    pr_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}"
    pr_response = requests.get(pr_url, headers=HEADERS)
    
    handle_github_response(pr_response, f"Failed to get PR #{pull_number}")
    
    pr_data = pr_response.json()
    sha = pr_data["head"]["sha"]
    
    # Then, get the combined status
    status_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits/{sha}/status"
    status_response = requests.get(status_url, headers=HEADERS)
    
    handle_github_response(status_response, f"Failed to get status for PR #{pull_number}")
    
    return status_response.json()


def merge_pull_request(
    owner: str, 
    repo: str, 
    pull_number: int, 
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Merge a pull request.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number
        options: Optional merge options (commit_title, commit_message, merge_method, etc.)
        
    Returns:
        Merge result data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}/merge"
    
    data = options or {}
    
    response = requests.put(url, headers=HEADERS, json=data)
    
    handle_github_response(response, f"Failed to merge PR #{pull_number}")
    
    return response.json()


def update_pull_request_branch(
    owner: str, 
    repo: str, 
    pull_number: int, 
    expected_head_sha: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update a pull request branch with latest changes from base branch.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number
        expected_head_sha: Optional expected head SHA for validation
        
    Returns:
        Update result data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}/update-branch"
    
    data = {}
    if expected_head_sha:
        data["expected_head_sha"] = expected_head_sha
    
    custom_headers = HEADERS.copy()
    custom_headers["Accept"] = "application/vnd.github.v3+json"
    
    response = requests.put(url, headers=custom_headers, json=data)
    
    handle_github_response(response, f"Failed to update branch for PR #{pull_number}")
    
    return response.json()
