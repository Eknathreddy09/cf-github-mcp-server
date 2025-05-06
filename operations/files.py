"""
GitHub files operations module.
"""
import json
import os
import requests
from typing import Any, Dict, List, Optional

from common.errors import handle_github_response
from common.utils import encode_content, decode_content

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# API headers
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}


def get_file_contents(owner: str, repo: str, path: str, branch: Optional[str] = None) -> Dict[str, Any]:
    """
    Get file contents from GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        path: File path
        branch: Optional branch name
        
    Returns:
        File content data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}"
    params = {}
    
    if branch:
        params["ref"] = branch
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    handle_github_response(response, f"Failed to get file contents for {path}")
    
    result = response.json()
    
    # Handle directory listing
    if isinstance(result, list):
        return {
            "type": "directory",
            "path": path,
            "contents": result
        }
    
    # Handle file content
    if result.get("type") == "file" and "content" in result:
        result["decoded_content"] = decode_content(result["content"])
    
    return result


def create_or_update_file(
    owner: str, 
    repo: str, 
    path: str, 
    content: str, 
    message: str, 
    branch: Optional[str] = None, 
    sha: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create or update a file in a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        path: File path
        content: File content
        message: Commit message
        branch: Optional branch name
        sha: Optional file SHA for updates
        
    Returns:
        API response data
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}"
    
    data = {
        "message": message,
        "content": encode_content(content)
    }
    
    if branch:
        data["branch"] = branch
    
    if sha:
        data["sha"] = sha
    
    response = requests.put(url, headers=HEADERS, json=data)
    
    handle_github_response(response, f"Failed to create/update file at {path}")
    
    return response.json()


def push_files(
    owner: str, 
    repo: str, 
    branch: str, 
    files: List[Dict[str, Any]], 
    message: str
) -> Dict[str, Any]:
    """
    Push multiple files to a GitHub repository in a single commit.
    
    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch name
        files: List of file objects with path and content
        message: Commit message
        
    Returns:
        API response data
    """
    # Get the reference
    ref_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/refs/heads/{branch}"
    ref_response = requests.get(ref_url, headers=HEADERS)
    handle_github_response(ref_response, f"Failed to get ref for branch {branch}")
    ref = ref_response.json()
    
    # Get the commit that the branch currently points to
    commit_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/commits/{ref['object']['sha']}"
    commit_response = requests.get(commit_url, headers=HEADERS)
    handle_github_response(commit_response, "Failed to get commit")
    commit = commit_response.json()
    
    # Create a tree with the new files
    tree_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/trees"
    tree_data = {
        "base_tree": commit["tree"]["sha"],
        "tree": []
    }
    
    for file_obj in files:
        tree_data["tree"].append({
            "path": file_obj["path"],
            "mode": "100644",  # File mode
            "type": "blob",
            "content": file_obj["content"]
        })
    
    tree_response = requests.post(tree_url, headers=HEADERS, json=tree_data)
    handle_github_response(tree_response, "Failed to create tree")
    tree = tree_response.json()
    
    # Create a new commit
    new_commit_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/commits"
    new_commit_data = {
        "message": message,
        "tree": tree["sha"],
        "parents": [commit["sha"]]
    }
    
    new_commit_response = requests.post(new_commit_url, headers=HEADERS, json=new_commit_data)
    handle_github_response(new_commit_response, "Failed to create commit")
    new_commit = new_commit_response.json()
    
    # Update the reference
    update_ref_data = {
        "sha": new_commit["sha"]
    }
    
    update_ref_response = requests.patch(ref_url, headers=HEADERS, json=update_ref_data)
    handle_github_response(update_ref_response, "Failed to update reference")
    
    return {
        "message": f"Successfully pushed {len(files)} files",
        "commit": new_commit,
        "branch": branch
    }
