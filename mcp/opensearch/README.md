# OpenSearch MCP Server

This directory contains the configuration for an OpenSearch MCP (Model Context Protocol) Server that supports multi-mode operation and uses stream as the transport method.

## Overview

The OpenSearch MCP Server provides a bridge between AI agents and OpenSearch clusters. It supports both single-cluster and multi-cluster configurations with various authentication methods including IAM roles, basic authentication, and AWS credentials.

This implementation specifically uses:
- Multi-mode configuration for connecting to multiple OpenSearch clusters
- Stream transport (SSE/HTTP streaming) for communication

## Files

- `Dockerfile`: Container definition for the OpenSearch MCP Server
- `cluster.yaml`: Configuration file defining multiple OpenSearch clusters with different authentication methods

## Multi-Mode Support

Multi-mode allows the MCP server to connect to multiple OpenSearch clusters simultaneously. Each cluster is defined in the `cluster.yaml` file with its own connection and authentication parameters.

Benefits of multi-mode:
- Connect to multiple clusters with different authentication methods
- All tools are available regardless of OpenSearch version
- Full tool schemas with all parameters exposed
- LLMs can specify which cluster to use for each operation via the `opensearch_cluster_name` parameter

## Stream Transport

The server uses stream transport (SSE/HTTP streaming) which provides:
- Real-time data streaming
- Efficient communication between the AI agent and OpenSearch
- Support for both SSE and HTTP streaming protocols

## Authentication Methods

The sample configuration demonstrates multiple authentication methods:

1. **No Authentication**: For clusters without authentication requirements
2. **Basic Authentication**: Username and password authentication
3. **AWS Credentials**: Using AWS access keys
4. **IAM Role Authentication**: Using AWS IAM roles
5. **OpenSearch Serverless**: For AWS OpenSearch Serverless collections

## Usage

### Building the Docker Image

```bash
docker build -t opensearch-mcp-server .
```

### Running the Container

```bash
docker run -p 9900:9900 opensearch-mcp-server
```

### Connecting to the Server

The MCP server will be available at:
- Host: localhost (or your Docker host IP)
- Port: 9900

### Using with AI Agents

When making requests to the OpenSearch MCP Server, AI agents need to include the `opensearch_cluster_name` parameter to specify which cluster to use for the operation.

Example:

```json
{
  "opensearch_cluster_name": "local-dev",
  "index": "my_index",
  "query": {
    "match": {
      "status": "active"
    }
  }
}
```

## Configuration

To modify the cluster configuration, edit the `cluster.yaml` file before building the Docker image.

## Environment Variables

For fallback authentication or additional configuration, you can set environment variables when running the container:

```bash
docker run -p 9900:9900 \
  -e AWS_PROFILE=my-aws-profile \
  opensearch-mcp-server
```
