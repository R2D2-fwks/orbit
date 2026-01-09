"""
MCPToolsAgent - An ORBIT agent that can use external MCP tools

This agent demonstrates how to integrate MCP client capabilities into
ORBIT's actor-based architecture, allowing agents to call external
MCP servers (GitHub, filesystem, web search, etc.)

The agent uses async/await patterns bridged with Thespian's actor model.
"""

from pathlib import Path
import asyncio
import json
from typing import Dict, Any, List, Optional
from thespian.actors import Actor
from loguru import logger

from messages.intent_agent_message import IntentAgentMessage
from messages.llm_message import LLMMessage
from model.llama_model import LlamaModel
from model.model_adapter import ModelAdapter
from services.file import FileService


class MCPToolRequest:
    """Message to request an MCP tool call."""
    def __init__(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any] = None
    ):
        self.server_name = server_name
        self.tool_name = tool_name
        self.arguments = arguments or {}


class MCPToolResponse:
    """Response from an MCP tool call."""
    def __init__(self, result: str, success: bool = True, error: str = None):
        self.result = result
        self.success = success
        self.error = error


class MCPToolsAgent(Actor):
    """
    An ORBIT agent with MCP tool capabilities.
    
    This agent can:
    1. Receive queries and determine which MCP tools to use
    2. Connect to external MCP servers
    3. Call MCP tools and integrate results into responses
    4. Use LLM to synthesize final responses
    
    Example MCP tools this agent can use:
    - GitHub: Search repos, get issues, analyze code
    - Filesystem: Read/write files, search directories
    - Fetch: Get web content
    - Memory: Store/retrieve knowledge
    """
    
    def __init__(self):
        super().__init__()
        self.model = ModelAdapter(LlamaModel())
        self.agent_name = "MCPToolsAgent"
        self.mcp_service = None
        self._loop = None
        
        # MCP servers this agent can use
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
    
    async def _initialize_mcp_service(self):
        """Initialize MCP client service with configured servers."""
        from services.mcp_client import MCPClientService
        import os
        
        if self.mcp_service is None:
            self.mcp_service = MCPClientService()
        
        # Connect to available MCP servers based on environment
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
                logger.info("[MCPToolsAgent] Connected to GitHub MCP server")
            except Exception as e:
                logger.warning(f"[MCPToolsAgent] Could not connect to GitHub: {e}")
        
        # Fetch server (no auth required)
        try:
            await self.mcp_service.connect_stdio_server(
                name="fetch",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-fetch"]
            )
            connected_servers.append("fetch")
            logger.info("[MCPToolsAgent] Connected to Fetch MCP server")
        except Exception as e:
            logger.warning(f"[MCPToolsAgent] Could not connect to Fetch: {e}")
        
        return connected_servers
    
    async def _call_mcp_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> str:
        """Call an MCP tool and return the result."""
        if self.mcp_service is None:
            await self._initialize_mcp_service()
        
        connection = self.mcp_service.get_connection(server_name)
        if not connection:
            return f"Error: MCP server '{server_name}' is not connected"
        
        try:
            result = await connection.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"[MCPToolsAgent] Error calling {server_name}.{tool_name}: {e}")
            return f"Error calling tool: {str(e)}"
    
    def _analyze_query_for_tools(self, query: str) -> List[Dict[str, Any]]:
        """
        Analyze the query to determine which MCP tools might be helpful.
        
        Returns a list of suggested tool calls.
        """
        tool_suggestions = []
        query_lower = query.lower()
        
        # GitHub-related queries
        if any(kw in query_lower for kw in ["github", "repo", "repository", "code", "issue", "pr", "pull request"]):
            if "search" in query_lower or "find" in query_lower:
                tool_suggestions.append({
                    "server": "github",
                    "tool": "search_repositories",
                    "reason": "Search GitHub repositories"
                })
            if "issue" in query_lower:
                tool_suggestions.append({
                    "server": "github",
                    "tool": "list_issues",
                    "reason": "List repository issues"
                })
        
        # Web content queries
        if any(kw in query_lower for kw in ["fetch", "website", "webpage", "url", "http", "download"]):
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
    
    def _build_tool_context(self, tool_results: Dict[str, str]) -> str:
        """Build context string from MCP tool results."""
        if not tool_results:
            return ""
        
        context_parts = ["## MCP Tool Results\n"]
        for tool_call, result in tool_results.items():
            context_parts.append(f"### {tool_call}\n{result}\n")
        
        return "\n".join(context_parts)
    
    async def _process_query_async(self, query: str) -> str:
        """Process query asynchronously with MCP tools."""
        # Initialize MCP connections
        connected = await self._initialize_mcp_service()
        logger.info(f"[MCPToolsAgent] Connected MCP servers: {connected}")
        
        # Analyze query for potential tool usage
        tool_suggestions = self._analyze_query_for_tools(query)
        tool_results = {}
        
        # Execute suggested tools
        for suggestion in tool_suggestions:
            server = suggestion["server"]
            tool = suggestion["tool"]
            
            if server in connected:
                logger.info(f"[MCPToolsAgent] Calling {server}.{tool}")
                
                # Build arguments based on tool type
                arguments = {}
                if tool == "search_repositories":
                    # Extract search query from user query
                    arguments = {"query": query, "max_results": 5}
                elif tool == "fetch":
                    # Try to extract URL from query
                    import re
                    urls = re.findall(r'https?://[^\s]+', query)
                    if urls:
                        arguments = {"url": urls[0]}
                
                if arguments:
                    result = await self._call_mcp_tool(server, tool, arguments)
                    tool_results[f"{server}.{tool}"] = result
        
        # Build context from tool results
        tool_context = self._build_tool_context(tool_results)
        
        # Load agent instructions
        file_path = Path(__file__).parent
        instructions = FileService().read_file(file_path / "mcpToolsAgentGuidelines.md")
        
        # Build complete prompt
        complete_prompt = f"""User Query: {query}

{tool_context}

Based on the user's query and any MCP tool results above, provide a helpful response.
"""
        
        # Generate response using LLM
        response = self.model.generate(prompt=complete_prompt, instruction=instructions)
        
        # Cleanup MCP connections
        if self.mcp_service:
            await self.mcp_service.disconnect_all()
        
        return response
    
    def receiveMessage(self, message, sender):
        """Handle incoming messages."""
        if isinstance(message, IntentAgentMessage):
            query = message.query
            logger.info(f"[{self.agent_name}] Received query: {query}")
            
            try:
                # Run async processing
                response_text = self._run_async(self._process_query_async(query))
                response = LLMMessage(response_text)
                self.send(sender, response)
            except Exception as e:
                logger.error(f"[{self.agent_name}] Error processing query: {e}")
                self.send(sender, LLMMessage(f"Error processing query: {str(e)}"))
        
        elif isinstance(message, MCPToolRequest):
            # Direct MCP tool call
            logger.info(f"[{self.agent_name}] Received MCP tool request: {message.server_name}.{message.tool_name}")
            
            try:
                result = self._run_async(
                    self._call_mcp_tool(
                        message.server_name,
                        message.tool_name,
                        message.arguments
                    )
                )
                self.send(sender, MCPToolResponse(result=result, success=True))
            except Exception as e:
                logger.error(f"[{self.agent_name}] Error calling MCP tool: {e}")
                self.send(sender, MCPToolResponse(
                    result="",
                    success=False,
                    error=str(e)
                ))
        
        else:
            self.send(sender, f"Unknown message type for {self.agent_name}")
