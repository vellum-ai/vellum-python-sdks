from dotenv import load_dotenv

from .inputs import Inputs
from .workflow import MCPDemoWorkflow


def main():
    load_dotenv()
    workflow = MCPDemoWorkflow()

    while True:
        query = input("Hi! I'm an MCP Chatbot for Github. What can I do for you today? ")
        inputs = Inputs(query=query)

        event_filter_set = {"node.execution.fulfilled", "workflow.execution.fulfilled", "workflow.execution.rejected"}
        stream = workflow.stream(inputs=inputs, event_filter=lambda workflow, event: event.name in event_filter_set)
        is_rejected = False
        for event in stream:
            if event.name == "node.execution.fulfilled":
                can_think = any(o[0].name == "thinking" for o in event.outputs)
                if can_think:
                    print(
                        "Finished Node",
                        event.node_definition,
                        "thinking",
                        event.outputs["thinking"],
                    )  # noqa: T201
                else:
                    print(
                        "Finished Node",
                        event.node_definition,
                    )  # noqa: T201
            elif event.name == "workflow.execution.fulfilled":
                print(event.outputs["answer"])  # noqa: T201
            elif event.name == "workflow.execution.rejected":
                print("Workflow rejected", event.error.code, event.error.message)  # noqa: T201
                is_rejected = True

        if is_rejected:
            exit(1)


if __name__ == "__main__":
    main()
