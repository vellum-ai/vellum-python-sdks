# Chatbot Example

This workflow demonstrates how to use Vellum's **previous execution ID** functionality to maintain conversation context across multiple workflow executions.

## Key Features

- **State Persistence**: Automatically loads and restores state using previous execution IDs
- **Continuous Conversations**: Maintain ongoing conversations across multiple workflow runs


## external_client.py

Remote API client for calling deployed Vellum workflows from applications.

### 1. Deploy the Workflow
```bash
vellum workflows push examples.workflows.continuous_chatbot_external --deploy
```

### 2. First Execution
Trigger with any message to get an execution ID:
python -m chatbot.external_client
```bash
# You'll see output like:
# WorkflowOutputJson(id='...', name='response', value=['First Message'])
```

**To get the execution ID:**
1. Go to your Vellum dashboard
2. Navigate to **Workflows** → **Deployments** → **Executions**
3. Find your recent execution and copy the execution ID

### 3. Continue Conversation
Use the execution ID from step 3 to continue the conversation:
```python
result = client.execute_workflow(
    workflow_deployment_name="your-deployment-name",
    release_tag="LATEST",
    inputs=[
        types.WorkflowRequestStringInputRequest(
            name="user_message",
            value="Second message",
        ),
    ],
    previous_execution_id="execution-id-from-step-2",
)
```

### 4. Verify State Persistence
The response will now include both messages:
```
WorkflowOutputJson(id='...', name='response', value=['User: First Message', 'User: Second Message'])
```

## chat.py

Local interactive chat interface for testing workflow state persistence locally.

### 1. Running the Example

```bash
python -m chatbot.chat
```

### 2. Conversation Flow

```
First message
```

```
Second message
```

You should see the response include both message
