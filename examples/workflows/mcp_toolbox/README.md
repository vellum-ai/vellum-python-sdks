# MCP Tool Calling Node Demo

This workflow demonstrates how to use the built-in `AgentNode` (ToolCallingNode) with [MCP Toolbox for databases](https://googleapis.github.io/genai-toolbox/getting-started/introduction/).

## Overview

This demo showcases the integration between Vellum's workflow and Google's MCP Toolbox, allowing you to create AI agents that can interact with databases through MCP (Model Context Protocol) tools.

## Setup

### 1. Database and CLI Setup

Follow Step 1 and Step 2 in the instructions in [Setup](https://googleapis.github.io/genai-toolbox/getting-started/local_quickstart/#:~:text=aiplatform.googleapis.com-,Step%201%3A%20Set%20up%20your%20database,-In%20this%20section) to set up your database.

### 3. Configure Tools

1. Modify the database configuration in `tools.yaml` according to your setup
2. Run the toolbox server:

```bash
toolbox --tools-file "tools.yaml"
```

## Usage

### Running the Demo

We include a `chat.py` file with the module for running locally. Invoke it by running:

```bash
python -m examples.workflows.mcp_tool_calling_node_demo.chat
```

### Example Queries

Once the demo is running, you can ask questions like:

```
Find hotels in Basel with Basel in its name.
```
