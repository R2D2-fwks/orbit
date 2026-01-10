"""
ORBIT MCP Server - Exposes ORBIT agents as MCP tools

This module creates an MCP server that allows external MCP clients (like Claude Desktop,
Cursor, VS Code) to interact with ORBIT's specialized agents.

Usage:
    python -m mcp_server
    
Or via uvicorn for HTTP transport:
    uvicorn mcp_server:app --host 0.0.0.0 --port 8000
"""

from mcp.server.fastmcp import FastMCP, Context
from pathlib import Path
import json
import asyncio
from typing import Optional
from loguru import logger
from src.actor_system import start_actor_system
from src.agent_registry import register_agents
from src.services.repo2Text import Repo2TextService
import concurrent.futures
from src.agents.agentRegistry import AgentRegistry


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
        agent_type: One of "auto", "troubleshooting", "orbit", or "intent"
                   - auto: Let IntentAgent decide the best agent
                   - troubleshooting: Technical debugging and code analysis
                   - orbit: Framework/toolkit questions
                   - intent: Just classify the intent without processing
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


@mcp.prompt()
def troubleshoot_issue(
    error_message: str,
    repo_urls: str = "",
    context: str = ""
) -> str:
    """
    Generate a prompt for troubleshooting technical issues.
    
    Args:
        error_message: The error or issue description
        repo_urls: Comma-separated list of repository URLs (optional)
        context: Additional context about the issue
    """
    prompt = f"""I need help troubleshooting the following issue:**Error/Issue:**{error_message}"""
    if repo_urls:
        prompt += f"""**Related Repositories:**{repo_urls}"""
    if context:
        prompt += f"""**Additional Context:**{context}"""
    prompt += "Please analyze this issue and provide a detailed troubleshooting plan."
    return prompt


@mcp.prompt()
def create_custom_agent(
    agent_purpose: str,
    capabilities: str = ""
) -> str:
    """
    Generate a prompt for creating a custom ORBIT agent.
    
    Args:
        agent_purpose: What the new agent should do
        capabilities: Specific capabilities the agent needs
    """
    return f"""I want to create a custom agent in ORBIT for the following purpose:

**Purpose:** {agent_purpose}

**Required Capabilities:** {capabilities if capabilities else "Not specified"}

Please provide:
1. The complete agent implementation code
2. The agent guidelines/instructions markdown file
3. How to register the agent in start.py
4. Example queries this agent should handle
"""


# Entry point for running the server
if __name__ == "__main__":
    # Run with stdio transport
    mcp.run(transport="stdio")