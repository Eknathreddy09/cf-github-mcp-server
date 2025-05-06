# Server-Sent Events (SSE) Endpoint Guide

This document provides detailed information about the SSE endpoints available in the MCP GitHub Server.

## What are Server-Sent Events?

Server-Sent Events (SSE) is a technology that allows a server to push real-time updates to clients over an HTTP connection. SSE is a standardized technology built into modern web browsers and is supported in many programming languages via libraries.

## Available SSE Endpoints

### Global Events Endpoint

**URL:** `/api/events`

This endpoint provides global server events, including:
- Connection status updates
- Heartbeat messages
- Server-wide notifications

### Repository-Specific Events Endpoint

**URL:** `/api/repos/{owner}/{repo}/events`

This endpoint provides events specific to a particular GitHub repository, including:
- Repository update notifications
- Star/fork count changes
- Error events related to the repository

## Event Format

SSE events follow the JSON-RPC 2.0 format which is required by the Java client:

```
event: message
data: {"jsonrpc":"2.0","method":"{method_name}","id":"{id}","params":{...}}

```

Where:
- The event type is always "message"
- `method_name` is the operation being performed (e.g., "open", "ready", "ping", "repo_update")
- `id` is a unique identifier for the message
- `params` is an object containing the event parameters

## Connecting to SSE Endpoints

### Using Browser JavaScript

```javascript
const eventSource = new EventSource('/api/events');

// For JSON-RPC format, all events come with event type "message"
eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  
  // Check the method to determine the type of message
  switch(data.method) {
    case 'open':
      console.log('Connection opened:', data);
      break;
    case 'ready':
      console.log('Server ready:', data);
      break;
    case 'ping':
      console.log('Heartbeat ping:', data);
      break;
    case 'repo_update':
      console.log('Repository update:', data.params);
      break;
    case 'error':
      console.error('Server error:', data.params.message);
      break;
    default:
      console.log('Unknown message:', data);
  }
});

// Handle connection errors
eventSource.onerror = (error) => {
  console.error('EventSource error:', error);
  eventSource.close();
};

// Close connection when done
// eventSource.close();
```

### Using Python Client

The included `client.py` provides helper methods for connecting to SSE endpoints. When using the Python client with the JSON-RPC format, you'll need to check the `method` field to determine the message type:

```python
from client import McpGithubClient
import json

client = McpGithubClient()

# Listen for global events
for event in client.connect_events():
    data = event['data']
    if data and 'method' in data:
        method = data['method']
        params = data.get('params', {})
        print(f"Method: {method}")
        print(f"Params: {json.dumps(params, indent=2)}")
        print("-" * 40)

# Listen for repository-specific events
for event in client.connect_repo_events('owner', 'repo'):
    data = event['data']
    if data and 'method' in data:
        method = data['method']
        params = data.get('params', {})
        print(f"Method: {method}")
        print(f"Params: {json.dumps(params, indent=2)}")
        print("-" * 40)
```

## Event Types

### Global Events

1. **open** - Initial connection event
   ```json
   {
     "jsonrpc": "2.0",
     "method": "open",
     "id": "6220882a-510d-4886-a9bd-6d73ddebd1fe",
     "params": {
       "time": 1746527895726
     }
   }
   ```

2. **ready** - Server ready event
   ```json
   {
     "jsonrpc": "2.0",
     "method": "ready",
     "id": "6220882a-510d-4886-a9bd-6d73ddebd1fe-ready",
     "params": {
       "time": 1746527895729
     }
   }
   ```

3. **ping** - Regular heartbeat event (every 10 seconds)
   ```json
   {
     "jsonrpc": "2.0",
     "method": "ping",
     "id": "ping-1",
     "params": {
       "time": 1746527905732
     }
   }
   ```

### Repository Events

1. **open** - Initial repository connection event
   ```json
   {
     "jsonrpc": "2.0",
     "method": "open",
     "id": "8a309ef7-62a0-4c32-b32e-5a72c0f38d91",
     "params": {
       "time": 1746527895726
     }
   }
   ```

2. **ready** - Repository ready event
   ```json
   {
     "jsonrpc": "2.0",
     "method": "ready",
     "id": "8a309ef7-62a0-4c32-b32e-5a72c0f38d91-ready",
     "params": {
       "time": 1746527895727,
       "repository": "owner/repo"
     }
   }
   ```

3. **repo_update** - Repository update event
   ```json
   {
     "jsonrpc": "2.0",
     "method": "repo_update",
     "id": "update-1",
     "params": {
       "time": 1746527955733,
       "repository": "repo-name",
       "stars": 123,
       "forks": 45
     }
   }
   ```

4. **error** - Repository error event
   ```json
   {
     "jsonrpc": "2.0",
     "method": "error",
     "id": "error-1",
     "params": {
       "time": 1746527955733,
       "message": "Error message"
     }
   }
   ```

## Best Practices

1. **Handle Reconnection**: Browsers will automatically attempt to reconnect if the connection is lost, but custom clients should implement reconnection logic.

2. **Error Handling**: Always implement error handlers for SSE connections.

3. **Resource Management**: Close SSE connections when they're no longer needed to free up server resources.

4. **Filtering**: Consider implementing client-side filtering for high-volume event streams.

5. **Timeouts**: Be aware that some proxies might time out long-lived connections. Configure your infrastructure accordingly.
