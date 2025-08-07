# MCP Tool Calling Node Demo

This workflow demonstrates how to use the built-in `ToolCallingNode` with MCP (Model Context Protocol) servers. It's a simplified version that uses Vellum's native MCP integration instead of manual HTTP client implementation.

The workflow uses the GitHub MCP Server to manage the user's GitHub account through natural language commands.

To use locally, you should create a [GitHub personal access token](https://github.com/settings/personal-access-tokens) and save it in a local `.env` file:

```bash
VELLUM_API_KEY=***********************
GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_**********************
```

We include a `chat.py` file with the module for help running locally. Invoke it by running:

```bash
python -m examples.workflows.mcp_tool_calling_node_demo.chat
```

## Key Differences from Manual Implementation

This example shows how to use the built-in `ToolCallingNode` with `MCPServer` instead of manually implementing MCP client functionality:

1. **Simplified Architecture**: Uses `ToolCallingNode` which handles tool calling internally
2. **Native MCP Integration**: Uses `MCPServer` type for seamless MCP server integration
3. **Automatic Tool Discovery**: The `ToolCallingNode` automatically discovers and hydrates available tools from the MCP server
