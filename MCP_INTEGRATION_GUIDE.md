# 🔌 MCP Integration Guide for ORBIT Framework

This guide covers how to integrate Model Context Protocol (MCP) capabilities into your ORBIT multi-agent orchestration framework.

## Table of Contents

1. [Overview](#overview)
2. [Integration Approaches](#integration-approaches)
3. [Installing MCP Dependencies](#installing-mcp-dependencies)
4. [Approach 1: ORBIT as MCP Server](#approach-1-orbit-as-mcp-server)
5. [Approach 2: ORBIT as MCP Client](#approach-2-orbit-as-mcp-client)
6. [Recommended MCP Servers](#recommended-mcp-servers)
7. [Configuration Examples](#configuration-examples)
8. [Best Practices](#best-practices)

---

## Overview

**Model Context Protocol (MCP)** is an open standard by Anthropic that standardizes how AI applications interact with external tools and data sources. It provides:

- **Tools**: Functions that perform actions (like POST endpoints)
- **Resources**: Data sources (like GET endpoints)
- **Prompts**: Reusable prompt templates

### Why Integrate MCP with ORBIT?

| Benefit | Description |
|---------|-------------|
| **Extensibility** | Access 1000+ pre-built MCP servers |
| **Standardization** | Universal protocol for tool integration |
| **Ecosystem** | Connect to GitHub, Slack, databases, browsers, etc. |
| **Interoperability** | Make ORBIT agents accessible from Claude Desktop, Cursor, VS Code |

---

## Integration Approaches

### Two-Way Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORBIT Framework                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │  ORBIT as MCP    │              │  ORBIT as MCP    │         │
│  │     SERVER       │              │     CLIENT       │         │
│  │                  │              │                  │         │
│  │  Expose agents   │              │  Use external    │         │
│  │  to Claude,      │◄────────────►│  MCP tools in    │         │
│  │  Cursor, etc.    │              │  your agents     │         │
│  └──────────────────┘              └──────────────────┘         │
│           │                                 │                    │
└───────────┼─────────────────────────────────┼────────────────────┘
            │                                 │
            ▼                                 ▼
    ┌───────────────┐              ┌───────────────────────┐
    │ Claude Desktop│              │   External MCP        │
    │ Cursor        │              │   Servers:            │
    │ VS Code       │              │   - GitHub            │
    │ Custom Apps   │              │   - Filesystem        │
    │               │              │   - Web Search        │
    └───────────────┘              │   - Databases         │
                                   └───────────────────────┘
```

---

## Installing MCP Dependencies

Add these to your `requirements.txt`:

```txt
# MCP SDK
mcp>=1.0.0

# For HTTP transport
uvicorn>=0.20.0
starlette>=0.27.0

# For async operations
httpx>=0.24.0
anyio>=3.0.0
```

Install:

```bash
pip install -r requirements.txt

# Or install MCP directly with CLI tools
pip install "mcp[cli]"
```

---

## Approach 1: ORBIT as MCP Server

This approach exposes your ORBIT agents as MCP tools that can be used by any MCP client.

### File Structure

```
orbit/
├── mcp_server/
│   ├── __init__.py      # FastMCP server implementation
│   └── __main__.py      # Entry point
├── agents/
│   └── ...
└── capabilities.json
```

### Implementation

```python
# mcp_server/__init__.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ORBIT Agent Server")

@mcp.tool()
async def query_orbit_agent(query: str, agent_type: str = "auto") -> str:
    """Send a query to ORBIT's intelligent agent system."""
    # ... implementation
    pass

@mcp.resource("orbit://documentation/{doc_type}")
def get_documentation(doc_type: str) -> str:
    """Get ORBIT framework documentation."""
    pass

@mcp.prompt()
def troubleshoot_issue(error_message: str) -> str:
    """Generate a troubleshooting prompt."""
    pass
```

### Running the Server

**Option 1: stdio transport** (for Claude Desktop)
```bash
python -m mcp_server
```

**Option 2: HTTP transport** (for web clients)
```bash
uvicorn mcp_server:mcp.asgi_app --host 0.0.0.0 --port 8000
```

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "orbit": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/orbit"
    }
  }
}
```

---

## Approach 2: ORBIT as MCP Client

This approach lets your ORBIT agents call external MCP tools.

### MCPClientService

The `MCPClientService` manages connections to external MCP servers:

```python
from services.mcp_client import MCPClientService

async def use_mcp_tools():
    service = MCPClientService()
    
    # Connect to GitHub MCP server
    await service.connect_stdio_server(
        name="github",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"}
    )
    
    # List available tools
    tools = await service.list_tools("github")
    
    # Call a tool
    result = await service.call_tool(
        "github",
        "search_repositories",
        {"query": "python actor framework"}
    )
    
    print(result)
    await service.disconnect_all()
```

### MCPToolsAgent

A specialized ORBIT agent that uses MCP tools:

```python
# In start.py
from agents.mcpToolsAgent import MCPToolsAgent

agent_registry.register_agent(
    "MCPToolsAgent",
    MCPToolsAgent,
    description="Agent with access to external MCP tools (GitHub, web, files, etc.)"
)
```

---

## Recommended MCP Servers

### Official Servers (modelcontextprotocol/servers)

| Server | Use Case | Install |
|--------|----------|---------|
| **GitHub** | Repo management, issues, PRs | `npx -y @modelcontextprotocol/server-github` |
| **Filesystem** | File operations | `npx -y @modelcontextprotocol/server-filesystem /path` |
| **Fetch** | Web content retrieval | `npx -y @modelcontextprotocol/server-fetch` |
| **Git** | Git operations | `npx -y @modelcontextprotocol/server-git` |
| **Memory** | Knowledge graph storage | `npx -y @modelcontextprotocol/server-memory` |
| **SQLite** | Database queries | `npx -y @modelcontextprotocol/server-sqlite` |
| **Puppeteer** | Browser automation | `npx -y @modelcontextprotocol/server-puppeteer` |

### Community Servers

| Server | Use Case | Source |
|--------|----------|--------|
| **Slack** | Team messaging | github.com/modelcontextprotocol/servers |
| **PostgreSQL** | Database access | github.com/modelcontextprotocol/servers |
| **Brave Search** | Web search | github.com/modelcontextprotocol/servers |
| **Docker** | Container management | github.com/appcypher/awesome-mcp-servers |
| **Kubernetes** | K8s cluster management | Various implementations |

### Finding More Servers

- **Official list**: https://github.com/modelcontextprotocol/servers
- **Awesome MCP**: https://github.com/wong2/awesome-mcp-servers
- **MCP Hub**: https://mcphub.io

---

## Configuration Examples

### Environment Variables

Create a `.env` file:

```env
# GitHub MCP server
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxx

# Existing ORBIT config
PAT_TOKEN=ghp_xxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxx
OPENAI_API_KEY=sk-xxxx
```

### MCP Server Configuration

```python
# services/mcp_client/__init__.py

COMMON_MCP_SERVERS = {
    "github": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env_required": ["GITHUB_PERSONAL_ACCESS_TOKEN"]
    },
    "filesystem": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem"],
        # Add allowed paths as extra args
    },
    "fetch": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
}
```

### Connecting to Remote/SSE Servers

```python
# For servers running on HTTP
await service.connect_sse_server(
    name="remote-tools",
    url="http://localhost:8000/sse",
    headers={"Authorization": "Bearer token"}
)
```

---

## Best Practices

### 1. Async/Actor Bridge

Since Thespian actors are synchronous but MCP is async, use this pattern:

```python
class MCPEnabledAgent(Actor):
    def _run_async(self, coro):
        """Run async code from sync actor context."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def receiveMessage(self, message, sender):
        result = self._run_async(self._process_async(message))
        self.send(sender, result)
```

### 2. Connection Lifecycle

```python
class MCPToolsAgent(Actor):
    def __init__(self):
        super().__init__()
        self.mcp_service = None  # Initialize lazily
    
    async def _ensure_connected(self):
        if self.mcp_service is None:
            self.mcp_service = MCPClientService()
            await self._connect_servers()
    
    def receiveMessage(self, message, sender):
        # Actor exit handling
        if isinstance(message, ActorExitRequest):
            if self.mcp_service:
                self._run_async(self.mcp_service.disconnect_all())
```

### 3. Error Handling

```python
async def _call_tool_safely(self, server, tool, args):
    try:
        return await self.mcp_service.call_tool(server, tool, args)
    except ConnectionError:
        logger.warning(f"MCP server {server} disconnected, reconnecting...")
        await self._reconnect(server)
        return await self.mcp_service.call_tool(server, tool, args)
    except Exception as e:
        logger.error(f"Tool call failed: {e}")
        return f"Error: {str(e)}"
```

### 4. Tool Selection with LLM

Let your LLM decide which tools to use:

```python
def _get_tool_selection_prompt(self, query: str, available_tools: list) -> str:
    return f"""Given this query: {query}

Available MCP tools:
{json.dumps(available_tools, indent=2)}

Which tools should be called? Return JSON:
{{"tools": [{{"server": "...", "tool": "...", "args": {{}}}}]}}
"""
```

---

## Integrating with Existing ORBIT Flow

### Update IntentAgent Guidelines

Add MCPToolsAgent to the intent detection:

```markdown
**MCPToolsAgent Indicators:**
- Requests involving external services (GitHub, web, files)
- "Search GitHub for...", "Fetch this URL...", "Look up..."
- Queries requiring real-time external data
- Browser automation requests
```

### Register in start.py

```python
from agents.mcpToolsAgent import MCPToolsAgent

agent_registry.register_agent(
    "MCPToolsAgent",
    MCPToolsAgent,
    description="Agent with access to external MCP tools including GitHub, web fetch, file operations, and more."
)
```

---

## Next Steps

1. **Install MCP SDK**: `pip install "mcp[cli]"`
2. **Test with MCP Inspector**: `mcp dev mcp_server/__init__.py`
3. **Add MCP servers** based on your needs
4. **Register MCPToolsAgent** in your ORBIT system
5. **Update intent detection** to route appropriate queries

For questions or issues, refer to:
- MCP Documentation: https://modelcontextprotocol.io
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- ORBIT README: ./README.md
