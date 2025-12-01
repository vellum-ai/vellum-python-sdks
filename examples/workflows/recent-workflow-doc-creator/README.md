# Recent Workflow Documentation Creator

This workflow automatically creates GitHub pull requests to document recently deployed Vellum workflows.

## Description

A scheduled workflow that runs daily to:
1. Fetch all workflow deployments created in the last 24 hours
2. Process each deployment by fetching its workflow code
3. Use a GitHub agent to create pull requests with workflow examples

## Key Features

- **Scheduled Trigger**: Runs automatically at 10:00 AM Mountain Time daily
- **Map Node Pattern**: Processes multiple deployments concurrently (max concurrency of 4)
- **Tool-Calling Agent**: Uses Claude with GitHub integration tools to:
  - Create new branches
  - Commit workflow code and README files
  - Open pull requests
- **Parallel Outputs**: Returns multiple outputs simultaneously (PR URLs, comments, deployments JSON)

## Workflow Structure

```
Scheduled Trigger → FetchRecentDeployments → ProcessDeployments (Map) → {
    DeploymentsOutput,
    CommentsOutput,
    PrUrlsOutput
}
```

## Notable Patterns

1. **Subworkflow with Map Node**: The `ProcessDeployments` node is a Map Node that contains its own subworkflow for processing each deployment.

2. **Vellum Integration Tools**: Uses `VellumIntegrationToolDefinition` with Composio's GitHub integration for branch/file/PR operations.

3. **Custom Node Display**: Nodes use custom icons and colors for better visual organization in the UI.

4. **API Client Access**: Accesses the Vellum client via `self._context.vellum_client` for fetching deployment data.

## Use Case

This workflow is perfect for teams who want to automatically document their workflows as they're deployed, maintaining an up-to-date examples repository without manual intervention.