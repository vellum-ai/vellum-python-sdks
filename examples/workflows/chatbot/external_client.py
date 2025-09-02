import os
import time

from dotenv import load_dotenv

from vellum.client import Vellum
from vellum.client.types.workflow_request_string_input_request import WorkflowRequestStringInputRequest

load_dotenv()

client = Vellum(api_key=os.getenv("VELLUM_API_KEY"))
workflow_deployment_name = "<workflow_deployment_name>"
release_tag = "LATEST"


def main():
    previous_execution_id = None

    iterations = 1

    while True:
        print("--- New Message ---")

        user_message = input(f"Your message ({iterations}): ").strip()

        if user_message.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        if not user_message:
            print("Please type a message!")
            continue

        if previous_execution_id:
            print(f"Resuming from previous execution ID: {previous_execution_id}")
            result = client.execute_workflow(
                workflow_deployment_name=workflow_deployment_name,
                release_tag=release_tag,
                inputs=[
                    WorkflowRequestStringInputRequest(
                        name="user_message",
                        type="STRING",
                        value=user_message,
                    ),
                ],
                previous_execution_id=previous_execution_id,
            )
        else:
            print("Starting new conversation")
            result = client.execute_workflow(
                workflow_deployment_name=workflow_deployment_name,
                release_tag=release_tag,
                inputs=[
                    WorkflowRequestStringInputRequest(
                        name="user_message",
                        type="STRING",
                        value=user_message,
                    ),
                ],
            )

        current_execution_id = None

        if result.data.state == "FULFILLED":
            print("workflow.execution.fulfilled", result.data.outputs)
            current_execution_id = str(result.execution_id)

        print(f"Current Execution ID: {current_execution_id}")
        previous_execution_id = current_execution_id

        iterations += 1

        time.sleep(60)


if __name__ == "__main__":
    main()
