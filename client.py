"""
MCP GitHub Client with SSE support

This client allows interaction with the MCP GitHub server,
including connecting to the SSE endpoint for real-time updates.
"""
import json
import requests
import sseclient
import time
from typing import Any, Dict, Generator, List, Optional

# Default server URL
DEFAULT_SERVER_URL = "http://localhost:8080"


class McpGithubClient:
    """
    Client for the MCP GitHub Server.
    """
    
    def __init__(self, server_url: Optional[str] = None):
        """
        Initialize the client.
        
        Args:
            server_url: Optional server URL (defaults to http://localhost:8080)
        """
        self.server_url = server_url or DEFAULT_SERVER_URL
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information.
        
        Returns:
            Server information dict
        """
        response = requests.get(f"{self.server_url}/api/info")
        response.raise_for_status()
        return response.json()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get server status.
        
        Returns:
            Server status dict
        """
        response = requests.get(f"{self.server_url}/api/status")
        response.raise_for_status()
        return response.json()
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools.
        
        Returns:
            List of tool dicts
        """
        response = requests.get(f"{self.server_url}/api/tools")
        response.raise_for_status()
        return response.json().get("tools", [])
    
    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call a specific tool.
        
        Args:
            name: Tool name
            arguments: Optional tool arguments
            
        Returns:
            Tool execution result
        """
        data = {
            "name": name,
            "arguments": arguments or {}
        }
        
        response = requests.post(f"{self.server_url}/api/call", json=data)
        response.raise_for_status()
        return response.json()
    
    def connect_events(self) -> Generator[Dict[str, Any], None, None]:
        """
        Connect to the SSE events endpoint.
        
        Yields:
            Event data as dict
        """
        response = requests.get(
            f"{self.server_url}/api/events", 
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        
        client = sseclient.SSEClient(response)
        
        for event in client.events():
            yield {
                "event": event.event,
                "data": json.loads(event.data) if event.data else None
            }
    
    def connect_repo_events(self, owner: str, repo: str) -> Generator[Dict[str, Any], None, None]:
        """
        Connect to the repository-specific SSE events endpoint.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Yields:
            Event data as dict
        """
        response = requests.get(
            f"{self.server_url}/api/repos/{owner}/{repo}/events",
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        
        client = sseclient.SSEClient(response)
        
        for event in client.events():
            yield {
                "event": event.event,
                "data": json.loads(event.data) if event.data else None
            }


# Example usage
if __name__ == "__main__":
    client = McpGithubClient()
    
    print("Server Info:")
    print(json.dumps(client.get_server_info(), indent=2))
    
    print("\nAvailable Tools:")
    tools = client.list_tools()
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")
    
    # Example: Listen for events
    print("\nListening for events (Ctrl+C to stop)...")
    try:
        for event in client.connect_events():
            print(f"Event: {event['event']}")
            print(f"Data: {json.dumps(event['data'], indent=2)}")
            print("-" * 40)
    except KeyboardInterrupt:
        print("\nStopped listening for events.")
