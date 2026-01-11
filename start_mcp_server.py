"""
ORBIT MCP Server - Exposes ORBIT agents as MCP tools

This module creates an MCP server that allows external MCP clients (like Claude Desktop,
Cursor, VS Code) to interact with ORBIT's specialized agents.

Usage:
    python -m mcp_server
    
Or via uvicorn for HTTP transport:
    uvicorn mcp_server:app --host 0.0.0.0 --port 8000
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
from typing import Optional
from loguru import logger
from src.actor_system import start_actor_system


# Initialize FastMCP server
mcp = FastMCP(
    "ORBIT Server"
)


# ============================================================================
# MCP Tools - These expose ORBIT's capabilities to MCP clients
# ============================================================================

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
    
    # Build the complete query with context if provided
    complete_query = query
    if context:
        complete_query = f"{query}\n\nAdditional Context:\n{context}"
    try:
        response = start_actor_system(complete_query)
        return response
    except Exception as e:
        logger.error(f"Error in query_orbit_agent: {e}")
        return f"Error processing query: {str(e)}"

# Entry point for running the server
if __name__ == "__main__":
    # Run with stdio transport
    mcp.run(transport="stdio")