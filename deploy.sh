#!/bin/bash
# Delete existing application if it exists
cf delete mcp-github-server -f

# Create new application with Python buildpack explicitly specified
cf push mcp-github-server -p . -m 256M -k 256M -b python_buildpack --no-start

# Start the application
cf start mcp-github-server
