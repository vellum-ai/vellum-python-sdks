import sys
import time

from vellum.client.types import ChatMessage
from vellum.workflows.emitters.vellum_emitter import VellumEmitter  # local SDK emitter

from .inputs import Inputs
from .workflow import Workflow

print("Trust Center Q&A Local Demo (Zero-Config Monitoring)")
print("=" * 50)

print("\nCreating Trust Center Q&A workflow...")
# Explicitly pass the local VellumEmitter instance so the workflow uses it
workflow = Workflow(emitters=[VellumEmitter()])

print("\nRunning Trust Center Q&A workflow...")
print("   (Monitoring URL will be printed automatically if enabled)")

# Minimal required inputs for this workflow
sample_question = "What security certifications does Vellum have?"
inputs = Inputs(chat_history=[ChatMessage(role="USER", text=sample_question)])

# Run the workflow - monitoring URL will be automatically printed!
result = workflow.run(inputs=inputs)

print(f"\nWorkflow completed! \n")


span_id = str(getattr(result, "span_id", ""))
if span_id:
    # Make sure all events are published to clickhouse before printing the link.
    print("   Preparing Monitoring URL. Waiting ~15 seconds so all events can be published to clickchouse...")
    print("   If details fail to load, refresh the page a few times until it shows up.\n")

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start_time = time.time()
    i = 0
    while time.time() - start_time < 15:
        dots = "." * (i % 10)
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r   {frame} Publishing events{dots:<9}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r   ✓ Events published. Generating link...       \n")

    url = workflow.context.get_monitoring_url(span_id)
    if url:
        print(f"   Monitoring URL: {url} \n")
else:
    print("   No span_id available to construct monitoring URL.\n")

print("\nTrust Center Q&A demo complete!")
