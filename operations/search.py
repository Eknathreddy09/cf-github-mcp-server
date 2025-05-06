"""
GitHub search operations module.
"""
import os
import requests
from typing import Any, Dict, List, Optional
import urllib.parse

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


def search_code(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search for code across GitHub repositories.
    
    Args:
        options: Search options (query, per_page, page, etc.)
        
    Returns:
        Search results with pagination info
    """
    url = f"{GITHUB_API_URL}/search/code"
    
    # Prepare query parameters
    query = options.get("query", "")
    page = options.get("page", 1)
    per_page = options.get("per_page", 30)
    
    params = {
        "q": query,
        "page": page,
        "per_page": per_page
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    handle_github_response(response, "Code search failed")
    
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


def search_issues(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search for issues and pull requests across GitHub repositories.
    
    Args:
        options: Search options (query, per_page, page, etc.)
        
    Returns:
        Search results with pagination info
    """
    url = f"{GITHUB_API_URL}/search/issues"
    
    # Prepare query parameters
    query = options.get("query", "")
    page = options.get("page", 1)
    per_page = options.get("per_page", 30)
    
    params = {
        "q": query,
        "page": page,
        "per_page": per_page
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    handle_github_response(response, "Issues search failed")
    
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


def search_users(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search for users on GitHub.
    
    Args:
        options: Search options (query, per_page, page, etc.)
        
    Returns:
        Search results with pagination info
    """
    url = f"{GITHUB_API_URL}/search/users"
    
    # Prepare query parameters
    query = options.get("query", "")
    page = options.get("page", 1)
    per_page = options.get("per_page", 30)
    
    params = {
        "q": query,
        "page": page,
        "per_page": per_page
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    handle_github_response(response, "Users search failed")
    
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
