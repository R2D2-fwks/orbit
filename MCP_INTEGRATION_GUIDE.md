# 🔌 MCP Integration Guide for ORBIT Framework

This guide covers how to integrate Model Context Protocol (MCP) capabilities into your ORBIT multi-agent orchestration framework.

## Table of Contents

1. [Overview](#overview)
2. [Integration Approaches](#integration-approaches)
3. [Installing MCP Dependencies](#installing-mcp-dependencies)
4. [Approach 1: ORBIT as MCP Server](#approach-1-orbit-as-mcp-server)
5. [Approach 2: ORBIT as MCP Client](#approach-2-orbit-as-mcp-client)
6. [MCPToolsAgent](#mcptoolsagent)
7. [Recommended MCP Servers](#recommended-mcp-servers)
8. [Configuration Examples](#configuration-examples)
9. [Best Practices](#best-practices)
10. [File Structure](#file-structure)

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

MCP dependencies are already included in `requirements.txt`:

```txt
# MCP SDK (already installed)
mcp==1.25.0

# For HTTP transport (already installed)
uvicorn==0.40.0
starlette==0.50.0

# For async operations (already installed)
httpx==0.28.1
httpx-sse==0.4.3
anyio==4.11.0
```

Install all dependencies:

```bash
pip install -r requirements.txt

```

---

## Approach 1: ORBIT as MCP Server

This approach exposes your ORBIT agents as MCP tools that can be used by any MCP client.

### File Location

The MCP server is implemented in `start_mcp_server.py` at the project root:

```
rbi/
├── start_mcp_server.py    # FastMCP server implementation
├── start.py               # CLI entry point
├── src/
│   └── agents/
│       └── ...
└── capabilities.json
```

### Current Implementation

```python
# start_mcp_server.py
from mcp.server.fastmcp import FastMCP
from src.actor_system import start_actor_system

mcp = FastMCP("ORBIT Server")

@mcp.tool()
async def query_orbit_agent(
    query: str,
    context: Optional[str] = None
) -> str:
    """
    Send a query to ORBIT's intelligent agent system.
    The query will be automatically routed to the appropriate specialized agent
    based on intent detection, or you can specify a specific agent type.
    
    Args:
        query: The user's question or request
        context: Optional additional context (e.g., repository URLs, code snippets)
    Returns:
        The agent's response to the query
    """
    complete_query = query
    if context:
        complete_query = f"{query}\n\nAdditional Context:\n{context}"
    
    response = start_actor_system(complete_query)
    return response

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Running the Server

**Option 1: stdio transport** (for Claude Desktop, Cursor, VS Code)
```bash
python start_mcp_server.py
```

**Option 2: HTTP transport** (for web clients)
```bash
uvicorn start_mcp_server:mcp.asgi_app --host 0.0.0.0 --port 8000
```

### Claude Desktop Configuration

Add to `~/Library/Application Support/VsCode/mcp.json` (macOS):

```json
{
  "servers": {
    "orbit": {
      "command": "conda",
      "args": ["run", "-n", "actorenv", "--no-capture-output", "python", "-u", "start_mcp_server.py"],
      "cwd": "/path/to/code",
      "env": {
        "PAT_TOKEN":"TOKEN"
        "PYTHONUNBUFFERED": "1",
		"DEFAULT_TIMEOUT": "300",
		"IS_LOCAL":"True"
      }
    }
  }
}
```

---

## Approach 2: ORBIT as MCP Client

This approach lets your ORBIT agents call external MCP tools.

### MCPClientService

The `MCPClientService` in `src/services/mcp_client/__init__.py` manages connections to external MCP servers:

```python
from src.services.mcp_client import MCPClientService

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
        {"query": "thespian actor python"}
    )
    
    # Read a resource (if supported)
    # resource = await service.read_resource("github", "repo://owner/repo/file.py")
    
    await service.disconnect_all()
```

### MCPServerConfig

The `MCPServerConfig` dataclass defines server configurations:

```python
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server connection."""
    name: str
    transport: str  # "stdio" or "sse" or "streamable-http"
    command: Optional[str] = None  # For stdio
    args: Optional[List[str]] = None  # For stdio
    env: Optional[Dict[str, str]] = None  # For stdio
    url: Optional[str] = None  # For SSE/HTTP
    headers: Optional[Dict[str, str]] = None  # For SSE/HTTP
```

### MCPConnection

The `MCPConnection` class manages individual server connections and caches capabilities:

```python
class MCPConnection:
    """Manages a single MCP server connection."""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.session: Optional[ClientSession] = None
        self.tools: List[Dict[str, Any]] = []      # Cached tools
        self.resources: List[Dict[str, Any]] = []  # Cached resources
        self.prompts: List[Dict[str, Any]] = []    # Cached prompts
    
    async def connect(self):
        """Establish connection to the MCP server."""
        # ... establishes connection and caches capabilities
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        # ... returns tool result
    
    async def read_resource(self, uri: str) -> str:
        """Read a resource from the MCP server."""
        # ... returns resource content
    
    async def get_prompt(self, prompt_name: str, arguments: Dict[str, str]) -> str:
        """Get a prompt from the MCP server."""
        # ... returns prompt content
```

---

## MCPToolsAgent

A specialized ORBIT agent that integrates MCP tools with the actor-based architecture.

### Location

`src/agents/mcpToolsAgent/__init__.py`

### Features

The MCPToolsAgent can:
1. **Receive queries** and determine which MCP tools to use
2. **Connect to external MCP servers** (GitHub, Fetch, Filesystem, etc.)
3. **Call MCP tools** and integrate results into responses
4. **Use LLM** to synthesize final responses

### Available MCP Servers

```python
self.available_servers = {
    "github": {
        "description": "GitHub API - search repos, get issues, PRs, code",
        "tools": ["search_repositories", "get_file_contents", "search_code", 
                 "list_issues", "create_issue", "get_pull_request"]
    },
    "filesystem": {
        "description": "File operations - read, write, search files",
        "tools": ["read_file", "write_file", "list_directory", "search_files"]
    },
    "fetch": {
        "description": "Web content - fetch and convert web pages",
        "tools": ["fetch"]
    },
    "memory": {
        "description": "Knowledge storage - store and retrieve information",
        "tools": ["create_entities", "search_nodes", "read_graph"]
    }
}
```

### Message Types

```python
class MCPToolRequest:
    """Message to request an MCP tool call."""
    def __init__(self, server_name: str, tool_name: str, arguments: Dict[str, Any] = None):
        self.server_name = server_name
        self.tool_name = tool_name
        self.arguments = arguments or {}

class MCPToolResponse:
    """Response from an MCP tool call."""
    def __init__(self, result: str, success: bool = True, error: str = None):
        self.result = result
        self.success = success
        self.error = error
```

### Registering MCPToolsAgent

To add MCPToolsAgent to your ORBIT system, update `src/agent_registry/__init__.py`:

```python
from src.agent_registry.register import AgentRegistry
from src.agents.orbitAgent import OrbitAgent
from src.agents.troubleshootingAgent import TroubleshootingAgent
from src.agents.mcpToolsAgent import MCPToolsAgent  # Add import

def register_agents():
    agent_registry = AgentRegistry()
    
    agent_registry.register_agent(
        "TroubleshootingAgent", 
        TroubleshootingAgent,
        description="Agent specialized in troubleshooting technical issues."
    )
    agent_registry.register_agent(
        "OrbitAgent", 
        OrbitAgent,
        description="Agent specialized in handling framework related queries."
    )
    # Add MCPToolsAgent registration
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

### Pre-configured Servers in MCPClientService

The `COMMON_MCP_SERVERS` dictionary in `src/services/mcp_client/__init__.py` provides ready-to-use configurations:

```python
COMMON_MCP_SERVERS = {
    "github": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env_required": ["GITHUB_PERSONAL_ACCESS_TOKEN"],
        "description": "GitHub API integration for repositories, issues, PRs"
    },
    "filesystem": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem"],
        "description": "Secure file operations with configurable access"
    },
    "git": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-git"],
        "description": "Git repository operations"
    },
    "fetch": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-fetch"],
        "description": "Web content fetching and conversion"
    },
    "memory": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"],
        "description": "Knowledge graph-based persistent memory"
    },
    "sqlite": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite"],
        "description": "SQLite database interaction"
    },
    "puppeteer": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "description": "Browser automation and web scraping"
    }
}
```

### Using Pre-configured Servers

```python
from src.services.mcp_client import MCPClientService, create_preconfigured_connection

async def connect_preconfigured():
    service = MCPClientService()
    
    # Connect using pre-configured settings
    await create_preconfigured_connection(
        service,
        server_name="github",
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"}
    )
    
    # For filesystem, add extra args for allowed directories
    await create_preconfigured_connection(
        service,
        server_name="filesystem",
        extra_args=["/path/to/allowed/directory"]
    )
```

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

> **Note**: MCPToolsAgent checks for both `GITHUB_PERSONAL_ACCESS_TOKEN` and `PAT_TOKEN` for GitHub authentication.

### MCP Server Configuration

Server configurations are defined in `src/services/mcp_client/__init__.py` using the `COMMON_MCP_SERVERS` dictionary. See the [Pre-configured Servers](#pre-configured-servers-in-mcpclientservice) section above.

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

Since Thespian actors are synchronous but MCP is async, the MCPToolsAgent uses this pattern:

```python
class MCPToolsAgent(Actor):
    def _get_event_loop(self):
        """Get or create an event loop for async operations."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def _run_async(self, coro):
        """Run an async coroutine from sync context."""
        loop = self._get_event_loop()
        return loop.run_until_complete(coro)
    
    def receiveMessage(self, message, sender):
        result = self._run_async(self._process_query_async(message.query))
        self.send(sender, LLMMessage(result))
```

### 2. Connection Lifecycle

The MCPToolsAgent uses lazy initialization for MCP connections:

```python
class MCPToolsAgent(Actor):
    def __init__(self):
        super().__init__()
        self.mcp_service = None  # Initialize lazily
    
    async def _initialize_mcp_service(self):
        """Initialize MCP client service with configured servers."""
        from src.services.mcp_client import MCPClientService
        import os
        
        if self.mcp_service is None:
            self.mcp_service = MCPClientService()
        
        connected_servers = []
        
        # GitHub server (requires token)
        github_token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or \
                       os.environ.get("PAT_TOKEN")
        if github_token:
            try:
                await self.mcp_service.connect_stdio_server(
                    name="github",
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-github"],
                    env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token}
                )
                connected_servers.append("github")
            except Exception as e:
                logger.warning(f"Could not connect to GitHub: {e}")
        
        # Fetch server (no auth required)
        try:
            await self.mcp_service.connect_stdio_server(
                name="fetch",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-fetch"]
            )
            connected_servers.append("fetch")
        except Exception as e:
            logger.warning(f"Could not connect to Fetch: {e}")
        
        return connected_servers
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

### 4. Tool Selection with Query Analysis

The MCPToolsAgent analyzes queries to determine which tools to use:

```python
def _analyze_query_for_tools(self, query: str) -> List[Dict[str, Any]]:
    """Analyze the query to determine which MCP tools might be helpful."""
    tool_suggestions = []
    query_lower = query.lower()
    
    # GitHub-related queries
    if any(kw in query_lower for kw in ["github", "repo", "repository", "code", "issue", "pr"]):
        if "search" in query_lower or "find" in query_lower:
            tool_suggestions.append({
                "server": "github",
                "tool": "search_repositories",
                "reason": "Search GitHub repositories"
            })
    
    # Web content queries
    if any(kw in query_lower for kw in ["fetch", "website", "webpage", "url", "http"]):
        tool_suggestions.append({
            "server": "fetch",
            "tool": "fetch",
            "reason": "Fetch web content"
        })
    
    # File-related queries
    if any(kw in query_lower for kw in ["file", "read", "write", "directory", "folder"]):
        tool_suggestions.append({
            "server": "filesystem",
            "tool": "read_file" if "read" in query_lower else "list_directory",
            "reason": "File system operations"
        })
    
    return tool_suggestions
```

---

## File Structure

Here's the complete MCP-related file structure in the ORBIT project:

```
rbi/
├── start_mcp_server.py           # ORBIT as MCP Server (FastMCP)
├── start.py                      # CLI entry point
├── requirements.txt              # Includes mcp==1.25.0
├── MCP_INTEGRATION_GUIDE.md      # This guide
├── src/
│   ├── services/
│   │   └── mcp_client/
│   │       └── __init__.py       # MCPClientService, MCPConnection, COMMON_MCP_SERVERS
│   └── agents/
│       └── mcpToolsAgent/
│           ├── __init__.py       # MCPToolsAgent actor implementation
│           └── mcpToolsAgentGuidelines.md  # Agent instructions
```

---

## Integrating with Existing ORBIT Flow

### Update IntentAgent Guidelines

Add MCPToolsAgent to the intent detection in `src/agents/intentAgent/intentAgentGuidelines.md`:

```markdown
**MCPToolsAgent Indicators:**
- Requests involving external services (GitHub, web, files)
- "Search GitHub for...", "Fetch this URL...", "Look up..."
- Queries requiring real-time external data
- Browser automation requests
```

### Register in Agent Registry

Update `src/agent_registry/__init__.py` to include MCPToolsAgent:

```python
from src.agent_registry.register import AgentRegistry
from src.agents.orbitAgent import OrbitAgent
from src.agents.troubleshootingAgent import TroubleshootingAgent
from src.agents.mcpToolsAgent import MCPToolsAgent

def register_agents():
    agent_registry = AgentRegistry()
    
    agent_registry.register_agent(
        "TroubleshootingAgent", 
        TroubleshootingAgent,
        description="Agent specialized in troubleshooting technical issues."
    )
    agent_registry.register_agent(
        "OrbitAgent", 
        OrbitAgent,
        description="Agent specialized in handling framework related queries."
    )
    agent_registry.register_agent(
        "MCPToolsAgent",
        MCPToolsAgent,
        description="Agent with access to external MCP tools including GitHub, web fetch, file operations, and more."
    )
```

---

## Next Steps

1. **Install MCP SDK**: Already included - `mcp==1.25.0` in requirements.txt
2. **Test MCP Server**: `python start_mcp_server.py`
3. **Test with MCP Inspector**: `mcp dev start_mcp_server.py`
4. **Add MCP servers** based on your needs
5. **Register MCPToolsAgent** by updating `src/agent_registry/__init__.py`
6. **Update intent detection** to route appropriate queries to MCPToolsAgent

For questions or issues, refer to:
- MCP Documentation: https://modelcontextprotocol.io
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- ORBIT README: ./README.md
