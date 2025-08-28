# pip install vellum-ai
import os

from vellum.client import Vellum
import vellum.types as types

# create your API key here: https://app.vellum.ai/organization?tab=workspaces&workspace-settings-tab=environments
client = Vellum(api_key="<your_api_key>")

result = client.execute_workflow(
    workflow_deployment_name="<workflow_deployment_name>",
    release_tag="LATEST",
    inputs=[
        types.WorkflowRequestStringInputRequest(
            name="user_message",
            type="STRING",
            value="First Message",
        ),
    ],
    previous_execution_id="<previous_execution_id>",
)

if result.data.state == "REJECTED":
    raise Exception(result.data.error.message)

print(result.data.outputs)
