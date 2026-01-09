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

# Initialize FastMCP server
mcp = FastMCP(
    "ORBIT Agent Server"
)


# ============================================================================
# MCP Tools - These expose ORBIT's capabilities to MCP clients
# ============================================================================

@mcp.tool()
async def query_orbit_agent(
    query: str,
    agent_type: str = "auto",
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
    from src.agents.agentRegistry import AgentRegistry
    from src.orchestrator import OrchestratorAgent
    from src.agents.intentAgent import IntentAgent
    from src.agents.troubleshootingAgent import TroubleshootingAgent
    from src.agents.orbitAgent import OrbitAgent
    from src.messages.query import QueryMessage
    from thespian.actors import ActorSystem
    
    # Build the complete query with context if provided
    complete_query = query
    if context:
        complete_query = f"{query}\n\nAdditional Context:\n{context}"
    
    # Load capabilities
    capabilities_path = Path(__file__).parent.parent / "capabilities.json"
    with open(capabilities_path, 'r') as f:
        capabilities = json.load(f)
    
    # Initialize actor system
    system = ActorSystem(capabilities=capabilities)
    
    try:
        # Register agents
        agent_registry = AgentRegistry()
        agent_registry.register_agent(
            "TroubleshootingAgent", 
            TroubleshootingAgent,
            description="Agent specialized in troubleshooting technical issues."
        )
        agent_registry.register_agent(
            "OrbitAgent", 
            OrbitAgent,
            description="Agent specialized in handling framework related queries and tasks."
        )
        
        # Create orchestrator and send query
        orchestrator_address = system.createActor(OrchestratorAgent)
        wrapped_query = QueryMessage(complete_query)
        
        # Wait for response with timeout
        response = system.ask(orchestrator_address, wrapped_query, timeout=120.0)
        
        return str(response) if response else "No response received from agent"
        
    except Exception as e:
        logger.error(f"Error in query_orbit_agent: {e}")
        return f"Error processing query: {str(e)}"
    finally:
        system.shutdown()


@mcp.tool()
async def analyze_repository(
    repo_url: str,
    analysis_type: str = "overview"
) -> str:
    """
    Analyze a GitHub repository using ORBIT's Repo2Text service.
    
    Args:
        repo_url: Full GitHub repository URL (e.g., https://github.com/user/repo)
        analysis_type: Type of analysis - "overview", "structure", "full"
    
    Returns:
        Repository analysis based on the requested type
    """
    from src.services.repo2Text import Repo2TextService
    
    try:
        service = Repo2TextService()
        result = service.call_service(repo_url)
        
        if analysis_type == "overview":
            return f"**Repository Summary:**\n{result.get('summary', 'No summary available')}"
        elif analysis_type == "structure":
            return f"**Repository Structure:**\n{result.get('structure', 'No structure available')}"
        else:  # full
            return f"""**Repository Analysis:**

**Summary:**
{result.get('summary', 'No summary available')}

**Structure:**
{result.get('structure', 'No structure available')}

**Content (truncated):**
{result.get('content', 'No content available')[:5000]}...
"""
    except Exception as e:
        logger.error(f"Error analyzing repository: {e}")
        return f"Error analyzing repository: {str(e)}"


@mcp.tool()
async def list_available_agents() -> str:
    """
    List all available ORBIT agents and their descriptions.
    
    Returns:
        JSON string containing agent names and descriptions
    """
    from src.agents.agentRegistry import AgentRegistry
    from src.agents.troubleshootingAgent import TroubleshootingAgent
    from src.agents.orbitAgent import OrbitAgent
    
    # Register agents
    agent_registry = AgentRegistry()
    agent_registry.register_agent(
        "TroubleshootingAgent", 
        TroubleshootingAgent,
        description="Agent specialized in troubleshooting technical issues, debugging code, and analyzing repositories for bugs."
    )
    agent_registry.register_agent(
        "OrbitAgent", 
        OrbitAgent,
        description="Agent specialized in handling framework related queries, explaining how to use ORBIT, and building custom agents."
    )
    
    agents = agent_registry.get_agents()
    agent_info = {name: info["description"] for name, info in agents.items()}
    
    return json.dumps(agent_info, indent=2)


# ============================================================================
# MCP Resources - Expose data/documentation via MCP
# ============================================================================

@mcp.resource("orbit://documentation/{doc_type}")
def get_documentation(doc_type: str) -> str:
    """
    Get ORBIT framework documentation.
    
    Args:
        doc_type: Type of documentation - "readme", "troubleshooting", "orbit", "intent"
    """
    base_path = Path(__file__).parent / "src"
    
    doc_paths = {
        "readme": base_path / "README.md",
        "troubleshooting": base_path / "agents/troubleshootingAgent/troubleshootingGuidelines.md",
        "orbit": base_path / "agents/orbitAgent/orbitAgentInstructions.md",
        "intent": base_path / "agents/intentAgent/intentAgentGuidelines.md"
    }
    
    if doc_type not in doc_paths:
        return f"Unknown documentation type: {doc_type}. Available: {list(doc_paths.keys())}"
    
    path = doc_paths[doc_type]
    if path.exists():
        return path.read_text()
    return f"Documentation file not found: {path}"


@mcp.resource("orbit://config")
def get_config() -> str:
    """Get ORBIT's current configuration."""
    config_path = Path(__file__).parent.parent / "capabilities.json"
    if config_path.exists():
        return config_path.read_text()
    return "{}"


# ============================================================================
# MCP Prompts - Reusable prompt templates
# ============================================================================

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
    prompt = f"""I need help troubleshooting the following issue:

**Error/Issue:**
{error_message}

"""
    if repo_urls:
        prompt += f"""**Related Repositories:**
{repo_urls}

"""
    if context:
        prompt += f"""**Additional Context:**
{context}

"""
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
    # Run with stdio transport (for Claude Desktop, etc.)
    mcp.run(transport="stdio")
