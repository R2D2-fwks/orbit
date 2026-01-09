"""
ORBIT MCP Client Service - Allows ORBIT agents to consume external MCP tools

This service enables ORBIT agents to connect to and use external MCP servers
like GitHub, filesystem, web search, databases, etc.

Usage:
    from services.mcp_client import MCPClientService
    
    async def use_mcp_tools():
        service = MCPClientService()
        
        # Connect to GitHub MCP server
        await service.connect_stdio_server(
            "github",
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
        
        await service.disconnect_all()
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from dataclasses import dataclass
from loguru import logger

# MCP SDK imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp import types


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


class MCPConnection:
    """Manages a single MCP server connection."""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.session: Optional[ClientSession] = None
        self._read = None
        self._write = None
        self._exit_stack = None
        self.tools: List[Dict[str, Any]] = []
        self.resources: List[Dict[str, Any]] = []
        self.prompts: List[Dict[str, Any]] = []
    
    async def connect(self):
        """Establish connection to the MCP server."""
        from contextlib import AsyncExitStack
        
        self._exit_stack = AsyncExitStack()
        
        if self.config.transport == "stdio":
            server_params = StdioServerParameters(
                command=self.config.command,
                args=self.config.args or [],
                env=self.config.env
            )
            
            stdio_transport = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self._read, self._write = stdio_transport
            
        elif self.config.transport == "sse":
            sse_transport = await self._exit_stack.enter_async_context(
                sse_client(self.config.url, headers=self.config.headers)
            )
            self._read, self._write = sse_transport
            
        else:
            raise ValueError(f"Unsupported transport: {self.config.transport}")
        
        # Create and initialize session
        self.session = await self._exit_stack.enter_async_context(
            ClientSession(self._read, self._write)
        )
        await self.session.initialize()
        
        # Cache available capabilities
        await self._refresh_capabilities()
        
        logger.info(f"Connected to MCP server: {self.config.name}")
        logger.info(f"  Tools: {len(self.tools)}")
        logger.info(f"  Resources: {len(self.resources)}")
        logger.info(f"  Prompts: {len(self.prompts)}")
    
    async def _refresh_capabilities(self):
        """Refresh the list of available tools, resources, and prompts."""
        # Get tools
        tools_result = await self.session.list_tools()
        self.tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in tools_result.tools
        ]
        
        # Get resources (if supported)
        try:
            resources_result = await self.session.list_resources()
            self.resources = [
                {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": getattr(resource, 'description', ''),
                    "mimeType": getattr(resource, 'mimeType', '')
                }
                for resource in resources_result.resources
            ]
        except Exception:
            self.resources = []
        
        # Get prompts (if supported)
        try:
            prompts_result = await self.session.list_prompts()
            self.prompts = [
                {
                    "name": prompt.name,
                    "description": getattr(prompt, 'description', ''),
                    "arguments": [
                        {"name": arg.name, "description": getattr(arg, 'description', ''), "required": getattr(arg, 'required', False)}
                        for arg in getattr(prompt, 'arguments', [])
                    ]
                }
                for prompt in prompts_result.prompts
            ]
        except Exception:
            self.prompts = []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Any:
        """Call a tool on the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        result = await self.session.call_tool(tool_name, arguments or {})
        
        # Parse the result
        response_parts = []
        for content in result.content:
            if isinstance(content, types.TextContent):
                response_parts.append(content.text)
            elif isinstance(content, types.ImageContent):
                response_parts.append(f"[Image: {content.mimeType}]")
            elif isinstance(content, types.EmbeddedResource):
                response_parts.append(f"[Resource: {content.resource.uri}]")
        
        return "\n".join(response_parts)
    
    async def read_resource(self, uri: str) -> str:
        """Read a resource from the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        result = await self.session.read_resource(uri)
        
        response_parts = []
        for content in result.contents:
            if hasattr(content, 'text'):
                response_parts.append(content.text)
            elif hasattr(content, 'blob'):
                response_parts.append(f"[Binary data: {len(content.blob)} bytes]")
        
        return "\n".join(response_parts)
    
    async def get_prompt(self, prompt_name: str, arguments: Dict[str, str] = None) -> str:
        """Get a prompt from the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        result = await self.session.get_prompt(prompt_name, arguments or {})
        
        response_parts = []
        for message in result.messages:
            role = message.role
            if hasattr(message.content, 'text'):
                response_parts.append(f"[{role}]: {message.content.text}")
        
        return "\n".join(response_parts)
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self._exit_stack:
            await self._exit_stack.aclose()
            self.session = None
            self._read = None
            self._write = None
            logger.info(f"Disconnected from MCP server: {self.config.name}")


class MCPClientService:
    """
    Service for managing multiple MCP server connections within ORBIT.
    
    This service allows ORBIT agents to dynamically connect to and use
    external MCP servers for enhanced capabilities.
    """
    
    def __init__(self):
        self.connections: Dict[str, MCPConnection] = {}
    
    async def connect_stdio_server(
        self,
        name: str,
        command: str,
        args: List[str] = None,
        env: Dict[str, str] = None
    ) -> MCPConnection:
        """
        Connect to an MCP server via stdio transport.
        
        Args:
            name: A unique name for this connection
            command: The command to run (e.g., "python", "npx", "node")
            args: Command arguments
            env: Environment variables
        
        Returns:
            The MCPConnection object
        """
        config = MCPServerConfig(
            name=name,
            transport="stdio",
            command=command,
            args=args or [],
            env=env
        )
        
        connection = MCPConnection(config)
        await connection.connect()
        self.connections[name] = connection
        return connection
    
    async def connect_sse_server(
        self,
        name: str,
        url: str,
        headers: Dict[str, str] = None
    ) -> MCPConnection:
        """
        Connect to an MCP server via SSE transport.
        
        Args:
            name: A unique name for this connection
            url: The server URL (e.g., "http://localhost:8000/sse")
            headers: HTTP headers to include
        
        Returns:
            The MCPConnection object
        """
        config = MCPServerConfig(
            name=name,
            transport="sse",
            url=url,
            headers=headers
        )
        
        connection = MCPConnection(config)
        await connection.connect()
        self.connections[name] = connection
        return connection
    
    def get_connection(self, name: str) -> Optional[MCPConnection]:
        """Get a connection by name."""
        return self.connections.get(name)
    
    async def list_tools(self, connection_name: str = None) -> Dict[str, List[Dict]]:
        """
        List available tools from MCP servers.
        
        Args:
            connection_name: Specific connection name, or None for all
        
        Returns:
            Dict mapping connection names to their tools
        """
        result = {}
        
        if connection_name:
            if connection_name in self.connections:
                result[connection_name] = self.connections[connection_name].tools
        else:
            for name, conn in self.connections.items():
                result[name] = conn.tools
        
        return result
    
    async def call_tool(
        self,
        connection_name: str,
        tool_name: str,
        arguments: Dict[str, Any] = None
    ) -> str:
        """
        Call a tool on a specific MCP server.
        
        Args:
            connection_name: The connection to use
            tool_name: Name of the tool to call
            arguments: Tool arguments
        
        Returns:
            The tool's response
        """
        connection = self.connections.get(connection_name)
        if not connection:
            raise ValueError(f"No connection named: {connection_name}")
        
        return await connection.call_tool(tool_name, arguments)
    
    async def read_resource(self, connection_name: str, uri: str) -> str:
        """Read a resource from an MCP server."""
        connection = self.connections.get(connection_name)
        if not connection:
            raise ValueError(f"No connection named: {connection_name}")
        
        return await connection.read_resource(uri)
    
    async def disconnect(self, connection_name: str):
        """Disconnect from a specific MCP server."""
        connection = self.connections.pop(connection_name, None)
        if connection:
            await connection.disconnect()
    
    async def disconnect_all(self):
        """Disconnect from all MCP servers."""
        for name in list(self.connections.keys()):
            await self.disconnect(name)


# ============================================================================
# Pre-configured MCP server definitions
# ============================================================================

# Common MCP servers that can be easily connected
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


async def create_preconfigured_connection(
    service: MCPClientService,
    server_name: str,
    env: Dict[str, str] = None,
    extra_args: List[str] = None
) -> MCPConnection:
    """
    Create a connection to a pre-configured MCP server.
    
    Args:
        service: The MCPClientService instance
        server_name: Name from COMMON_MCP_SERVERS
        env: Environment variables (merges with defaults)
        extra_args: Additional command arguments
    
    Returns:
        The MCPConnection object
    """
    if server_name not in COMMON_MCP_SERVERS:
        raise ValueError(f"Unknown server: {server_name}. Available: {list(COMMON_MCP_SERVERS.keys())}")
    
    config = COMMON_MCP_SERVERS[server_name]
    args = config["args"].copy()
    if extra_args:
        args.extend(extra_args)
    
    return await service.connect_stdio_server(
        name=server_name,
        command=config["command"],
        args=args,
        env=env
    )


# ============================================================================
# Example usage and testing
# ============================================================================

async def example_usage():
    """Example demonstrating MCP client usage within ORBIT."""
    import os
    
    service = MCPClientService()
    
    try:
        # Connect to filesystem server with a specific directory
        # The last argument is the allowed directory
        await service.connect_stdio_server(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        )
        
        # List available tools
        tools = await service.list_tools("filesystem")
        print("Available filesystem tools:")
        for tool in tools.get("filesystem", []):
            print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
        
        # Connect to GitHub if token is available
        github_token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
        if github_token:
            await service.connect_stdio_server(
                name="github",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token}
            )
            
            # List GitHub tools
            github_tools = await service.list_tools("github")
            print("\nAvailable GitHub tools:")
            for tool in github_tools.get("github", []):
                print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
            
            # Example: Search repositories
            result = await service.call_tool(
                "github",
                "search_repositories",
                {"query": "thespian actor python", "max_results": 5}
            )
            print(f"\nGitHub search result:\n{result}")
        
    finally:
        await service.disconnect_all()


if __name__ == "__main__":
    asyncio.run(example_usage())
