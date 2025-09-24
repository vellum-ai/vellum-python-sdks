# MCP Toolbox Agent Node Demo

This workflow demonstrates how to use the built-in `AgentNode` (ToolCallingNode) with [MCP Toolbox for databases](https://googleapis.github.io/genai-toolbox/getting-started/introduction/).

## Overview

This demo showcases the integration between Vellum's workflow and Google's MCP Toolbox, allowing you to create AI agents that can interact with databases through MCP (Model Context Protocol) tools.

## Setup

### Quickstart: Local Postgres via Docker

Build and run a local Postgres seeded with demo `hotels` data:

```bash
cd examples/workflows/mcp_toolbox/db
docker build -t mcp-demo-pg .
docker run --name mcp-demo-pg -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d mcp-demo-pg

cd ../../../../  # go back to vellum-python-sdks root dir
```

### Database and CLI Setup

Follow Step 1 and Step 2 in the instructions in [Setup](https://googleapis.github.io/genai-toolbox/getting-started/local_quickstart/#:~:text=aiplatform.googleapis.com-,Step%201%3A%20Set%20up%20your%20database,-In%20this%20section) to set up your database.

### Configure Tools

1. Modify the database configuration in `tools.yaml` according to your setup
2. Run the toolbox server:

```bash
toolbox --tools-file "tools.yaml"
```

## Usage

### Running the Demo

We include a `chat.py` file with the module for running locally. Invoke it by running:

```bash
# pip install vellum-ai if it's not in python environemnt yet
VELLUM_API_KEY=<your-api-key> python -m examples.workflows.mcp_toolbox.chat
```

### Example Queries

Once the workflow is running, you can ask questions like:

```
Find hotels in Basel with Basel in its name.
```
