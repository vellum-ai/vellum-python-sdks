from dotenv import load_dotenv

from vellum.workflows.workflows.event_filters import root_workflow_event_filter

from .inputs import Inputs
from .workflow import IndeedWorkflow


def main():
    load_dotenv()
    workflow = IndeedWorkflow()

    while True:
        query = input("Hi! I'm an Indeed Chatbot. What can I do for you today? ")
        inputs = Inputs(query=query)

        stream = workflow.stream(inputs=inputs, event_filter=root_workflow_event_filter)
        error = None
        for event in stream:
            if event.name == "node.execution.fulfilled":
                print("Finished Node", event.node_definition)  # noqa: T201
            elif event.name == "workflow.execution.fulfilled":
                print(event.outputs["answer"])  # noqa: T201
            elif event.name == "workflow.execution.rejected":
                error = event.error.message

        if error:
            raise Exception(error)


if __name__ == "__main__":
    main()
