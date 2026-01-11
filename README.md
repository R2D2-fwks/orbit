# 🚀 ORBIT - Multi-Agent Orchestration Framework

ORBIT is an intelligent multi-agent orchestration framework built using the **Actor Model** pattern with [Thespian](https://thespianpy.com/doc/). It enables dynamic routing of user queries to specialized AI agents based on intent detection, leveraging Large Language Models (LLMs) for intelligent response generation.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture Overview](#-architecture-overview)
- [Code Flow](#-code-flow)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [1. Create Conda Environment](#1-create-conda-environment)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
  - [4. Setup Local LLM (Optional)](#4-setup-local-llm-optional)
- [Running the Application](#-running-the-application)
- [Project Structure](#-project-structure)
- [Building Custom Agents](#-building-custom-agents)
- [Model Adapters](#-model-adapters)
- [Services](#-services)
- [Message Types](#-message-types)
- [Chain of Responsibility Pattern](#-chain-of-responsibility-pattern)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## ✨ Features

- **Multi-Agent Architecture**: Modular agent system with specialized agents for different tasks
- **Intent Detection**: Automatic routing of queries to appropriate agents using AI
- **Multiple LLM Support**: Supports Ollama (Llama), GitHub Copilot, OpenAI, and Claude models
- **Actor Model**: Built on Thespian for concurrent, distributed agent communication
- **Chain of Responsibility**: Flexible message handling and validation pipeline
- **Repository Analysis**: Ingest and analyze GitHub repositories for context-aware responses
- **MCP Integration**: Model Context Protocol support for external tool integration

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Query                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OrchestratorAgent                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           Chain of Responsibility Validators            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │    │
│  │  │ LLMResponse  │──│   Query      │──│   Intent     │  │    │
│  │  │  Validator   │  │  Validator   │  │  Validator   │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
            ┌───────────────────┴───────────────────┐
            │ QueryValidator routes                 │
            │ QueryMessage to IntentAgent           │
            ▼                                       │
┌───────────────────────────────────┐               │
│         IntentAgent               │               │
│  (Analyzes query & determines     │               │
│   which agent should handle)      │               │
└───────────────────────────────────┘               │
            │                                       │
            │ Returns IntentAgentMessage            │
            │ (contains target agent name)          │
            ▼                                       │
┌─────────────────────────────────────────────────────────────────┐
│                    OrchestratorAgent                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  IntentAgentMessageValidator identifies sender,         │    │
│  │  creates the target agent & forwards the query          │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │  OrbitAgent  │ │Troubleshooting│ │ CustomAgent  │
        │              │ │    Agent     │ │   (Yours)    │
        └──────────────┘ └──────────────┘ └──────────────┘
                │               │               │
                │         LLM Processing        │
                └───────────────┼───────────────┘
                                │
                                ▼ Returns LLMMessage
┌─────────────────────────────────────────────────────────────────┐
│                    OrchestratorAgent                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  LLMResponseValidator extracts response & sends to user │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                        ┌──────────────┐
                        │    User      │
                        │  (Response)  │
                        └──────────────┘
```

---

## 🔄 Code Flow

### 1. **Application Startup** (`start.py`)
   - Initializes the Thespian ActorSystem with capabilities from `capabilities.json`
   - Creates the `OrchestratorAgent` as the main entry point
   - Registers specialized agents in the `AgentRegistry`
   - Prompts user for a query and wraps it in a `QueryMessage`

### 2. **Query Processing**
   ```
   QueryMessage → OrchestratorAgent → MessageTypeResolver (Chain of Responsibility)
   ```

### 3. **Intent Detection**
   - `QueryMessageValidator` routes `QueryMessage` to `IntentAgent`
   - `IntentAgent` uses an LLM to analyze the query and determine the appropriate agent
   - Returns an `IntentAgentMessage` with the target agent name

### 4. **Agent Routing**
   - `IntentAgentMessageValidator` receives the intent response
   - Looks up the target agent from `AgentRegistry`
   - Creates and forwards the query to the specialized agent

### 5. **Specialized Agent Processing**
   - The target agent (e.g., `OrbitAgent`, `TroubleshootingAgent`) processes the query
   - May fetch repository data using `Repo2TextService`
   - Generates response using configured LLM
   - Returns `LLMMessage` to orchestrator

### 6. **Response Delivery**
   - `LLMResponseValidator` extracts the final response
   - Response is sent back to the original sender (user)

---

## 📦 Prerequisites

- **Python 3.13+**
- **Conda** (Miniconda or Anaconda)
- **Git**
- **Ollama** (for local LLM - optional)
- **GitHub Personal Access Token** (for repository analysis)

---

## 🛠 Installation

### 1. Create Conda Environment

```bash
# Create a new conda environment with Python 3.13
conda create -n actorenv python=3.13

# Activate the environment
conda activate actorenv
```

**Verify installation:**
```bash
python --version
# Should output: Python 3.13.x
```

### 2. Install Dependencies

```bash
# Navigate to the project directory
cd /path/to/orbit

# Install all required packages
pip install -r requirements.txt
```

**Key Dependencies:**
| Package | Purpose |
|---------|---------|
| `thespian` | Actor model framework for agent communication |
| `openai` | OpenAI API client |
| `anthropic` | Claude API client |
| `ghcopilot` | GitHub Copilot integration |
| `gitingest` | Repository-to-text conversion |
| `loguru` | Logging framework |
| `tiktoken` | Token counting for LLM context management |
| `python-dotenv` | Environment variable management |
| `mcp` | Model Context Protocol SDK |

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following configuration:

```env
# GitHub Personal Access Token (Required for repository analysis)
PAT_TOKEN=your_github_personal_access_token

# OpenAI API Key (Optional - if using OpenAI models)
OPENAI_API_KEY=your_openai_api_key

# Anthropic API Key (Optional - if using Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key

# Default timeout for operations
DEFAULT_TIMEOUT=300
```

**To generate a GitHub PAT:**
1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens
2. Generate a new token with `repo` scope
3. Copy and paste into `.env` file

### 4. Setup Local LLM (Optional)

If using Ollama for local LLM inference:

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama server
ollama serve

# Pull the Llama model (in a new terminal)
ollama pull llama3
```

The default configuration expects Ollama running at `http://127.0.0.1:11434`.

---

## 🚀 Running the Application

```bash
# Ensure conda environment is active
conda activate actorenv

# Run the application
python start.py
```

**Expected Output:**
```
  ___  ____  ____  ___ _____ _  _
 / _ \|  _ \| __ )_ _|_   _| || |
| | | | |_) |  _ \| |  | | | || |_
| |_| |  _ <| |_) | |  | | |__   _|
 \___/|_| \_\____/___| |_|    |_|

Welcome...
To ORBIT

Press any key to continue . . .
```

Enter your query when prompted, and ORBIT will route it to the appropriate agent.

---

## 📁 Project Structure

```
orbit/
├── start.py                    # Application entry point
├── start_mcp_server.py         # MCP server for external integration
├── capabilities.json           # ActorSystem configuration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
│
├── src/
│   ├── actor_system/           # Actor system initialization
│   │   └── __init__.py
│   │
│   ├── agent_registry/         # Agent registration and discovery
│   │   ├── __init__.py
│   │   └── register.py
│   │
│   ├── agents/                 # Agent implementations
│   │   ├── intentAgent/        # Intent detection agent
│   │   │   ├── __init__.py
│   │   │   └── intentAgentGuidelines.md
│   │   ├── orbitAgent/         # Framework assistance agent
│   │   │   ├── __init__.py
│   │   │   └── orbitAgentInstructions.md
│   │   ├── troubleshootingAgent/   # Technical troubleshooting agent
│   │   │   ├── __init__.py
│   │   │   ├── troubleshootingGuidelines.md
│   │   │   └── repo_details.json
│   │   └── mcpToolsAgent/      # MCP tools integration agent
│   │       ├── __init__.py
│   │       └── mcpToolsAgentGuidelines.md
│   │
│   ├── orchestrator/           # Main orchestration logic
│   │   ├── __init__.py
│   │   ├── messageTypeResolver.py
│   │   ├── queryMessageValidator.py
│   │   ├── intentAgentMessageValidator.py
│   │   ├── llmResponseValidator.py
│   │   └── actorMessageValidator.py
│   │
│   ├── chain/                  # Chain of Responsibility pattern
│   │   └── baseHandler.py
│   │
│   ├── messages/               # Message type definitions
│   │   ├── query.py
│   │   ├── intent_agent_message.py
│   │   └── llm_message.py
│   │
│   ├── model/                  # LLM model adapters
│   │   ├── model_interface.py
│   │   ├── model_adapter.py
│   │   ├── llama_model.py
│   │   ├── copilot_model.py
│   │   ├── open_ai.py
│   │   └── claude.py
│   │
│   └── services/               # External service integrations
│       ├── service_interface.py
│       ├── file/
│       ├── repo2Text/
│       ├── mcp_client/
│       └── singleton/
│
└── temp/                       # Temporary files
```

---

## 🤖 Building Custom Agents

### Step 1: Create Agent Directory

```bash
mkdir -p src/agents/myCustomAgent
touch src/agents/myCustomAgent/__init__.py
touch src/agents/myCustomAgent/guidelines.md
```

### Step 2: Implement the Agent

Create your agent in `src/agents/myCustomAgent/__init__.py`:

```python
from pathlib import Path
from src.messages.intent_agent_message import IntentAgentMessage
from src.messages.llm_message import LLMMessage
from src.model.llama_model import LlamaModel
from src.model.model_adapter import ModelAdapter
from src.services.file import FileService
from thespian.actors import Actor
from loguru import logger


class MyCustomAgent(Actor):
    """
    Custom agent for handling specific domain queries.
    """

    def __init__(self):
        super().__init__()
        self.model = ModelAdapter(LlamaModel())
        self.agent_name = "MyCustomAgent"

    def receiveMessage(self, message, sender):
        """
        Handle incoming messages from the orchestrator.
        
        Args:
            message: The incoming message (usually IntentAgentMessage)
            sender: The address of the sending actor
        """
        if isinstance(message, IntentAgentMessage):
            query = message.query
            logger.info(f"[{self.agent_name}] Received query: {query}")
            
            # Load agent-specific instructions
            file_path = Path(__file__).parent
            instructions = FileService().read_file(file_path / "guidelines.md")
            
            # Add any custom context or data processing here
            complete_prompt = f"User Query: {query}"
            
            # Generate response using LLM
            response_text = self.model.generate(
                prompt=complete_prompt,
                instruction=instructions
            )
            
            # Wrap and send response back
            response = LLMMessage(response_text)
            self.send(sender, response)
        else:
            self.send(sender, f"Unknown message type for {self.agent_name}")
```

### Step 3: Create Guidelines

Create `src/agents/myCustomAgent/guidelines.md`:

```markdown
# MyCustomAgent Guidelines

You are a specialized agent for [your domain].

## Your Responsibilities:
- Handle queries related to [specific topic]
- Provide detailed and accurate responses
- Reference relevant documentation when available

## Response Format:
- Be concise but thorough
- Use code examples when applicable
- Structure your response with clear sections
```

### Step 4: Register the Agent

In `src/agent_registry/__init__.py`, register your agent:

```python
from src.agent_registry.register import AgentRegistry
from src.agents.myCustomAgent import MyCustomAgent

def register_agents():
    agent_registry = AgentRegistry()
    
    # ... existing registrations ...
    
    agent_registry.register_agent(
        "MyCustomAgent",
        MyCustomAgent,
        description="Agent specialized in [your domain description]."
    )
```

### Step 5: Update Intent Agent

The `IntentAgent` will automatically consider your new agent based on its description in the registry. Ensure the description clearly indicates when to use your agent.

---

## 🔌 Model Adapters

The framework supports multiple LLM backends through the adapter pattern:

### Using Ollama (Local LLM)
```python
from src.model.llama_model import LlamaModel
from src.model.model_adapter import ModelAdapter

# Default: llama3 on localhost:11434
model = ModelAdapter(LlamaModel())

# Custom model and URL
model = ModelAdapter(LlamaModel(
    model_name="codellama",
    model_url="http://192.168.1.100:11434"
))
```

### Using GitHub Copilot
```python
from src.model.copilot_model import CopilotModel
from src.model.model_adapter import ModelAdapter

model = ModelAdapter(CopilotModel("gpt-4o"))
```

### Creating a Custom Model Adapter

Implement the `ModelInterface`:

```python
from src.model.model_interface import ModelInterface

class MyCustomModel(ModelInterface):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate(self, prompt: str, instruction: str) -> str:
        """Single-turn generation"""
        # Your implementation here
        pass

    def chat(self, prompt: str, instruction: str) -> str:
        """Multi-turn conversation"""
        # Your implementation here
        pass
```

---

## 🔧 Services

### FileService

File I/O operations:

```python
from src.services.file import FileService

fs = FileService()
content = fs.read_file("path/to/file.txt")
data = fs.read_json_file("path/to/config.json")
fs.write_file("path/to/output.txt", "content")
```

### Repo2TextService

Convert GitHub repositories to text for LLM context:

```python
from src.services.repo2Text import Repo2TextService

service = Repo2TextService()
result = service.call_service("https://github.com/user/repo", {"max_file_size": 5 * 1024 * 1024})
# Returns: {"summary": ..., "structure": ..., "content": ...}
```

### MCPClientService

Connect to external MCP servers:

```python
from src.services.mcp_client import MCPClientService

service = MCPClientService()
await service.connect_stdio_server(
    name="github",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": "token"}
)
```

---

## 📨 Message Types

| Message Type | Purpose | Flow |
|--------------|---------|------|
| `QueryMessage` | Wraps user's initial query | User → Orchestrator → IntentAgent |
| `IntentAgentMessage` | Contains detected intent and target agent | IntentAgent → Orchestrator |
| `LLMMessage` | Wraps LLM response | SpecializedAgent → Orchestrator → User |

---

## ⛓ Chain of Responsibility Pattern

The orchestrator uses the Chain of Responsibility pattern for message handling:

```
LLMResponseValidator → QueryMessageValidator → ActorMessageValidator → IntentAgentMessageValidator
```

Each validator checks if it can handle the message type:
- **LLMResponseValidator**: Extracts final response from `LLMMessage`
- **QueryMessageValidator**: Routes `QueryMessage` to `IntentAgent`
- **ActorMessageValidator**: Handles Thespian system messages
- **IntentAgentMessageValidator**: Creates and routes to specialized agents

### Creating Custom Validators

```python
from src.chain.baseHandler import BaseHandler
from src.messages.my_message import MyMessage

class MyMessageValidator(BaseHandler):
    def handle(self, context):
        message, orchestrator_self, sender = context
        
        if isinstance(message, MyMessage):
            # Handle your custom message
            return context
            
        # Pass to next handler in chain
        return super().handle(context)
```

Register in `messageTypeResolver.py`:
```python
my_validator = MyMessageValidator()
# Add to chain: .set_next(my_validator)
```

---

## 🤝 Contributing

We welcome contributions to ORBIT! This section provides guidelines for contributing to the project.

### Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. We expect all contributors to:

- Be respectful and considerate in all interactions
- Welcome newcomers and help them get started
- Focus on constructive feedback and collaboration
- Accept responsibility for mistakes and learn from them

### How to Contribute

#### 1. Reporting Issues

Before creating an issue, please:

- Search existing issues to avoid duplicates
- Use the issue templates when available
- Provide detailed information including:
  - Clear description of the problem or suggestion
  - Steps to reproduce (for bugs)
  - Expected vs actual behavior
  - Environment details (OS, Python version, etc.)
  - Relevant logs or error messages

**Issue Labels:**
| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or improvement |
| `documentation` | Documentation updates |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention needed |
| `agent` | Related to agent development |
| `model` | Related to LLM integrations |

#### 2. Setting Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/orbit.git
cd orbit

# Create development environment
conda create -n orbit-dev python=3.13
conda activate orbit-dev

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black isort flake8 mypy

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

#### 3. Development Workflow

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number-description
   ```

2. **Make your changes** following our coding standards (see below)

3. **Test your changes**:
   ```bash
   # Run tests
   pytest tests/
   
   # Run with coverage
   pytest --cov=src tests/
   ```

4. **Format your code**:
   ```bash
   # Format with black
   black src/ tests/
   
   # Sort imports
   isort src/ tests/
   
   # Check linting
   flake8 src/ tests/
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "type: brief description of changes"
   ```

#### 4. Commit Message Convention

Follow the conventional commits specification:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting, etc.) |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |
| `agent` | Agent-related changes |
| `model` | Model adapter changes |

**Examples:**
```
feat(agent): add MCPToolsAgent for external tool integration
fix(orchestrator): resolve message routing deadlock
docs: update README with MCP integration guide
refactor(model): extract common LLM interface methods
```

#### 5. Pull Request Process

1. **Update documentation** if your changes affect it

2. **Ensure all tests pass** and add new tests for new functionality

3. **Create Pull Request** with:
   - Clear title following commit convention
   - Description of changes and motivation
   - Reference to related issues (e.g., "Fixes #123")
   - Screenshots/recordings for UI changes

4. **PR Review Checklist:**
   - [ ] Code follows project style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex logic
   - [ ] Documentation updated
   - [ ] Tests added/updated
   - [ ] No breaking changes (or documented if necessary)

5. **Address review feedback** promptly and respectfully

### Coding Standards

#### Python Style Guide

- Follow [PEP 8](https://pep8.org/) guidelines
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use docstrings for all public functions and classes

```python
from typing import Dict, Optional
from loguru import logger


class ExampleAgent(Actor):
    """
    A well-documented agent class.
    
    Attributes:
        model: The LLM model adapter
        agent_name: Unique identifier for this agent
    """
    
    def __init__(self, model_name: str = "llama3") -> None:
        """
        Initialize the agent.
        
        Args:
            model_name: Name of the LLM model to use
        """
        super().__init__()
        self.model = ModelAdapter(LlamaModel(model_name))
        self.agent_name = "ExampleAgent"
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Process a user query.
        
        Args:
            query: The user's input query
            context: Optional additional context
            
        Returns:
            The generated response string
            
        Raises:
            ValueError: If query is empty
        """
        if not query:
            raise ValueError("Query cannot be empty")
        
        logger.info(f"[{self.agent_name}] Processing query: {query}")
        return self.model.generate(query, self._get_instructions())
```

#### Agent Development Guidelines

When creating new agents:

1. **Inherit from `Actor`** base class
2. **Implement `receiveMessage`** method
3. **Create guidelines file** (`.md`) for LLM instructions
4. **Register in `agent_registry`** with clear description
5. **Handle errors gracefully** and log appropriately
6. **Return `LLMMessage`** for responses

```python
# Template for new agents
from thespian.actors import Actor
from src.messages.intent_agent_message import IntentAgentMessage
from src.messages.llm_message import LLMMessage
from loguru import logger


class NewAgent(Actor):
    def __init__(self):
        super().__init__()
        self.agent_name = "NewAgent"
    
    def receiveMessage(self, message, sender):
        try:
            if isinstance(message, IntentAgentMessage):
                response = self._process(message.query)
                self.send(sender, LLMMessage(response))
            else:
                logger.warning(f"[{self.agent_name}] Unknown message type")
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error: {e}")
            self.send(sender, LLMMessage(f"Error processing request: {e}"))
```

#### File Organization

- Place agents in `src/agents/<agent_name>/`
- Place services in `src/services/<service_name>/`
- Place message types in `src/messages/`
- Place model adapters in `src/model/`
- Keep tests mirroring source structure in `tests/`

### Types of Contributions

#### 🐛 Bug Fixes
- Fix issues in existing functionality
- Improve error handling
- Resolve edge cases

#### ✨ New Features
- New agents for specialized domains
- Additional LLM model integrations
- New services and utilities
- MCP server/tool integrations

#### 📚 Documentation
- Improve existing documentation
- Add examples and tutorials
- Translate documentation
- Create video guides

#### 🧪 Testing
- Add unit tests
- Add integration tests
- Improve test coverage
- Performance testing

#### 🎨 UI/UX (for future GUI)
- Design improvements
- Accessibility enhancements
- User experience optimizations

### Getting Help

- **Questions**: Open a [Discussion](https://github.com/R2D2-fwks/orbit/discussions)
- **Bugs**: Open an [Issue](https://github.com/R2D2-fwks/orbit/issues)
- **Security**: Email security concerns privately (do not open public issues)

### Recognition

Contributors will be recognized in:
- The project's CONTRIBUTORS.md file
- Release notes for significant contributions
- Special acknowledgment for first-time contributors

---

---

## 📧 Contact

**Kartikeya Sharma**

- **GitHub**: [@R2D2-fwks](https://github.com/R2D2-fwks)
- **Project Link**: [https://github.com/R2D2-fwks/orbit](https://github.com/R2D2-fwks/orbit)

### Acknowledgments

- [Thespian](https://thespianpy.com/doc/) - Actor model framework
- [Anthropic](https://www.anthropic.com/) - Claude AI models
- [OpenAI](https://openai.com/) - GPT models
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification

---

<p align="center">
  Made with ❤️ by the ORBIT team
</p>