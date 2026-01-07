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

---

## ✨ Features

- **Multi-Agent Architecture**: Modular agent system with specialized agents for different tasks
- **Intent Detection**: Automatic routing of queries to appropriate agents using AI
- **Multiple LLM Support**: Supports Ollama (Llama), GitHub Copilot, OpenAI, and Claude models
- **Actor Model**: Built on Thespian for concurrent, distributed agent communication
- **Chain of Responsibility**: Flexible message handling and validation pipeline
- **Repository Analysis**: Ingest and analyze GitHub repositories for context-aware responses

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
┌───────────────────────────────┐                   │
│         IntentAgent           │                   │
│  (Analyzes query & determines │                   │
│   which agent should handle)  │                   │
└───────────────────────────────┘                   │
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
cd /path/to/rbi

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
| `colorama` | Terminal color output |
| `art` | ASCII art generation |

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
rbi/
├── start.py                    # Application entry point
├── capabilities.json           # ActorSystem configuration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
│
├── agents/                     # Agent implementations
│   ├── agentRegistry.py        # Singleton registry for agent management
│   ├── intentAgent/            # Intent detection agent
│   │   ├── __init__.py
│   │   └── intentAgentGuidelines.md
│   ├── orbitAgent/             # Framework assistance agent
│   │   ├── __init__.py
│   │   └── orbitAgentInstructions.md
│   ├── troubleshootingAgent/   # Technical troubleshooting agent
│   │   ├── __init__.py
│   │   ├── troubleshootingGuidelines.md
│   │   └── repo_details.json
│   └── orchestrator/           # Main orchestration logic
│       ├── __init__.py
│       ├── messageTypeResolver.py
│       ├── queryMessageValidator.py
│       ├── intentAgentMessageValidator.py
│       ├── llmResponseValidator.py
│       └── actorMessageValidator.py
│
├── chain/                      # Chain of Responsibility pattern
│   └── baseHandler.py          # Base handler class
│
├── messages/                   # Message type definitions
│   ├── query.py                # User query message
│   ├── intent_agent_message.py # Intent detection result
│   ├── llm_message.py          # LLM response wrapper
│   └── agent_message.py        # Generic agent message
│
├── model/                      # LLM model adapters
│   ├── model_interface.py      # Abstract model interface
│   ├── model_adapter.py        # Adapter pattern implementation
│   ├── llama_model.py          # Ollama/Llama integration
│   ├── copilot_model.py        # GitHub Copilot integration
│   ├── open_ai.py              # OpenAI API integration
│   └── claude.py               # Anthropic Claude integration
│
├── services/                   # External service integrations
│   ├── service_interface.py    # Service interface
│   ├── file/                   # File operations service
│   │   └── __init__.py
│   └── repo2Text/              # Repository analysis service
│       └── __init__.py
│
└── temp/                       # Temporary files
    ├── copilot_token.txt       # Cached Copilot auth token
    └── llm_response.txt        # Last LLM response output
```

---

## 🤖 Building Custom Agents

### Step 1: Create Agent Directory

```bash
mkdir -p agents/myCustomAgent
touch agents/myCustomAgent/__init__.py
touch agents/myCustomAgent/guidelines.md
```

### Step 2: Implement the Agent

Create your agent in `agents/myCustomAgent/__init__.py`:

```python
from pathlib import Path
from messages.intent_agent_message import IntentAgentMessage
from messages.llm_message import LLMMessage
from model.copilot_model import CopilotModel
from model.model_adapter import ModelAdapter
from services.file import FileService
from thespian.actors import Actor
from loguru import logger


class MyCustomAgent(Actor):
    """
    Custom agent for handling specific domain queries.
    """

    def __init__(self):
        super().__init__()
        # Choose your model: CopilotModel, LlamaModel, etc.
        self.model = ModelAdapter(CopilotModel("gpt-4o"))
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

Create `agents/myCustomAgent/guidelines.md`:

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

In `start.py`, import and register your agent:

```python
from agents.myCustomAgent import MyCustomAgent

# In the main block, after creating the orchestrator:
agent_registry = AgentRegistry()
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
from model.llama_model import LlamaModel
from model.model_adapter import ModelAdapter

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
from model.copilot_model import CopilotModel
from model.model_adapter import ModelAdapter

model = ModelAdapter(CopilotModel("gpt-4o"))
```

### Creating a Custom Model Adapter

Implement the `ModelInterface`:

```python
from model.model_interface import ModelInterface

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
from services.file import FileService

fs = FileService()
content = fs.read_file("path/to/file.txt")
data = fs.read_json_file("path/to/config.json")
fs.write_file("path/to/output.txt", "content")
```

### Repo2TextService

Convert GitHub repositories to text for LLM context:

```python
from services.repo2Text import Repo2TextService

service = Repo2TextService()
result = service.call_service("https://github.com/user/repo")
# Returns: {"summary": ..., "structure": ..., "content": ...}
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
from chain.baseHandler import BaseHandler
from messages.my_message import MyMessage

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

## 📝 License

[Add your license here]

---

## 🤝 Contributing

[Add contribution guidelines here]

---

## 📧 Contact

[kartikeya Sharma]