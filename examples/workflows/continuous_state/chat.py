import time

from dotenv import load_dotenv

from .workflow.inputs import Inputs
from .workflow.workflow import Workflow


def main():
    load_dotenv()
    previous_execution_id = None

    iterations = 0

    while True:
        print("--- New Message ---")

        user_message = input(f"Your message ({iterations}): ").strip()

        if user_message.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        if not user_message:
            print("Please type a message!")
            continue

        workflow = Workflow()

        if previous_execution_id:
            print(f"Resuming from previous execution ID: {previous_execution_id}")
            events = list(
                workflow.stream(inputs=Inputs(user_message=user_message), previous_execution_id=previous_execution_id)
            )
        else:
            print("Starting new conversation")
            events = list(workflow.stream(inputs=Inputs(user_message=user_message)))

        current_execution_id = None

        initiated_event = next(event for event in events if event.name == "workflow.execution.initiated")
        if initiated_event:
            current_execution_id = str(initiated_event.span_id)

        fulfilled_event = next(event for event in events if event.name == "workflow.execution.fulfilled")
        if fulfilled_event:
            print("fulfilled_event.outputs", fulfilled_event.outputs)

        print(f"Current Execution ID: {current_execution_id}")
        previous_execution_id = current_execution_id

        iterations += 1

        time.sleep(60)


if __name__ == "__main__":
    main()
