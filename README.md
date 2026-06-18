# example-mcp

MCP server demo — CRUD SQLite with FastMCP.

## Setup

```bash
source .venv/bin/activate
uv sync
```

## MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run python server.py
```

## MCP Http Transport
```bash
# Run Server
fastmcp run server.py:mcp --transport http --port 8080

# in .mcp.json
 "sqlite-crud-http": {
      "url": "http://localhost:8000/mcp"
    }
```

## Tools

| Tool | Action |
|------|--------|
| `create_item` | Add new item |
| `list_items` | List / search items |
| `get_item` | Get item by ID |
| `update_item` | Update item fields |
| `delete_item` | Delete item by ID |

## Connect to Claude Code

Project includes `.mcp.json` — auto-detected by Claude Code.

## Files

```
server.py       MCP server (CRUD tools)
.mcp.json       Claude Code MCP config
pyproject.toml  Dependencies (fastmcp, aiosqlite)
```
