"""
Utility functions for the MCP GitHub server.
"""
import base64
import json
import re
from typing import Any, Dict, List, Optional, Union


def encode_content(content: str) -> str:
    """
    Base64 encode content for GitHub API.
    
    Args:
        content: The content to encode
        
    Returns:
        Base64 encoded content as string
    """
    return base64.b64encode(content.encode('utf-8')).decode('utf-8')


def decode_content(encoded_content: str) -> str:
    """
    Decode base64 encoded content from GitHub API.
    
    Args:
        encoded_content: Base64 encoded content
        
    Returns:
        Decoded content as string
    """
    return base64.b64decode(encoded_content).decode('utf-8')


def format_json_response(obj: Any, indent: int = 2) -> str:
    """
    Format an object as a JSON string.
    
    Args:
        obj: The object to format
        indent: Indentation level
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(obj, indent=indent)


def validate_input(
    data: Dict[str, Any], 
    required_fields: List[str], 
    field_validators: Optional[Dict[str, callable]] = None
) -> Dict[str, str]:
    """
    Validate input data for API requests.
    
    Args:
        data: The input data
        required_fields: List of required field names
        field_validators: Optional dict of field validators
        
    Returns:
        Dict of validation errors, empty if validation passes
    """
    errors = {}
    
    # Check required fields
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            errors[field] = f"Field '{field}' is required"

    # Apply field validators
    if field_validators:
        for field, validator in field_validators.items():
            if field in data and data[field] is not None and field not in errors:
                try:
                    validator(data[field])
                except ValueError as e:
                    errors[field] = str(e)
    
    return errors


def parse_link_header(link_header: Optional[str]) -> Dict[str, str]:
    """
    Parse GitHub API Link headers for pagination.
    
    Args:
        link_header: Link header string from GitHub API
        
    Returns:
        Dict of link relations and URLs
    """
    links = {}
    
    if not link_header:
        return links
    
    for link in link_header.split(','):
        match = re.search(r'<([^>]*)>;\s*rel="([^"]*)"', link)
        if match:
            url, rel = match.groups()
            links[rel] = url
    
    return links


def create_event_data(event_type: str, data: Any) -> str:
    """
    Format data for Server-Sent Events.
    
    Args:
        event_type: The event type name
        data: The data payload
        
    Returns:
        Formatted SSE data string
    """
    if isinstance(data, (dict, list)):
        data = json.dumps(data)
    
    return f"event: {event_type}\ndata: {data}\n\n"
