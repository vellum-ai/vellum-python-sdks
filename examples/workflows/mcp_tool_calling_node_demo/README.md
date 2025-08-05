# MCP tool calling node Demo (WIP)


This Workflow is similar to `mcp_demo` but without using mcp sdk.

To use locally, you should create a [GitHub personal access token](https://github.com/settings/personal-access-tokens) and save it in a local `.env` file:

```bash
VELLUM_API_KEY=***********************
GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_**********************
```

We include a `chat.py` file with the module for help running locally. Invoke it by running:

```bash
python -m mcp_without_sdk.chat
```
