from dotenv import load_dotenv

from .inputs import Inputs
from .workflow import MCPToolboxWorkflow


def main():
    load_dotenv()  # load your vellum api key
    workflow = MCPToolboxWorkflow()

    while True:
        query = input("Hi! I'm an your hotel booking assistant. What can I do for you today? ")
        inputs = Inputs(query=query)

        terminal_event = workflow.run(inputs=inputs)
        if terminal_event.name == "workflow.execution.fulfilled":
            print("Answer:", terminal_event.outputs["text"])
        elif terminal_event.name == "workflow.execution.rejected":
            print("Workflow rejected", terminal_event.error.code, terminal_event.error.message)


if __name__ == "__main__":
    main()
