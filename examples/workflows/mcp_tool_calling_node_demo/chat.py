from dotenv import load_dotenv

from .inputs import Inputs
from .workflow import MCPDemoWorkflow


def main():
    load_dotenv()
    workflow = MCPDemoWorkflow()

    while True:
        query = input("Hi! I'm an MCP Chatbot for Github. What can I do for you today? ")
        inputs = Inputs(query=query)

        event_filter_set = {"workflow.execution.fulfilled", "workflow.execution.rejected"}
        stream = workflow.stream(inputs=inputs, event_filter=lambda workflow, event: event.name in event_filter_set)
        is_rejected = False
        for event in stream:
            if event.name == "workflow.execution.fulfilled":
                print("Answer:", event.outputs["text"])  # noqa: T201
                print("Chat History Length:", len(event.outputs["chat_history"]))  # noqa: T201
            elif event.name == "workflow.execution.rejected":
                print("Workflow rejected", event.error.code, event.error.message)  # noqa: T201
                is_rejected = True

        if is_rejected:
            exit(1)


if __name__ == "__main__":
    main()
