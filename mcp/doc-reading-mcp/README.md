# Document Reading and Converter Tool

The goal is to have a tool that can read and edit files, using Cursor or Claude Desktop.

The `filesystem` MCP already allows reading, writing and editing documents, but is limited in that it cannot:

- Read pdfs or docx files
- Reads the full document, which can cause context overflow

To address these issues, we create:

- A fresh `doc-reading-mcp` mcp service allowing for document conversions between pdf, docx and markdown.

## Features

- PDF to Markdown conversion using marker-pdf
- DOCX to Markdown conversion using pandoc
- Markdown to DOCX conversion using pandoc
- Markdown to PDF conversion using pandoc

## Prerequisites

- Python 3.10 or higher
- [pandoc] (https://pandoc.org/installing.html) installed on your system
- [uv] (https://docs.astral.sh/uv/) for Python package management 

# Installation

```bash
uv add doc-reading-mcp
```

Or install directly from the source:

```bash
uv add git+https://github.com/mffrydman/doc-reading-mcp.git
```

# Usage

## Run as a standalone server

```bash
uv run mcp install -m doc_reading_mcp
```

Or run directly:

```bash
uv run -m doc_reading_mcp
```

## Use with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uvx run -m doc_reading_mcp
```

## Configure in Claude Desktop, Cursor or Windsurf

Add this to your MCP Configuration:

```json
{
    "mcpServers": {
        "doc-reading-mcp": {
            "command": "uvx",
            "args": [
                "doc-reading-mcp",
            ]
        }
    }
}
```

Run in Cursor/Windsurf/Claude using the following configuration:
```json
    "doc-reading-mcp": {
        "command": "uv",
        "args": [
            "--directory",
            "/absolute/path/to/mffrydman/doc-reading-mcp",
            "run",
            "-m",
            "doc_reading_mcp"
        ]
    }
```

Replace
- `/absolute/path/to/` with the actual path on your system.