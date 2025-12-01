# Recent Workflow Doc Creator

A scheduled workflow that automatically creates GitHub pull requests to document recently deployed Vellum workflows.

## Overview

This workflow runs on a daily schedule (10:00 AM Denver time) and:

1. **Fetches Recent Deployments**: Queries the Vellum API to find all workflow deployments created in the last 24 hours.

2. **Processes Each Deployment**: Uses a MapNode to process each deployment concurrently (up to 4 at a time):
   - Fetches the workflow code using the Vellum pull API
   - Uses an AI agent with GitHub tools to create a PR

3. **Outputs Results**: Returns PR URLs, processing counts, and raw deployment data.

## Notable Features & Patterns

### 1. Scheduled Trigger
```python
class Scheduled(ScheduleTrigger):
    class Config(ScheduleTrigger.Config):
        cron = "0 10 * * *"
        timezone = "America/Denver"
```
Demonstrates how to set up cron-based scheduling with timezone support.

### 2. MapNode for Parallel Processing
```python
class ProcessDeployments(MapNode):
    items = FetchRecentDeployments.Outputs.deployments
    subworkflow = ProcessDeploymentsWorkflow
    max_concurrency = 4
```
Shows how to use MapNode to process a list of items in parallel with concurrency limits.

### 3. ToolCallingNode with External Integrations
```python
class GitHubAgent(ToolCallingNode):
    ml_model = "claude-opus-4-5-20251101"
    functions = [
        VellumIntegrationToolDefinition(
            provider="COMPOSIO",
            integration_name="GITHUB",
            name="GITHUB_CREATE_A_PULL_REQUEST",
            ...
        ),
    ]
```
Demonstrates using `ToolCallingNode` with Composio integrations to give an AI agent access to GitHub API operations.

### 4. Nested Subworkflows
The `ProcessDeploymentsWorkflow` is a complete subworkflow with its own inputs, nodes, and outputs, demonstrating how to compose complex workflows from smaller, reusable pieces.

### 5. Custom BaseNode with API Calls
```python
class FetchRecentDeployments(BaseNode):
    def run(self) -> Outputs:
        client = self._context.vellum_client
        # ... paginated AP