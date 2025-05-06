"""
GitHub API Error classes
"""
from datetime import datetime
from typing import Any, Dict, Optional


class GitHubError(Exception):
    """Base class for GitHub API errors."""
    def __init__(self, message: str, response: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.response = response


class GitHubValidationError(GitHubError):
    """Error for input validation failures."""
    pass


class GitHubResourceNotFoundError(GitHubError):
    """Error for resources not found in GitHub."""
    pass


class GitHubAuthenticationError(GitHubError):
    """Error for authentication failures."""
    pass


class GitHubPermissionError(GitHubError):
    """Error for permission issues."""
    pass


class GitHubRateLimitError(GitHubError):
    """Error for rate limiting issues."""
    def __init__(self, message: str, reset_at: datetime, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, response)
        self.reset_at = reset_at


class GitHubConflictError(GitHubError):
    """Error for resource conflicts."""
    pass


def is_github_error(error: Exception) -> bool:
    """Check if an exception is a GitHub API error."""
    return isinstance(error, GitHubError)


def handle_github_response(response, error_message: str = "GitHub API error"):
    """
    Handle GitHub API response and raise appropriate errors.
    
    Args:
        response: The requests response object
        error_message: Default error message
        
    Raises:
        GitHubError: Various subclasses depending on the error type
    """
    if response.ok:
        return
        
    status_code = response.status_code
    response_json = {}
    
    try:
        response_json = response.json()
    except:
        pass

    message = response_json.get("message", error_message)
    
    if status_code == 400:
        raise GitHubValidationError(message, response_json)
    elif status_code == 401:
        raise GitHubAuthenticationError(message, response_json)
    elif status_code == 403:
        if "rate limit" in message.lower():
            reset_at = datetime.utcfromtimestamp(response.headers.get("X-RateLimit-Reset", 0))
            raise GitHubRateLimitError(message, reset_at, response_json)
        else:
            raise GitHubPermissionError(message, response_json)
    elif status_code == 404:
        raise GitHubResourceNotFoundError(message, response_json)
    elif status_code == 409:
        raise GitHubConflictError(message, response_json)
    else:
        raise GitHubError(f"{message} (Status code: {status_code})", response_json)
