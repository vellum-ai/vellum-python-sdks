# MCP Demo

This Workflow is an example of how to use a Vellum Workflow as an [MCP](https://modelcontextprotocol.io/introduction) Client. It depends on the [Github MCP Server](https://github.com/github/github-mcp-server) for performing actions on the user's GitHub account on their behalf.

To use locally, you should create a [GitHub personal access token](https://github.com/settings/personal-access-tokens) and save it in a local `.env` file:

```bash
VELLUM_API_KEY=***********************
GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_**********************
```

We include a `chat.py` file with the module for help running locally. Invoke it by running:

```bash
python -m mcp_demo.chat
```
