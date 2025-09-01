import time

from dotenv import load_dotenv

from vellum.workflows.emitters.vellum_emitter import VellumEmitter
from vellum.workflows.resolvers.resolver import VellumResolver

from .inputs import Inputs
from .workflow import Workflow


def main():
    load_dotenv()
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

        workflow = Workflow(
            emitters=[VellumEmitter()], resolvers=[VellumResolver()]  # needed for sdk first  # needed for sdk first
        )

        if previous_execution_id:
            print(f"Resuming from previous execution ID: {previous_execution_id}")
            terminal_event = workflow.run(
                inputs=Inputs(user_message=user_message), previous_execution_id=previous_execution_id
            )
        else:
            print("Starting new conversation")
            terminal_event = workflow.run(inputs=Inputs(user_message=user_message))

        current_execution_id = None

        if terminal_event.name == "workflow.execution.fulfilled":
            print("workflow.execution.fulfilled", terminal_event.outputs)
            current_execution_id = str(terminal_event.span_id)

        print(f"Current Execution ID: {current_execution_id}")
        previous_execution_id = current_execution_id

        iterations += 1

        time.sleep(60)


if __name__ == "__main__":
    main()
