import json
import os
import time
import uuid
from flask import Flask, jsonify, request, Response, stream_with_context
from functools import wraps
import traceback

# Import operations modules
from operations import repository, files, issues, pulls, branches, search, commits
from common.errors import GitHubError, is_github_error
from common.utils import create_event_data
from common.version import VERSION

# Initialize Flask app
app = Flask(__name__)

# Get GitHub token from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
if not GITHUB_TOKEN:
    raise ValueError("Missing GITHUB_TOKEN. Set it in your environment variables.")
# Set GitHub token for operations modules
os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN

# MCP Protocol version
MCP_PROTOCOL_VERSION = "1.0"

# Available tools configuration
TOOLS = [
    {
        "name": "create_or_update_file",
        "description": "Create or update a single file in a GitHub repository"
    },
    {
        "name": "search_repositories",
        "description": "Search for GitHub repositories"
    },
    {
        "name": "create_repository",
        "description": "Create a new GitHub repository in your account"
    },
    {
        "name": "get_file_contents",
        "description": "Get the contents of a file or directory from a GitHub repository"
    },
    {
        "name": "push_files",
        "description": "Push multiple files to a GitHub repository in a single commit"
    },
    {
        "name": "create_issue",
        "description": "Create a new issue in a GitHub repository"
    },
    {
        "name": "create_pull_request",
        "description": "Create a new pull request in a GitHub repository"
    },
    {
        "name": "fork_repository",
        "description": "Fork a GitHub repository to your account or specified organization"
    },
    {
        "name": "create_branch",
        "description": "Create a new branch in a GitHub repository"
    },
    {
        "name": "list_commits",
        "description": "Get list of commits of a branch in a GitHub repository"
    },
    {
        "name": "list_issues",
        "description": "List issues in a GitHub repository with filtering options"
    },
    {
        "name": "update_issue",
        "description": "Update an existing issue in a GitHub repository"
    },
    {
        "name": "add_issue_comment",
        "description": "Add a comment to an existing issue"
    },
    {
        "name": "search_code",
        "description": "Search for code across GitHub repositories"
    },
    {
        "name": "search_issues",
        "description": "Search for issues and pull requests across GitHub repositories"
    },
    {
        "name": "search_users",
        "description": "Search for users on GitHub"
    },
    {
        "name": "get_issue",
        "description": "Get details of a specific issue in a GitHub repository"
    },
    {
        "name": "get_pull_request",
        "description": "Get details of a specific pull request"
    },
    {
        "name": "list_pull_requests",
        "description": "List and filter repository pull requests"
    },
    {
        "name": "create_pull_request_review",
        "description": "Create a review on a pull request"
    },
    {
        "name": "merge_pull_request",
        "description": "Merge a pull request"
    },
    {
        "name": "get_pull_request_files",
        "description": "Get the list of files changed in a pull request"
    },
    {
        "name": "get_pull_request_status",
        "description": "Get the combined status of all status checks for a pull request"
    },
    {
        "name": "update_pull_request_branch",
        "description": "Update a pull request branch with the latest changes from the base branch"
    },
    {
        "name": "get_pull_request_comments",
        "description": "Get the review comments on a pull request"
    },
    {
        "name": "get_pull_request_reviews",
        "description": "Get the reviews on a pull request"
    }
]


def handle_error(func):
    """Decorator to handle errors consistently."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GitHubError as e:
            error_response = {
                "error": e.__class__.__name__,
                "message": str(e)
            }
            if hasattr(e, 'response') and e.response:
                error_response["details"] = e.response
            
            app.logger.error(f"GitHub API Error: {str(e)}")
            return jsonify(error_response), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            app.logger.error(traceback.format_exc())
            return jsonify({
                "error": "ServerError",
                "message": str(e)
            }), 500
    
    return wrapper


# Basic routes
@app.route("/", methods=["GET"])
def home():
    """Home endpoint."""
    return jsonify({
        "name": "MCP GitHub Server",
        "version": VERSION,
        "status": "running"
    })


@app.route("/api/status", methods=["GET"])
def status():
    """Status endpoint."""
    return jsonify({
        "status": "UP",
        "version": VERSION,
        "github_token": "configured" if GITHUB_TOKEN else "missing"
    })


# Model Context Protocol routes
@app.route("/api/info", methods=["GET"])
def server_info():
    """Get server information."""
    return jsonify({
        "name": "github-mcp-server",
        "version": VERSION,
        "capabilities": {
            "tools": {}
        }
    })


@app.route("/api/tools", methods=["GET"])
def list_tools():
    """List available tools."""
    return jsonify({
        "tools": TOOLS
    })


@app.route("/api/call", methods=["POST"])
@handle_error
def call_tool():
    """Call a specific tool with arguments."""
    request_data = request.json
    
    if not request_data:
        return jsonify({"error": "No request data provided"}), 400
    
    tool_name = request_data.get("name")
    if not tool_name:
        return jsonify({"error": "Tool name is required"}), 400
    
    args = request_data.get("arguments", {})
    
    # Call the appropriate tool
    result = None
    
    if tool_name == "search_repositories":
        result = repository.search_repositories(
            args.get("query", ""),
            args.get("page", 1),
            args.get("perPage", 30)
        )
    
    elif tool_name == "get_repository":
        result = repository.get_repository(
            args.get("owner"),
            args.get("repo")
        )
    
    elif tool_name == "create_repository":
        result = repository.create_repository(args)
    
    elif tool_name == "fork_repository":
        result = repository.fork_repository(
            args.get("owner"),
            args.get("repo"),
            args.get("organization")
        )
    
    elif tool_name == "get_file_contents":
        result = files.get_file_contents(
            args.get("owner"),
            args.get("repo"),
            args.get("path"),
            args.get("branch")
        )
    
    elif tool_name == "create_or_update_file":
        result = files.create_or_update_file(
            args.get("owner"),
            args.get("repo"),
            args.get("path"),
            args.get("content"),
            args.get("message"),
            args.get("branch"),
            args.get("sha")
        )
    
    elif tool_name == "push_files":
        result = files.push_files(
            args.get("owner"),
            args.get("repo"),
            args.get("branch"),
            args.get("files"),
            args.get("message")
        )
    
    elif tool_name == "create_branch":
        result = branches.create_branch_from_ref(
            args.get("owner"),
            args.get("repo"),
            args.get("branch"),
            args.get("from_branch")
        )
    
    elif tool_name == "list_commits":
        result = commits.list_commits(
            args.get("owner"),
            args.get("repo"),
            args.get("page", 1),
            args.get("perPage", 30),
            args.get("sha")
        )
    
    elif tool_name == "create_issue":
        options = {k: v for k, v in args.items() if k not in ("owner", "repo")}
        result = issues.create_issue(
            args.get("owner"),
            args.get("repo"),
            options
        )
    
    elif tool_name == "list_issues":
        options = {k: v for k, v in args.items() if k not in ("owner", "repo")}
        result = issues.list_issues(
            args.get("owner"),
            args.get("repo"),
            args.get("state"),
            args.get("sort"),
            args.get("direction"),
            args.get("page", 1),
            args.get("perPage", 30)
        )
    
    elif tool_name == "update_issue":
        issue_number = args.pop("issue_number", None)
        options = {k: v for k, v in args.items() if k not in ("owner", "repo")}
        result = issues.update_issue(
            args.get("owner"),
            args.get("repo"),
            issue_number,
            options
        )
    
    elif tool_name == "add_issue_comment":
        result = issues.add_issue_comment(
            args.get("owner"),
            args.get("repo"),
            args.get("issue_number"),
            args.get("body")
        )
    
    elif tool_name == "get_issue":
        result = issues.get_issue(
            args.get("owner"),
            args.get("repo"),
            args.get("issue_number")
        )
    
    elif tool_name == "create_pull_request":
        result = pulls.create_pull_request(args)
    
    elif tool_name == "get_pull_request":
        result = pulls.get_pull_request(
            args.get("owner"),
            args.get("repo"),
            args.get("pull_number")
        )
    
    elif tool_name == "list_pull_requests":
        options = {k: v for k, v in args.items() if k not in ("owner", "repo")}
        result = pulls.list_pull_requests(
            args.get("owner"),
            args.get("repo"),
            args.get("state"),
            args.get("head"),
            args.get("base"),
            args.get("sort"),
            args.get("direction"),
            args.get("page", 1),
            args.get("perPage", 30)
        )
    
    elif tool_name == "get_pull_request_files":
        result = pulls.get_pull_request_files(
            args.get("owner"),
            args.get("repo"),
            args.get("pull_number")
        )
    
    elif tool_name == "create_pull_request_review":
        options = {k: v for k, v in args.items() if k not in ("owner", "repo", "pull_number")}
        result = pulls.create_pull_request_review(
            args.get("owner"),
            args.get("repo"),
            args.get("pull_number"),
            options
        )
    
    elif tool_name == "merge_pull_request":
        options = {k: v for k, v in args.items() if k not in ("owner", "repo", "pull_number")}
        result = pulls.merge_pull_request(
            args.get("owner"),
            args.get("repo"),
            args.get("pull_number"),
            options
        )
    
    elif tool_name == "get_pull_request_status":
        result = pulls.get_pull_request_status(
            args.get("owner"),
            args.get("repo"),
            args.get("pull_number")
        )
    
    elif tool_name == "update_pull_request_branch":
        result = pulls.update_pull_request_branch(
            args.get("owner"),
            args.get("repo"),
            args.get("pull_number"),
            args.get("expected_head_sha")
        )
    
    elif tool_name == "get_pull_request_comments":
        result = pulls.get_pull_request_comments(
            args.get("owner"),
            args.get("repo"),
            args.get("pull_number")
        )
    
    elif tool_name == "get_pull_request_reviews":
        result = pulls.get_pull_request_reviews(
            args.get("owner"),
            args.get("repo"),
            args.get("pull_number")
        )
    
    elif tool_name == "search_code":
        result = search.search_code(args)
    
    elif tool_name == "search_issues":
        result = search.search_issues(args)
    
    elif tool_name == "search_users":
        result = search.search_users(args)
    
    else:
        return jsonify({"error": f"Unknown tool: {tool_name}"}), 400
    
    return jsonify({
        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
    })


def generate_standard_sse_headers():
    """Generate the standard headers for SSE responses."""
    return {
        "Cache-Control": "no-cache",
        "Content-Type": "text/event-stream",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # For NGINX
        "X-MCP-Protocol-Version": MCP_PROTOCOL_VERSION
    }


# MCP message event format (with exact field format expected by client)
def generate_mcp_message_stream():
    """Generate exact MCP-compliant message events in JSON-RPC format.
    
    These formats are based on the MCP Java client expectations which uses JSON-RPC format.
    """
    # Generate server ID and timestamp
    server_id = str(uuid.uuid4())
    now = int(time.time() * 1000)  # milliseconds timestamp
    
    # Use proper event type and JSON-RPC format
    yield f"event: message\ndata: {{\"jsonrpc\":\"2.0\",\"method\":\"open\",\"id\":\"{server_id}\",\"params\":{{\"time\":{now}}}}}\n\n"
    
    # Send a ready event in JSON-RPC format
    yield f"event: message\ndata: {{\"jsonrpc\":\"2.0\",\"method\":\"ready\",\"id\":\"{server_id}-ready\",\"params\":{{\"time\":{now}}}}}\n\n"
    
    # In a real implementation, you would maintain a message queue
    try:
        message_id = 1
        while True:
            now = int(time.time() * 1000)
            # Send ping events with JSON-RPC format
            yield f"event: message\ndata: {{\"jsonrpc\":\"2.0\",\"method\":\"ping\",\"id\":\"ping-{message_id}\",\"params\":{{\"time\":{now}}}}}\n\n"
            message_id += 1
            time.sleep(10)
    except:
        # Client disconnected
        pass


# Endpoint to handle synchronous initialization
@app.route("/initialize", methods=["POST"])
def initialize():
    """Initialize endpoint for synchronous MCP client setup."""
    try:
        # Return session details with streaming endpoint
        return jsonify({
            "id": str(uuid.uuid4()),
            "messageEndpoint": "/message/stream",
            "status": "ready",
            "protocolVersion": MCP_PROTOCOL_VERSION
        })
    except Exception as e:
        app.logger.error(f"Initialization error: {str(e)}")
        return jsonify({
            "error": "InitializationError",
            "message": str(e)
        }), 500


# Endpoint for message sending
@app.route("/send", methods=["POST"])
def send_message():
    """Endpoint for sending messages to the server."""
    try:
        message = request.json
        message_id = message.get("id", str(uuid.uuid4()))
        
        # Log the received message
        app.logger.info(f"Received message: {message}")
        
        # Process the message (implement your logic here)
        # This is a simplified example - you would normally queue this for processing
        
        # Return acknowledgement
        return jsonify({
            "id": message_id,
            "status": "received",
            "time": int(time.time() * 1000)
        })
    except Exception as e:
        app.logger.error(f"Message sending error: {str(e)}")
        return jsonify({
            "error": "MessageError",
            "message": str(e)
        }), 500


# MCP message stream endpoint - specific format for Java client
@app.route("/message/stream", methods=["GET"])
def message_stream_endpoint():
    """MCP message stream endpoint in the exact format required by the Java client."""
    return Response(
        stream_with_context(generate_mcp_message_stream()),
        mimetype="text/event-stream",
        headers=generate_standard_sse_headers()
    )


# Fallback endpoint for any other paths
@app.route("/messages", methods=["GET"])
@app.route("/sse", methods=["GET"])
@app.route("/events", methods=["GET"])
@app.route("/api/events", methods=["GET"])
def generic_events():
    """Generic SSE endpoint that redirects to the message stream endpoint."""
    return message_stream_endpoint()


# Repository-specific SSE endpoint
@app.route("/api/repos/<owner>/<repo>/events", methods=["GET"])
def repo_events(owner, repo):
    """SSE endpoint for repository-specific events."""
    def event_stream():
        """Generate repository-specific SSE events in JSON-RPC format."""
        server_id = str(uuid.uuid4())
        now = int(time.time() * 1000)
        
        # Send JSON-RPC formatted events
        yield f"event: message\ndata: {{\"jsonrpc\":\"2.0\",\"method\":\"open\",\"id\":\"{server_id}\",\"params\":{{\"time\":{now}}}}}\n\n"
        yield f"event: message\ndata: {{\"jsonrpc\":\"2.0\",\"method\":\"ready\",\"id\":\"{server_id}-ready\",\"params\":{{\"time\":{now},\"repository\":\"{owner}/{repo}\"}}}}}\n\n"
        
        # In a real implementation, you would subscribe to repository webhooks
        try:
            message_id = 1
            while True:
                now = int(time.time() * 1000)
                try:
                    # Get latest repository info
                    repo_info = repository.get_repository(owner, repo)
                    
                    # Send repository update event in JSON-RPC format
                    yield f"event: message\ndata: {{\"jsonrpc\":\"2.0\",\"method\":\"repo_update\",\"id\":\"update-{message_id}\",\"params\":{{\"time\":{now},\"repository\":\"{repo_info['name']}\",\"stars\":{repo_info.get('stargazers_count', 0)},\"forks\":{repo_info.get('forks_count', 0)}}}}}\n\n"
                except Exception as e:
                    # Send error event in JSON-RPC format
                    error_message = str(e).replace('"', '\\"')
                    yield f"event: message\ndata: {{\"jsonrpc\":\"2.0\",\"method\":\"error\",\"id\":\"error-{message_id}\",\"params\":{{\"time\":{now},\"message\":\"{error_message}\"}}}}}\n\n"
                
                message_id += 1
                # Wait before checking again
                time.sleep(60)
        except:
            # Client disconnected
            pass
    
    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers=generate_standard_sse_headers()
    )


if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8080))
    
    print(f"Starting MCP GitHub Server on port {port}...")
    print(f"Server version: {VERSION}")
    print(f"GitHub token: {'configured' if GITHUB_TOKEN else 'missing'}")
    
    # Print available endpoints
    print("\nAvailable MCP endpoints:")
    print("  - /initialize (POST) - Initialize MCP session")
    print("  - /message/stream (GET) - SSE message stream")
    print("  - /send (POST) - Send messages to server")
    print("\nLegacy endpoints (all redirect to /message/stream):")
    print("  - /messages")
    print("  - /sse")
    print("  - /events")
    print("  - /api/events")
    print("\nRepository-specific endpoint:")
    print("  - /api/repos/<owner>/<repo>/events")
    
    # Run Flask app
    app.run(host="0.0.0.0", port=port, debug=os.getenv("DEBUG", "False").lower() == "true")
